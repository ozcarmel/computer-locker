import time
import tkinter as tk

from countdown import format_seconds, next_remaining_seconds
from parent_auth import configured_parent_password, verify_parent_password


REGULAR_BREAK_MESSAGE = "Computer is locked for 20 min. Take a break"


class LockScreen:
    def __init__(
        self,
        root,
        duration_seconds=20 * 60,
        message=REGULAR_BREAK_MESSAGE,
        on_released=None,
        password_provider=configured_parent_password,
    ):
        self.root = root
        self.duration_seconds = int(duration_seconds)
        self.message = message
        self.on_released = on_released
        self.password_provider = password_provider
        self.started_at = None
        self.is_finished = False

        self.window = None
        self.timer_label = None
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="")

    def show(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        self.started_at = time.monotonic()
        self.is_finished = False
        self.password_var.set("")
        self.status_var.set("")

        self.window = tk.Toplevel(self.root)
        self.window.title("Computer Locked")
        self.window.configure(bg="#111827")
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)
        self.window.bind("<Alt-F4>", self._ignore_key)
        self.window.bind("<Escape>", self._ignore_key)
        self.window.bind("<space>", self._space_pressed)

        frame = tk.Frame(self.window, bg="#111827")
        frame.pack(expand=True, fill="both")

        message_label = tk.Label(
            frame,
            text=self.message,
            bg="#111827",
            fg="#f9fafb",
            font=("Segoe UI", 34, "bold"),
            wraplength=1000,
            justify="center",
        )
        message_label.pack(expand=True, pady=(80, 20))

        self.timer_label = tk.Label(
            frame,
            text=format_seconds(self.duration_seconds),
            bg="#111827",
            fg="#93c5fd",
            font=("Consolas", 72, "bold"),
        )
        self.timer_label.pack(pady=(0, 32))

        parent_frame = tk.Frame(frame, bg="#111827")
        parent_frame.pack(pady=(0, 18))

        password_label = tk.Label(
            parent_frame,
            text="Parent password",
            bg="#111827",
            fg="#d1d5db",
            font=("Segoe UI", 13),
        )
        password_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        password_entry = tk.Entry(
            parent_frame,
            textvariable=self.password_var,
            show="*",
            width=24,
            font=("Segoe UI", 15),
        )
        password_entry.grid(row=1, column=0, padx=(0, 10))
        password_entry.bind("<Return>", self._submit_parent_password)

        unlock_button = tk.Button(
            parent_frame,
            text="Finish break",
            command=self._submit_parent_password,
            font=("Segoe UI", 12, "bold"),
            padx=14,
            pady=4,
        )
        unlock_button.grid(row=1, column=1)

        status_label = tk.Label(
            parent_frame,
            textvariable=self.status_var,
            bg="#111827",
            fg="#fca5a5",
            font=("Segoe UI", 11),
        )
        status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        hint_label = tk.Label(
            frame,
            text="",
            bg="#111827",
            fg="#d1d5db",
            font=("Segoe UI", 18),
        )
        hint_label.pack(pady=(0, 80))
        self.hint_label = hint_label

        self.window.focus_force()
        self._tick()

    def _tick(self):
        if self.window is None or not self.window.winfo_exists():
            return

        remaining = next_remaining_seconds(
            self.started_at,
            self.duration_seconds,
            time.monotonic(),
        )
        self.timer_label.configure(text=format_seconds(remaining))

        if remaining == 0:
            self._finish_countdown()
        else:
            self.window.after(250, self._tick)

    def _finish_countdown(self):
        self.is_finished = True
        if self.timer_label is not None:
            self.timer_label.configure(text="00:00")
        self.hint_label.configure(text="Press spacebar to continue")

    def _submit_parent_password(self, _event=None):
        if verify_parent_password(self.password_var.get(), self.password_provider()):
            self.password_var.set("")
            self.status_var.set("")
            self._finish_countdown()
            return "break"

        self.password_var.set("")
        self.status_var.set("Incorrect password.")
        return "break"

    def _space_pressed(self, _event):
        if self.is_finished:
            self.close()
            if self.on_released is not None:
                self.on_released()
        return "break"

    def _ignore_key(self, _event=None):
        return "break"

    def close(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.destroy()
        self.window = None
