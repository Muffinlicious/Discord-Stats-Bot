import discord
import asyncio
import logging

from discord.ext import commands
from msgstats import GuildStatistics

import config

STATS_FOLDER = 'DiscordStats'

class StatsCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.scraped_messages = 0 
  @commands.Cog.listener()
  async def on_ready(self):
    self.bot.guildstats = GuildStatistics(self.bot.get_guild(config.primary_guild))
    async for message in self.bot.get_channel(self.bot.guildstats.chanlist[0].id).history(limit=config.limit).filter(lambda msg: not msg.author.bot):
      self.bot.guildstats.feed(message)
      self.scraped_messages += 1
    self.bot.guildstats.json_upload()
def setup(bot):
  bot.add_cog(StatsCog(bot))
