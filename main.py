# 873429697793515551 client id
# ODczNDI5Njk3NzkzNTE1NTUx.YQ4Syw.aJaBinbcumiUmrsuDWQW7ATIRG4 token
# 8 permission

import discord
client = discord.Client()  

# wrapper / decorator
@client.event
# async คือ ทํางานได้หลายฟังชันพร้อมกัน โดยไม่รอ spawn()
async def on_ready():
    print(f"Logged is as {client.user}")

# async/await
# await จะถูกกัาหนดไว้ให้ใช้ตอนไหน ให้ดูใน docuemnt
@client.event
async def on_message(message):
    if message.content == '!send':
        print(message)
        await message.channel.send('asd')
    elif message.content == '!logout':
        await client.logout()

client.run("ODczNDI5Njk3NzkzNTE1NTUx.YQ4Syw.aJaBinbcumiUmrsuDWQW7ATIRG4")