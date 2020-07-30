from bot import client

import asyncio

import discord
import youtube_dl

from discord.ext import commands

import os
from discord.utils import get

playlist_path = os.path.abspath(__file__)
playlist_path = playlist_path.rsplit('/', 1)[0] + '/playlist/'

working_dir = os.getcwd()

emoji_play_stop = '🔴'
emoji_repeat = '🔂'

control_message = ''
song_name = ''

######################################################################################

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    #'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'outtmpl': '%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    def download_song(self, url):
        try:
            ytdl.download([url])
        except:
            raise Exception('Not a valid link!')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

######################################################################################

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['j'])
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        
        # channel = ctx.author.voice.channel

        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

        await ctx.send(f'Joined: {channel}')

    @commands.command(aliases=['l'])
    async def leave(self, ctx, *, channel: discord.VoiceChannel):
        try:
            await ctx.voice_client.disconnect()
            await ctx.send(f'Left: {channel}')
        except:
            await ctx.send('Cannot leave any channel')

    @commands.command(aliases=['p'])
    async def play(self, ctx, query, *args):
        global song_name, repeat
        repeat = False
        is_queue = False

        # PLAY FROM PLAYLIST
        if query.isnumeric():
            """Plays a file from the local filesystem"""

            os.chdir(playlist_path)

            try:
                song = os.listdir(playlist_path)[int(query)]
                song_name = song.replace('.mp3', '').replace('.webm', '')
            except:
                await ctx.send('Not in playlist!')
                return

            player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song))

            os.chdir(working_dir)
        # PLAY FROM YOUTUBE - LINK / SEARCH
        else:
            """Streams from a url (same as yt, but doesn't predownload)"""

            async with ctx.typing():
                player = await YTDLSource.from_url(f'{query} {" ".join(args)}', loop=self.bot.loop, stream=True)
                song_name = player.title


        # play
        ctx.voice_client.play(player)
        #ctx.voice_client.play(player, after=repeat_wrapper)

        # control message
        global control_message
        try:
            await control_message.edit( content=str(control_message.content).strip('++ ') )
        except:
            pass
        control_message = await ctx.send(f"++ Playing: {song_name} 🎵")
        await control_message.add_reaction(emoji_play_stop)
        await control_message.add_reaction(emoji_repeat)

    @commands.command(aliases=['pt'])
    async def playlist(ctx, option, url=''):
        os.chdir(playlist_path)

        if option in ('add', 'ad', 'a'):
            await ctx.send('Adding song to playlist...')
            try:
                YTDLSource.download_song(url)
            except Exception as e:
                await ctx.send(e)
                return

            await ctx.send('Song successfully added to playlist ✅')
        elif option in ('remove', 'remov', 'rm', 'r'):
            try:
                song = os.listdir()[int(url)]
                os.remove(song)
                await ctx.send(f'{song} has been removed from playlist ❌')
            except:
                await ctx.send('Not in playlist!')
        elif option in ('show', 'sho', 's'):
            pt = [
                f'{num}:   👉  {song.replace(".mp3", "").replace(".webm", "")}  👈'
                for num, song in enumerate(os.listdir())
            ]

            await ctx.send('\n'.join(pt))

        os.chdir(working_dir)

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()

                channel = ctx.author.voice.channel
                await ctx.send(f'Joined: {channel}')
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

######################################################################################

@client.event
async def on_reaction_add(reaction, user):
    global control_message
    if user == client.user or str(reaction.message) != str(control_message):
        return

    if str(reaction.emoji) == emoji_play_stop:
        voice = get(client.voice_clients, guild=reaction.message.channel.guild)

        if voice and voice.is_playing():
            voice.pause()
        elif voice and voice.is_paused():
            voice.resume()
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

        if voice and voice.is_playing():
            voice.pause()
        elif voice and voice.is_paused():
            voice.resume()
    elif str(reaction.emoji) == emoji_repeat:
        if reaction.count == 1:
            global repeat
            repeat = False


@client.command(aliases=['pa'])
async def panel(ctx):
    global control_message
    control_message = await ctx.send(control_message.content)
    await control_message.add_reaction(emoji_play_stop)
    await control_message.add_reaction(emoji_repeat)


client.add_cog(Music(client))
