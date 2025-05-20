FROM openjdk:17-slim as lavalink

WORKDIR /opt/Lavalink

RUN apt-get update && \
    apt-get install -y wget && \
    wget https://github.com/freyacodes/Lavalink/releases/download/3.7.11/Lavalink.jar

COPY application.yml application.yml


FROM python:3.11-slim

WORKDIR /app

# Copy Lavalink from builder stage
COPY --from=lavalink /opt/Lavalink /opt/Lavalink

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run Lavalink in background and then your bot
CMD java -jar /opt/Lavalink/Lavalink.jar & \
    python main.py
