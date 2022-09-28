import os
import csv
import discord
from dotenv import load_dotenv
from collections import namedtuple

Match = namedtuple("Match","p1 p2 bo3 done")
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
NEEDS_CONFIRMATION = set()

def update_users():
    global USERS
    USERS = set()
    with open(USER_PATH,mode="r",newline="") as users:
        reader = csv.reader(users,delimiter=",")
        for row in reader:
            USERS.add(User(row[0],row[1],int(row[2])))

def user_exists(disc:str,USERS):
    discs = [user.disc for user in USERS]
    return str(disc) in discs
def name_exists(name:str,USERS):
    return str(name) in (user.name for user in USERS)
def user_by_disc(disc:str,USERS) -> User:
    return [user for user in USERS if user.disc == disc][0]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    update_users()
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
            to start a match and ```!report [@ winner] to report results``` or ```!myrank``` for your ranking, or ```!top10``` to see the current top 10')

        elif msg.startswith("reg"):
            user_info = msg.split(" ")[1:]
            if len(user_info) > 1:
                await message.channel.send("Command not recognized. Type !help if you need it")
                return

            if user_exists(str(message.author),USERS) or name_exists(user_info,USERS):
                await message.channel.send("Already registered! Your name must be unique")
                return
            USERS.add(User(user_info[0],str(message.author),1000))

            with open(USER_PATH,mode="a",newline="") as users:
                writer = csv.writer(users,delimiter=',')
                writer.writerow([user_info[0],str(message.author),1000])

            await message.channel.send(f"Registered {user_info[0]}")

        elif msg.startswith("match"):
            opp = msg.split(" ")[1]
            opp = (await client.fetch_user(int(opp[2:-1])))
            you = str(message.author)
            try:
                bo3 =msg.split(" ")[2].lower() == "bo3"
            except:
                await message.channel.send("Please specify whether the match is a bo3 or bo5")
                return
            if not user_exists(opp,USERS):
                await message.channel.send("Opponent is not registered")
                return

            elif not user_exists(you,USERS):
                await message.channel.send("You must be registered to match")
                return
            else:
                bo3 = msg.split(" ")[2].lower() == "bo3"
                CURRENT_MATCHES.add(Match(you,opp,bo3,False))
                await message.channel.send(f"{you} vs {opp}, {'best of 3' if bo3 else 'best of 5'}\
                \nReport match results with ```!report [winner]```")

        elif msg.startswith("report"):
            if len(CURRENT_MATCHES) == 0:
                await message.channel.send("No matches ongoing!")
                return
            try:
                this_match = [match for match in CURRENT_MATCHES if (str(message.author) in (match.p1,match.p2))][0]
            except:
                await message.channel.send("You are not currently in any matches")
                return
            winner = msg.split(" ")[1]
            winner = (await client.fetch_user(int(winner[2:-1])))
            if str(message.author) == this_match.p1:
                other = this_match.p2
            else:
                other = this_match.p1
            NEEDS_CONFIRMATION.add((other,winner==other,this_match.bo3))
            await message.channel.send(f"Winner: {winner}\n@{other}, please type !confirm to verify the match results or !dispute to dispute the loss")

        elif msg.startswith("confirm"):
            matches = [match for match in NEEDS_CONFIRMATION if str(message.author) == str(match[0])]
            print(NEEDS_CONFIRMATION)
            print(matches)
            if len(matches)!=1:
                await message.channel.send("No matches to confirm")
                return
            confirmation_info = matches[0]
            this_match = [match for match in CURRENT_MATCHES if (str(message.author) in\
            (match.p1,match.p2))][0]

            if str(message.author) == this_match.p1:
                other = this_match.p2
            else:
                other = this_match.p1

            NEEDS_CONFIRMATION.remove(this_match)
            user_by_disc(message.author,USERS).match(user_by_disc(other,USERS),
            confirmation_info[1],confirmation_info[2])
            await message.channel.send("Results confirmed")

        elif msg.startswith("dispute"):
            matches = [match for match in NEEDS_CONFIRMATION if str(message.author) == match[0]]
            if len(matches)!=1:
                await message.channel.say("No matches to dispute")
                return

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
