from discord.ext import commands

class VoiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bing(self, ctx):
        await ctx.send('bong!')

async def setup(bot):
    await bot.add_cog(VoiceCommands(bot))
