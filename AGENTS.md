# Use administrator account

## Project Agent

Agent name: Use administrator account

## Operating Rules

- Always use the Admin account to run the application created for this project.
- Always use the Admin account when creating, configuring, or running scheduled tasks for this project.
- Scheduled tasks must be configured to run automatically when non-admin users are logged in.
- Do not require non-admin users to manually launch privileged project tasks.
- Keep any credentials, secrets, or account-specific configuration out of source control.

# Locking mechanism

## Project Agent

Agent name: Locking mechanism

## Responsibility

This agent is responsible for thinking through and defining the locking mechanism for the computer locking application. It owns the timing rules, lock-screen behavior, parent override behavior, and test-lock behavior.

## Locking Rules

- When a standard account is using the computer, the computer must be locked every 20 minutes.
- Each regular lock period lasts 20 minutes.
- When the computer is locked, a lock screen must appear.
- The regular lock screen must show this message: "Computer is locked for 20 min. Take a break"
- The lock screen must show a descending timer that starts at 20:00 in minutes:seconds format.
- After 20 minutes, the timer must show 00:00, but the lock screen remains visible until the user presses the spacebar.
- Accumulated unlocked computer usage is limited to 2 hours per day.
- The 2-hour daily limit is reached after six 20-minute unlocked usage cycles.
- Once the daily usage limit is reached, the computer must be locked with this message: "you've reached the limit usage for today. Try again tomorrow"
- The daily-limit lock screen must remain until the next day at 8:00.
- The daily-limit lock screen must not be removable or manipulable by any keyboard key or keyboard shortcut.
- The daily-limit lock screen must include a parent password window.
- A parent can enter the password to unlock the computer and add usage time for the child.
- Parent-added usage time is limited to a maximum of 1 additional hour per day.
- A test button must allow the parent to immediately test and display the lock screen at any time.

# Mobile reporting app

## Project Agent

Agent name: Mobile reporting app

## Responsibility

This agent is responsible for defining and maintaining the simple mobile reporting app for parents.

## Reporting Rules

- The mobile app must report the child's daily logged-in computer usage hours.
- The mobile app must report when the screen lock appeared during the day.
- Reports should be organized by date.
- Reports should be simple, readable, and parent-facing.

# Activity reporting agent

## Project Agent

Agent name: Activity reporting agent

## Responsibility

This agent is responsible for collecting simple parent-facing activity reports without interfering with the computer locker.

## Activity Reporting Rules

- The activity reporter must run separately from the lock application.
- Failure in activity reporting must not stop, delay, or modify the locker.
- The reporter may sample active app/window usage while the child account is logged in.
- The reporter may read local browser history for Chrome, Edge, and Firefox when generating reports.
- Activity reports must be simple and parent-facing.
- Activity data and reports must be stored outside source control.
- Activity reports should be available to the mobile reporting app.
- Scheduled activity reporting tasks must be installed and managed by the Admin account.
