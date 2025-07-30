FROM python:3.13-slim-bookworm

ARG PORT

ENV PORT=$PORT

RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /source

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT uvicorn server:app --host 0.0.0.0 --port PORT
