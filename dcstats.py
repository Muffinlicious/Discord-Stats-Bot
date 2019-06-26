from datetime import timedelta
from emoji import emoji_lis, demojize
from re import findall
import matplotlib.pyplot as plt
import numpy

RE_CUSTOM_EMOJI = r'<a?(:[^\s:]+:)\d{1,20}>'
# ^ Captures :cathug-3: from the string '<a:cathug-3:443111261899718658>'

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
    if curse in string.lower():
      return True
  return False

def getemojis(string):
  emojis = list()
  for d in emoji_lis(string):
    emojis.append(demojize(d['emoji']))
  for e in findall(RE_CUSTOM_EMOJI, string):
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
    self.emojis = dict()
    self.links = dict()
    self.pings = dict()
    
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
    # Cursing
    if hascurse(message.content):
      self.curses += 1
    # Mentions (Pings)
    for user in message.mentions:
      self.pings = _autotallydict(self.pings, user.name)
    # Character and Word count
    self.chars += len(message.content) # NOTE: CUSTOM EMOJIS AFFECT CHAR COUNT?
    self.words += len(message.content.split())
    # Emojis
    for e in getemojis(message.content):
      self.emojis = _autotallydict(self.emojis, e)
    # Times
    self.hourslots[(message.created_at - timedelta(hours=7)).hour] += 1 # -7 is PST
  
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
    self.id = user.id
    self.name = user.name
    _MsgStatistics.__init__(self)
  def __repr__(self):
    return self.name
  '''
  ### Benched code for if using the user object is necessary 
  def __getstate__(self): # object isn't pickleable with user object attribute
    state = self.__dict__.copy()
    del state["user"]
    return state
  def __setstate__(self, state):
    self.__dict__.update(state)
    self.user = None
  '''
