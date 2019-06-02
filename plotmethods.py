from datetime import datetime, timedelta
import numpy
import matplotlib.pyplot as plt

def timebar(dtlist):
  bardata = {t:0 for t in range(24)}
  for dt in dtlist:
    dt = dt - timedelta(hours=7)
    bardata[dt.hour] += 1
  y_pos = numpy.arange(len(bardata))
  plt.bar(y_pos, list(bardata.values()), align='center', alpha=0.5)
  plt.xticks(y_pos, list(bardata))
  plt.ylabel('Messages')
  plt.title('Messages per Daytime Hour (PST)')
  plt.savefig('bar.png')
  
def userpie(userdict):
  other = 0
  truncdict = dict()
  for user in userdict:
    if userdict[user] / sum(userdict.values()) > 0.01:
      truncdict[user] = userdict[user]
    else:
      other += userdict[user]
  userdict = truncdict
  fig1, ax1 = plt.subplots()
  names = [f'Other\n{other}'] + [f'{user.name}\n{userdict[user]}' for user in \
                                 sorted(userdict.keys(), key=lambda i: userdict[i])]
  ax1.pie([other] + sorted(userdict.values()), labels=names, autopct='%1.1f%%', startangle=90,\
          textprops={'fontsize':'x-small'})
  ax1.axis('equal')
  plt.savefig('pie.png')
