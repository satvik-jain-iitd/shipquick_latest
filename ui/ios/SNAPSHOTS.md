# ui/ios snapshots: how the reference images are made and refreshed (story #219)

Every screen template in `templates/` has a snapshot test. CI draws the template and compares the
picture with a reference image in `ShipQuickUITests/__Snapshots__/`. A changed pixel fails the job.

## What is compared

`ShipQuickUITests/TemplateSnapshotTests.swift` has one test per template. Each test draws eight images:

| Axis | Values |
|---|---|
| Colour scheme | light, dark |
| Dynamic Type | smallest (`extraSmall`), largest (`accessibilityExtraExtraExtraLarge`) |
| Device | iPhone SE, iPhone Pro Max |

The images are drawn at scale 1, so each PNG stays far under the 500 KB commit limit.
Prefire adds one more test per `#Preview` in `templates/`. Its images sit in `__Snapshots__/PreviewTests/`.
Both use `swift-snapshot-testing`. The two packages are test-only: `Package.swift` adds them only when the
env var `SHIPQUICK_SNAPSHOTS` is set. A child that depends on `ShipQuickUI` never downloads them.

## Where it runs

Job `ui-ios-snapshots` in `.github/workflows/ci.yml`. It runs when `ui/**` or `tests/fixtures/**` changes.
Pins: `macos-15`, Xcode 16.4, simulator iPhone 16 on iOS 18.5, `timeout-minutes: 45`.
The pins matter. Another simulator draws text a little differently, so the images are compared only on CI,
and only on this exact simulator. Change a pin and the images must be recorded again.

## Record the references on CI

Do this on a branch, the first time and after any wanted change to a template.

1. Push the branch.
2. Start a record run: `gh workflow run ci.yml --ref <branch> -f record=true`.
   The job then runs with `SNAPSHOT_TESTING_RECORD=all` and writes new images instead of comparing.
   The job ends red on purpose (record mode fails every assertion). Ignore that.
3. Find the run: `gh run list --workflow ci.yml --branch <branch> --event workflow_dispatch -L 1`.
4. Download the images: `gh run download <run id> -n ios-snapshots -D ui/ios/ShipQuickUITests/__Snapshots__`.
5. Look at a few PNGs. Then commit them: `git add ui/ios/ShipQuickUITests/__Snapshots__ && git commit`.
6. Push. The normal CI run now compares against the new images and must be green.

The folder `ui/ios/ShipQuickUITests/__Snapshots__/*` is a protected path (`scripts/protected_paths.txt`).
A PR that changes an image is a design change: the owner merges it himself, in every mode.

## Read a failure

The job log names each failing image and the two paths it compared. There is no diff picture in the
artifact. To see the new look, do a record run (above) and open the downloaded PNG.

## On a Mac with Xcode

```
cd ui/ios
SHIPQUICK_SNAPSHOTS=1 xcodebuild test -scheme ShipQuickUI \
  -destination 'platform=iOS Simulator,name=iPhone 16,OS=18.5' \
  -skipPackagePluginValidation -skipMacroValidation -parallel-testing-enabled NO CODE_SIGNING_ALLOWED=NO
```

Needs Xcode 16.4 with the iOS 18.5 simulator. Expect small differences from CI. Never commit images
recorded on a Mac; record them on CI.
