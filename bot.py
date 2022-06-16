import requests
import sys
import json
import discord
from discord.ext import commands, tasks
import asyncio
import traceback
import secrets
import cmds.ping.ping
import cmds.ping.refresh
import os

CLIENT_ID = '1f8715ac1db9caf0d35c43809d9e02fa'
CLIENT_SECRET = '20c6696977545ee3e18baaabf0be11ebdb5406d2197561ccac413a91b67b713c'
TOKEN = {}
@tasks.loop(seconds=3600)
async def refresh():
    global TOKEN
    with open("./config/token.json", "r") as data:
        token = json.loads(data.read())
        data.close()

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': os.environ["refresh_token"],
        'grant_type': 'refresh_token'
    }

    response = requests.post(url, data)
    response.raise_for_status()  # Check whether the requests contains errors

    token = response.json()
    TOKEN = token
    response.close()
    print('Token generated successfully!')

    with open('./config/token.json', 'w') as file:
        json.dump(token, file, indent = 4)
        print('Token saved in "token.json"')
    await cmds.ping.refresh.refresh(client)
    print("Sleeping for an hour...")


statusify = {"watching": "Watching", "completed": "Completed", "on_hold": "On Hold", "dropped": "Dropped", "plan_to_watch": "Plan to Watch"}

client = commands.Bot(command_prefix=["jerome, ", "j "], owner_id = 458304698827669536, case_insensitive=True)

with open("./config/config.json", "r") as data:
    config = json.loads(data.read())
    data.close()

client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='over the server | Type "jerome, help"'))
    print(f'Logged in as {client.user}.')
    await cmds.ping.refresh.refresh(client)
    #await refresh()


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await client.process_commands(message)

@client.command()
async def help(ctx):
    print("Received command help")
    embed=discord.Embed(title="You need help?", description="", color=0x489d9c)
    embed.add_field(name="Prefixes", value="`jerome, `, `j `\ne.g. `jerome, search Boku no Pico`", inline=False)
    embed.add_field(name="Commands", value="""\> `help` - shows this message.
\> `search <query>` or `s <query>` - searches `<query>` on MAL. Can be a name of a show or an ID. Numbers `like this` are MAL IDs.
\> `searchname <query>`, `sname <query>`, or `sn <query>` - forces name search.
\> `searchid <query>`, `sid <query>`, or `si <query>` - forces ID search.
\> `list <username>` or `l <username>` - shows <username>'s list.""", inline=False)
    embed.add_field(name="Features", value=f"""*Plainping*
Ever wanted to ping someone but forgot their discord tag? Just type @[real name] and Jerome's expertly curated database pulled from <#{os.environ["whoswho"]}> will ping that user for you!""", inline=False)
    await ctx.send(embed=embed)


@client.command()
@commands.is_owner()
async def reload(ctx):
    try:
        client.reload_extension("cmds.mal.mal")
        client.reload_extension("cmds.user_channels.user_channels")
    except Exception as e:
        await ctx.send('\N{PISTOL}')
        await ctx.send('{}: {}'.format(type(e).__name__, e))
    else:
        await ctx.send('\N{OK HAND SIGN}')

@client.command(aliases=["q"])
@commands.is_owner()
async def quit(ctx, *, arg):
    ctx.send("damn... guess i'll go")
    quit()

@client.event
async def on_message(msg):
    if "@" in msg.clean_content and msg.author != client.user:
        await cmds.ping.ping.ping(client, msg)
    await client.process_commands(msg)

#refresh.start()
client.load_extension("cmds.mal.mal")
client.load_extension("cmds.user_channels.user_channels")
client.run(os.environ["token"])
