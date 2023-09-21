from pytube import YouTube
from discord.ext import commands, tasks
from logger_template import Formatter
import discord
import asyncio
import urllib.request
import re
import logging

"""" 
#################################################
#       Cog that manages the youtube player     # 
#################################################

Acknowledgements / Future features:
    - Every function has redundant lines of code to delete user's and bot's message
        -> Have yet to find a way to find an elegant way to only delete this cog's messages
    - Bot can get rate limmited if user does too many actions too fast, will need to add a cooldown feature
    - In the !q pagination loop, there can be a situation where user reacts for over 60 seconds and 
    the pagination loop outlives the bot message's delete_after timer. This results in a message not found error
    - Will add basic_commands.join function and incorporate it here
    - Will add a database to see how many times a song has been played + more stats
    - Need to add support to non ascii characters ( like japanese )
    - Age restricted videos can not be played

"""

# Set up logging
logger = logging.getLogger("Ytplayer logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(Formatter())
logger.handlers.clear()
logger.addHandler(handler)


class Ytplayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None
        self.paused = False
        self.steps = 0
        self.loop_enabled = False
        self.loop_q = []


    async def main_player(self, ctx):

        # Join if user is in a channel and bot is not
        if ctx.author.voice is not None and not self.bot.voice_clients:
            await ctx.author.voice.channel.connect()

        if self.paused:
            return

        while self.queue:
            url = self.queue.pop(0)
            await self.play_music(ctx, url)
        
        self.current_song = None
        await ctx.send("```Queue is empty```")
        # delete_after=60

    @commands.command()
    async def play(self, ctx, *args):
        """ Function to queue up songs """

        # Delete the user's command message after a delay
        #await ctx.message.delete(delay=60)

        # Function to check if arguments are URLS
        url_pattern = r"https?://\S+"
        def is_url(input_string):
            return re.match(url_pattern, input_string) is not None


        url = ""
        if not args:
            url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley" # No arguments -> rick roll
            
        elif not is_url(args[0]): # First argument is not a url-> search for song

            query = "+".join(args)
            logger.info(f"search query: {query}")

            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())[:10]

            titles = [YouTube(f"https://youtube.com/watch?v={video_id}").title.lower() for video_id in video_ids]
            logger.info(f"titles: {titles[:5]}")

            # Return the first title that matches at least one word of the query
            url = ""
            for i, title in enumerate(titles):
                if any(arg.lower() in title for arg in args):
                    url = "https://youtube.com/watch?v=" + video_ids[i]
                    logger.info(f"found: {title}")
                    break
                
            if not url:
                await ctx.send("```Not found, please check spelling```", delete_after=60)
                return
            
        else:
            url = args[0]


        self.queue.append(url)
        if self.loop:
            self.loop_q.append(url)

        # If there is no song currently playing, start the main player
        if self.current_song == None:
            try:
                await self.main_player(ctx)
                logger.info("Main player process ended successfully")
            except Exception as e:
                logger.error(f"Error in play(): {e}")
            return

        await ctx.send(f"```{YouTube(url).title} queued```", delete_after=60)

        

    async def play_music(self, ctx, url):
        """ Main player - controls when songs should be played and when to loop """

        if url is None:
            return

        # Set current song and display the current song in discord
        self.current_song = url
        await ctx.invoke(self.np)

        try:
            # Download audio
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            stream.download(filename="audio_file")

            # Play the audio
            audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source="audio_file")
            ctx.voice_client.play(audio_source, after=lambda e: logger.info(f"Done playing: {yt.title} --- Cleaning up resources"))

            # Wait for the audio to finish playing
            while ctx.voice_client.is_playing() or self.paused:
                if self.steps:
                    ctx.voice_client.stop()
                    self.skip_to(self.steps)
                    self.steps = 0
                await asyncio.sleep(1)
            
            if self.loop_enabled:
                if not self.queue:
                    self.queue = self.loop_q[:]

            ctx.voice_client.stop()

        except Exception as e:
            logger.error(f"Error in play_music(): {e}")


    @commands.command()
    async def q(self, ctx):
        """ Shows the queue of songs """

        # Delete the user's command message after a delay
        await ctx.message.delete(delay=60)

        current_page = 1
        s = self.q_message(current_page)
        bot_message = await ctx.send(s , delete_after=120)
        await bot_message.add_reaction("⬅️")
        await bot_message.add_reaction("➡️")

        # Pagination loop
        def check(reaction, user):
            return (
                reaction.message.id == bot_message.id
                and user == ctx.author
                and str(reaction.emoji) in ["⬅️", "➡️"]
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == "➡️" and current_page < 5:
                    current_page += 1
                elif str(reaction.emoji) == "⬅️" and current_page > 1:
                    current_page -= 1
                else:
                    continue

                page_message = self.q_message(current_page)
                await bot_message.edit(content=page_message)
                await bot_message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                await bot_message.clear_reactions()
                break

    def q_message(self, page):
        s = f"```{len(self.queue)} track(s) queued:\n"
        if page * 5 >= len(self.queue):
            for i in range((page - 1) * 5, len(self.queue)):
                s += f"{i + 1}. {YouTube(self.queue[i]).title}\n"
        else:
            for i in range((page - 1) * 5, page * 5):
                s += f"{i + 1}. {YouTube(self.queue[i]).title}\n"
        s += "```"
        return s
    

    # NEED TO RESTRUCTURE THIS/ MAKE IT NEATER <!---
    def skip_to(self, index):
        if index > len(self.queue):
            logger.error(f"Error: Queue only has {len(self.queue)} songs")
            return
        else:
            self.queue = self.queue[index - 1:]

    @commands.command()
    async def skip(self, ctx):
        # Delete the user's command message after a delay
        await ctx.message.delete(delay=60)

        if self.current_song:
            self.steps = 1
            await ctx.send(f"```Skipped {YouTube(self.current_song).title}```", delete_after=60)
        else:
            await ctx.send(f"```Not playing anything currently```", delete_after=60)

    @commands.command()
    async def jump(self, ctx, index):
        # Delete the user's command message after a delay
        await ctx.message.delete(delay=60)

        index = int(index)
        if index < 1:
            await ctx.send("```Invalid index```", delete_after=60)
            return
        if index > len(self.queue):
            await ctx.send(f"```Error: Queue only has {len(self.queue)} songs```", delete_after=60)
            return
        self.steps = index
        await ctx.send(f"```Jumped to {index}```", delete_after=60)

    
    @commands.command()
    async def np(self, ctx):
        """ Displays current song """

        await ctx.message.delete(delay=60)

        if not self.current_song:
            await ctx.send(f"```Not playing anything currently```", delete_after=60)
            return

        title = YouTube(self.current_song).title
        await ctx.send(f"```Now playing: {title}```", delete_after=60)

    @commands.command()
    async def pause(self, ctx):
        # Delete the user's command message after a delay
        await ctx.message.delete(delay=60)

        if ctx.voice_client.is_playing():
            self.paused = True
            ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        # Delete the user's command message after a delay
        await ctx.message.delete(delay=60)

        if ctx.voice_client.is_paused():
            self.paused = False
            ctx.voice_client.resume()

    @commands.command()
    async def clear(self, ctx):
        # Delete the user's command message after a delay
        await ctx.message.delete(delay=60)

        self.queue = []
        self.loop_q = []
        ctx.voice_client.stop()

    @commands.command()
    async def loop(self, ctx):
        """ Toggle loop feature """

        # Delete the user's command message after a delay
        await ctx.message.delete(delay=60)

        if not self.loop_enabled:
            if self.current_song:
                self.loop_q = [self.current_song] + self.queue[:]
            else:
                self.loop_q = self.queue[:]

        self.loop_enabled = not self.loop_enabled

        s = "enabled" if self.loop_enabled else "disabled"
        await ctx.send(f"```Loop {s}```", delete_after=60)
    
    @commands.command()
    async def remove(self, ctx, index):
        # Delete the user's command message after a delay
        await ctx.message.delete(delay=60)

        index = int(index)
        if index < 1:
            await ctx.send("Invalid index", delete_after=60)
            return
        if index > len(self.queue):
            await ctx.send(f"Error: Queue only has {len(self.queue)} songs", delete_after=60)
            return
        
        url = self.queue.pop(index - 1)
        await ctx.send(f"Removed {YouTube(url).title}", delete_after=60)

async def setup(bot):
    await bot.add_cog(Ytplayer(bot))