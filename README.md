# LinkIt Fork — macOS cosmetic fixes

This is a reproducible **patch overlay** for the original [kalki-kgp/Linkit](https://github.com/kalki-kgp/Linkit), pinned at commit `4caea673f0fd827ba6ffb754895df9a7f0694dc8`. The upstream source is retrieved during the build; Android and the file-transfer protocol are unchanged.

## Changes

1. Remove the black square matte around the rounded Launchpad icon. Create a clean, transparent macOS `.icns`.
2. Remove the rectangular window shadow surrounding the rounded floating transfer-progress dialog. Keep continuous rounded corners.
3. Do not display the **global yellow warning in the Mac menu popover** for the two optional Android permissions `phone_control` and `battery_exemption` that the upstream Android app marks as `attention` even when unrequested. Keep notifications for other actual failures, and keep **all** existing entries in Settings → Diagnostics. This doesn't delete or disable any feature.

## Build for MacBook Air M1 (Sequoia)

1. Open **Actions** in this repository.
2. Select **Build LinkIt Fork (macOS arm64)** and click **Run workflow**.
3. Download the resulting artifact `LinkIt-Fork-macOS-arm64`; inside is a ZIP containing `Linkit.app`.

The workflow checks out pinned upstream source, applies strict patches, regenerates the icon, runs the Swift test suite, compiles the native arm64 app, and applies ad-hoc signing. Build status has not yet been verified by a real Actions run.

**Important:** Quit the running Linkit app and retain a backup before replacing it. This build has the same bundle identifier as upstream; macOS may request Local Network/Keychain access again. It is not notarized. No modified Android APK is required.

The app updater uses this fork's (currently nonexistent) release manifest, so it cannot silently replace your fork with the original build.

## Scope and license

This is an overlay fork, not an imported full Git mirror. All upstream GPL-3.0 obligations apply. The original author reserves the name and logo for redistributed derivative builds; use this prototype privately, and rebrand before publishing a public fork binary. See the original [licensing notes](https://github.com/kalki-kgp/Linkit#license--contact).
