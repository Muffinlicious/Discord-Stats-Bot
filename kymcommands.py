from urllib.request import urlopen, HTTPError
import time
import random
import re

### LOOK INTO USING AIOHTTP
RE_IMAGE_PAGE = r'\/photos\/\d{1,8}'
RE_IMAGE_URL = r'https?:\/\/i\.kym\-cdn\.com\/photos\/images\/original\/\d{3}\/\d{3}\/\d{3}\/[^\s"\']+\.(?:jpg|gif|png|jpeg)'
RE_OP_PROFILE = r'<a href=[\"\']\/users\/.+?[\"\']>(.+?)<\/a>' # username in first capture group

MAX_IMAGE = 1509400

def get_image(page): #NOTE: Fix issue with banned authors
  print(page)
  time.sleep(3) # wait between requests to avoid IP ban
  with urlopen(page) as info:
    html = info.read().decode('utf-8')
  if not re.search(RE_OP_PROFILE, html):
    img = {'url': re.search(RE_IMAGE_URL, html).group(), 'OP': '[deactivated user]'}
  else:
    img = {'url': re.search(RE_IMAGE_URL, html).group(), 'OP': re.search(RE_OP_PROFILE, html).group(1)}
  return img

def get_random_image():
  while 1:
    randompage = "https://knowyourmeme.com/photos/%s" % random.randint(4, MAX_IMAGE)
    try:
      img = get_image(randompage)
    except HTTPError as errmsg:
      if str(errmsg) == 'HTTP Error 404: Not Found':
        print("404 " + randompage)
        continue
      else:
        raise HTTPError(errmsg) # Give traceback in the case of non-404 exception
    else:
      return img

#https://knowyourmeme.com/search?context=images&q=test+search

def get_image_from_tags(tags):
  query = 'https://knowyourmeme.com/search?context=images&q=%s' % '+'.join(tags)
  time.sleep(3)
  with urlopen(query) as info:
    html = info.read().decode('utf-8')
  photos = re.findall(RE_IMAGE_PAGE, html)
  if not photos: #Return blank dictionary if there are no results
    return {}
  return get_image('https://knowyourmeme.com%s' % random.choice(photos))
  
