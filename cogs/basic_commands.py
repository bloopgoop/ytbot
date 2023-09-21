from discord.ext import commands

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self,ctx):
        if ctx.author.voice is None:
            await ctx.send("You have to be in a voice channel first!")
            return
        
        if self.bot.voice_clients:
            await ctx.send("I'm already in a voice channel!")
            return
        
        await ctx.author.voice.channel.connect()

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
    
    @commands.command()
    async def clear_messages(self, ctx, amount: int):
        """Clear a specified number of messages in the channel."""
        if amount <= 0:
            await ctx.send("Please provide a positive number of messages to clear.")
            return

        # Delete the command message as well
        await ctx.message.delete()

        # Use the purge() method to clear messages
        deleted_messages = await ctx.channel.purge(limit=amount)

        await ctx.send(f"Cleared {len(deleted_messages)} messages.", delete_after=5)


async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
