FROM registry.jetbrains.team/p/paddle/docker/paddle-py-3-9:0.4.7

COPY . /hyperstyle-analysis-prod
WORKDIR /hyperstyle-analysis-prod

RUN python3 -m pip install --upgrade pip
RUN paddle install

ENTRYPOINT ["java", "-jar", "/paddle.jar"]