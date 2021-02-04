import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='aide')
    async def help(self, ctx):
        """
        Commande: !help ou !aide
        Argument: /
        
        Affiche un embed avec des informations pour obtenir de l'aide
        """
        
        utils = self.bot.get_cog('UtilsCog')

        embed = discord.Embed(title="Aide")
        
        embed.description = ""
        embed.description += "==== Hacking Industry Camp - Aide ====\n"
        embed.description += "- `!help` : pour obtenir l'aide des commandes\n"
        embed.description += "- `@bénévoles` : pour appeler un bénévole\n"
        embed.description += "- `@coach` : pour être coaché\n"
        embed.description += f"- `@{utils.settings.ADMIN_ROLE}` : si quelqu'un doit passer au conseil disciplinaire\n"
        embed.description += "\n"
        embed.description += "Votez en cliquant sous les emojis. Y a un nombre max de vote!\n"

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(HelpCog(bot))