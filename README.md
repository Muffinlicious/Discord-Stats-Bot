# Discord-Stats-Bot
Scrapes messages from discord channels and returns statistics/graphs.

Python 3.7

Required packages: discord, dill, matplotlib, numpy, emoji 

Required files: SWEARS.txt with a list of curse words, WORDS.txt with a list of all words, urlmarker.py with a regex for capturing URLs (provided but not written by me).

Creates a folder called DCSTATS containing folders for guilds and sub-folders for channels. Each channel folder has two files: `statslog.log` for logging message scraping info, and `userstats.pkl` for retaining statistics information between scrape sessions.
