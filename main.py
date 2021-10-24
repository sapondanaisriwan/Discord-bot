import discord
from discord import embeds
from discord.colour import Color
from discord.ext import commands
from datetime import datetime, timedelta

message_lastseen = datetime.now()

bot = commands.Bot(command_prefix='!',help_command=None)

# wrapper / decorator
# #sync คือ ทํางานได้หลายฟังชันพร้อมกัน โดยไม่รอ spawn()
@bot.event
async def on_ready():
    print(f"Logged is as {bot.user}")

@bot.command()
async def test(ctx, *, agr): # * รับข้อความมาทั้งหมด ถ้าไม่มีก็รับแค่ข้อความหน้าก่อน specbar input: hello world > output: hello
    await ctx.channel.send(f'You typed {agr}')

@bot.command()
async def help(ctx): # 0x = base 16
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
    await bot.process_commands(message) # ประมวลผลว่าอันไหนควรรันก่อน

bot.run("ODczNDI5Njk3NzkzNTE1NTUx.YQ4Syw.XEAh6bBJN5QxXNyW3OCXsL0alZk")