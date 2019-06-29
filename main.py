#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
import discord
import asyncio
import dill
import logging
import os
from datetime import timedelta
from statstuff import *

client = discord.Client()

MUFFIN_ID = 173610171883454464


data = ''
@client.event
async def on_ready():
  global userlist, data # get rid of this
  ### CONNECTION INITIALIZATION
  await client.wait_until_ready()
  print('Logged in as %s' % client.user.name)
  print(client.user.id)
  print('------')

  ### VARIABLE INITIALIZATION
  batchinfo = dict()

  
  ### SERVER/CHANNEL SELECTION INTERFACE
  for n in range(len(client.guilds)):
    print(f'[{n}] {client.guilds[n]}')
  selection = int(input('Select a server:'))
  guild = client.guilds[selection]
  for n in range(len(guild.text_channels)):
    print(f'[{n}] {guild.text_channels[n]}')
  selection = int(input('Select a channel:'))
  channel = guild.text_channels[selection]
  limit = int(input('Message limit?'))
  ### FILE PREPERATION
  # Setting up directories for logging/saving
  if not os.path.exists(f'DCSTATS/{guild}/{channel}'):
    os.makedirs(f'DCSTATS/{guild}/{channel}')
  if os.path.exists(f'DCSTATS/{guild}/{channel}/userstats.pkl'):
    with open(f'DCSTATS/{guild}/{channel}/userstats.pkl', 'rb') as f:
      data = dill.load(f)
      userlist = data['stats']
      lastloggedmessageid = data['last']['id']
  else:
    userlist = list()
    lastloggedmessageid = 0
    
  logging.basicConfig(filename=f'DCSTATS/{guild}/{channel}/statslog.log',\
                      format='At %(asctime)s - %(message)s\n', level=logging.INFO)
  # Getting info from current directories 
  
  ### MESSAGE SCRAPING (ignores bot messages)
  n = 0
  if limit != 0:
    aftermsg = await channel.fetch_message(lastloggedmessageid) if lastloggedmessageid else None
    async for message in channel.history(limit=limit, after=aftermsg,\
                                          oldest_first=True).filter(lambda msg: not msg.author.bot):
      if n == 0:
        batchinfo['first'] = {'id':message.id, 'dt':message.created_at - timedelta(hours=7)} 
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
        print(f'{n} Messages scraped')
      n += 1
    print(f'Message scraping completed ({n} messages)')

    
    # Store UserStatistics object list in pickle file, update scrape log
    batchinfo['last'] = {'id':message.id, 'dt':message.created_at - timedelta(hours=7)}
    batchinfo['stats'] = userlist
    with open(f'DCSTATS/{guild}/{channel}/userstats.pkl', 'wb') as f:
      dill.dump(batchinfo, f, dill.HIGHEST_PROTOCOL)


    # LOG MESSAGE RANGE
    logging.info(f''' READ {n} MESSAGES
First: ID: {batchinfo['first']['id']} / DAETIME: {batchinfo['first']['dt']}
Last: ID: {batchinfo['last']['id']} / DATETIME: {batchinfo['last']['dt']}''')
    logging.shutdown()
    
  else:
    print('No Messages Scraped')


@client.event
async def on_message(message):
  if message.content.startswith('!hug'):
    if message.mentions:
      await message.channel.send(message.mentions[0].mention + '<:cathug:443111261899718658>')
    else:
      await message.channel.send('<:cathug:443111261899718658>')
  if message.content.startswith('!quit'):
    if message.author.id == MUFFIN_ID:
      await client.close()
  if message.content.startswith('!ayy'):
    await message.channel.send('lmao')
client.run('token')
