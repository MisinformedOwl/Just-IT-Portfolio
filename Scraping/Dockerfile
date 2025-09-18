# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12.10

FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y ca-certificates firefox-esr wget \
    && wget -q https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz \
    && tar -xzf geckodriver-v0.36.0-linux64.tar.gz -C /usr/local/bin \
    && chmod +x /usr/local/bin/geckodriver \
    && rm geckodriver-v0.36.0-linux64.tar.gz \
    && apt-get remove -y wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos "" --home "/app" --shell "/sbin/nologin" --no-create-home --uid "${UID}" appuser

RUN --mount=type=cache,target=/root/.cache/pip --mount=type=bind,source=requirements.txt,target=requirements.txt python -m pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/.cache/selenium && chown -R appuser:appuser /app

USER appuser

ENV XDG_CACHE_HOME=/app/.cache

CMD ["python", "/app/scraper/LinkedInScraper.py"]