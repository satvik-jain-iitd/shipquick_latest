// Story #185: lints src/good or src/bad with the kit's own configs. Nothing here compiles the screens;
// detekt and Konsist read text only. Every version is exact. Pass -PuiDir=src/bad and -Ptier=ci (default tier: local).
plugins {
    kotlin("jvm") version "2.0.21"
    id("io.gitlab.arturbosch.detekt") version "1.23.8"
}

val uiDir = (findProperty("uiDir") ?: "src/good").toString()
val ci = findProperty("tier") == "ci"
val lint = rootDir.resolve("../../../ui/android/lint")

detekt {
    buildUponDefaultConfig = false
    config.setFrom(if (ci) files(lint.resolve("detekt.yml"), lint.resolve("detekt-ci.yml")) else files(lint.resolve("detekt.yml")))
    source.setFrom(uiDir)
    ignoreFailures = !ci
}

kotlin {
    sourceSets.test { kotlin.srcDir(lint) } // UiRulesKonsistTest.kt is the only .kt file there
}

dependencies {
    testImplementation("com.lemonappdev:konsist:0.17.3")
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.4")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher:1.11.4")
}

tasks.test {
    useJUnitPlatform()
    systemProperty("shipquick.ui.dir", "tests/fixtures/android/$uiDir") // Konsist reads a path from the repository root
    testLogging { exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL }
}
