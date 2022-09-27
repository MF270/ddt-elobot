import os
import csv
import discord
from dotenv import load_dotenv
from user import User


load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD = os.getenv("GUILD")
AUTHORIZED = os.getenv("AUTHOR")
USER_PATH = os.getenv("USERS")
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)



#programming gods forgive me

CURRENT_MATCHES = set()
def update_users():
    global USERS
    USERS = set()
    with open(USER_PATH,mode="r",newline="") as users:
        reader = csv.reader(users,delimiter=",")
        for row in reader:
            USERS.add(User(row[0],row[1],int(row[2])))
    for i in range(1,11):
        USERS.add(User(f"Dummy{i}",f"LMAO#696{i}",100*i))


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    update_users()
    print(USERS)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!"):
        msg = message.content[1:]
        if msg.startswith("help"):
            await message.channel.send('Type```!reg [name]``` to get started or ```!match [@ your opponent] [bo3/bo5]```\
            to start a match and ```!winner [@ winner] to report results``` or ```!myrank``` for your ranking, or ```!top10``` to see the current top 10')

        elif msg.startswith("reg"):
            user_info = msg.split(" ")[1:]
            if len(user_info) > 1:
                await message.channel.send("Command not recognized. Type !help if you need it")
                return

            already_in = [user for user in USERS if (user.name == user_info[0] or user.disc == str(message.author))]
            if len(already_in) >=1:
                await message.channel.send("Already registered! Your name must be unique")
                return
            USERS.add(User(user_info[0],str(message.author),1000))

            with open(USER_PATH,mode="a",newline="") as users:
                writer = csv.writer(users,delimiter=',')
                writer.writerow([user_info[0],str(message.author),1000])

            await message.channel.send(f"Registered {user_info[0]}")

        elif msg.startswith("match"):
            print(msg.split(" "))
            opp = msg.split(" ")[1]
            print(await client.fetch_user(int(opp[2:-1])))
            if msg.split(" ")[2].lower() not in ("bo3","bo5"):
                await message.channel.send("Please specify whether the match is a bo3 or bo5")

        elif msg.startswith("winner"):
            await message.channel.send("That's not yet implemented because I'm lazy!")

        elif msg.startswith("myrank"):
            top_rank = sorted(USERS,key=lambda x:x.elo,reverse=True)
            await message.channel.send(*[f"{user} | Rank {i+1}" for i,user in enumerate(top_rank) if user.disc == str(message.author)])
        
        elif msg.startswith("top10"):
            top_rank = sorted(USERS,key=lambda x:x.elo,reverse=True)
            await message.channel.send("".join([f"{i+1}. {user}\n" for i,user in enumerate(top_rank[:10])]))

        
        elif msg.startswith("reset"):
            update_users()

        elif msg.startswith("hard-reset") and str(message.author)==AUTHORIZED:
            with open(USER_PATH,mode="w",newline="") as users:
                pass

client.run(TOKEN)
