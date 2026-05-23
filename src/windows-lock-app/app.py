import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from countdown import format_seconds
from daily_limit_screen import DailyLimitScreen
from lock_screen import LockScreen, REGULAR_BREAK_MESSAGE
from parent_auth import configured_parent_password, verify_parent_password
from reporting import (
    APP_STARTED_EVENT,
    DAILY_LIMIT_STARTED_EVENT,
    EventLogger,
    PARENT_ACTION_DENIED_EVENT,
    PARENT_EXIT_ALLOWED_EVENT,
    PARENT_EXTRA_GRANTED_EVENT,
    REGULAR_LOCK_RELEASED_EVENT,
    REGULAR_LOCK_STARTED_EVENT,
    TEST_LOCK_STARTED_EVENT,
    USAGE_EVENT,
)
from usage_timer import UsageTimer, UsageTimerSettings


def env_seconds(name, default):
    value = os.environ.get(name)
    if value:
        try:
            return max(1, int(value))
        except ValueError:
            pass
    return default


def build_timer_settings():
    return UsageTimerSettings(
        work_seconds=env_seconds("LOCK_APP_WORK_SECONDS", 20 * 60),
        break_seconds=env_seconds("LOCK_APP_BREAK_SECONDS", env_seconds("LOCK_APP_TEST_SECONDS", 20 * 60)),
        daily_limit_seconds=env_seconds("LOCK_APP_DAILY_LIMIT_SECONDS", 2 * 60 * 60),
        parent_extra_seconds_limit=env_seconds("LOCK_APP_PARENT_EXTRA_SECONDS_LIMIT", 60 * 60),
    )


def parent_password():
    return configured_parent_password()


class ParentControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Computer Locker - Parent Controls")
        self.root.geometry("520x340")
        self.root.minsize(480, 320)
        self.root.protocol("WM_DELETE_WINDOW", self._request_parent_exit)
        self.root.bind("<Alt-F4>", self._request_parent_exit)

        self.timer = UsageTimer(build_timer_settings())
        self.timer.start_unlocked_interval()
        self.event_logger = EventLogger()
        self.event_logger.log(
            APP_STARTED_EVENT,
            workSeconds=self.timer.settings.work_seconds,
            breakSeconds=self.timer.settings.break_seconds,
            dailyLimitSeconds=self.timer.settings.daily_limit_seconds,
            parentExtraSecondsLimit=self.timer.settings.parent_extra_seconds_limit,
        )

        self.lock_screen = LockScreen(
            root,
            duration_seconds=self.timer.settings.break_seconds,
            message=REGULAR_BREAK_MESSAGE,
            on_released=self._break_released,
        )
        self.daily_limit_screen = DailyLimitScreen(
            root,
            password_provider=parent_password,
            on_extra_time_granted=self._grant_parent_extra_time,
        )

        self._build_ui()
        self._tick()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=24)
        container.pack(fill="both", expand=True)

        title = ttk.Label(
            container,
            text="Computer Locker",
            font=("Segoe UI", 20, "bold"),
        )
        title.pack(anchor="w")

        intro = ttk.Label(
            container,
            text="Step 7 prototype: protected parent controls with automatic breaks and daily-limit lock.",
            wraplength=450,
        )
        intro.pack(anchor="w", pady=(8, 18))

        self.status_label = ttk.Label(container, text="", wraplength=450)
        self.status_label.pack(anchor="w", pady=(0, 16))

        button_row = ttk.Frame(container)
        button_row.pack(anchor="w")

        test_button = ttk.Button(
            button_row,
            text="Test Lock Screen",
            command=self._request_test_lock,
        )
        test_button.pack(side="left")

        exit_button = ttk.Button(
            button_row,
            text="Parent Exit",
            command=self._request_parent_exit,
        )
        exit_button.pack(side="left", padx=(12, 0))

        note = ttk.Label(
            container,
            text="Parent-only actions require the parent password. Prototype password defaults to 'parent' unless LOCK_APP_PARENT_PASSWORD is set before launch.",
            wraplength=450,
            foreground="#4b5563",
        )
        note.pack(anchor="w", pady=(24, 0))

    def _tick(self):
        status = self.timer.status()
        if self.daily_limit_screen.is_visible() and not status["daily_limit_reached"]:
            self.daily_limit_screen.close()
            self.timer.start_unlocked_interval()

        if self.timer.should_start_break():
            lock_kind, elapsed_seconds = self.timer.begin_break()
            self.event_logger.log(
                USAGE_EVENT,
                durationSeconds=elapsed_seconds,
                unlockedSecondsToday=self.timer.unlocked_seconds_today,
                completedCycles=self.timer.completed_cycles,
            )
            if lock_kind == "break":
                self.event_logger.log(
                    REGULAR_LOCK_STARTED_EVENT,
                    breakSeconds=self.timer.settings.break_seconds,
                    completedCycles=self.timer.completed_cycles,
                )
                self.lock_screen.show()
            elif lock_kind == "daily_limit":
                self.event_logger.log(
                    DAILY_LIMIT_STARTED_EVENT,
                    unlockedSecondsToday=self.timer.unlocked_seconds_today,
                    effectiveDailyLimitSeconds=self.timer.effective_daily_limit_seconds,
                )
                self.daily_limit_screen.show()

        self._update_status()
        self.root.after(500, self._tick)

    def _update_status(self):
        status = self.timer.status()
        usage = format_seconds(status["unlocked_seconds_today"])
        limit = format_seconds(status["effective_daily_limit_seconds"])
        remaining = format_seconds(status["remaining_work_seconds"])
        extra_remaining = format_seconds(status["parent_extra_seconds_remaining"])
        self.status_label.configure(
            text=(
                f"Unlocked today: {usage} of {limit}\n"
                f"Current work interval remaining: {remaining}\n"
                f"Completed cycles: {status['completed_cycles']} of {status['max_cycles']}\n"
                f"Parent extra time remaining today: {extra_remaining}"
            )
        )

    def _request_test_lock(self):
        if not self._confirm_parent_action("test the lock screen"):
            return

        self.event_logger.log(TEST_LOCK_STARTED_EVENT)
        self.lock_screen.show()

    def _request_parent_exit(self, _event=None):
        if not self._confirm_parent_action("exit Computer Locker"):
            return "break"

        self.event_logger.log(PARENT_EXIT_ALLOWED_EVENT)
        self.root.destroy()
        return "break"

    def _confirm_parent_action(self, action_name):
        password = simpledialog.askstring(
            "Parent Password",
            f"Enter parent password to {action_name}.",
            show="*",
            parent=self.root,
        )
        if verify_parent_password(password):
            return True

        self.event_logger.log(PARENT_ACTION_DENIED_EVENT, action=action_name)
        if password is not None:
            messagebox.showerror("Parent Password", "Incorrect password.", parent=self.root)
        return False

    def _break_released(self):
        self.timer.finish_break()
        self.event_logger.log(REGULAR_LOCK_RELEASED_EVENT)

    def _grant_parent_extra_time(self, requested_seconds):
        granted_seconds = self.timer.grant_parent_extra_time(requested_seconds)
        if granted_seconds > 0:
            self.event_logger.log(
                PARENT_EXTRA_GRANTED_EVENT,
                grantedSeconds=granted_seconds,
                parentExtraSecondsToday=self.timer.parent_extra_seconds_today,
            )
            self._update_status()
        return granted_seconds


def main():
    root = tk.Tk()
    ParentControlApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
