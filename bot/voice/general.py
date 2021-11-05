from bot import client

from youtube_dl.utils import bug_reports_message
from youtube_dl import YoutubeDL

import discord
from discord.ext import commands
from discord.utils import get

# Suppress noise about console usage from errors
bug_reports_message = lambda: ''


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.emoji_play_stop = '🔴'
        self.emoji_repeat = '🔁'

        self.repeat = None
        self.panel = None

        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
        }
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }


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
    async def play(self, ctx, *args):
        """Plays song from youtube (search or link)"""

        # find
        async with ctx.typing():
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                try:
                    info = ydl.extract_info("ytsearch:%s" % ' '.join(args), download=False)["entries"][0]
                except Exception as e:
                    print(e)
                    await ctx.send('Could not play, try again...')
                    return

            data = {
                "url": info["formats"][0]["url"],
                "title": info["title"],
                "length": info["duration"],
            }

        self.repeat = False

        # play
        def play_next(ctx=ctx, data=data):
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(data['url'], **self.FFMPEG_OPTIONS),
                after=lambda _: play_next() if self.repeat else None
            )
        play_next()

        # panel
        if (self.panel != None):
            await self.panel.delete()

        embed = discord.Embed (
            title = 'Playing 🎵',
            description = data['title'],
            colour = discord.Colour.green()
        )
        embed.insert_field_at(0, name='LOOPING', value='❌')

        self.panel = await ctx.send(embed = embed)

        await self.panel.add_reaction(self.emoji_play_stop)
        await self.panel.add_reaction(self.emoji_repeat)


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


    @commands.command(aliases=['pa'])
    async def panel(self, ctx):
        """Shows music control panel"""

        if (self.panel == None):
            return

        await self.panel.delete()
        self.panel = await ctx.send(embed=self.panel.embeds[0])

        await self.panel.add_reaction(self.emoji_play_stop)
        await self.panel.add_reaction(self.emoji_repeat)


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == client.user or str(reaction.message) != str(self.panel):
            return

        voice = get(client.voice_clients, guild=reaction.message.channel.guild)

        if (reaction.emoji == self.emoji_play_stop):
            if voice and voice.is_playing():
                voice.pause()
                self.panel.embeds[0].title = "Paused"
                self.panel.embeds[0].color = discord.Colour.red()
            else:
                voice.resume()
                self.panel.embeds[0].title = "Playing 🎵"
                self.panel.embeds[0].color = discord.Colour.green()
        elif (reaction.emoji == self.emoji_repeat):
            if self.repeat:
                self.repeat = False
                self.panel.embeds[0].set_field_at(0, name=self.panel.embeds[0].fields[0].name, value='❌')
            else:
                self.repeat = True
                self.panel.embeds[0].set_field_at(0, name=self.panel.embeds[0].fields[0].name, value='✅')

        # remove reaction
        await reaction.message.remove_reaction(reaction, user)

        # edit panel
        await self.panel.edit(embed = self.panel.embeds[0])


client.add_cog(Music(client))
