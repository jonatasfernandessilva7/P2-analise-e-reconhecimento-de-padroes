FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /source

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn server:app --reload --port 9999", "your_script_name.py"]