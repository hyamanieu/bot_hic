import discord
from discord.ext import tasks, commands
from datetime import datetime

class AutoMessageCog(commands.Cog):
    guild = None
    messages = []

    channel_msg_auto = None

    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=1.0)
    async def send_msg_auto(self):
        test = discord.utils.find(lambda c: c.name == 'dev', self.guild.channels)
        await test.send('Test')

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            if guild.name.startswith('HIC 2021'):
                self.guild = guild

        self.channel_msg_auto = discord.utils.find(lambda c: c.name == 'msg_auto', guild.channels)
        
        await self.loadMessagesAuto()

    async def loadMessagesAuto(self):
        self.messages = []

        async for message in self.channel_msg_auto.history(limit=None):
            content = message.content
            raw_headers, body = content.split('-----\n')

            message = dict({
                'title': None,
                'couleur': '1EB9EA',
                'body': body
            })

            for raw_header in raw_headers.split('\n'):
                if ':' not in raw_header:
                    continue
                
                key, value = raw_header.split(':', 1)

                if key == 'Date':
                    message[key.strip().lower()] = datetime.strptime(value.strip(), '%d/%m/%Y %H:%M')
                else:
                    message[key.strip().lower()] = value.strip()

            print(message)
        
        # self.send_msg_auto.start()


    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.channel

        if channel == self.channel_msg_auto:
            await self.loadMessagesAuto()

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        channel_id = payload.channel_id

        if channel_id == self.channel_msg_auto.id:
            await self.loadMessagesAuto()

def setup(bot):
    bot.add_cog(AutoMessageCog(bot))