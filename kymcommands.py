from urllib.request import urlopen, HTTPError
import time
import random
import re

RE_IMAGE_PAGE = r'\/photos\/\d{1,8}'
RE_IMAGE_URL = r'https?:\/\/i\.kym\-cdn\.com\/photos\/images\/original\/\d{3}\/\d{3}\/\d{3}\/[^\s"\']+\.(?:jpg|gif|png)'

MAX_IMAGE = 1509222

def get_image_url(page):
  with urlopen(page) as info:
    html = info.read().decode('utf-8')
  return re.search(RE_IMAGE_URL, html).group(0)

def get_random_image():
  while 1:
    time.sleep(3) # wait between requests to avoid IP ban
    randompage = "https://knowyourmeme.com/photos/%s" % random.randint(4, MAX_IMAGE)
    print(randompage)
    try:
      url = get_image_url(randompage)
    except HTTPError as errmsg:
      if str(errmsg) == 'HTTP Error 404: Not Found':
        print("404 " + url)
        continue
      else:
        raise HTTPError(errmsg) # Give traceback in the case of non-404 exception
    else:
      return url
