import discord
import asyncio
import typing
from discord.ext import commands
from statsbot import StatsBot
import kymcommands as kym


bot = StatsBot(command_prefix='!')

def is_statschannel(): # Ensures that stastistics commands can only be invoked in the channel in which the statistics were collected
    async def predicate(ctx):
        if ctx.channel.id == bot.channelstats.id:
          return True
        else:
          return False
    return commands.check(predicate)
  
@bot.command()
@is_statschannel()
async def stats(ctx, mention: typing.Optional[discord.Member], arg: str = None):
  if arg:
    if arg == 'me':
      await ctx.send(bot.channelstats.get_user_by_id(ctx.author.id).display_info())
    elif arg == 'channel':
      await ctx.send(bot.channelstats.display_info())
    else:
      await ctx.send('Invalid argument')
  elif mention:
    await ctx.send(bot.channelstats.get_user_by_id(mention.id).display_info())
    
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

if __name__ == '__main__':
  bot.run('token')
