FROM openjdk:17-slim

RUN apt-get update && apt-get install -y python3 python3-pip netcat-openbsd wget && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/Lavalink

RUN wget -O Lavalink.jar https://github.com/freyacodes/Lavalink/releases/download/3.7.11/Lavalink.jar

COPY application.yml .

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD java -jar /opt/Lavalink/Lavalink.jar & \
    echo "Waiting for Lavalink on port 2333..." && \
    until nc -z localhost 2333; do sleep 1; done && \
    echo "Starting Python bot" && \
    python3 main.py
