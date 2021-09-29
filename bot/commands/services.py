from bot import client
from aws import aws_s3, s3_sync, simpnotes

import math as m
import re

import requests
from bs4 import BeautifulSoup

from tabulate import tabulate


## MATH ##
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


## MENZA ##
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


## kino ##
@client.command(aliases=['ki', 'kin'])
async def kino(ctx, *args):
    '''Program sušického kina'''
    link = 'https://www.kinosusice.cz/klient-2366/kino-382/stranka-13561'

    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    program = soup.find_all('div', class_='program')

    res = ''
    for i, movie in enumerate(program):
        name = movie.find('h3').text

        s_time = movie.find('div', class_='time')
        day = s_time.find(class_='day').text.strip()
        hour = s_time.find(class_='time').text.strip()

        price = movie.find(class_=re.compile('price')).text

        res += f'📅 {day} 🕒 {hour} 🎞 {name} 💵 {price}\n'

        if i == 15: # message is too long, must be sent partially
            await ctx.send(res)
            res = ''
    
    await ctx.send(res)


## SIMP ##
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
            await ctx.send('Špatný formát')    
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
