import requests
import sys
import json
import discord
from discord.ext import commands, tasks
import cmds.ping.ping
import cmds.ping.refresh
import os
import asyncio
import traceback
import secrets

# Check environment variables

for i in ["token", "whoswho", "refresh_token", "user_channel_category", "default_channel", "jeromes"]:
    try:
        os.environ[i]
    except KeyError:
        print("Missing " + i + ". Terminating bot.")
        quit()


statusify = {"watching": "Watching", "completed": "Completed", "on_hold": "On Hold", "dropped": "Dropped", "plan_to_watch": "Plan to Watch"}

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=["jerome, ", "j "], owner_ids=[458304698827669536, 583832173048496129], case_insensitive=True, intents=intents)

with open("./config/config.json", "r") as data:
    config = json.loads(data.read())
    data.close()

client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='over the server | Type "jerome, help"'))
    print(f'Logged in as {client.user}.')
    client.load_extension("cmds.mal.mal")
    client.load_extension("cmds.user_channels.user_channels")
    await cmds.ping.refresh.refresh(client)

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
    print("Reload command received!")
    try:
        client.reload_extension("cmds.mal.mal")
        client.reload_extension("cmds.user_channels.user_channels")
    except Exception as e:
        await ctx.send('\N{PISTOL}')
        await ctx.send('{}: {}'.format(type(e).__name__, e))
        print(e)
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

client.run(os.environ["token"])
