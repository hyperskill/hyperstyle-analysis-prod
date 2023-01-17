job("HyperstyleUtilities / Release / Docker") {
    startOn {
        gitPush {
            enabled = false
        }
    }

    val version = "0.0.1"
    val type = "hyperstyle-utilities"

    container("openjdk:11") {}

    kaniko {
        build {
            context = "."
            dockerfile = "Dockerfile"
            target = "paddle-py-3-9"
            args["VERSION"] = version
        }
        push("registry.jetbrains.team/p/code-quality-for-online-learning-platforms/hyperstyle-utilities/${type}") {
            tags(version)
        }
    }
}