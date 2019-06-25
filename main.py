#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
import discord
import asyncio
from dcstats import *

client = discord.Client()
users = dict()
@client.event
async def on_ready():
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
  async for message in channel.history(limit=limit).filter(lambda msg: not msg.author.bot):
    if message.author:
      pass
  
    
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
