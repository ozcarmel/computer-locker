# Admin Setup Scripts

This folder contains administrator-run setup scripts.

Responsibilities:

- Create or update the Windows scheduled task that launches the lock app.
- Configure startup behavior for the child standard user.
- Remove the scheduled task if needed.
- Keep secrets and account-specific values out of source control.

Do not store administrator passwords in this repository.

## Current Scripts

- `install_startup_task.ps1` - run from an elevated Administrator PowerShell window to create the startup task.
- `launch_lock_app.ps1` - task launcher used by the scheduled task.
- `uninstall_startup_task.ps1` - run from an elevated Administrator PowerShell window to remove the startup task.

See `docs\ADMIN_STARTUP_SETUP.md` for usage.
