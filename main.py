import os
import discord
from discord.ext import commands
import wavelink
import datetime
import asyncio
from typing import Optional
import re

# Fetch secrets
TOKEN = os.environ.get("TOKEN")
LAVALINK_HOST = os.environ.get("LAVALINK_HOST")
LAVALINK_PORT = int(os.environ.get("LAVALINK_PORT", 2333))  # fallback in case it's unset
LAVALINK_PASSWORD = os.environ.get("LAVALINK_PASSWORD")
LAVALINK_REGION = os.environ.get("LAVALINK_REGION", "us_central")

# Continue with your existing code...

class MusicBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='&',
            intents=discord.Intents.all(),
            help_command=None
        )
        self.add_listener(self.on_wavelink_node_ready, 'on_wavelink_node_ready')

    async def setup_hook(self):
        node: wavelink.Node = wavelink.Node(
            uri=f"http://{LAVALINK_HOST}:{LAVALINK_PORT}",
            password=LAVALINK_PASSWORD,
            region=LAVALINK_REGION
        )
        await wavelink.NodePool.connect(client=self, nodes=[node])


    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f'Node {node.identifier} is ready!')

    async def on_ready(self):
        print(f'Bot is ready! Logged in as {self.user}')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="&help"))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        
    def get_queue(self, guild_id):
        if guild_id not in self.queue:
            self.queue[guild_id] = []
        return self.queue[guild_id]

    @commands.command(name='connect', aliases=['join'])
    async def connect_command(self, ctx):
        """Connect to a voice channel"""
        if not ctx.author.voice:
            return await ctx.send(embed=discord.Embed(description="❌ You must be in a voice channel!", color=EMBED_COLOR))
            
        if ctx.voice_client:
            return await ctx.send(embed=discord.Embed(description="❌ I'm already connected to a voice channel!", color=EMBED_COLOR))
            
        await ctx.author.voice.channel.connect(cls=wavelink.Player)
        embed = discord.Embed(description=f"✅ Connected to {ctx.author.voice.channel.mention}", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.command(name='play', aliases=['p'])
    async def play_command(self, ctx, *, query: str):
        """Play a song with the given search query"""
        if not ctx.voice_client:
            await ctx.invoke(self.connect_command)
            
        player: wavelink.Player = ctx.voice_client
        
        # Check if it's a valid URL
        if not re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', query):
            query = f'ytsearch:{query}'
            
        tracks = await wavelink.NodePool.get_node().get_tracks(query=query)
        
        if not tracks:
            return await ctx.send(embed=discord.Embed(description="❌ No songs were found!", color=EMBED_COLOR))
            
        track = tracks[0]
        
        if not player.is_playing():
            await player.play(track)
            embed = discord.Embed(title="🎵 Now Playing", description=f"[{track.title}]({track.uri})", color=EMBED_COLOR)
            embed.add_field(name="Duration", value=str(datetime.timedelta(seconds=track.length)))
            embed.add_field(name="Requested by", value=ctx.author.mention)
            embed.set_thumbnail(url=track.thumbnail)
            await ctx.send(embed=embed)
        else:
            self.get_queue(ctx.guild.id).append(track)
            embed = discord.Embed(title="🎵 Added to Queue", description=f"[{track.title}]({track.uri})", color=EMBED_COLOR)
            embed.add_field(name="Duration", value=str(datetime.timedelta(seconds=track.length)))
            embed.add_field(name="Position in queue", value=len(self.get_queue(ctx.guild.id)))
            embed.set_thumbnail(url=track.thumbnail)
            await ctx.send(embed=embed)

    @commands.command(name='stop')
    async def stop_command(self, ctx):
        """Stop the currently playing song"""
        if not ctx.voice_client:
            return await ctx.send(embed=discord.Embed(description="❌ I'm not connected to a voice channel!", color=EMBED_COLOR))
            
        player: wavelink.Player = ctx.voice_client
        
        if not player.is_playing():
            return await ctx.send(embed=discord.Embed(description="❌ Nothing is playing!", color=EMBED_COLOR))
            
        await player.stop()
        self.queue[ctx.guild.id] = []
        embed = discord.Embed(description="⏹️ Stopped playing and cleared the queue", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.command(name='skip', aliases=['s'])
    async def skip_command(self, ctx):
        """Skip the currently playing song"""
        if not ctx.voice_client:
            return await ctx.send(embed=discord.Embed(description="❌ I'm not connected to a voice channel!", color=EMBED_COLOR))
            
        player: wavelink.Player = ctx.voice_client
        
        if not player.is_playing():
            return await ctx.send(embed=discord.Embed(description="❌ Nothing is playing!", color=EMBED_COLOR))
            
        await player.stop()
        embed = discord.Embed(description="⏭️ Skipped the current song", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.command(name='queue', aliases=['q'])
    async def queue_command(self, ctx):
        """Display the current queue"""
        if not ctx.voice_client:
            return await ctx.send(embed=discord.Embed(description="❌ I'm not connected to a voice channel!", color=EMBED_COLOR))
            
        player: wavelink.Player = ctx.voice_client
        queue = self.get_queue(ctx.guild.id)
        
        if not player.is_playing() and not queue:
            return await ctx.send(embed=discord.Embed(description="❌ Queue is empty!", color=EMBED_COLOR))
            
        embed = discord.Embed(title="🎵 Queue", color=EMBED_COLOR)
        
        if player.is_playing():
            embed.add_field(name="Now Playing", value=f"[{player.track.title}]({player.track.uri})", inline=False)
            
        if queue:
            queue_list = ""
            for i, track in enumerate(queue, 1):
                queue_list += f"{i}. [{track.title}]({track.uri})\n"
            embed.add_field(name="Up Next", value=queue_list, inline=False)
            
        await ctx.send(embed=embed)

    @commands.command(name='pause')
    async def pause_command(self, ctx):
        """Pause the currently playing song"""
        if not ctx.voice_client:
            return await ctx.send(embed=discord.Embed(description="❌ I'm not connected to a voice channel!", color=EMBED_COLOR))
            
        player: wavelink.Player = ctx.voice_client
        
        if not player.is_playing():
            return await ctx.send(embed=discord.Embed(description="❌ Nothing is playing!", color=EMBED_COLOR))
            
        await player.pause()
        embed = discord.Embed(description="⏸️ Paused the current song", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.command(name='resume')
    async def resume_command(self, ctx):
        """Resume the currently paused song"""
        if not ctx.voice_client:
            return await ctx.send(embed=discord.Embed(description="❌ I'm not connected to a voice channel!", color=EMBED_COLOR))
            
        player: wavelink.Player = ctx.voice_client
        
        if not player.is_paused():
            return await ctx.send(embed=discord.Embed(description="❌ Nothing is paused!", color=EMBED_COLOR))
            
        await player.resume()
        embed = discord.Embed(description="▶️ Resumed the current song", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show all commands"""
        embed = discord.Embed(title="🎵 Music Bot Commands", color=EMBED_COLOR)
        embed.add_field(name="&play [song]", value="Play a song or add it to queue", inline=False)
        embed.add_field(name="&stop", value="Stop playing and clear the queue", inline=False)
        embed.add_field(name="&skip", value="Skip the current song", inline=False)
        embed.add_field(name="&queue", value="Show the current queue", inline=False)
        embed.add_field(name="&pause", value="Pause the current song", inline=False)
        embed.add_field(name="&resume", value="Resume the paused song", inline=False)
        embed.add_field(name="&connect", value="Connect to your voice channel", inline=False)
        embed.set_footer(text="Made with ❤️ | Prefix: &")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))


def main():
    bot = MusicBot()

    @bot.event
    async def setup_hook():
        await bot.load_extension('main')  # Only if you're using cogs/main.py

    bot.run(os.environ["TOKEN"])

# Entry point
if __name__ == "__main__":
    main()
