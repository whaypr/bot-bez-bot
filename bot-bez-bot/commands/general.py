from bot import client

import math as m
from discord.utils import get

@client.command(aliases=['m'])
async def math(ctx, *args):
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
        res = 'Neplatný výraz, bráško'

    if res == 69:
        res = str(res) + ' 😂'
    elif res == 420:
        res = str(res) + ' BLAZE IT!'

    await ctx.send(res)


@client.command(aliases=['c'])
async def clear(ctx):
    await ctx.channel.purge()
    await ctx.send('Uklizeno ✅')


@client.command(aliases=['h'])
async def hello(ctx, *args):
    await ctx.channel.purge(limit=1)
    for arg in args:
        await ctx.send(f'Hello, {arg}! 👋')


@client.command(aliases=['e'])
async def echo(ctx, *args):
    await ctx.channel.purge(limit=1)
    res = ' '.join(args)
    await ctx.send(res)
