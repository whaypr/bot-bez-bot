from bot import client


## CLEAR ##
@client.command(aliases=['c'])
async def clear(ctx):
    '''Clears messages in channel'''

    await ctx.channel.purge()
    await ctx.send('Uklizeno ✅')
    