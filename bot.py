import json
import discord
from discord.ext import commands, tasks
import cmds.ping.ping
import cmds.ping.refresh
import os
from random_words import RandomWords
import traceback

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

client = commands.Bot(command_prefix=["jerome, ", "jerome,", "Jerome, ", "Jerome,", "j ", "J "], owner_ids=[458304698827669536, 583832173048496129, 987818986156740648], case_insensitive=True, intents=intents)

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
async def help(ctx, *args):
    print("Received command help")
    embed=discord.Embed(title="You need help?", description="", colour=0x489d9c)

    if not args:
        embed.add_field(name="Prefixes", value="`jerome, `, `j `\ne.g. **`jerome, search Attack on Titan`**", inline=False)
        embed.add_field(name="Commands", value="""\> **`help`** - shows this message.
For information on the other commands, type
\> **`help MAL`** for MyAnimeList searching
\> **`help user channels` or `help user`** for user channels.
For a tutorial on setting up your own user channel, type **`j help setup`**""", inline=False)
        embed.add_field(name="Helpful stuff", value=f"""*Plainping*
Ever wanted to ping someone but forgot their discord tag? Just type @[real name] and Jerome's expertly curated database pulled from <#{os.environ["whoswho"]}> will ping that user for you!""", inline=False)
    else:
        match args[0].lower():
            case "mal":
                embed.add_field(name="MAL", value="""These are commands that help with querying MyAnimeList (MAL).
\> `search <query>` or `s <query>` - searches `<query>` on MAL. Can be a name of a show or an ID. Numbers `like this` are MAL IDs.
\> `searchname <query>`, `sname <query>`, or `sn <query>` - forces name search.
\> `searchid <query>`, `sid <query>`, or `si <query>` - forces ID search.
\> `list <username>` or `l <username>` - shows <username>'s list.""", inline=False)

            case "user channels" | "user" | "uc" | "user ch":
                embed.add_field(name="USER CHANNELS", value="""User channels are essentially Discord DMs on Jerome's but without the dumb 10 person cap. Start your own by typing `jerome, create my-cool-channel`!
`#<channel>` or `@<user>` indicate that you must ping the channel or user. `<channel>` or `<user>` indicate that you mustn't.

__**Managing your user channel**__

**\> `create <channel> as <type>` or `cr <channel> <type>`** - creates a new user channel called `<channel>`. `<type>` can either be `text` or `voice`.
**\> `delete #<channel>`** - deletes the user channel called `#<channel>`. *Destructive!*
**\> `archive #<channel>`** - archives the user channel called `#<channel>` and sends a download link to all members. *Destructive!*
""", inline=False)
                embed.add_field(name="\u200b", value="""
**\> `add <user>` or `a <user>`** - adds `<user>` as a member of the user channel.
**\> `leave`** - leaves the user channel.
**\> `remove @<user>` or `r @<user>`** - removes `@<user>` as a member of the user channel.
**\> `transfer @<user>`** - transfers ownership of the user channel to `@<user>`. *Destructive!*
**\> `promote @<user>`** - promotes `@<user>` to an owner of the user channel. *Destructive!*
**\> `resign`** - resign as owner of the user channel. *Destructive!*
""", inline=False)
                embed.add_field(name="\u200b", value="""
__**Customising your user channel**__

Discord offers four `<attribute>`s you can change about your channel. *Note that these are heavily rate limited. Changing these too quickly can break your channel.*
`name`: The channel name.
`description`: The channel description.
`slowmode`: The channel slowmode delay. Set this value to `0` to disable slowmode.
`nsfw`: The channel NSFW status. *If you have not verified your age, changing this setting can break your channel! Be careful!*
**\> `change <attribute> to <value>` or `ch <attribute> <value>`** - changes the channel `<attribute>` to `<value>`.
Further `<attributes>` (cannot be changed using `change`):
`members`: The members in the user channel.
`owners`: The owners of the user channel.
`links`: The chain and the channels in the chain of the user channel.
**\> `show <attribute>` or `sh <attribute>`** - shows the current value of `<attribute>`.
""", inline=False)

            case "setup":
                embed.add_field(name="Setting up your own user channel", value=f"""User channels are (thankfully) pretty simple to set up.

First, create a user channel using the `create` command. We'll call our channel `bussin-dm`, so we type `j create bussin-dm`.
Next, switch to the channel, and start adding friends! To do this, we need to use `add` and the *username* of the friend (because you can't ping people if they can't see a channel). Let's say we want to invite <@679983361774714891>. Then, we type `j add "Jerome The Snowman#6097"`. (You can find a person's full username by clicking on their profile and selecting and copy and pasting it across.)
When you're done with a channel, use `delete` or `archive`! Remember to *ping the channel name*: if we wanted to delete this channel (for some reason) we want to type "j delete <#{ctx.channel.id}>", not "j delete #{ctx.channel.name}".

For information on the rest of the commands, type `j help user`.""", inline=False)

            case _:
                embed.add_field(name="Prefixes", value="`jerome, `, `j `\ne.g. **`jerome, search Attack on Titan`**", inline=False)
                embed.add_field(name="Commands", value="""\> **`help`** - shows this message.
For information on the other commands, type
\> **`help MAL`** for MyAnimeList searching
\> **`help user channels` or `help user`** for user channels.
For a tutorial on setting up your own user channel, type **`help setup`**""", inline=False)
                embed.add_field(name="Helpful stuff", value=f"""**Plainping**
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

@client.event
async def on_command_error(ctx, error):
    filename = RandomWords().random_word()
    error_msg = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    async with ctx.typing():
        with open(filename+".txt", "w") as data:
            data.write(error_msg)
            data.close
        with open(filename+".txt", "rb") as data:
            await ctx.send(embed=discord.Embed(
                title="Undefined error!",
                description="Something terribly wrong has happened! Please send <@458304698827669536> the text file above.", colour=0xff2727
                ).set_footer(text="YIKES_THATS_BAD"),
                file=discord.File(data, filename+".txt"))
        os.remove(filename+".txt")
    return


client.run(os.environ["token"])
