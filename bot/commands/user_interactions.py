from bot import client


## ECHO ##
@client.command(aliases=['e'], hidden=True)
async def echo(ctx, *args):
    '''Sends message as bot'''

    await ctx.channel.purge(limit=1)
    res = ' '.join(args)
    await ctx.send(res)

    
## HELLO ##
@client.command(aliases=['h'])
async def hello(ctx, *args):
    '''Says hello to whatever you specify'''

    await ctx.channel.purge(limit=1)
    for arg in args:
        await ctx.send(f'Hello, {arg}! 👋')
