FROM python:3.11-slim-bookworm

RUN apt update \
    && apt install --no-install-recommends -y git python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install git+https://github.com/anz-hexe/insightful-routines.git
