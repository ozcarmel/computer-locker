import tkinter as tk

from parent_auth import verify_parent_password


DAILY_LIMIT_MESSAGE = "you've reached the limit usage for today. Try again tomorrow"


class DailyLimitScreen:
    def __init__(
        self,
        root,
        password_provider,
        on_extra_time_granted,
        extra_seconds=20 * 60,
        message=DAILY_LIMIT_MESSAGE,
    ):
        self.root = root
        self.password_provider = password_provider
        self.on_extra_time_granted = on_extra_time_granted
        self.extra_seconds = int(extra_seconds)
        self.message = message

        self.window = None
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Parent password required for extra time.")

    def show(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        self.password_var.set("")
        self.status_var.set("Parent password required for extra time.")

        self.window = tk.Toplevel(self.root)
        self.window.title("Daily Limit Reached")
        self.window.configure(bg="#111827")
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)

        for sequence in (
            "<Alt-F4>",
            "<Escape>",
            "<space>",
            "<Control-w>",
            "<Control-q>",
        ):
            self.window.bind(sequence, self._ignore_key)

        frame = tk.Frame(self.window, bg="#111827")
        frame.pack(expand=True, fill="both")

        message_label = tk.Label(
            frame,
            text=self.message,
            bg="#111827",
            fg="#f9fafb",
            font=("Segoe UI", 32, "bold"),
            wraplength=1000,
            justify="center",
        )
        message_label.pack(expand=True, pady=(80, 24))

        form = tk.Frame(frame, bg="#111827")
        form.pack(pady=(0, 80))

        password_label = tk.Label(
            form,
            text="Parent password",
            bg="#111827",
            fg="#d1d5db",
            font=("Segoe UI", 15),
        )
        password_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        password_entry = tk.Entry(
            form,
            textvariable=self.password_var,
            show="*",
            width=28,
            font=("Segoe UI", 18),
        )
        password_entry.grid(row=1, column=0, padx=(0, 12))
        password_entry.bind("<Return>", self._submit_password)

        add_button = tk.Button(
            form,
            text="Add 20 minutes",
            command=self._submit_password,
            font=("Segoe UI", 14, "bold"),
            padx=18,
            pady=6,
        )
        add_button.grid(row=1, column=1)

        status_label = tk.Label(
            form,
            textvariable=self.status_var,
            bg="#111827",
            fg="#fca5a5",
            font=("Segoe UI", 12),
        )
        status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 0))

        password_entry.focus_force()
        self.window.focus_force()

    def close(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.destroy()
        self.window = None

    def is_visible(self):
        return self.window is not None and self.window.winfo_exists()

    def _submit_password(self, _event=None):
        expected_password = self.password_provider()
        if not verify_parent_password(self.password_var.get(), expected_password):
            self.password_var.set("")
            self.status_var.set("Incorrect password.")
            return "break"

        granted_seconds = self.on_extra_time_granted(self.extra_seconds)
        if granted_seconds <= 0:
            self.password_var.set("")
            self.status_var.set("No parent extra time remains today.")
            return "break"

        self.close()
        return "break"

    def _ignore_key(self, _event=None):
        return "break"
