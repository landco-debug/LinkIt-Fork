# Disaster recovery: rebuilding LinkIt Fork if the original project disappears

## Verified snapshot

The original source **tree**, not the author's full Git history, is preserved in this repository under `upstream/`. The original commit is recorded in `UPSTREAM_SNAPSHOT_COMMIT`:

```text
4caea673f0fd827ba6ffb754895df9a7f0694dc8
```

Both macOS and Android source files, app resources, original documentation, GNU GPLv3 license, Android Gradle wrapper and upstream build scripts are committed here. The two independent GitHub Actions workflows use **only this repository's copy** of LinkIt source. This remains true if `kalki-kgp/Linkit` is removed.

A second copy of the source can be retained offline by downloading the source archive from our GitHub recovery Release, or by running:

```sh
git clone https://github.com/landco-debug/LinkIt-Fork.git
```

For a completely air-gapped build, external compiler/SDK versions and Gradle/Maven dependencies also need to be cached or mirrored in advance. This source archive does not contain macOS/Xcode, the Android SDK, the Gradle distribution ZIP or all Maven artifacts. The upstream Gradle wrapper JAR and version/hash configuration *are* preserved.

## Permanent unmodified installer copies (verified hashes)

The [recovery Release](https://github.com/landco-debug/LinkIt-Fork/releases/tag/recovery-source-2026-10-16) also contains:
- `LinkIt-Fork-macOS-arm64.zip`: our working macOS fork binary, built from **our own** source tree and retained without Actions artifact expiry.
- `Linkit-v0.9.6-OFFICIAL-Android.apk`: the **unmodified original author's signed APK**; this is an immediately reusable Android installer and retains the author's signature. Its SHA-256 was verified to match the original official GitHub v0.9.6 Release.
- `Linkit-v0.9.6-OFFICIAL-macOS.zip`: the unmodified original Mac installer (also verified).
- Corresponding SHA-256 checksum files.

For recovering the existing phone installation, retaining that exact signed original Android APK is preferable to replacing it with a differently signed debug APK. It is **not** the source-built Android fork. You can still build an Android fork from `upstream/android` using our own key, but an in-place upgrade from the author's signed APK using a different signature cannot be assumed.

## GitHub Actions: no original source required

Go to **Actions** in this repository:

1. Run **Build LinkIt Fork (macOS arm64)** to obtain `LinkIt-Fork-macOS-arm64.zip` and its SHA-256 file.
2. Run **Build LinkIt Fork (Android APK)** to obtain the debug APK and an unsigned release APK, plus SHA-256 checksums.

Workflow artifacts are temporary (configured to expire after 30 days). The source committed to Git and the separate recovery Release remain available for as long as our repository and Release are retained.

## Rebuilding on a Mac directly

Prerequisites: macOS with Apple developer command-line tools/Xcode (Swift), Python 3 and Pillow. Work from a **fresh clone**, because the macOS patch script intentionally refuses to patch an already-patched file.

```sh
git clone https://github.com/landco-debug/LinkIt-Fork.git
cd LinkIt-Fork
python3 -m pip install Pillow
python3 scripts/apply_macos_ui_fixes.py upstream
python3 scripts/fix_mac_icon.py upstream
(cd upstream/macos && swift test)
LINKIT_VERSION=0.9.6 LINKIT_BUILD=962 \
  LINKIT_UPDATE_MANIFEST_URL=https://github.com/landco-debug/LinkIt-Fork/releases/latest/download/linkit-macos-update.json \
  ./upstream/scripts/build-macos-app.sh
```

App location: `upstream/dist/Linkit.app`. It is ad-hoc signed, not Apple-notarized. The fork reuses the original bundle identifier and app brand for private testing.

## Rebuilding Android locally

Prerequisites: JDK 17 and Android SDK (API level 36 / build tools), Gradle dependencies downloadable from official third-party artifact repositories.

```sh
cd LinkIt-Fork/upstream/android
chmod +x ./gradlew
./gradlew testDebugUnitTest assembleDebug assembleRelease
```

Outputs:
- `app/build/outputs/apk/debug/app-debug.apk`: test/debug APK signed with a build-machine debug key.
- `app/build/outputs/apk/release/app-release-unsigned.apk`: **not installable as an unsigned APK** until properly signed.

### Long-term Android release signing — important

Android's signature must remain constant for in-place application updates. **The original author's private release key is not included and cannot be reconstructed from source.** We deliberately do not store a shared release signing key or passwords in this public GitHub repository.

For your own future fork releases:

1. Create a new Android release keystore **once**, privately (using `keytool -genkeypair` or Android Studio).
2. Keep backed-up copies of the keystore, alias and passwords in a secure location independent from public GitHub; never commit them to this public repository.
3. Place the keystore in `upstream/android/` and create a private `upstream/android/keystore.properties` with `storeFile`, `storePassword`, `keyAlias` and `keyPassword`, referring to that key.
4. Run `(cd upstream/android && ./gradlew assembleRelease)`. The configured signing section in `app/build.gradle.kts` creates a signed release APK when private keystore properties exist.
5. Preserve **the same keystore** for every subsequent fork release. The key must be stored securely; losing it generally prevents seamless future updates under the same package name.

**Important:** An APK signed by your new key generally cannot update the original author's installed APK in place because the certificates differ. The same is true of GitHub Actions debug APKs from different fresh runners. Record/backup necessary local app data before replacing the original, uninstall/reinstall if required, and re-pair the phone and Mac afterward. App pairing's private keys and runtime credentials are intentionally **not** backed up in this source repository.

For unattended GitHub Actions signing, configure repository Actions secrets privately first (never add keystore bytes or passwords to a public commit) and use a secret-aware signing workflow. Currently the automated Android job intentionally produces a debug APK and unsigned release, not a permanent signed production build.

## Other limitations

- This is a snapshot at one specified commit, not a guaranteed archive of all prior commits, releases, issues or the author's entire Git history.
- Future OS/SDK changes may require maintenance even with complete source. Neither a successful build now nor saved source guarantees operation on all later OS releases.
- macOS ad-hoc signing is not equivalent to Apple Developer ID signing/notarization.
- Updater manifests must be hosted on our own GitHub Releases for fully managed future updates; builds currently point toward our repository, not the author's release feed.
- Source is GPLv3. The author reserves trademark rights to the original LinkIt name and logo; rebrand a publicly distributed derivative.
