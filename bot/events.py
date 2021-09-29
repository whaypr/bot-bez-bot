from bot import client

from random import randrange, choice
import re

import requests
from bs4 import BeautifulSoup


bot_ids = ['<@!729654314728947782>', '<@729654314728947782>']

haha_msg = [
    'XDD', 'xDDDD', 'xxxDDDD', 'XDDdd', 'xdddd rofl',
    'LMAO', 'LMAOOOo', 'lMaooooOoo',
    'LOl xDDD', 'lolololo', 'LOOOOOl',
    'nice one XD', 'so funny 😆', 'si zabil! 😵',
    '😂 🤣 😂 🤣 😂 🤣', '🤣 👌', '😄 😁 😆 😅 😂 🤣',
]
haha_react = [
    '😄', '😁', '😆', '😅', '😂', '🤣',
    '😝', '😜', '🤪',
    '👌', '❤️' , '🤯', '🙀'
]

unknown_msg = ['?', 'Co pro Vás mohu udělat, pane?', 'co chceš?', 'huh', 'neruš', ':)']

challenged = False


## ON READY ##
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


## ON MESSAGE ##
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith('°'):
        message.content = message.content.lower().strip()
        
    global challenged

    # 'xd'
    if 'xd' in message.content:
        await message.channel.send(choice(reaccs_msg))
        await message.add_reaction(choice(reaccs_emoji))

    # 'jsem dobrej'
    if message.content.startswith( ('jsem dobrej', 'jsem dobrý') ):
        if randrange(100) < 50:
            await message.add_reaction('😍')
            await message.channel.send('jasně, že jo')
        else:
            await message.add_reaction('👎')
            await message.channel.send('haha, ne 🙂')

    
    # AT BOT
    if message.content.startswith( (bot_ids[0], bot_ids[1]) ):
        message.content = message.content.strip(bot_ids[0] + ' ')
        message.content = message.content.strip(bot_ids[1] + ' ')

        # pozdrav
        if message.content.startswith( ('ahoj', 'čus', 'čau', 'zdar', 'nazdar', 'zdraví','hello', 'hi', 'greetings') ):
            await message.add_reaction('👋')
            await message.channel.send(f'<@{message.author.id}> Ahoj!')
        # nálada
        elif message.content.startswith( ('jak je', 'jak se máš', 'jak se daří') ):
            await message.channel.send('Veri gut. Majne taktik skusit šůšn')
        # 'kde máš boty' 
        elif message.content.startswith('kde máš boty'):
            challenged = False
            await message.channel.send('Ve sklepě')
        # 'tě sejmu'
        elif message.content.startswith('tě sejmu'):
            challenged = True
            await message.channel.send(f'<@{message.author.id}> Are you challenging me, human?!')
        # tě sejmu - 'ano'
        elif message.content.startswith( ('jo', 'yes', 'ano', 'y', 'jop', 'jup') ) and challenged:
            challenged = False
            await message.channel.send(f'<@{message.author.id}> I will find you and i will destroy you')
        # tě sejmu - 'ne'
        elif message.content.startswith( ('ne', 'no', 'n', 'nope') ) and challenged:
            challenged = False
            await message.channel.send(f'<@{message.author.id}> Máš stěstí') 
        # other
        else:
            challenged = False
            await message.channel.send(f'<@{message.author.id}> {choice(unknown_msg)}')

    
    await client.process_commands(message)
    