from datetime import timedelta
from emoji import emoji_lis, demojize
from urlmarker import URL_REGEX
from urllib.parse import urlparse
from collections import Counter
import re
import matplotlib.pyplot as plt
import numpy
import functools

RE_CUSTOM_EMOJI = r'<a?(:[^\s:]+:)\d{1,20}>'
# ^ Captures :cathug-3: from the string '<a:cathug-3:443111261899718658>'

with open('swears.txt') as f:
  SWEARS = f.read().lower().split('\n')

with open('words.txt') as f:
  WORDS = f.read().lower().split('\n')


def hascurse(string):
  for curse in SWEARS:
    if curse in string.lower():
      return True
  return False

def getemojis(string):
  emojis = list()
  for d in emoji_lis(string):
    emojis.append(demojize(d['emoji']))
  for e in re.findall(RE_CUSTOM_EMOJI, string):
    emojis.append(e)
  return emojis

class _MsgStatistics:
  def __init__(self):
    self.msgs = 0
    self.curses = 0
    self.chars = 0
    self.words = 0
    self.files = 0

    self.idlist = list()
    self.emojis = Counter()
    self.sites = Counter()
    self.pings = Counter()
    self.uniquewords = Counter()
    
    self.hourslots = {h:0 for h in range(24)}
    self.monthslots = dict()
    
  @property
  def curseratio(self):
    return float('%.3f' % (self.curses / self.msgs))
  @property
  def charratio(self):
    return float('%.2f' % (self.chars / self.msgs))
  @property
  def wordratio(self):
    return float('%.2f' % (self.words / self.msgs))
  
  def feed(self, message):
    # Check if message is a duplicate
    if message.id in self.idlist:
      raise ValueError("Message has already been logged")
    self.msgs += 1
    self.idlist.append(message.id)
    
    # Unique Words
    for word in message.content.lower().split():
      if not word in WORDS and word.isalnum() and word[0].isalpha():
        self.uniquewords[word] += 1

    # Cursing
    if hascurse(message.content):
      self.curses += 1
      
    # Mentions (Pings)
    for user in message.mentions:
      self.pings[user.name] += 1
      
    # Character and Word count
    self.chars += len(message.content) # NOTE: CUSTOM EMOJIS AFFECT CHAR COUNT?
    self.words += len(message.content.split())
    
    # Emojis
    for e in getemojis(message.content):
      self.emojis[e] += 1
    # Links
    for url in re.findall(URL_REGEX, message.content):
      self.sites[urlparse(url).hostname] += 1
    # Times
    self.hourslots[(message.created_at - timedelta(hours=7)).hour] += 1 # -7 is PST
    
  def hourgraph(self, fname='bar.png', label='Messages', show=0):
    plt.clf()
    y_pos = numpy.arange(len(self.hourslots))
    plt.bar(y_pos, list(self.hourslots.values()), align='center', alpha=0.5)
    plt.xticks(y_pos, list(self.hourslots))
    plt.ylabel(label)
    plt.title('Messages per Daytime Hour (PST)')
    if show:
      plt.show()
    else:
      plt.savefig(fname)
      
  def display_info(self):
    display = f'''{self.msgs} messages
{self.words} words ({self.wordratio} words per message)
{self.chars} characters ({self.charratio} characters per message)
{self.curses} curses ({self.curseratio} curses per message)
Top three emojis: {self.emojis.most_common(3)}
Top three pinged users: {self.pings.most_common(3)}
Top three most linked-to websites: {self.sites.most_common(3)}
Top five unique words: {self.uniquewords.most_common(5)}
'''
    return display
  
class UserStatistics(_MsgStatistics):
  def __init__(self, user):
    super().__init__()
    self.id = user.id
    self.name = user.name
    self.discrim = user.discriminator
    
  def __repr__(self):
    return self.name
  
  def hourgraph(self, show=0):
    super().hourgraph(f'{self.name}bar.png', f'{self.name}\'s Messages', show)
    
  def display_info(self):
    display = 'Statistics for user: %s \n' % self.name
    display += super().display_info()
    return display
    
class ChannelStatistics(_MsgStatistics):
  def __init__(self, channel):
    super().__init__()
    self.name = channel.name
    self.id = channel.id
    self.userlist = list()
    
  def __repr__(self):
    return self.name
  
  def __getattribute__(self, name):
    '''
Whenever the class returns a statistic attribute, it does so by taking every UserStatistics \
object in the class and summing all of their values for that attribute, rather than consistently storing the values.
This is done to reduce memory use.
    '''
    if name in ['msgs', 'curses', 'words', 'chars', 'emojis', 'pings', 'uniquewords', 'sites', 'idlist']:
      return functools.reduce(lambda a, b: a + b, [getattr(obj, name) for obj in self.userlist])
    else:
      return object.__getattribute__(self, name)
    
  def get_user(self, username, discrim=None):
    users = [u for u in self.userlist if u.name == username]
    if discrim:
      return next(u for u in users if u.discrim == discrim)
    return next(iter(users))
  
  def get_user_by_id(self, userid):
    return [u for u in self.userlist if u.id == userid][0] # NOTE: make this not as shitty
  
  def get_users_by_activity(self):
    return sorted(self.userlist, key=lambda u: u.msgs, reverse=True)
  
  def get_users_by_wordratio(self):
    return sorted(self.userlist, key=lambda u: u.wordratio)
  
  def feed(self, message):
    for user in self.userlist:
      if user.id == message.author.id:
        user.feed(message)
        break
    else: #for-else construct is intentional
      user = UserStatistics(message.author)
      user.feed(message)
      self.userlist.append(user)
      
  def display_info(self):
    display = 'Statistics for channel: #%s \n' % self.name
    display += 'Most Active Users: %s (%s in total)\n' % (', '.join([repr(obj) for obj in self.get_users_by_activity()[:25]]) + ('. . .' if len(self.userlist) >= 25 else ''), len(self.userlist))
    display += super().display_info()
    return display
      
