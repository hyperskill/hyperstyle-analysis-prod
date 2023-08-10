FROM registry.jetbrains.team/p/code-quality-for-online-learning-platforms/hyperstyle-analysis-prod/hyperstyle-analysis-prod-base:py3.9.17-java17.0.8.7

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


# Installing poetry:
RUN pip install --upgrade "poetry==$POETRY_VERSION"

# Coping repo
COPY . /hyperstyle-analysis-prod
WORKDIR /hyperstyle-analysis-prod

# Installing dependencies:
RUN  poetry  \
     install \
     --no-interaction  \
     --no-ansi  \
     --with data-collection,data-collection,data-labelling,jba,preprocessing,templates

ENTRYPOINT ["/bin/bash"]
