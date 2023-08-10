job("Hyperstyle Analysis Prod | Release base Docker") {
    startOn {
        gitPush {
            enabled = false
        }
    }

    val version = "py3.9.17-java17.0.8.7"
    val type = "hyperstyle-analysis-prod-base"

    kaniko {
        build {
            context = "."
            dockerfile = "Dockerfile.base"
        }

        push("registry.jetbrains.team/p/code-quality-for-online-learning-platforms/hyperstyle-analysis-prod/${type}") {
            tags(version)
        }
    }
}
