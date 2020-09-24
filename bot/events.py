from bot import client

from random import randrange
import re

import requests
from bs4 import BeautifulSoup

bot_ids = ['<@!729654314728947782>', '<@729654314728947782>']
challenged = False

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith('!'):
        message.content = message.content.lower().strip()
        
    global challenged

    # censorship
    is_bad = False
    blacklist = [
        'kurv', 'kurev', 'píč', 'pič', 'prdel', 'debil', 'idiot', 'kokot', 'hajzl', 'čurák', 'curak', 'curac', 'šulin', 'sulin',
        'srač', 'srac', 'sráč', 'imbecil', 'kund', 'hovn', 'hoven', 'kokot', 'kokůt', 'kokut', 'kkt', 'mrd', 'mrda', 'šuk', 'prc', 'vojet',
        'vojed', 'dement', 'buzer',
        'bitch', 'cock', 'ass', 'suck', 'fuck', 'cum', 'nigg', 'dick', 'dong',
        'pexes'
    ]
    replaces = [
        'mňauky', 'haf', 'baf', 'fuj', 'hihi', '...', 'nope' 
    ]

    for bad_word in blacklist:
        if bad_word in str(message.content):
            index = randrange(len(replaces))
            message.content = re.sub(f'[a-zěščřžýáíéůú]*{bad_word}[a-zěščřžýáíéůú]*', f'*{replaces[index]}*', str(message.content))
            is_bad = True
    
    if is_bad:
        await message.channel.purge(limit=1)
        await message.channel.send(f'Nemluv sprostě!')
        await message.channel.send(f'<@{message.author.id}> Se snaží říct:\n {message.content}')

    # 'xd'
    if 'xd' in message.content:
        reaccs_msg = [
            'XDD', 'xDDDD', 'xxxDDDD', 'XDDdd', 'xdddd rofl',
            'LMAO', 'LMAOOOo', 'lMaooooOoo',
            'LOl xDDD', 'lolololo', 'LOOOOOl',
            'nice one XD', 'so funny 😆', 'si zabil! 😵',
            '😂 🤣 😂 🤣 😂 🤣', '🤣 👌', '😄 😁 😆 😅 😂 🤣',
        ]
        reaccs_emoji = [
            '😄', '😁', '😆', '😅', '😂', '🤣',
            '😝', '😜', '🤪',
            '👌', '❤️' , '🤯', '🙀'
        ]

        index = randrange(len(reaccs_msg))
        await message.channel.send(reaccs_msg[index])

        index = randrange(len(reaccs_emoji))
        await message.add_reaction(reaccs_emoji[index])

    # 'helo'
    if message.content.startswith('helo'):
        await message.add_reaction('❓')
        await message.channel.send('co chceš? 🧐')

    # 'i am dead'
    if message.content.startswith(('i am dead', 'im dead', 'i\'m dead')):
        await message.channel.send('Target sherminated')

    # 'je ti něco'
    if 'je ti něco' in message.content:
        await message.channel.send('no to mu je teda')

    # 'jsem dobrej'
    if message.content.startswith('jsem dobrej'):
        if randrange(100) < 50:
            await message.add_reaction('😍')
            await message.channel.send('jasně, že jo')
        else:
            await message.add_reaction('👎')
            await message.channel.send('haha, ne 🙂')


    # cinema
    if message.content.startswith('co dávají v kině'):
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
                await message.channel.send(res)
                res = ''        
        
        await message.channel.send(res)
    
    # AT BOT
    if message.content.startswith(bot_ids[0]) or message.content.startswith(bot_ids[1]):
        message.content = message.content.strip(bot_ids[0] + ' ')
        message.content = message.content.strip(bot_ids[1] + ' ')

        # greeting
        if message.content.startswith( ('ahoj', 'čus', 'čau', 'zdar', 'nazdar', 'zdraví','hello', 'hi', 'greetings') ):
            await message.add_reaction('👋')
            await message.channel.send(f'<@{message.author.id}> Ahoj!')
        # 'kde máš boty' 
        elif message.content.startswith('kde máš boty'):
            challenged = False
            await message.channel.send(f'<@{message.author.id}> Ve sklepě')
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
            await message.channel.send(f'<@{message.author.id}> ?')

    
    await client.process_commands(message)
    