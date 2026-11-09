# Vendor backup

Story #242. ADR-012 makes the kit depend on outside packages. Those packages can vanish or turn closed.
So we keep a copy of them. The copy lives in one git branch: `backup/vendor`.

## What is in the branch

- `npm-cache/`: every npm package from `ui/tool/package-lock.json`, as npm itself stores them. There are about 130.
- `maven/`: the Compose BOM `2025.10.00`, `material3` 1.4.0, `material-icons-core`, and everything they need.
  Each has its `.pom`, its `.module` file and its `.aar` or `.jar`, in the normal Maven folder layout.
  Most come from Google Maven. A few Kotlin parts come from Maven Central, because Google's POMs point there.
- `licenses/`: one license file for each package. If a package ships none, the file says what the package declares.
- `MANIFEST.json`: for each file, the name, version, `sha256`, source URL, license file and the date.

The pins are listed in `scripts/vendor_pins.json`. The M3 version must match `docs/research/android-m3-api.md`.
`python3 scripts/vendor_backup.py --plan` prints the list. Run it any time. It downloads nothing.

## Size

First build, 9 Nov 2026: about 290 MB of files and 1,423 entries in the MANIFEST. The workflow prints the size and the
count after each push; read them in the run log. No single file may pass 90 MB, because GitHub refuses 100 MB.
The build stops with a clear message if one does. The backup holds more than the Android build needs, on purpose:
it also keeps the desktop and stub variants Google publishes, so any variant can be restored.

## Who builds it

Only GitHub CI. Nothing is downloaded or installed on the owner's Mac. The workflow is `.github/workflows/vendor-backup.yml`.

1. It runs every Monday, by hand (`workflow_dispatch`), and when a pin changes on `dev`.
2. Step 1, job `backup`: it fetches. npm checks each tarball against the lockfile integrity. Each Maven file is checked
   against the `.sha256` (or `.sha1`) that sits beside it. A file with no checksum is refused.
   It writes `MANIFEST.json` and the licenses. It pushes to `backup/vendor`. If the branch is missing, it creates it.
3. Step 2, job `restore`: it checks out `backup/vendor` only. It runs `scripts/restore_vendor.sh`.
   That runs `npm ci --offline` and then a Gradle `--offline` resolve. If a file is missing, the job fails.

Nobody pushes to `backup/vendor` by hand.

## How the size checks skip it

The file-size check (500 KB) and pre-commit run on `dev` and on pull requests. `ci.yml` runs on pushes to `dev` and
`main` only, so a push to `backup/vendor` never starts it. No pull request ever targets that branch.
`scripts/check_local.sh sizes` skips itself when the branch is `backup/vendor`.

## How to restore

Use a CI job. On the Mac the script refuses.

```bash
git clone --branch backup/vendor --depth 1 <repo url> backup
bash scripts/restore_vendor.sh backup
```

`restore_vendor.sh` checks the MANIFEST first. Then it installs `ui/tool` with `npm ci --offline`, with the npm cache
pointed at `backup/npm-cache`. Then it resolves the Compose artifacts with Gradle `--offline`. The only Maven
repository is the `backup/maven` folder. To use the backup in your own build, point your Gradle at that folder and run offline.

`python3 scripts/vendor_backup.py --manifest-check backup` tells you if the folder is whole.

## How it is used

The normal path uses the live sources. The branch is only a backup. A child project never fetches it.
A child fetches the ShipQuick submodule commit and nothing else.

## Why SwiftUI is not in it

SwiftUI is part of iOS and Xcode. Apple ships it inside the system. There is no package to copy.
If Apple changes it, the Xcode and iOS version we build with is the pin. We keep the screens, not the library.

## What not backed up

- `org.jetbrains.skiko:skiko-android:0.7.7`: a desktop and iOS drawing library that a Compose POM names. No repository we use has its
  POM. The Android restore does not need it. The MANIFEST lists it under `unresolved`.
- The Gradle distribution and the Android Gradle plugin. The kit has no Gradle build yet (stories S6 and S7).
  When it has, add its wrapper and plugins to the pins.
- The Astryx source on GitHub. We use the npm package, which is in the backup.

## If a source goes closed

1. Do not panic. The last good copy is in `backup/vendor`.
2. Run the `restore` job, or `restore_vendor.sh` on CI, to prove it still works.
3. Point the build at the backup folder. The files are the same, byte for byte (see `sha256` in the MANIFEST).
4. Read the license file of the package. Most are MIT or Apache-2.0, so a fork is allowed.
5. Open an ADR. Choose: stay on the pinned copy, fork it, or replace it.

Decision: ADR-012. See also `docs/ADOPTION.md`.
