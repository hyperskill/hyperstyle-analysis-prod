FROM registry.jetbrains.team/p/paddle/docker/paddle-py-3-8:0.5.2 as paddle-py-3-8

COPY . /hyperstyle-analysis-prod
WORKDIR /hyperstyle-analysis-prod

RUN paddle install

ENTRYPOINT ["java", "-jar", "/paddle.jar"]