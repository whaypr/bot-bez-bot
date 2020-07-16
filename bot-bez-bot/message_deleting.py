from bot import client

import asyncio
import datetime

treshhold = 5

async def my_background_task():
    await client.wait_until_ready()
    
    while not client.is_closed():
        hour = datetime.datetime.now().hour - 2
        minute = datetime.datetime.now().minute

        for ch in client.get_all_channels():
            if str(ch.type) == 'text':
                messages = await ch.history(limit=100).flatten()

                for mes in messages:
                    if not mes.content.startswith('++') and ( mes.created_at.hour < hour or minute - mes.created_at.minute >= treshhold ):
                        await mes.delete()

        await asyncio.sleep(30) # task runs every 30 seconds


client.loop.create_task(my_background_task())
