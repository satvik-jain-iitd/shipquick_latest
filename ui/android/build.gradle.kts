// Story #217: compile every template and the generated proof/ApiProof.kt against real Compose Material 3.
// Every version is exact. AGP 8.13.2 supports API 36.1 and needs Gradle 8.13 or newer (Google's AGP 8.13 notes).
// Compose BOM 2025.10.00 maps material3 to 1.4.0, the version docs/research/android-m3-api.md counts.
plugins {
    id("com.android.library") version "8.13.2"
    id("org.jetbrains.kotlin.android") version "2.2.21"
    id("org.jetbrains.kotlin.plugin.compose") version "2.2.21"
}

android {
    namespace = "com.shipquick.ui"
    compileSdk = 36
    defaultConfig {
        minSdk = 24
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    sourceSets["main"].java.srcDirs("templates", "theme", "proof")
}

kotlin {
    compilerOptions {
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2025.10.00"))
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-core")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.ui:ui")
}
