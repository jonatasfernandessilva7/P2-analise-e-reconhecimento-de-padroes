FROM python:3.13-slim-bookworm

RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /source

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "13444"]
