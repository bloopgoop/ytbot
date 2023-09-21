from pytube import YouTube
from discord.ext import commands, tasks
import discord
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load Cogs
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.load_extension("cogs.basic_commands")
    await bot.load_extension("cogs.voice")
    await bot.load_extension("cogs.ytplayer")


@bot.command()
async def reyt(ctx):
    # Delete the user's command message after a delay
    await ctx.message.delete(delay=60)

    try:
        await bot.reload_extension("cogs.ytplayer")
        await ctx.send(f"Reloaded module: Ytplayer", delete_after=60)
    except commands.ExtensionNotFound:
        await ctx.send(f"Module not found: Ytplayer", delete_after=60)
    except Exception as e:
        await ctx.send(f"Error reloading module: Ytplayer\n{str(e)}", delete_after=60)

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN, log_handler=handler)
