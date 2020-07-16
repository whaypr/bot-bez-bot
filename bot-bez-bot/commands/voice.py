from bot import client

import os
import asyncio
import discord
from discord.utils import get
import youtube_dl
from youtube_search import YoutubeSearch

song_path = os.path.abspath(__file__)
song_path = song_path.rsplit('/', 2)[0] + '/songs/'

working_dir = os.getcwd()

emoji_play_stop = '🔴'
emoji_repeat = '🔂'

control_message = ''
song_name = ''
repeat = False

def download_song(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        #'outtmpl': '%(title)s-%(id)s.%(ext)s',
        'outtmpl': '%(title)s.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except:
            raise Exception('Not a valid link!')

    return ydl.extract_info(url, download=False).get('title', None)


def repeat_song():
    global repeat
    if not repeat:
        return

    os.chdir(song_path)
    if song_name + '.mp3' not in os.listdir():
        os.chdir(song_path + '/playlist')

    voice = get(client.voice_clients, guild=control_message.channel.guild)

    voice.play( discord.FFmpegPCMAudio( song_name + '.mp3' ), after=repeat_wrapper )
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.3

    os.chdir(working_dir)


def repeat_wrapper(error):
    try:
        fut = asyncio.run_coroutine_threadsafe(repeat_song(), client.loop)
        fut.result()
    except Exception as e:
        print(e)

########################################################################

@client.command(aliases=['j'])
async def join(ctx):
    channel = ctx.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await ctx.send(f'Joined: {channel}')


@client.command(aliases=['l'])
async def leave(ctx):
    channel = ctx.author.voice.channel
    try:
        await ctx.voice_client.disconnect()
        await ctx.send(f'Left: {channel}')
    except:
        await ctx.send('Cannot leave any channel')


@client.command(aliases=['p'])
async def play(ctx, url, *args):
    # working in song dir
    os.chdir(song_path)

    global song_name, repeat
    repeat = False
    is_queue = False

    # PLAY FROM PLAYLIST
    if url.isnumeric():
        os.chdir(song_path + '/playlist')

        try:
            song = os.listdir()[int(url)]
            song_name = song.replace('.mp3', '')
        except:
            await ctx.send('Not in playlist!')
            os.chdir(working_dir)
            return
    # REPLAY
    elif url in ('replay', 'rp', 'r'):
        for file in os.listdir():
            if file.endswith('.mp3'):
                song_name = file.replace('.mp3', '')
                break
    # PLAY FROM YOUTUBE - LINK
    elif url.startswith('http'):
        # delete previous
        for file in os.listdir():
            if file.endswith('.mp3'):
                os.remove(file)

        # download
        await ctx.send('Downloading song...')
        try:
            song_name = download_song(url)
        except Exception as e:
            await ctx.send(e)
            os.chdir(working_dir)
    # PLAY FROM YOUTUBE - SEARCH
    else:
        url = YoutubeSearch(f'{url} {" ".join(args)}', max_results=1).to_dict()
        url = 'https://www.youtube.com' + url[0]['url_suffix']

        # delete previous
        for file in os.listdir():
            if file.endswith('.mp3'):
                os.remove(file)

        # download
        await ctx.send('Downloading song...')
        try:
            song_name = download_song(url)
        except Exception as e:
            await ctx.send(e)
            os.chdir(working_dir)


    # join if not joined
    channel = ctx.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if not ( voice and voice.is_connected() ):
        voice = await channel.connect()
        await ctx.send(f'Joined: {channel}')

    # stop if playing
    if voice.is_playing():
        voice.stop()

    # play
    voice.play( discord.FFmpegPCMAudio( song_name + '.mp3' ), after=repeat_wrapper )
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.3

    global control_message
    control_message = await ctx.send(f"Playing: {song_name} 🎵")
    await control_message.add_reaction(emoji_play_stop)
    await control_message.add_reaction(emoji_repeat)

    os.chdir(working_dir)


@client.command(aliases=['pt'])
async def playlist(ctx, option, url=''):
    os.chdir(song_path + '/playlist')

    if option in ('add', 'ad', 'a'):
        await ctx.send('Adding song to playlist...')
        try:
            download_song(url)
        except Exception as e:
            await ctx.send(e)

        await ctx.send('Song successfully added to playlist ✅')
    elif option in ('remove', 'remov', 'rm', 'r'):
        try:
            song = os.listdir()[int(url)]
            os.remove(song)
            await ctx.send(f'{song} has been removed from playlist ❌')
        except:
            await ctx.send('Not in playlist!')
    elif option in ('show', 'sho', 's'):
        for num, file in enumerate(os.listdir()):
            await ctx.send(f'{num}:   👉  {file.replace(".mp3", "")}  👈')

    os.chdir(working_dir)

########################################################################

@client.event
async def on_reaction_add(reaction, user):
    global control_message
    if user == client.user or str(reaction.message) != str(control_message):
        return

    if str(reaction.emoji) == emoji_play_stop:
        voice = get(client.voice_clients, guild=reaction.message.channel.guild)

        if voice and voice.is_connected():
            voice.pause()
    elif str(reaction.emoji) == emoji_repeat:
        global repeat
        repeat = True


@client.event
async def on_reaction_remove(reaction, user):
    global control_message
    if user == client.user or str(reaction.message) != str(control_message):
        return

    if str(reaction.emoji) == emoji_play_stop:
        voice = get(client.voice_clients, guild=reaction.message.channel.guild)

        if voice and voice.is_paused():
            voice.resume()
    elif str(reaction.emoji) == emoji_repeat:
        global repeat
        repeat = False
