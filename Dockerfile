FROM openjdk:17-slim as lavalink

WORKDIR /opt/Lavalink

RUN apt-get update && \
    apt-get install -y wget && \
    wget https://github.com/freyacodes/Lavalink/releases/download/3.7.11/Lavalink.jar

COPY application.yml application.yml

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"] 
