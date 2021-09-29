from bot import client

from discord import Embed

import requests
from bs4 import BeautifulSoup
import feedparser

from random import choice
import re


## KEK ##
@client.command(aliases=['k'])
async def kek(ctx, *args):
    '''Random kek from lamer.cz'''
    page = requests.get('http://www.lamer.cz/quote/random')
    soup = BeautifulSoup(page.content, 'html.parser')

    res = ''

    kek = soup.find('div', class_='first').find('p', class_='text')
    for line in str(kek).split('\n'):
        name = re.sub('^.*<span[^>]*>', '', line)
        name = re.sub('</span>.*', '', name)

        text = re.sub('.*</span>&gt; ', '', line)
        text = re.sub('(<br/>)|(</p>)', '', text)

        res += f'*{name}:*\n{text}\n\n'

    try:
        comment = soup.find('div', class_='first').find('p', class_='comment').text
        comment = re.sub('Komentář: ', '', comment)
        res += f'*--- komentář ---*\n{comment}'
    except:
        pass

    await ctx.send(res)


## CUTE ##
@client.command(aliases=['cut'])
async def cute(ctx, *args):
    '''Random cute animal'''

    subreddits = ['aww', 'Awww', 'cute_animals', 'babyanimals']
    limit = 1
    timeframe = 'all' #hour, day, week, month, year, all
    listing = 'random' # controversial, best, hot, new, random, rising, top
    base_url = f'https://www.reddit.com/r/{choice(subreddits)}/{listing}.json?limit={limit}&t={timeframe}'

    res = ""
    while not res.lower().endswith(('.jpg', '.png', '.gif', '.jpeg')):
        response = requests.get(base_url, headers = {'User-agent': 'Pure cuteness dealer'}).json()
        res = response[0]["data"]["children"][0]["data"]["url"]

    await ctx.send(res)


## RAJCE ##
@client.command(aliases=['rajc', 'rce'])
async def rajce(ctx, *args):
    '''Random fotka z brontíckého Rajčete'''

    account = feedparser.parse("https://brontici-rokycany.rajce.idnes.cz/?rss=news")
    album_link = choice(account.entries).link

    album = feedparser.parse(f"{album_link}/?rss=media")
    image_link = choice(album.entries).media_thumbnail[0]['url']

    title = album_link.replace('https://brontici-rokycany.rajce.idnes.cz/', '')
    title = ''.join([
        x.replace('_', ' ')
        for x in title
        if not x.isdigit() and x not in ('.', ',', '-', '/')
    ]).strip()

    embed = Embed(title=f'📷  {title}  📷', description=f'🔗 [odkaz na album]({album_link})', color=0xf82222)
    embed.set_image(url=image_link)

    await ctx.send(embed=embed)
