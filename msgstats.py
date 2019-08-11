import discord
import os
import json
import re
import emoji

from collections import Counter
from functools import reduce
from urlmarker import URL_REGEX
from urllib.parse import urlparse

JSON_FOLDER = 'DiscordStatistics'

with open('swears.txt') as f:
  SWEARS = set(curse.lower().strip() for curse in f)

with open('words.txt') as f:
  WORDS = set(word.lower().strip() for word in f)

def get_emojis(string):
  RE_CUSTOM_EMOJI = r'<(a?)(:[A-Za-z0-9_]+:)([0-9]+)>'
  emojis = list()
  for e in emoji.emoji_lis(string):
    emojis.append(e['emoji'])
  for e in re.findall(RE_CUSTOM_EMOJI, string):
    emojis.append(e[1])
  return emojis

def get_links(string):
  links = list()
  for url in re.findall(URL_REGEX, string):
    parsed = urlparse(url)
    links.append('%s://%s' % (parsed.scheme, parsed.hostname))
  return links

class _MsgStatistics:
  def __init__(self):
    self.msgs = 0
    self.chars = 0
    self.words = 0
    
    self.idlist = list()
    self.curses = Counter()
    self.emojis = Counter()
    self.sites = Counter()
    self.pings = Counter()
    self.uniquewords = Counter()

    self.hourslots = Counter({h:0 for h in range(24)})
    self.monthslots = Counter()

  @property
  def curseratio(self):
    return float('%.3f' % (sum(self.curses.values()) / self.msgs))
  
  @property
  def charratio(self):
    return float('%.2f' % (self.chars / self.msgs))
  
  @property
  def wordratio(self):
    return float('%.2f' % (self.words / self.msgs))
  
  @property
  def earliest_message_id(self):
    return sorted(self.idlist)[0] if self.idlist else 0 # ids get sorted by timestamp 

  @property
  def latest_message_id(self):
    return sorted(self.idlist)[-1] if self.idlist else 0
  
  def feed(self, message: discord.Message):
    assert message.id not in self.idlist, 'Message has already been logged: %s' % message.id

    self.idlist.append(message.id)
    self.msgs += 1

    # Curses and Unique Words
    for word in message.content.lower().split():
      if word.isalnum() and word[0].isalpha():
        if word not in WORDS:
          self.uniquewords[word] += 1
        if word in SWEARS:
          self.curses[word] += 1
  
    # Mentions (Pings)
    for user in message.mentions:
      self.pings[user.name] += 1

    # Character and Word count
    self.chars += len(message.content)
    self.words += len(message.content.split())

    # Emojis 
    for e in get_emojis(message.content):
      self.emojis[e] += 1
    
    # Links
    for url in get_links(message.content):
      self.sites[url] += 1
    
    # Times
    self.hourslots[message.created_at.hour] += 1
    self.monthslots[message.created_at.date().isoformat()] += 1

class UserStatistics(_MsgStatistics):
  def __init__(self, user: discord.User):
    super().__init__()
    self.id = user.id
    self.name = user.name
    self.discrim = user.discriminator
    self.icon = str(user.avatar_url_as(static_format='png'))    
  def __repr__(self):
    return '%s#%s' % (self.name, self.discrim)

class ChannelStatistics(_MsgStatistics):
  def __init__(self, channel: discord.TextChannel):
    self.name = channel.name
    self.id = channel.id
    self.userlist = [UserStatistics(member) for member in channel.members]

  def __repr__(self):
    userstr = self.userlist if len(self.userlist) <= 25 else str(self.userlist[:25]) + '. . . '
    return f'<ChannelStatistics id={self.id}, msgs={self.msgs}, name=\'#{self.name}\', userlist={userstr}>'
  
  def __getattr__(self, attr):
    return sum((getattr(obj, attr) for obj in self.userlist), getattr(_MsgStatistics(), attr))
  
  def get_user_by_id(self, userid) -> UserStatistics:
    for user in self.userlist:
      if user.id == userid:
        return user
    else:
      raise LookupError('Couldn\'t find user')
    
  def feed(self, message: discord.Message):
    self.get_user_by_id(message.author.id).feed(message)
    
class GuildStatistics(_MsgStatistics):
  '''This class creates json files storing info on itself.'''
  def __init__(self, guild: discord.Guild):
    self.name = guild.name
    self.id = guild.id
    self.chanlist = [ChannelStatistics(channel) for channel in guild.text_channels \
                        if channel.permissions_for(guild.me).read_message_history]
  def __repr__(self):
    return f'<GuildStatistics id={self.id}, name=\'#{self.name}\', chanlist={[channel.name for channel in self.chanlist]}>'
  
  def __getattr__(self, attr):
    return sum((getattr(obj, attr) for obj in self.chanlist), getattr(_MsgStatistics(), attr))
  
  def get_channel_by_id(self, channelid) -> ChannelStatistics:
    for channel in self.chanlist:
      if channel.id == channelid:
        return channel
    else:
      raise LookupError('Couldn\'t find channel')
    
  def feed(self, message: discord.Message):
    self.get_channel_by_id(message.channel.id).feed(message)
    
  def json_upload(self, folder=JSON_FOLDER):
    path = f'{folder}/{self.name}/guildstats.json'
    if not os.path.exists(path):
      os.mkdir(f'{folder}/{self.name}')
    
    with open(path, 'w') as file:
      json.dump(self, file, default=lambda obj: {obj.__class__.__name__: obj.__dict__})
