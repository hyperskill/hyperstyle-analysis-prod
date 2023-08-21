job("Release base Docker") {
    startOn {
        gitPush { enabled = false }
    }

    val version = "py3.11.4-java20.0.2.9"
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
        gitPush { enabled = false }
    }

    val type = "hyperstyle-analysis-prod"

    kaniko {
        beforeBuildScript {
            content = """
                export DOCKER_TAG=${'$'}(grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d ' ' -f 3)
            """
        }

        build {
            dockerfile = "./Dockerfile"
        }

        push("registry.jetbrains.team/p/code-quality-for-online-learning-platforms/hyperstyle-analysis-prod/${type}") {
            tags {
                +"\$DOCKER_TAG"
            }
        }
    }
}