from sys import prefix
import discord
from discord.utils import get
from youtube_dl import YoutubeDL

from discord.ext import commands
from datetime import datetime, timedelta

message_lastseen = datetime.now()

prefix = '!!'
bot = commands.Bot(command_prefix=prefix, help_command=None)

# wrapper / decorator
# #sync คือ ทํางานได้หลายฟังชันพร้อมกัน โดยไม่รอ spawn()
# ctx = ผู้ใช้
# bot =


@bot.event
async def on_ready():
    print(f"Logged is as {bot.user}")

@bot.command()
async def test(ctx, *, agr):  # * รับข้อความมาทั้งหมด ถ้าไม่มีก็รับแค่ข้อความหน้าก่อน specbar input: hello world > output: hello
    await ctx.channel.send(f'You typed {agr}')

@bot.command(name='wtf')
async def wtf(ctx):
    await ctx.channel.send('hello')

@bot.command()
async def help(ctx):  # 0x = base 16
    emBed = discord.Embed(
        title='Testing', 
        description='Show all avaiable bot commands', 
        color=0x32a852
    )
    emBed.add_field(name='help', value='Get help command', inline=False)
    emBed.add_field(name='test', value="Respond message that you've send", inline=False)
    emBed.add_field(name='send', value='Send something to user', inline=False)
    emBed.set_thumbnail(url='https://c.tenor.com/XhYqu5fu4LgAAAAd/boiled-soundcloud-boiled.gif')
    emBed.set_footer(text='test footer',icon_url='https://c.tenor.com/XhYqu5fu4LgAAAAd/boiled-soundcloud-boiled.gif')
    await ctx.channel.send(embed=emBed)

# async/await
# await จะถูกกัาหนดไว้ให้ใช้ตอนไหน ให้ดูใน docuemnt


@bot.event
async def on_message(message):
    global message_lastseen
    if message.content == '!send':
        await message.channel.send('asd')
    elif message.content == "what's your name" and datetime.now() >= message_lastseen:
        await message.channel.send(f"I'm {bot.user.id}")
        message_lastseen = datetime.now() + timedelta(seconds=1)
    elif message.content == '!logout':
        await bot.logout()
    await bot.process_commands(message)  # ประมวลผลว่าอันไหนควรรันก่อน


@bot.command(aliases=['play', 'p'])
# ctx = คนใช้คำสั่ง/ผู้ใช้
async def _play(ctx, url):
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

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not voice_client.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        
        # Variables
        URL = info['formats'][0]['url']
        titleVideo = info['title']
        thumbnailVideo = info['thumbnails'][-1]['url']
        convertDuration = str(timedelta(seconds=info['duration']))
        channelYT = info['channel']

        # Embed
        emBed = discord.Embed(title=titleVideo, url=URL,color=0x30d96b)
        emBed.set_thumbnail(url=thumbnailVideo)
        emBed.add_field(name='Channel', value=channelYT, inline=True)
        emBed.add_field(name='Duration', value=convertDuration, inline=True)
        emBed.set_author(name='Added to queue', icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=emBed)

        voice_client.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice_client.is_playing()
    else:
        await ctx.channel.send('Already playing song')
        return

# @bot.command()
# async def stop(ctx):
#     voice_client = get(bot.voice_clients, guild=ctx.guild)
#     if ctx.author.voice == None: # if user not in the vc
#         emBed = discord.Embed(color=0xff0000)
#         emBed.set_author(name=" | You're not in a voice channel", icon_url=ctx.message.author.avatar_url)
#         await ctx.send(embed=emBed)
#         return
#     if voice_client == None: # ถ้าบอทยังไม่ได้อยู่ใน vc ไหนเลย ระหว่างกับผู้ใช้อยู่ใน vc // ผู้ใช้ยังไม่ได้ใช้ command play //  there is nothing playing on this guild
#         emBed = discord.Embed(color=0xff0000)
#         emBed.set_author(name=" | There is nothing playing on this guild", icon_url=bot.user.avatar_url)
#         await ctx.send(embed=emBed)
#         return
#     if voice_client.channel != ctx.author.voice.channel: # ห้องของบอทไมไ่ด้อยู่ห้องเดียวกับผู้ใช้
#         await ctx.channel.send(f"❌ **| You're not in the same voice channel with me. Please join** <#{voice_client.channel.id}>")
#         return
#     emBed=discord.Embed(description="Stopped the song.", color=0x00ff00)
#     await ctx.send(embed=emBed)
#     voice_client.stop()


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


@bot.command(aliases=['leave', 'stop', 'dis', 'disconnect'])
async def _leave(ctx):
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

# :x2: You need to be in the same voice channel as Rythm to use this command
bot.run("Token")
