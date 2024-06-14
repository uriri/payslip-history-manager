FROM python:3.10-slim as python-base

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYSETUP_PATH="/opt/pysetup"

ARG USERNAME=user
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} -s /bin/bash \
    && pip install --upgrade pip

FROM python-base as python-builder

SHELL [ "/bin/bash", "-o", "pipefail", "-c" ]

USER root

# hadolint ignore=DL3008,DL3015
RUN apt-get update \
    && apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python

FROM python-base as develop

COPY --from=python-builder ${POETRY_HOME} ${POETRY_HOME}

WORKDIR /workspace

ENV PATH="${POETRY_HOME}/bin:${PATH}" \
    TZ="Asia/Tokyo"

USER root

# hadolint ignore=DL3008,DL3009,DL3015
RUN apt-get update \
    && apt-get install -y sudo vim git \
    && echo ${USERNAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

USER ${USERNAME}

FROM python-base AS product
