import discord
import asyncio
import os
import logging
import dill
from discord.ext import commands
from dcstats import ChannelStatistics

MUFFIN_ID = 173610171883454464

class StatsBot(commands.Bot):
  
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
If there's no folder for logging and pickling, create one. Otherwise get the data from the pickle file.
Initializes the logger (set to INFO)
From the pickle file, Returns a tuple with 1) a ChannelStatistics object and 2) the id of the last message logged. If the pickle file doesn't yet exist return (NoneType, 0)
    '''
    
    
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
        return dill.load(f)
    else:
      return (None, 0)

############################################################################################################    
  async def on_ready(self):
    print('Logged in as %s' % self.user.name)
    print(self.user.id)
    print('------')
    
    ### SERVER/CHANNEL SELECTION
    self.scrape_guild, self.scrape_channel, self.scrape_limit = self._selection_interface()
    
    ### END FUNCITON IF NO SCRAPING
    if self.scrape_limit == 0:
      print('No messages scraped')
      return
    
    ### INITIALIZE CHANNELSTATISTICS OBJECT. VERY IMPORTANT!!! (ALSO lastmsgid and scrape_count WHICH ARE LESS IMPORTANT)
    self.scrape_count = 0
    self.channelstats, lastmsgid = self._fileinit()
    if not self.channelstats:
      self.channelstats = ChannelStatistics(self.scrape_channel)
      
    # Check if ChannelStatistics object is assigned to the correct channel
    if not self.channelstats.id == self.scrape_channel.id:
      raise ValueError("ChannelStatistics object assigned to incorrect channel (this shouldn't happen)") # NOTE: Change ValueError to a more accurate exception object
    
    ### SCRAPE ALL THE MESSAGES
    aftermsg = await self.scrape_channel.fetch_message(lastmsgid) if lastmsgid else None
    async for message in self.scrape_channel.history(limit=self.scrape_limit, after=aftermsg, oldest_first=True).filter(lambda msg: not msg.author.bot):
      if self.scrape_count == 0: self.firstmsg = message
      self.channelstats.feed(message)
      self.scrape_count += 1
      if self.scrape_count % 200 == 0: # Give updates on how many messages have been scraped every 200 messages
        print('%s messages scraped' % self.scrape_count)
    print('Scraping completed')
    self.lastmsg = message

  async def on_disconnect(self):
    print('Goodbye!')
    if self.scrape_limit == 0:
      return
    ### UPLOAD CHANNELSTATISTICS OBJECT AND LAST LOGGED MESSAGE ID TO PICKLE FILE, LOG INFO ON SCRAPED MESSAGES
    with open(f'{self.scrape_path}/userstats.pkl' , 'wb') as f:
      dill.dump((self.channelstats, self.lastmsg.id), f, dill.HIGHEST_PROTOCOL)
    self.logger.info(f''' READ {self.scrape_count} MESSAGES
First: ID: {self.firstmsg.id} / DAETIME: {self.firstmsg.created_at}
Last: ID: {self.lastmsg.id} / DATETIME: {self.lastmsg.created_at}''')
    logging.shutdown()
