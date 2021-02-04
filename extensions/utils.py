import discord
from discord.ext import commands
import structlog 

import os

from . import settings

log = structlog.get_logger()

class UtilsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = settings.Settings()

    async def bot_log_message(self, *args, **kwargs):
        BOT_LOG_CHANNEL_ID = os.getenv('BOT_LOG_CHANNEL_ID')

        try:
            if BOT_LOG_CHANNEL_ID:
                BOT_LOG_CHANNEL_ID = int(BOT_LOG_CHANNEL_ID)
                bot_log_channel = discord.utils.get(self.bot.get_all_channels(), id=BOT_LOG_CHANNEL_ID)
                
                if bot_log_channel:
                    await bot_log_channel.send(*args, **kwargs)
                else:
                    log.warning(f'Could not find bot log channel with id {BOT_LOG_CHANNEL_ID}')
        except Exception as e:
            log.error('Could not post message to bot log channel', exc_info=e)

def setup(bot):
    bot.add_cog(UtilsCog(bot))