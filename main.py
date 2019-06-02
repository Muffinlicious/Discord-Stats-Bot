#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
import discord
import asyncio
from plotmethods import *

client = discord.Client()

@client.event
async def on_ready():
    mtimes = list()
    musers = dict()
    await client.wait_until_ready()
    print('Logged in as %s' % client.user.name)
    print(client.user.id)
    print('------')
    print(client.guilds)
    async for message in client.guilds[0].text_channels[1]\
          .history(limit=100).filter(lambda msg: not msg.author.bot):
        mtimes.append(message.created_at)
        if message.author in musers:
          musers[message.author] += 1
        else:
          musers[message.author] = 1
    timebar(mtimes)
    userpie(musers)
    
@client.event
async def on_message(message):
  global cheat
  print(message.channel.guild.me.guild_permissions.read_message_history)
  if message.content.startswith('!quit'):
    await client.close()
  if message.content.startswith('!ayy'):
    await message.channel.send('lmao')
client.run('token')
