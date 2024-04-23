FROM python:3.11.9-slim-bookworm as base

WORKDIR /application

RUN apt-get update && \
    apt-get install -y gcc libpq-dev wget && \
    apt clean && \
    rm -rf /var/cache/apt/*

ENV \
    PYTHONIOENCODING=utf-8 \
	# Turns off writing .pyc files
	PYTHONDONTWRITEBYTECODE=1 \
	# Seems to speed things up
	PYTHONUNBUFFERED=1 \
	# Default VENV usage
	PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_NO_CACHE=true \
    UV_SYSTEM_PYTHON=true


COPY requirements/ /tmp/requirements
RUN pip install -U pip && \
	pip install uv && \
    uv pip install -r /tmp/requirements/dev.txt

COPY . .

RUN chmod +x ./scripts/* && \
    chmod +x ./docker/*

EXPOSE 8000

CMD [ "./docker/entrypoint-dev.sh" ]
