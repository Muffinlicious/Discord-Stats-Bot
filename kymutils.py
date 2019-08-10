from bs4 import BeautifulSoup

from datetime import datetime
import pytz

def _g(url):
  from urllib.request import urlopen
  with urlopen(url) as url:
    return url.read().decode('utf-8')
  
def PST_to_UTC(dt):
  tz = pytz.timezone('US/Pacific')
  utcdate = tz.normalize(tz.localize(dt).astimezone(pytz.utc))
  return utcdate

def get_comment(html):
  soup = BeautifulSoup(html, 'html.parser')
  article = soup.find('article', {'class':'comment rel thumbable'})
  
  content = article.find('div', {'class':'message'})
  for imgtag in content.find_all('img'): # replaces image tags with links to image
    link = imgtag['data-src']
    content.img.replace_with(link)
    
  message_dict = {'contents': content.text}

  message_dict['score'] = article.find('div', {'class':'thumb_mini_container'}).text
  message_dict['date'] = PST_to_UTC(datetime.fromtimestamp(int(article['data-timestamp'])))
  
  authorlink = article.find('a', {'class':'photo abs'})
  
  if authorlink: # in case the account is 404'd
    message_dict['account'] = 'http://knowyourmeme.com' + authorlink['href']
  else:
    authorlink = article.find('span', {'class':'photo abs'})
    message_dict['account'] = None
  authorinfo = authorlink.find('img')

  message_dict['author'] = authorinfo['title']
  message_dict['avatar'] = authorinfo['data-src']

  message_dict['url'] = 'http://knowyourmeme.com' + article.find('a', {'class':'permalink'})['href']
  return message_dict

def get_image(html):
  soup = BeautifulSoup(html, 'html.parser')
  info = soup.find('div', {'class':'x_brb6 c'})
  

