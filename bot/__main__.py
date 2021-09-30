from bot import client
import commands, events, voice

import os
try:
    TOKEN = os.environ['TOKEN']
except:
    print('No token provided!', 'Terminating...')
    quit()

client.run(TOKEN)
