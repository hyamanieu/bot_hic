import re
import discord
from discord.ext import commands

class WelcomeCog(commands.Cog):
    guild = None
    users = []

    channel_welcome = None
    channel_help = None
    channel_bdd_users = None

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            if guild.name.startswith('HIC 2021'):
                self.guild = guild

        self.channel_welcome = discord.utils.find(lambda c: c.name == 'bienvenue', guild.channels)
        self.channel_help = discord.utils.find(lambda c: c.name == 'demandes-aide', guild.channels)
        self.channel_bdd_users = discord.utils.find(lambda c: c.name == 'users', guild.channels)

        await self.loadUsers()

    async def loadUsers(self):
        self.users = []

        async for message in self.channel_bdd_users.history(limit=None):
            content = message.content

            for line in content.split('\n'):
                data = line.split(',')

                if len(data) >= 4:
                    self.users.append({
                        'name': data[0],
                        'firstname': data[1],
                        'mail': data[2],
                        'role': data[3]
                    })

    @commands.Cog.listener()
    async def on_member_join(self, member):
        dm_channel = member.dm_channel

        if dm_channel is None:
            dm_channel = await member.create_dm()

        msg = (
            f"Bonjour {member.mention} vous débarquez ici, on dirait !\n"
            f"Je suis {self.bot.user.mention}, je suis un gentil robot et je vais vous accompagner\n"
            f"Tout d’abord pouvez-vous me donner l’adresse mail avec laquelle vous vous êtes inscrit(e) à l’évènement"
        )

        await dm_channel.send(msg)

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.channel

        if channel == self.channel_bdd_users:
            await self.loadUsers()
        elif isinstance(channel, discord.DMChannel):
            author = message.author
            member = self.guild.get_member(author.id)

            if member is None:
                await channel.send("Vous n'êtez pas présent sur le serveur HIC 2021 !")
                return

            if len(member.roles) <= 1:
                content = message.content.strip()

                if(re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', content)):
                    user = next((user for user in self.users if user["mail"] == content), None)

                    if user is None:
                        await channel.send("Désolé ! Je n’arrive pas à reconnaître votre adresse ! J’ai envoyé un message aux organisateurs pour qu’ils viennent vous aider !")
                        await self.channel_help.send(f"{member.mention} n’a pas été reconnu(e) dans la liste des participants, merci de le contacter !")
                        return
                    
                    role = discord.utils.find(lambda r: r.name == user['role'], self.guild.roles)

                    if role is None:
                        await channel.send("Désolé ! Je n’arrive pas à reconnaître le rôle que je dois t'assigner ! J’ai envoyé un message aux organisateurs pour qu’ils viennent vous aider !")
                        await self.channel_help.send(f"Le rôle {user['role']} de {member.mention} n’existe pas !")
                        return

                    await member.add_roles(role)
                    await member.edit(nick=f"{user['firstname']} {user['name'][0]}.")

                    await channel.send((
                        f"Bienvenue au HIC ! Vous êtes reconnu(e) en tant que {user['role']}, vous avez maintenant accès à l’ensemble des canaux\n"
                        f"Vous pouvez me demander de l’aide à tout moment en tapant !aide"
                    ))

                    await self.channel_welcome.send(f"Bienvenue à {member.mention} sur le Discord du Hacking Industry Camp !")

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        channel_id = payload.channel_id

        if channel_id == self.channel_bdd_users.id:
            await self.loadUsers()

def setup(bot):
    bot.add_cog(WelcomeCog(bot))