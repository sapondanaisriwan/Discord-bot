from sys import prefix
import discord
from discord import guild
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

from discord import embeds
from discord.colour import Color
from discord.ext import commands
from datetime import datetime, timedelta

message_lastseen = datetime.now()

prefix = '!!'
bot = commands.Bot(command_prefix=prefix, help_command=None)

# wrapper / decorator
# #sync คือ ทํางานได้หลายฟังชันพร้อมกัน โดยไม่รอ spawn()


@bot.event
async def on_ready():
    print(f"Logged is as {bot.user}")

@bot.command()
async def test(ctx, *, agr):  # * รับข้อความมาทั้งหมด ถ้าไม่มีก็รับแค่ข้อความหน้าก่อน specbar input: hello world > output: hello
    await ctx.channel.send(f'You typed {agr}')

@bot.command()
async def help(ctx):  # 0x = base 16
    emBed = discord.Embed(title='Testing', description='Show all avaiable bot commands', color=0x32a852)
    emBed.add_field(name='help', value='Get help command', inline=False)
    emBed.add_field(name='test', value="Respond message that you've send", inline=False)
    emBed.add_field(name='send', value='Send something to user', inline=False)
    emBed.set_thumbnail(url='https://c.tenor.com/XhYqu5fu4LgAAAAd/boiled-soundcloud-boiled.gif')
    emBed.set_footer(text='test footer', icon_url='https://c.tenor.com/XhYqu5fu4LgAAAAd/boiled-soundcloud-boiled.gif')
    await ctx.channel.send(embed=emBed)

# async/await
# await จะถูกกัาหนดไว้ให้ใช้ตอนไหน ให้ดูใน docuemnt


@bot.event
async def on_message(message):
    global message_lastseen
    if message.content == '!send':
        print(message)
        await message.channel.send('asd')
    elif message.content == "what's your name" and datetime.now() >= message_lastseen:
        await message.channel.send(f"I'm {bot.user.id}")
        message_lastseen = datetime.now() + timedelta(seconds=1)
    elif message.content == '!logout':
        await bot.logout()
    await bot.process_commands(message)  # ประมวลผลว่าอันไหนควรรันก่อน

@bot.command(aliases=['play', 'p'])
async def _play(ctx, url):
    channel = ctx.author.voice.channel
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client == None:
        ctx.channel.send('Bot has joined')
        await channel.connect()
        voice_client = get(bot.voice_clients, guild=ctx.guild)

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not voice_client.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice_client.is_playing()
    else:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice_client.is_playing()
        # await ctx.channel.send('Already playing song')
        # return

@bot.command(aliases=['leave', 'dis', 'disconnect'])
async def _leave(ctx):
    if ctx.voice_client:  # If the bot is in a voice channel
        await ctx.voice_client.disconnect()
        await ctx.message.add_reaction('👋')
    else:
        emBed = discord.Embed(color=0x32a852) 
        pfp = ctx.message.author.avatar_url # user profile picture
        emBed.set_author(name=" | There's nothing playing in this server", icon_url=pfp)
        await ctx.send(embed=emBed)

# :x2: You need to be in the same voice channel as Rythm to use this command
bot.run("ODczNDI5Njk3NzkzNTE1NTUx.YQ4Syw.RHvCz7ywC1PaW_f1Bkekj3RI1Ac")