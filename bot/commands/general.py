from bot import client
from aws import aws_s3, s3_sync, simpnotes

from discord.utils import get
from discord import Embed

import math as m
from random import randrange, choice
import re

import requests
from bs4 import BeautifulSoup
import feedparser

from tabulate import tabulate

@client.command(aliases=['m'])
async def math(ctx, *args):
    '''Performs basic math operations'''

    expr = ' '.join(args)

    fuctions = {
        '__builtins__': None,
        'sqrt': m.sqrt, 
        'pow': m.pow
    }

    try:
        res = eval(expr, fuctions, {})
        #res = eval(expr) # for exploits :)
    except Exception as e:
        print(e)
        res = 'Neplatný výraz'

    if res == 42:
        res = 'you know what\'s the answer'
    elif res == 69:
        res = str(res) + ' 😂👌'
    elif res == 1337:
        res = str(res) + ', haxx0rrrrrz!'

    await ctx.send(res)


@client.command(aliases=['c'])
async def clear(ctx):
    '''Clears messages in channel'''

    await ctx.channel.purge()
    await ctx.send('Uklizeno ✅')


@client.command(aliases=['h'])
async def hello(ctx, *args):
    '''Says hello to whatever you specify'''

    await ctx.channel.purge(limit=1)
    for arg in args:
        await ctx.send(f'Hello, {arg}! 👋')


@client.command(aliases=['cut'])
async def cute(ctx, *args):
    '''Random cute animal'''

    subreddits = ['aww', 'Awww', 'cute_animals', 'babyanimals']
    limit = 1
    timeframe = 'all' #hour, day, week, month, year, all
    listing = 'random' # controversial, best, hot, new, random, rising, top
    base_url = f'https://www.reddit.com/r/{random.choice(subreddits)}/{listing}.json?limit={limit}&t={timeframe}'

    res = ""
    while not res.lower().endswith(('.jpg', '.png', '.gif', '.jpeg')):
        response = requests.get(base_url, headers = {'User-agent': 'Pure cuteness dealer'}).json()
        res = response[0]["data"]["children"][0]["data"]["url"]

    await ctx.send(res)


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


@client.command(aliases=['menz'])
async def menza(ctx, *args):
    '''Menzas CTU'''

    menza_choices = '''
    Možnosti:
    0 - ArchiCafé
    1 - Masarykova kolej
    2 - MEGA BUF FAT
    3 - Kladno
    4 - Podolí
    5 - Strahov
    6 - Studentský dům
    7 - Technická
    8 - Horská
    9 - Karlovo náměstí 
    '''

    if len(args) == 0:
        msg = await ctx.send(menza_choices)        
        return

    link = 'https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem='

    if   args[0] in ('0', 'archicafé', 'archicafe', 'archicaf', 'archi', 'arch', 'a'):
        link += '15'
    elif args[0] in ('1', 'masarykova', 'masaryk', 'mas', 'm'):
        link += '5'
    elif args[0] in ('2', 'megabuffat', 'megabufat', 'megabufet', 'megabuf', 'mega', 'bufet', 'but', 'mb'):
        link += '12'
    elif args[0] in ('3', 'kladno', 'kladn', 'kl'):
        link += '9'
    elif args[0] in ('4', 'podolí', 'podoli', 'podol', 'pod', 'p'):
        link += '4'
    elif args[0] in ('5', 'strahov', 'stra', 'str', 'st'):
        link += '4'
    elif args[0] in ('6', 'studentský', 'studentsky', 'student', 'stude', 'stud', 's'):
        link += '2'
    elif args[0] in ('7', 'technická', 'technicka', 'techni', 'tech', 't'):
        link += '3'
    elif args[0] in ('8', 'horská', 'horska', 'horsk', 'hor', 'h'):
        link += '6'
    elif args[0] in ('9', 'karlák', 'karlak', 'karl', 'karlovo', 'karlov', 'k'):
        link += '8'
    else:
        await ctx.send(menza_choices) 
        return

    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    res = ''

    rows = soup.find('table').find('tbody').findAll('tr')
    if not rows:
        await ctx.send('Dneska nevaříme bráško :)') 
        return

    for row in rows:
        category = row.find('th')

        if category:
            res += f'\n\n*{category.text}*\n'
        else:
            data = row.findAll('td')

            weight = data[1].text.strip()
            name = data[2].text
            price = data[5].text.strip()

            res += f'⚖️ {weight} 🍔 {name} 💵 {price}\n'

    await ctx.send(res)


@client.command(aliases=['s'], hidden=True)
async def simp(ctx, *args):
    if str(ctx.channel.id) != '757945999246229564':
        return

    async def show_simpnotes():
        if simpnotes == {}:
            await ctx.send('Simptýsek je prázdný')    
        else:
            res = tabulate(simpnotes, simpnotes.keys(), tablefmt="grid")
            await ctx.send(f'```\n{res}```\n')

    if len(args) == 0:
        await show_simpnotes()
        return

    if args[0].lower() == 'c':
        try:
            tmp = re.split( r'[c] ', ' '.join(args) )
            
            simp = tmp[1].upper()
            simpnotes.pop(simp)
        except:
            await ctx.send('Nelze odebrat')
            return

        await ctx.send(f'{simp} už nikoho nesimpuje 😦')
    else:
        await ctx.channel.purge(limit=1)
        
        try:
            tmp = re.split( r' ([+-]) ', ' '.join(args) )

            simp = tmp[0].upper()
            operation = tmp[1]
            simped = tmp[2][0].upper() + tmp[2][1:].lower()
        except:
            await ctx.send('Šptaný formát')    
            return

        if operation == '+':
            try:
                simpnotes[simp].append(simped)
            except:
                simpnotes[simp] = [simped]

            await ctx.send(f'{simp} simpuje {simped.upper()} 🥰') 
        elif operation == '-':
            try:
                simpnotes[simp].remove(simped)
            except:
                await ctx.send('Nelze odebrat')
                return

            if simpnotes[simp] == []:
                del simpnotes[simp]
            
            await ctx.send(f'{simp} už nesimpuje {simped.upper()} 💔') 
        else:
            await ctx.send('Neplatná operace')    
            return

    s3_sync(simpnotes)
    await show_simpnotes()


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


@client.command(aliases=['e'], hidden=True)
async def echo(ctx, *args):
    '''Sends message as bot'''

    await ctx.channel.purge(limit=1)
    res = ' '.join(args)
    await ctx.send(res)
