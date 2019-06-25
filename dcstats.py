from datetime import timedelta
from emoji import emoji_lis, demojize
from re import findall
import matplotlib.pyplot as plt
import numpy

RE_CUSTOM_EMOJI = r'<a?(:[^\s:]+:)\d{1,20}>'

with open('swears.txt') as f:
  SWEARS = f.read().lower().split('\n')

def _autotallydict(dictionary, key): 
  if key in dictionary:
    dictionary[key] += 1
  else:
    dictionary[key] = 1
  return dictionary

def hascurse(string):
  for curse in SWEARS:
    if curse in string:
      return True
  return False

def getemojis(string):
  emojis = list()
  for d in emoji_lis(string):
    emojis.append(d['emoji'])
  for e in findall(RE_CUSTOM_EMOJI, string):
    emojis.append(e)

class _MsgStatistics:
  def __init__(self):
    self.curses = 0
    self.chars = 0
    self.words = 0
    self.files = 0

    self.idlist = list()
    self.emojis = dict()
    self.links = dict()
    self.pings = dict()
    
    self.hourslots = {h:0 for h in range(24)}
    self.monthslots = dict()
  def curseratio(self):
    return self.curses / self.msgs
  
  def charratio(self):
    return self.chars / self.msgs

  def wordratio(self):
    return self.words / self.msgs
  
  def feed(self, message):
    self.idlist.append(message.id)
    # Cursing
    if hascurse(message.content):
      self.curses += 1
    # Mentions (Pings)
    for user in message.mentions:
      self.pings = _autotallydict(self.pings, user)
    # Character and Word count
    self.chars += len(message.content) # NOTE: CUSTOM EMOJIS AFFECT CHAR COUNT?
    self.words += len(message.content.split())
    # Emojis
    for e in getemojis(message.content):
      self.emojis = _autotallydict(self.emojis, e)
    # Times
    self.hourslots[(message.created_at - timedelta(hours=7)).hour] += 1
  
  def hourgraph(self, fname='bar.png', show=0):
    y_pos = numpy.arange(len(self.hourslots))
    plt.bar(y_pos, list(self.hourslots.values()), align='center', alpha=0.5)
    plt.xticks(y_pos, list(self.hourslots))
    plt.ylabel('Messages')
    plt.title('Messages per Daytime Hour (PST)')
    if show:
      plt.show()
    else:
      plt.savefig(fname)
  
class UserStatistics(_MsgStatistics):
  def __init__(self, user):
    self.user = user
    _MsgStatistics.__init__(self)
    
