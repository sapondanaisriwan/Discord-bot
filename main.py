# 873429697793515551 client id
# ODczNDI5Njk3NzkzNTE1NTUx.YQ4Syw.j5Iv8dEWN-QDxn0FnHC4h8JDK60 token
# 8 permission

import discord
client = discord.Client()

# wrapper / decorator
@client.event
async def on_ready():
    print(f"Logged is as {client.user}")
client.run("ODczNDI5Njk3NzkzNTE1NTUx.YQ4Syw.j5Iv8dEWN-QDxn0FnHC4h8JDK60")