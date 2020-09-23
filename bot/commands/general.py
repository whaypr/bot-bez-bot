from bot import client

import math as m
import re
from random import randrange
import requests
from bs4 import BeautifulSoup

from discord.utils import get

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

    if res == 69:
        res = str(res) + ' 😂👌'
    elif res == 1337:
        res = str(res) + ', haxxorrrrrz!'

    await ctx.send(res)


@client.command(aliases=['c'])
async def clear(ctx):
    '''Clears all messages in channel'''

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

    image_number = randrange(9999)

    page = requests.get(f'http://attackofthecute.com/on/?i={image_number}')
    soup = BeautifulSoup(page.content, 'html.parser')
    image_link = soup.find('div', class_='image').find('img')['src']

    await ctx.send(image_link)


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
    1 - ArchiCafé
    2 - Masarykova kolej
    3 - MEGA BUF FAT
    4 - Kladno
    5 - Podolí
    6 - Strahov
    7 - Studentský dům
    8 - Technická
    9 - Horská
    10 - Karlovo náměstí 
    '''

    if not len(args):
        await ctx.send(menza_choices)        
        return

    if args[0] in ('1', 'archicafé', 'archicafe', 'archicaf', 'archi', 'arch', 'a'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=15')
    elif args[0] in ('2', 'masarykova', 'masaryk', 'mas', 'm'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=5')
    elif args[0] in ('3', 'megabuffat', 'megabufat', 'megabufet', 'megabuf', 'mega', 'bufet', 'but', 'mb'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=12')
    elif args[0] in ('4', 'kladno', 'kladn', 'kl'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=9')
    elif args[0] in ('5', 'podolí', 'podoli', 'podol', 'pod', 'p'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=4')
    elif args[0] in ('6', 'strahov', 'stra', 'str', 'st'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=1')
    elif args[0] in ('7', 'studentský', 'studentsky', 'student', 'stude', 'stud', 's'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=2')
    elif args[0] in ('8', 'technická', 'technicka', 'techni', 'tech', 't'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=3')
    elif args[0] in ('9', 'horská', 'horska', 'horsk', 'hor', 'h'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=6')
    elif args[0] in ('10', 'karlák', 'karlak', 'karl', 'karlovo', 'karlov', 'k'):
        page = requests.get('https://agata.suz.cvut.cz/jidelnicky/index.php?clPodsystem=8')
    else:
        await ctx.send(menza_choices) 
        return

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


@client.command(aliases=['e'], hidden=True)
async def echo(ctx, *args):
    '''Sends message as bot'''

    await ctx.channel.purge(limit=1)
    res = ' '.join(args)
    await ctx.send(res)
