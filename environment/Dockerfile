FROM python:3.11-slim@sha256:b5b2b1e4e0c3a1d5f8e2b9c4d1e8a5f2b9c4d1e8a5f2b9c4d1e8a5f2b9c

RUN pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5

WORKDIR /app

COPY access.log /app/access.log
