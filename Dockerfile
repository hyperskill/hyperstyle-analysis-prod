FROM registry.jetbrains.team/p/paddle/docker/paddle-py-3-9:0.4.8 as paddle-py-3-9

COPY . /hyperstyle-analysis-prod
WORKDIR /hyperstyle-analysis-prod

RUN paddle install

ENTRYPOINT ["java", "-jar", "/paddle.jar"]