job("HyperstyleUtilities / Release / Docker") {
    startOn {
        gitPush {
            enabled = false
        }
    }

    val version = "0.0.1"
    val type = "hyperstyle-utilities"

    kaniko {
        build {
            context = "."
            dockerfile = "Dockerfile"
            target = type
            args["VERSION"] = version
        }
        push("registry.jetbrains.team/p/code-quality-for-online-learning-platforms/hyperstyle-utilities/docker/${type}") {
            tags(version)
        }
    }
}