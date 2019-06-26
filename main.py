#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
import discord
import asyncio
import dill
from statstuff import *

client = discord.Client()
userlist = list()
channel = ''
@client.event
async def on_ready():
  global userlist, channel, guild
  # Connection Initialization
  await client.wait_until_ready()
  print('Logged in as %s' % client.user.name)
  print(client.user.id)
  print('------')
  
  # Server/Channel Selection Interface
  for n in range(len(client.guilds)):
    print(f'[{n}] {client.guilds[n]}')
  selection = int(input('Select a server:'))
  guild = client.guilds[selection]
  for n in range(len(guild.text_channels)):
    print(f'[{n}] {guild.text_channels[n]}')
  selection = int(input('Select a channel:'))
  channel = guild.text_channels[selection]
  limit = int(input('Message limit?'))
  
  # Message Collection (ignores bot messages)
  n = 0
  async for message in channel.history(limit=limit).filter(lambda msg: not msg.author.bot):
    #REMINDER: Discriminators are strings, no hashtag
    for user in userlist:
      if user.id == message.author.id:
        user.feed(message)
        break
    else: #for-else construct is intentional
      user = UserStatistics(message.author)
      user.feed(message)
      userlist.append(user)
    #Keep track of how many messages have been scraped 
    if (n % 100 == 0):
      print(n)
    n += 1
    # Store UserStatistics object list in pickle file
    with open(f'{guild}:{channel}:userstats.pkl', 'wb') as f:
      dill.dump(userlist, f, dill.HIGHEST_PROTOCOL)
@client.event
async def on_message(message):
  if message.content.startswith('!hug'):
    if message.mentions:
      await message.channel.send(message.mentions[0].mention + '<:cathug:443111261899718658>')
    else:
      await message.channel.send(message.author.mention + '<:cathug:443111261899718658>')
  if message.content.startswith('!quit'):
    await client.close()
  if message.content.startswith('!ayy'):
    await message.channel.send('lmao')
client.run('token')
