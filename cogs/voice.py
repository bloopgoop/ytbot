from discord.ext import commands

class VoiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kys(self, ctx):
        await ctx.send('no u!')

async def setup(bot):
    await bot.add_cog(VoiceCommands(bot))
