import discord
import asyncio
import os
import logging
import dill
from discord.ext import commands
from dcstats import UserStatistics

MUFFIN_ID = 173610171883454464

class StatsBot(commands.Bot):
  def __init__(self, command_prefix, **options):
    super().__init__(command_prefix, **options)
    self.userlist = list()
    self.scrape_count = 0
  
  @property
  def scrape_path(self):
    return f'DCSTATS/{self.scrape_guild}/{self.scrape_channel}'

  def _selection_interface(self):
    '''
SERVER/CHANNEL SELECTION:
Lets the user choose guild, channel, and a message scraping limit; returns a tuple with all three values
    '''
    for n in range(len(self.guilds)):
      print(f'[{n}] {self.guilds[n]}')
    selection = int(input('Select a server:'))
    guild = self.guilds[selection]
    for n in range(len(guild.text_channels)):
      print(f'[{n}] {guild.text_channels[n]}')
    selection = int(input('Select a channel:'))
    channel = guild.text_channels[selection]
    limit = int(input('Message limit?'))
    return guild, channel, limit
  
  def _fileinit(self):
    '''
Creates a folder for logging/pickling if there's none, else gets the info from the pickle file
From the pickle file, Returns a tuple with 1) a list of UserStatistic objects and 2) the id of the last message logged
    '''
    if not os.path.exists(self.scrape_path):
      print(self.scrape_path)
      os.makedirs(self.scrape_path)
    logging.basicConfig(filename=f'{self.scrape_path}/statslog.log',\
                        format='At %(asctime)s - %(message)s\n', level=logging.INFO)
    if os.path.exists(f'{self.scrape_path}/userstats.pkl'):
      with open(f'{self.scrape_path}/userstats.pkl', 'rb') as f:
        return dill.load(f)
    else:
      return (list(), 0)
  
  def feedmsg(self, message):
    ''' Feeds a message into the userlist'''
    for user in self.userlist:
      if user.id == message.author.id:
        user.feed(message)
        break
    else: #for-else construct is intentional
      user = UserStatistics(message.author)
      user.feed(message)
      self.userlist.append(user)


############################################################################################################    
  async def on_ready(self):
    print('Logged in as %s' % self.user.name)
    print(self.user.id)
    print('------')
    ### SERVER/CHANNEL SELECTION
    self.scrape_guild, self.scrape_channel, self.scrape_limit = self._selection_interface()
    if self.scrape_limit == 0:
      print('No messages scraped')
      return
    self.userlist, lastmsgid = self._fileinit()
    aftermsg = await self.scrape_channel.fetch_message(lastmsgid) if lastmsgid else None
    async for message in self.scrape_channel.history(limit=self.scrape_limit, after=aftermsg, oldest_first=True).filter(lambda msg: not msg.author.bot):
      if self.scrape_count == 0: self.firstmsg = message
      self.feedmsg(message)
      self.scrape_count += 1
    self.lastmsg = message

  async def on_disconnect(self):
    if self.scrape_limit == 0:
      print('Goodbye!')
      return
    with open(f'{self.scrape_path}/userstats.pkl' , 'wb') as f:
      dill.dump((self.userlist, self.lastmsg.id), f, dill.HIGHEST_PROTOCOL)
    logging.info(f''' READ {self.scrape_count} MESSAGES
First: ID: {self.firstmsg.id} / DAETIME: {self.firstmsg.created_at}
Last: ID: {self.lastmsg.id} / DATETIME: {self.lastmsg.created_at}''')
    logging.shutdown()
    print('Goodbye!')
