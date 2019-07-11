#!/Library/Frameworks/Python.framework/Versions/3.7/bin/python3.7
import discord
import asyncio
from discord.ext import commands
from statsbot import StatsBot
import kymcommands as kym


bot = StatsBot(command_prefix='!')

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
client.run('token')
