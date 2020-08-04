from bot import client

import asyncio
import datetime

threshold = 5 * 60 # in seconds

async def my_background_task():
    await client.wait_until_ready()
    
    while not client.is_closed():
        timestamp_now = datetime.datetime.now().timestamp() - 7200 # timezone, 2 hours = 7200 seconds

        for ch in client.get_all_channels():
            if str(ch.type) == 'text':
                messages = await ch.history(limit=100).flatten()

                for mes in messages:
                    timestamp_mes = mes.created_at.timestamp()

                    if not mes.content.startswith('++') and ( timestamp_now - timestamp_mes > threshold ):
                        await mes.delete()

        await asyncio.sleep(30) # task runs every 30 seconds


client.loop.create_task(my_background_task())
