# Hardening Notes

Step 7 improves casual bypass resistance for the current Python prototype.

## Implemented

- The parent control window no longer exits directly from the window close button.
- Alt+F4 on the parent control window opens a parent password prompt instead of closing immediately.
- The `Test Lock Screen` button now requires the parent password.
- The `Parent Exit` button requires the parent password.
- Incorrect parent password attempts are recorded in the local event log.
- Authorized parent exits are recorded in the local event log.
- The daily-limit screen continues to ignore spacebar and common close shortcuts.

## Current Limits

This is still a user-mode Python prototype. A determined standard user may still attempt to bypass it by:

- Ending the Python process from Task Manager if Task Manager is available.
- Renaming or moving project files if filesystem permissions allow it.
- Preventing the scheduled task from running if the task is not protected by administrator policy.
- Using Windows system-level screens or shortcuts that normal desktop apps cannot intercept.

## Recommended Future Hardening

For stronger enforcement, consider combining the app with administrator-controlled Windows restrictions:

- Install app files under a protected location such as `C:\Program Files\ComputerLocker`.
- Restrict write permissions on app files and configuration.
- Use Task Scheduler restart settings and possibly a separate watchdog task.
- Restrict Task Manager and command-line tools for the child account through Windows policy.
- Consider Microsoft Family Safety for additional screen-time enforcement.
- Consider a Windows service for monitoring, while keeping the visible lock UI in the child user's interactive session.

These stronger controls require administrator approval and careful testing.
