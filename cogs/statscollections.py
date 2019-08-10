import discord
import asyncio
import logging

from discord.ext import commands
from msgstats import ChannelStatistics

import config

STATS_FOLDER = 'DiscordStats'

class StatsCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.Cog.listener()
  async def on_ready(self):
    chan = self.bot.get_channel(433103377015242754)
    self.bot.channelstats = ChannelStatistics(chan)
    async for message in chan.history(limit=100).filter(lambda msg: not msg.author.bot):
      self.bot.channelstats.feed(message)
    
def setup(bot):
  bot.add_cog(StatsCog(bot))
