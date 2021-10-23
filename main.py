# 873429697793515551 client id
# ODczNDI5Njk3NzkzNTE1NTUx.YQ4Syw.aJaBinbcumiUmrsuDWQW7ATIRG4 token
# 8 permission

from typing import Sequence
import discord
from datetime import date, datetime, timedelta

client = discord.Client()  

message_lastseen = datetime.now()

# wrapper / decorator
# # async คือ ทํางานได้หลายฟังชันพร้อมกัน โดยไม่รอ spawn()
@client.event
async def on_ready():
    print(f"Logged is as {client.user}")

# async/await
# await จะถูกกัาหนดไว้ให้ใช้ตอนไหน ให้ดูใน docuemnt
@client.event
async def on_message(message):
    global message_lastseen
    if message.content == '!send':
        print(message)
        await message.channel.send('asd')
    elif message.content == "what's your name" and datetime.now() >= message_lastseen:
        await message.channel.send(f"I'm {client.user.id}")
        message_lastseen = datetime.now() + timedelta(seconds=1)
    elif message.content == '!logout':
        await client.logout()

client.run("Your token")