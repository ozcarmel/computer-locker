# Mobile App Install

The phone app is an installable web app for the parent report.

## Open On Phone

When the computer and phone are on the same home network, open:

```text
http://192.168.100.95:8088
```

If the computer's IP changes, run this on the computer:

```powershell
ipconfig
```

Use the current IPv4 address with port `8088`.

## Install On Android

1. Open the report URL in Chrome.
2. Tap the three-dot menu.
3. Tap `Add to Home screen` or `Install app`.
4. Accept the name `Gili Activity`.

## Install On iPhone

1. Open the report URL in Safari.
2. Tap the Share button.
3. Tap `Add to Home Screen`.
4. Accept the name `Gili Activity`.

## Notes

- The app reads reports from the computer, so the computer must be on and serving the report.
- The installed phone icon opens the same local report page.
- The phone and computer must stay on the same home network.

## Away From Home With OneDrive

The computer also syncs a copy of the app and latest reports to:

```text
C:\Users\gilic\OneDrive\Gili Activity Report
```

Share this folder privately from OneDrive with the parent iPhone account. Away from home, the parent can open the OneDrive copy of `index.html` or the shared folder contents to view the latest synced report.

OneDrive sync depends on the computer being online and OneDrive being signed in.
