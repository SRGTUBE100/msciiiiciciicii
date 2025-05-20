FROM python:3.11-slim

WORKDIR /app

# Install Java runtime + wget (to download Lavalink if needed)
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless wget && \
    rm -rf /var/lib/apt/lists/*

# Download Lavalink
RUN mkdir -p /opt/Lavalink && \
    wget -O /opt/Lavalink/Lavalink.jar https://github.com/freyacodes/Lavalink/releases/download/3.7.11/Lavalink.jar

# Copy your Lavalink config file
COPY application.yml /opt/Lavalink/application.yml

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot files
COPY . .

# Start Lavalink in background, then run your bot
CMD java -jar /opt/Lavalink/Lavalink.jar & \
    python main.py
