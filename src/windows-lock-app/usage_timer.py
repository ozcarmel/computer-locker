from dataclasses import dataclass
from datetime import datetime, time, timedelta


@dataclass(frozen=True)
class UsageTimerSettings:
    work_seconds: int = 20 * 60
    break_seconds: int = 20 * 60
    daily_limit_seconds: int = 2 * 60 * 60
    parent_extra_seconds_limit: int = 60 * 60
    daily_reset_time: time = time(hour=8, minute=0)

    @property
    def max_cycles(self):
        return self.daily_limit_seconds // self.work_seconds


class UsageTimer:
    def __init__(self, settings=None, now=None):
        self.settings = settings or UsageTimerSettings()
        self.day_started_at = self._current_day_start(now or datetime.now())
        self.unlocked_seconds_today = 0
        self.completed_cycles = 0
        self.parent_extra_seconds_today = 0
        self.active_interval_started_at = None
        self.is_locked = False
        self.daily_limit_reached = False

    def start_unlocked_interval(self, now=None):
        current_time = now or datetime.now()
        self._reset_if_needed(current_time)

        if self.daily_limit_reached:
            return False

        self.active_interval_started_at = current_time
        self.is_locked = False
        return True

    def stop_unlocked_interval(self, now=None):
        if self.active_interval_started_at is None:
            return 0

        current_time = now or datetime.now()
        elapsed = max(0, int((current_time - self.active_interval_started_at).total_seconds()))
        self.unlocked_seconds_today += elapsed
        self.active_interval_started_at = None
        return elapsed

    def remaining_work_seconds(self, now=None):
        if self.active_interval_started_at is None:
            return self.settings.work_seconds

        current_time = now or datetime.now()
        elapsed = max(0, int((current_time - self.active_interval_started_at).total_seconds()))
        return max(0, self.settings.work_seconds - elapsed)

    def should_start_break(self, now=None):
        self._reset_if_needed(now or datetime.now())
        return (
            not self.daily_limit_reached
            and self.active_interval_started_at is not None
            and self.remaining_work_seconds(now) == 0
        )

    def begin_break(self, now=None):
        elapsed_seconds = self.stop_unlocked_interval(now)
        self.completed_cycles += 1
        self.is_locked = True

        if self.unlocked_seconds_today >= self.effective_daily_limit_seconds:
            self.daily_limit_reached = True
            return "daily_limit", elapsed_seconds

        return "break", elapsed_seconds

    def finish_break(self, now=None):
        self.is_locked = False
        return self.start_unlocked_interval(now)

    def parent_extra_seconds_remaining(self):
        return max(
            0,
            self.settings.parent_extra_seconds_limit - self.parent_extra_seconds_today,
        )

    def grant_parent_extra_time(self, requested_seconds, now=None):
        grant_seconds = min(
            max(0, int(requested_seconds)),
            self.parent_extra_seconds_remaining(),
        )
        if grant_seconds == 0:
            return 0

        self.parent_extra_seconds_today += grant_seconds
        self.daily_limit_reached = False
        self.is_locked = False
        self.start_unlocked_interval(now)
        return grant_seconds

    @property
    def effective_daily_limit_seconds(self):
        return self.settings.daily_limit_seconds + self.parent_extra_seconds_today

    def status(self, now=None):
        current_time = now or datetime.now()
        self._reset_if_needed(current_time)

        current_interval_elapsed = 0
        if self.active_interval_started_at is not None:
            current_interval_elapsed = max(
                0,
                int((current_time - self.active_interval_started_at).total_seconds()),
            )

        return {
            "unlocked_seconds_today": self.unlocked_seconds_today + current_interval_elapsed,
            "completed_cycles": self.completed_cycles,
            "max_cycles": self.settings.max_cycles,
            "remaining_work_seconds": self.remaining_work_seconds(current_time),
            "daily_limit_reached": self.daily_limit_reached,
            "effective_daily_limit_seconds": self.effective_daily_limit_seconds,
            "parent_extra_seconds_today": self.parent_extra_seconds_today,
            "parent_extra_seconds_remaining": self.parent_extra_seconds_remaining(),
            "is_locked": self.is_locked,
            "day_started_at": self.day_started_at,
        }

    def _reset_if_needed(self, now):
        current_day_start = self._current_day_start(now)
        if current_day_start > self.day_started_at:
            self.day_started_at = current_day_start
            self.unlocked_seconds_today = 0
            self.completed_cycles = 0
            self.parent_extra_seconds_today = 0
            self.active_interval_started_at = None
            self.is_locked = False
            self.daily_limit_reached = False

    def _current_day_start(self, now):
        reset_today = datetime.combine(now.date(), self.settings.daily_reset_time)
        if now >= reset_today:
            return reset_today
        return reset_today - timedelta(days=1)
