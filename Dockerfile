FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless wget netcat && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/Lavalink && \
    wget -O /opt/Lavalink/Lavalink.jar https://github.com/freyacodes/Lavalink/releases/download/3.7.11/Lavalink.jar

COPY application.yml /opt/Lavalink/application.yml

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD java -jar /opt/Lavalink/Lavalink.jar & \
    echo "Waiting for Lavalink to start on port 2333..." && \
    until nc -z localhost 2333; do echo "Waiting..."; sleep 1; done && \
    echo "Lavalink is up, starting Python bot..." && \
    python main.py
