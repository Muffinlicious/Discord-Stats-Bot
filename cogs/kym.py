from discord.ext import commands
import kymcommands as kym

class KYMCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.command()
  async def kymrandom(self, ctx):
    '''gets a random image from know your meme dot com'''
    await ctx.trigger_typing()
    img = kym.get_random_image()
    await ctx.send('Image OP: **%s**\n%s' % (img['OP'], img['url']))
    
  @commands.command()
  async def kymbooru(self, ctx, *tags):
    '''Searches for KYM images with the given tags, and randomly returns one of the results'''
    await ctx.trigger_typing()
    img = kym.get_image_from_tags(tags)
    if not img:
      await ctx.send('No results for "%s"' % ' '.join(tags))
    else:
      await ctx.send('Image OP: **%s**\n%s' % (img['OP'], img['url']))

def setup(bot):
  bot.add_cog(KYMCog(bot))
