# LinkIt Fork — independent macOS and Android source backup

This repository contains **the complete original source snapshot of both platforms**, plus our macOS cosmetic changes and independent GitHub Actions builds. It is no longer a patch-only overlay that must clone the original author's GitHub repository.

## What's saved, and where

- `upstream/macos/` — full native macOS source and resources.
- `upstream/android/` — full Android source, Gradle wrapper, build configuration and resources.
- `upstream/scripts/`, `upstream/assets/`, `upstream/docs/`, `upstream/LICENSE` — bundled upstream build scripts, assets, documentation and GPLv3 license.
- `UPSTREAM_SNAPSHOT_COMMIT` — original commit `4caea673f0fd827ba6ffb754895df9a7f0694dc8`.
- `scripts/apply_macos_ui_fixes.py`, `scripts/fix_mac_icon.py` — our macOS presentation fixes.
- `.github/workflows/build-macos.yml` — independent macOS arm64 build from `upstream/`.
- `.github/workflows/build-android.yml` — independent Android build from `upstream/`.
- `RECOVERY.md` — recovery procedure, signing details and limitations.

The original source repository can be deleted without deleting these checked-in source files. **Neither of the two build workflows clones the original LinkIt repository.** They still need operating-system toolchains and third-party dependencies from their respective normal package repositories.

## Cosmetic changes in the macOS app

1. Remove the rectangular black matte from the original dark macOS icon, preserving the original artwork.
2. Remove the rectangular AppKit shadow around the rounded floating transfer-progress dialog.
3. Hide the *global yellow attention banner* for optional Android phone-control and battery-exemption permissions; keep the statuses in Diagnostics and keep other warnings.

Android behavior and the existing phone-to-Mac protocol remain unchanged. **The Android client is archived, but not modified.**

## Build without the original repository

Open **Actions** here and run either:
- **Build LinkIt Fork (macOS arm64)** — macOS Sequoia / Apple Silicon app ZIP.
- **Build LinkIt Fork (Android APK)** — debug APK (signed with a temporary runner debug key) plus an **unsigned** release APK.

These build outputs expire after 30 days; the **source in the Git repository and the recovery release do not use that expiry**. For a new, consistently updatable Android production APK, use a **private, permanently backed-up signing keystore** as described in `RECOVERY.md`. Do not commit passwords or signing keys to this public repository.

The Mac app uses ad-hoc signing rather than Apple notarization. The old app bundle identifier is maintained for compatibility. Updating an already installed Android release with a separately signed fork APK will normally require a different strategy (e.g., uninstall then reinstall and re-pair); signing compatibility cannot be assumed.

## Restoration instructions

See [RECOVERY.md](RECOVERY.md). The full source is present at this repository, so no links to original author's GitHub are needed to restore it.

## License and brand

Original LinkIt source: GNU GPLv3; modifications inherit the same open-source obligations. The original author does **not** license the original app name and logo for redistributed derivative builds. Do not publicly distribute a branded derivative as if it were officially authorized; rebrand before a separate public production release. This repository preserves the original resources for source recovery and private experimentation.
