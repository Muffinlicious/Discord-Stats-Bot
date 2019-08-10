import asyncio
import discord
import random
import re
import aiohttp
from aiohttp.web import HTTPNotFound

from discord.ext import commands
from bs4 import BeautifulSoup

import kymutils 
import config

MAX_IMAGE = 1515562
MAX_COMMENT = 5155387

KYM_COLOR_INT = 1184575 # (18, 19, 63) / #12133F
KYM_LOGO = 'https://i.kym-cdn.com/photos/images/original/001/170/526/3db.png'

def comment_as_embed(html):
  comment = kymutils.get_comment(html)
    
  embed = discord.Embed(title='KYM Comment', color=KYM_COLOR_INT)
  embed.description = comment['contents']
  embed.url = comment['url']
  embed.timestamp = comment['date']
    
  authorkwargs = {'name':comment['author'], 'icon_url':comment['avatar']}
  if comment['account']:
    authorkwargs['url'] = comment['account'] # for if the account is 404'd
      
  embed.set_author(**authorkwargs)
  embed.set_footer(icon_url=KYM_LOGO, text='Score: %s' % comment['score'])
  return embed

class KYMCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  def cog_check(self, ctx): # This just disables it on homiecraft. probs remove later
    return ctx.guild.id != 433103377015242752
      
  async def fetch(self, url):
    await asyncio.sleep(3)
    async with aiohttp.ClientSession(loop=self.bot.loop) as session:
      async with session.get(url) as resp:
        if resp.status == 404:
          raise HTTPNotFound
        assert resp.status == 200
        return await resp.text()
      
  @commands.Cog.listener()
  async def on_message(self, message):
    commenturl = re.search(r'http?s:\/\/knowyourmeme\.com\/comments\/\d{1,8}', message.content)
    if commenturl:
      await message.channel.trigger_typing()
      html = await self.fetch(commenturl.group())
      await message.channel.send(embed=comment_as_embed(html))
      
  @commands.command()
  async def kymcomment(self, ctx):
    '''Returns a random KYM comment'''
    await ctx.trigger_typing()
    while True: # retry until non-404 page
      url = 'https://knowyourmeme.com/comments/%s' % random.randint(4, MAX_COMMENT)
      try:
        html = await self.fetch(url)
      except HTTPNotFound:
        continue
      else:
        break
    await ctx.send(embed=comment_as_embed(html))
    
  '''
  @commands.command()
  async def kymrandom(self, ctx):
    'gets a random image from know your meme dot com''
    await ctx.trigger_typing()
    img = kym.get_random_image()
    await ctx.send('Image OP: **%s**\n%s' % (img['OP'], img['url']))
    
  @commands.command()
  async def kymbooru(self, ctx, *tags):
    ''Searches for KYM images with the given tags, and randomly returns one of the results''
    await ctx.trigger_typing()
    img = kym.get_image_from_tags(tags)
    if not img:
      await ctx.send('No results for "%s"' % ' '.join(tags))
    else:
      await ctx.send('Image OP: **%s**\n%s' % (img['OP'], img['url']))
  '''
def setup(bot):
  bot.add_cog(KYMCog(bot))
