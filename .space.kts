import java.io.File

job("Release base Docker") {
    startOn {
        gitPush { enabled = false }
    }

    val version = "py3.9.17-java17.0.8.7"
    val type = "hyperstyle-analysis-prod-base"

    kaniko {
        build {
            dockerfile = "./Dockerfile.base"
        }

        push("registry.jetbrains.team/p/code-quality-for-online-learning-platforms/hyperstyle-analysis-prod/${type}") {
            tags(version)
        }
    }
}


job("Release Docker") {
    startOn {
        gitPush {
            enabled = false
        }
    }

    val type = "hyperstyle-analysis-prod"

    kaniko {
        beforeBuildScript {
            content = """
                echo Hello, World!
                python --version
            """
        }

        build {
            dockerfile = "./Dockerfile"
        }

        push("registry.jetbrains.team/p/code-quality-for-online-learning-platforms/hyperstyle-analysis-prod/${type}") {
            tags {
                +"1.2.3"
            }
        }
    }
}