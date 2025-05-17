# Discord Music Bot 🎵

A feature-rich Discord music bot with a beautiful UI and comprehensive music commands.

## Features

- Play music from YouTube, SoundCloud, and more
- Queue system with beautiful embeds
- Easy to use commands with prefix `&`
- Docker support for easy deployment
- High-quality audio playback using Lavalink

## Commands

- `&play [song]` - Play a song or add it to queue
- `&stop` - Stop playing and clear the queue
- `&skip` - Skip the current song
- `&queue` - Show the current queue
- `&pause` - Pause the current song
- `&resume` - Resume the paused song
- `&connect` - Connect to your voice channel
- `&help` - Show all commands

## Setup

1. Create a Discord Bot:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the Bot section and create a bot
   - Copy the bot token
   - Enable all Privileged Gateway Intents

2. Configure the bot:
   - Copy your bot token into `config.py`
   - Update the Lavalink configuration in `application.yml` if needed

3. Run with Docker:
```bash
docker-compose up --build
```

4. Run without Docker:
   - Install Java 17 or higher
   - Download Lavalink.jar
   - Run Lavalink server:
   ```bash
   java -jar Lavalink.jar
   ```
   - Install Python requirements:
   ```bash
   pip install -r requirements.txt
   ```
   - Run the bot:
   ```bash
   python main.py
   ```

## Requirements

- Python 3.8 or higher
- Java 17 or higher (for Lavalink)
- Discord.py
- Wavelink
- Docker (optional)

## Support

If you need help or want to report a bug, please open an issue on GitHub. 
