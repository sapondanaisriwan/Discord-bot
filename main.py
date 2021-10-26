# coding:utf-8

import io
import os
import qrcode

import discord
from discord.utils import get
from discord.ext import commands

from sys import prefix
from googletrans import Translator
import youtube_dl
import asyncio 
from async_timeout import timeout
from functools import partial

# from pythainlp.translate import Translate
# from pythainlp.util import countthai
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv('TOKEN')

prefix = '!!'
bot = commands.Bot(command_prefix=prefix, help_command=None)

# wrapper / decorator
# #sync คือ ทํางานได้หลายฟังชันพร้อมกัน โดยไม่รอ spawn()
# ctx = ผู้ใช้
# bot =

""" Check for the bot is ready or not """
@bot.event
async def on_ready():
    print(f"Logged is as {bot.user}")
    await bot.change_presence(activity=discord.Game(name='with you mom'))
    # await bot.change_presence(activity=discord.Activity(name='your mom', type=discord.ActivityType.watching))


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}


ffmpeg_options = {'options': '-vn',"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.thumbnail = data.get('thumbnail')
        self.channel = data.get('channel')
        self.duration = data.get('duration')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        # send an embed
        emBed = discord.Embed(title=data['title'], url=data['formats'][0]['url'], color=0x30d96b)
        emBed.set_thumbnail(url=data['thumbnail'])
        emBed.add_field(name='Channel', value=data['channel'], inline=True)
        emBed.add_field(name='Duration', value=str(timedelta(seconds=data['duration'])), inline=True)
        emBed.set_author(name='Added to queue', icon_url=ctx.message.author.avatar_url)

        # await ctx.send(embed=emBed, delete_after=15)
        await ctx.send(embed=emBed)

        # await ctx.send(f'```ini\n[Added {data["title"]} to the Queue.]\n```', delete_after=15)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source , **ffmpeg_options), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'] ,**ffmpeg_options), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', '_message', '_author','queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        # print('ctx=\n' + str(dir(ctx)))
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self._message = ctx.message
        self._author = ctx.author
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            # print('\n_message=\n' + str(dir(self._message)))
            # print('\n_author=\n' + str(dir(self._author)))
            # print(self._author.avatar_url)
            # emBed = discord.Embed(title=source.title, url=source.web_url, color=0x30d96b)
            # emBed.set_thumbnail(url=source.thumbnail)
            # emBed.add_field(name='Channel', value=source.channel, inline=True)
            # emBed.add_field(name='Duration', value=source.duration, inline=True)
            # emBed.set_author(name='Added to queue', icon_url=self._author.avatar_url)
            # self.np = await self._channel.send(embed=emBed)

            # await ctx.send(embed=emBed)
            # self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
            #                                    f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                pass
                # We are no longer playing this song...
                # await self.np.delete()
            except discord.HTTPException:
                pass

    async def destroy(self, guild):
        """Disconnect and cleanup the player."""
        await self._guild.voice_client.disconnect()
        return self.bot.loop.create_task(self._cog.cleanup(guild))

@bot.command()
async def test(ctx, *, agr):  # * รับข้อความมาทั้งหมด ถ้าไม่มีก็รับแค่ข้อความหน้าก่อน specbar input: hello world > output: hello
    print(ctx, dir(ctx))
    await ctx.channel.send(f'You typed {agr}')


""" Generator qrcode """
@bot.command(aliases=['qr', 'qrcode'])
async def _qrcode(ctx, *, url):
    try:
        q = qrcode.make(url)
        arr = io.BytesIO()
        q.save(arr, format="PNG")
        arr.seek(0)
        await ctx.send(file=discord.File(fp=arr, filename="image.png"))
    except:
        await ctx.send('Please send url only')


""" Translate to Thai """
@bot.command(aliases=['translate', 'tsl'])
async def _translate(ctx, *, message):
    # checkThai = countthai(message)
    hexColor = 0x74d9fb
    # fieldName = ''
    # translated = None
    # if checkThai >= 80:
    #     translated = Translate('th', 'en').translate(message)
    #     fieldName = 'TH to EN'
    # else:
    #     translated = Translate('en', 'th').translate(message)
    #     fieldName = 'EN to TH'
    translator = Translator()
    result = translator.translate(message, dest='th').text
    embed = discord.Embed(color=hexColor)
    embed.set_author(
        name="แปลภาษา", icon_url="https://www.aniaetleprogrammeur.com/wp-content/uploads/2019/02/Google_Translate_Icon.png")
    embed.add_field(name='แปลประโยค',
                    value=f'```diff\n{message}```', inline=False)
    embed.add_field(name='ความหมาย',
                    value=f'```yaml\n{result}```', inline=False)
    embed.set_footer(text=f'cr.code design by : LuckyToT#1251')

    await ctx.send(embed=embed)


""" Show Help Command """
@bot.command()
async def help(ctx):  # 0x = base 16
    emBed = discord.Embed(
        title='Testing',
        description='Show all avaiable bot commands',
        color=0x32a852
    )
    emBed.add_field(name='help', value='Get help command', inline=False)
    emBed.add_field(
        name='test', value="Respond message that you've send", inline=False)
    emBed.add_field(name='send', value='Send something to user', inline=False)
    emBed.set_thumbnail(
        url='https://c.tenor.com/XLIIrXBMrgcAAAAd/tom-china.gif')
    emBed.set_footer(text='test footer',
                     icon_url='https://c.tenor.com/XLIIrXBMrgcAAAAd/tom-china.gif')
    await ctx.channel.send(embed=emBed)

# async/await
# await จะถูกกัาหนดไว้ให้ใช้ตอนไหน ให้ดูใน docuemnt


message_lastseen = datetime.now()
""" On Message """
@bot.event
async def on_message(message):
    global message_lastseen
    if message.content == '!test':
        await message.channel.send(f'{bot.owner_id} {bot.owner_ids}')
    elif message.content == "what's your name" and datetime.now() >= message_lastseen:
        await message.channel.send(f"I'm {bot.user.id}")
        message_lastseen = datetime.now() + timedelta(seconds=1)
    elif message.content == '!logout':
        await bot.logout()
    await bot.process_commands(message)  # ประมวลผลว่าอันไหนควรรันก่อน


""" Play music command """
@bot.command(aliases=['play', 'p'])
async def _play(ctx, *, search: str): # ctx = คนใช้คำสั่ง/ผู้ใช้
    if ctx.author.voice == None:
        emBed = discord.Embed(color=0xff0000)
        emBed.set_author(name=" | You're not in a voice channel",
                         icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=emBed)
        return
    channel = ctx.author.voice.channel
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client == None:
        await channel.connect()
        voice_client = get(bot.voice_clients, guild=ctx.guild)

    _player = get_player(ctx)
    source = await YTDLSource.create_source(ctx, search, loop=bot.loop, download=False)

    await _player.queue.put(source)

    # YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
    # FFMPEG_OPTIONS = {
    #     'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    # if not voice_client.is_playing():
    #     with YoutubeDL(YDL_OPTIONS) as ydl:
    #         info = ydl.extract_info(url, download=False)

        # # Variables
        # URL = info['formats'][0]['url']
        # titleVideo = info['title']
        # thumbnailVideo = info['thumbnails'][-1]['url']
        # convertDuration = str(timedelta(seconds=info['duration']))
        # channelYT = info['channel']

        # # Embed
        # emBed = discord.Embed(title=titleVideo, url=url, color=0x30d96b)
        # emBed.set_thumbnail(url=thumbnailVideo)
        # emBed.add_field(name='Channel', value=channelYT, inline=True)
        # emBed.add_field(name='Duration', value=convertDuration, inline=True)
        # emBed.set_author(name='Added to queue',
        #                  icon_url=ctx.message.author.avatar_url)
        # await ctx.send(embed=emBed)

        # voice_client.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        # voice_client.is_playing()


players = {}
def get_player(ctx):
    try:
        player = players[ctx.guild.id]
    except:
        player = MusicPlayer(ctx)
        players[ctx.guild.id] = player    
    return player


"""Pause music"""
@bot.command()
async def pause(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if ctx.author.voice == None:  # if user not in the vc
        emBed = discord.Embed(color=0xff0000)
        emBed.set_author(name=" | You're not in a voice channel",
                         icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=emBed)
        return
    if voice_client == None:  # ถ้าบอทยังไม่ได้อยู่ใน vc ไหนเลย ระหว่างกับผู้ใช้อยู่ใน vc // ผู้ใช้ยังไม่ได้ใช้ command play //  there is nothing playing on this guild
        emBed = discord.Embed(color=0xff0000)
        emBed.set_author(
            name=" | There is nothing playing on this guild", icon_url=bot.user.avatar_url)
        await ctx.send(embed=emBed)
        return
    if voice_client.channel != ctx.author.voice.channel:  # ห้องของบอทไมไ่ด้อยู่ห้องเดียวกับผู้ใช้
        await ctx.channel.send(f"❌ **| You're not in the same voice channel with me. Please join** <#{voice_client.channel.id}>")
        return
    emBed = discord.Embed(description="Paused the song.", color=0x00ff00)
    await ctx.send(embed=emBed)
    voice_client.pause()


""" Resume Music """
@bot.command()
async def resume(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if ctx.author.voice == None:  # if user not in the vc
        emBed = discord.Embed(color=0xff0000)
        emBed.set_author(name=" | You're not in a voice channel",
                         icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=emBed)
        return
    if voice_client == None:
        emBed = discord.Embed(color=0xff0000)
        emBed.set_author(
            name=" | Bot is not connected to voice channel yet", icon_url=bot.user.avatar_url)
        await ctx.send(embed=emBed)
        return
    if voice_client.channel != ctx.author.voice.channel:  # channel ของ bot != คนพิมพ์
        await ctx.channel.send(f"❌ **| You're not in the same voice channel with me. Please join** <#{voice_client.channel.id}>")
        return
    emBed = discord.Embed(description="Resumed the song.", color=0x00ff00)
    await ctx.send(embed=emBed)
    voice_client.resume()


""" Leave command """
@bot.command(aliases=['leave', 'stop', 'dis', 'disconnect'])
async def _leave(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client.channel != ctx.author.voice.channel:  # ห้องของบอทไมไ่ด้อยู่ห้องเดียวกับผู้ใช้
        await ctx.channel.send(f"❌ **| You're not in the same voice channel with me. Please join** <#{voice_client.channel.id}>")
        return
    if ctx.author.voice == None:  # if user not in the vc
        emBed = discord.Embed(color=0xff0000)
        emBed.set_author(name=" | You're not in the same voice channel",
                         icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=emBed)
        return
    if ctx.voice_client:  # If the bot is in a voice channel
        await ctx.voice_client.disconnect()
        await ctx.message.add_reaction('👌')
    else:
        emBed = discord.Embed(color=0xff0000)
        emBed.set_author(
            name=" | There's nothing playing in this server", icon_url=bot.user.avatar_url)
        await ctx.send(embed=emBed)

bot.run(TOKEN)
