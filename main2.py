import discord
import asyncio
from discord.ext import commands
import kymcommands as kym


bot = commands.Bot(command_prefix='!')
bot.userstats = list()

def _selection_interface():
  '''
SERVER/CHANNEL SELECTION:
Lets the user choose guild, channel, and a message scraping limit; returns a tuple with all three values
  '''
  for n in range(len(bot.guilds)):
    print(f'[{n}] {bot.guilds[n]}')
  selection = int(input('Select a server:'))
  guild = bot.guilds[selection]
  for n in range(len(guild.text_channels)):
    print(f'[{n}] {guild.text_channels[n]}')
  selection = int(input('Select a channel:'))
  channel = guild.text_channels[selection]
  limit = int(input('Message limit?'))
  return (guild, channel, limit)

@bot.event
async def on_ready():
  print('Logged in as %s' % bot.user.name)
  print(bot.user.id)
  print('------')

  ### SERVER/CHANNEL SELECTION
  server, channel, limit = _selection_interface()
  

@bot.command()
async def ayy(ctx):
  await ctx.send('lmao')

@bot.command()
async def kymrandom(ctx):
  await ctx.trigger_typing()
  img = kym.get_random_image()
  await ctx.send('Image OP: **%s**\n%s' % (img['OP'], img['url']))

@bot.command()
async def kymbooru(ctx, *tags):
  await ctx.trigger_typing()
  img = kym.get_image_from_tags(tags)
  if not img:
    await ctx.send('No results for "%s"' % ' '.join(tags))
  else:
    await ctx.send('Image OP: **%s**\n%s' % (img['OP'], img['url']))

@bot.command()
@commands.is_owner()
async def quit(ctx):
  await bot.logout()
