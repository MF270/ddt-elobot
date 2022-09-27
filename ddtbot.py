#MeanBot
import discord
import user
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD = os.getenv("GUILD")
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if  message.content.startswith("!"):
        msg = message.content[1:]
        if msg.startswith("help"):
            await message.channel.send('Type```!reg [name]``` to get started or ```!match [@ your opponent] [bo3/bo5]``` for a match and ```!winner [@ winner] to report results```')
        if msg.startswith("reg"):
            pass
        if msg.startswith(""):
        elif message.content.startswith("reg"):
            with open("users.csv",mode="r",newline="") as users:
                pass

client.run(TOKEN)
