import discord
import asyncio
import os
import typing
import logging
import dill
from discord.ext import commands
from msgstats import ChannelStatistics

import config

STATS_FOLDER = 'DCSTATS'

class StatsCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    self.scrape_guild = config.default_guild
    self.scrape_channel = config.default_channel
    self.scrape_limit = config.limit
    self.scrape_count = 0
    self.lastmsg = None
    
    self.scrape_path = f"{STATS_FOLDER}/{self.scrape_guild['name']}/{self.scrape_channel['name']}"
    if not os.path.exists(self.scrape_path):
      os.makedirs(self.scrape_path)
      
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)
    handler = logging.FileHandler(f'{self.scrape_path}/statslog.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('At %(asctime)s - %(message)s\n'))
    self.logger.addHandler(handler)

    if os.path.exists(f'{self.scrape_path}/userstats.pkl'):
      with open(f'{self.scrape_path}/userstats.pkl', 'rb') as f:
        self.bot.channelstats, self.lastmsgid = dill.load(f)
    else:
      self.bot.channelstats = ChannelStatistics(self.scrape_channel['name'],self.scrape_channel['id'])
      self.lastmsgid = 0

  async def scrape(self):
    aftermsg = await self.scrape_channel.fetch_message(self.lastmsgid) if self.lastmsgid else None
    channel = self.bot.get_channel(self.scrape_channel['id'])
    async for message in channel.history(limit=self.scrape_limit, after=aftermsg, oldest_first=True).filter(lambda msg: not msg.author.bot):
      if self.scrape_count == 0: self.firstmsg = message
      self.bot.channelstats.feed(message)
      self.scrape_count += 1
      if self.scrape_count % 200 == 0: # Give updates on how many messages have been scraped every 200 messages
        print('%s messages scraped' % self.scrape_count)
    print('Scraping completed')
    self.lastmsg = message

  async def upload_info(self): #this might not need to be async
    with open(f'{self.scrape_path}/userstats.pkl' , 'wb') as f:
      dill.dump((self.bot.channelstats, self.lastmsg.id), f, dill.HIGHEST_PROTOCOL)
    self.logger.info(f''' READ {self.scrape_count} MESSAGES
First: ID: {self.firstmsg.id} / DAETIME: {self.firstmsg.created_at}
Last: ID: {self.lastmsg.id} / DATETIME: {self.lastmsg.created_at}''')
    logging.shutdown()

  @commands.Cog.listener()
  async def on_ready(self):
    print('Logged in as %s' % self.bot.user.name)
    print('Server: %s' % self.scrape_guild['name'])
    print('Channel: %s' % self.scrape_channel['name'])
    print(self.bot.user.id)
    print('------')
    if not self.scrape_limit == 0:
      await self.scrape()
    else:
      print('No messages scraped')

  @commands.Cog.listener()
  async def on_disconnect(self):
    print('Goodbye!')
    if self.scrape_limit == 0:
      return
    await self.upload_info()

  @commands.command(alias='statistics')
  async def stats(self, ctx, mention: typing.Optional[discord.Member], what: str = None):
    '''Returns statistcs on a user (or the channel itself) for whatever channel MuffinBot is presently logging. Only usable in that channel's server
!stats me -> returns statistics on YOU! :)
!stats channel -> returns statistics on the present logging channel
!stats [ping user here] -> returns statistics on the pinged user'''
    if what == 'me':
      await ctx.send(self.bot.channelstats.get_user_by_id(ctx.author.id).display_info())
    elif what == 'channel':
      await ctx.send(self.bot.channelstats.display_info())
    elif mention:
      await ctx.send(self.bot.channelstats.get_user_by_id(mention.id).display_info())
    else:
      await ctx.send('Invalid argument')
    
def setup(bot):
  bot.add_cog(StatsCog(bot))

