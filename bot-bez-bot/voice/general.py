from bot import client

import asyncio

import discord
import youtube_dl

from discord.ext import commands

import os
from discord.utils import get

######################################################################################

playlist_path = os.path.abspath(__file__)
playlist_path = playlist_path.rsplit('/', 1)[0] + '/playlist/'

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    #'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'outtmpl': playlist_path + '/' + '%(title)s.%(ext)s',
    #'restrictfilenames': True,
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
    def download_song(self, *args):
        try:
            ytdl.download([' '.join(args)])
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

emoji_play_stop = '🔴'
emoji_repeat = '🔂'

control_message = ''

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['j'])
    async def join(self, ctx, *, channel: discord.VoiceChannel=None):
        """Joins a voice channel"""

        if channel is None and ctx.author.voice:
            channel = ctx.author.voice.channel

        try:
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
        except:
            await ctx.send('I don\'t know, where to connect')
            return

        await ctx.send(f'Joined: {channel}')

    @commands.command(aliases=['l'])
    async def leave(self, ctx):
        """Leaves a voice channel"""

        try:
            await ctx.voice_client.disconnect()
            await ctx.send('Channel left')
        except Exception as e:
            print(e)
            await ctx.send('Cannot leave any channel')

    @commands.command(aliases=['p'])
    async def play(self, ctx, query, *args):
        """Plays song from playlist or from youtube (search or link)"""

        global repeat
        repeat = False

        # PLAY FROM PLAYLIST
        if query.isnumeric():
            try:
                song = os.listdir(playlist_path)[int(query)]
                song_name = song.replace('.mp3', '').replace('.webm', '')
            except:
                await ctx.send('Not in playlist!')
                return

            player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(playlist_path + '/' + song))
        # PLAY FROM YOUTUBE - LINK / SEARCH
        else:
            async with ctx.typing():
                player = await YTDLSource.from_url(f'{query} {" ".join(args)}', loop=self.bot.loop, stream=True)
                song_name = player.title


        # play
        ctx.voice_client.play(player)

        # control message
        global control_message
        try:
            await control_message.edit( content=str(control_message.content).strip('++ ') )
        except:
            pass
        control_message = await ctx.send(f"++ Playing: {song_name} 🎵")
        await control_message.add_reaction(emoji_play_stop)
        await control_message.add_reaction(emoji_repeat)

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

    @commands.command(aliases=['pt'])
    async def playlist(self, ctx, option, *args):
        '''Adds/removes/shows song(s) to/from/in playlist'''

        # ADD
        if option in ('add', 'ad', 'a'):
            try:
                YTDLSource.download_song(*args)
            except Exception as e:
                await ctx.send(e)
                return

            await ctx.send('Song successfully added to playlist ✅')
        # REMOVE
        elif option in ('remove', 'remov', 'rm', 'r'):
            try:
                song = os.listdir(playlist_path)[int(args[0])]
                os.remove(playlist_path + '/' + song)
                await ctx.send(f'{song} has been removed from playlist ❌')
            except:
                await ctx.send('Not in playlist!')
        # SHOW
        elif option in ('show', 'sho', 's'):
            pt = [
                f'{num}:   👉  {song.replace(".mp3", "").replace(".webm", "")}  👈'
                for num, song in enumerate(os.listdir(playlist_path))
            ]

            await ctx.send('\n'.join(pt))

    @commands.command(aliases=['pa'])
    async def panel(self, ctx):
        """Shows music control panel"""

        global control_message
        control_message = await ctx.send(control_message.content)
        await control_message.add_reaction(emoji_play_stop)
        await control_message.add_reaction(emoji_repeat)


client.add_cog(Music(client))

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
