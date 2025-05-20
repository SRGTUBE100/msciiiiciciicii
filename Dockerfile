FROM openjdk:17-slim

# Install dependencies
RUN apt-get update && apt-get install -y python3 python3-pip netcat-openbsd wget && rm -rf /var/lib/apt/lists/*

# Download Lavalink server jar
WORKDIR /opt/Lavalink
RUN wget -O Lavalink.jar https://github.com/freyacodes/Lavalink/releases/download/3.7.11/Lavalink.jar

# Copy Lavalink config
COPY application.yml /opt/Lavalink/application.yml

# Copy Python app
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY . /app/

# Start Lavalink on Railway dynamic port and wait for it, then start Python bot
CMD java -Dserver.port=$PORT -jar /opt/Lavalink/Lavalink.jar & \
    echo "Waiting for Lavalink on port $PORT..." && \
    until nc -z localhost $PORT; do sleep 1; done && \
    echo "Starting Python bot" && \
    python3 main.py
