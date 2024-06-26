FROM python:3.11-slim-bookworm

RUN apt update \
    && apt install --no-install-recommends -y gcc git python3-pip libpq-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install git+https://github.com/anz-hexe/insightful-routines.git@0.2.0

