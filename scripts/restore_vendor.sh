#!/usr/bin/env bash
# Story #242: prove the vendor backup restores with no network (docs/VENDOR_BACKUP.md).
# Usage: restore_vendor.sh <backup-dir> [work-dir]
#   <backup-dir> is a checkout of the backup/vendor branch. Nothing else is read.
# Installs ui/tool with `npm ci --offline` from the backup's npm cache, then resolves the pinned Compose
# artifacts with Gradle --offline from the backup's local Maven folder. Runs on CI only (RESTORE_ALLOW_LOCAL=1 overrides).
set -euo pipefail
[ "${CI:-}" = "true" ] || [ "${RESTORE_ALLOW_LOCAL:-}" = "1" ] || { echo "restore_vendor.sh runs on GitHub CI only. Set RESTORE_ALLOW_LOCAL=1 to run it here."; exit 2; }
B=$(cd "${1:?usage: restore_vendor.sh <backup-dir> [work-dir]}" && pwd)
W="${2:-$(mktemp -d)}"
export GRADLE_USER_HOME="$W/gradle-home"   # an empty Gradle cache, so nothing can come from anywhere else
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)

python3 "$HERE/vendor_backup.py" --manifest-check "$B"

# npm: a copy of the cache (npm writes logs into it), then no registry at all.
mkdir -p "$W/tool"
cp "$ROOT/ui/tool/package.json" "$ROOT/ui/tool/package-lock.json" "$W/tool/"
cp -R "$B/npm-cache" "$W/npm-cache"
(cd "$W/tool" && npm ci --ignore-scripts --offline --no-audit --no-fund --cache "$W/npm-cache")
test -d "$W/tool/node_modules/@astryxdesign/core"
echo "ok   npm ci --offline restored $(ls "$W/tool/node_modules" | wc -l) top-level entries"

# Gradle: the only repository is the backup folder.
BOM=$(python3 -c "import json,sys; print(json.load(open('$HERE/vendor_pins.json'))['bom'])")
mkdir -p "$W/gradle"
cat > "$W/gradle/settings.gradle" <<EOF
rootProject.name = 'vendor-restore-proof'
dependencyResolutionManagement {
  repositoriesMode = RepositoriesMode.FAIL_ON_PROJECT_REPOS
  repositories { maven { url = uri('$B/maven') } }
}
EOF
cat > "$W/gradle/build.gradle" <<EOF
plugins { id 'java-library' }
configurations {
  vendorCompile {
    canBeResolved = true
    canBeConsumed = false
    attributes {
      attribute(Usage.USAGE_ATTRIBUTE, objects.named(Usage, Usage.JAVA_API))
      attribute(Attribute.of('org.jetbrains.kotlin.platform.type', String), 'androidJvm')
    }
  }
}
dependencies {
  vendorCompile platform('$BOM')
  vendorCompile 'androidx.compose.material3:material3'
  vendorCompile 'androidx.compose.material:material-icons-core'
}
tasks.register('resolveVendor') {
  doLast {
    def files = configurations.vendorCompile.incoming.files.files
    files.each { println "resolved \${it.name}" }
    if (files.size() < 5) throw new GradleException("only \${files.size()} files resolved from the backup")
  }
}
EOF
(cd "$W/gradle" && gradle --offline --no-daemon --console=plain resolveVendor)
echo "ok   Gradle --offline resolved the pinned Compose artifacts from the backup"
