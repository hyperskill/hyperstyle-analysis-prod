FROM registry.jetbrains.team/p/code-quality-for-online-learning-platforms/hyperstyle-analysis-prod/hyperstyle-analysis-prod-base:py3.11.4-java20.0.2.9

# python:
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  PIP_ROOT_USER_ACTION=ignore \
  # poetry:
  POETRY_VERSION=1.5.1


# Installing poetry and git:
RUN set -eux && \
    apt-get update && \
    apt-get install -y --no-install-recommends git && \
    pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Coping repo
COPY . /hyperstyle-analysis-prod
WORKDIR /hyperstyle-analysis-prod

# Installing and building dependencies:
RUN set -eux && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    poetry  \
    install \
    --no-interaction  \
    --no-ansi  \
    --with data-collection,data-collection,data-labelling,jba,preprocessing,templates && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false gcc python3-dev && \
    yes | poetry cache clear . --all

CMD ["/bin/bash"]
