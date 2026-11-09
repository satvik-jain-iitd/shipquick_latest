// Story #185: the fixture build for the Android UI lint. It runs on GitHub CI only (ADR-012).
pluginManagement {
    repositories {
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
    }
}
rootProject.name = "ui-lint-fixture"
