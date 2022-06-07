import requests
import sys
import json
import discord
from discord.ext import commands, tasks
import asyncio
import traceback
import secrets

CLIENT_ID = '1f8715ac1db9caf0d35c43809d9e02fa'
CLIENT_SECRET = '20c6696977545ee3e18baaabf0be11ebdb5406d2197561ccac413a91b67b713c'
TOKEN = {}

statusify = {"watching": "Watching", "completed": "Completed", "on_hold": "On Hold", "dropped": "Dropped", "plan_to_watch": "Plan to Watch"}

client = commands.Bot(command_prefix=["jerome, ", "j "], case_insensitive=True)

@tasks.loop(seconds=3600)
async def refresh():
    global TOKEN
    with open("./token.json", "r") as data:
        token = json.loads(data.read())
        data.close()

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': token["refresh_token"],
        'grant_type': 'refresh_token'
    }

    response = requests.post(url, data)
    response.raise_for_status()  # Check whether the requests contains errors

    token = response.json()
    TOKEN = token
    response.close()
    print('Token generated successfully!')

    with open('./token.json', 'w') as file:
        json.dump(token, file, indent = 4)
        print('Token saved in "token.json"')

    print(token)
    print("Sleeping for an hour...")

with open("./config.json", "r") as data:
    config = json.loads(data.read())
    data.close()

client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='over the server | Type "jerome, help"'))
    print('We have logged in as {0.user}'.format(client))

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
    await ctx.send(embed=embed)

async def error_message(ctx):
    embed=discord.Embed(title="Error", description="That query was either not found on MAL, or my code sucks. Might want to look into it if this error message is unexpected.", color=0xf06a85)
    await ctx.send(embed=embed)

@client.command(aliases=["s"])
async def search(ctx, *, arg):
    token = TOKEN
    print("Recieved command search: " + arg)
    try:
        if not arg.isdigit():
            response = requests.get(f'https://api.myanimelist.net/v2/anime?q={arg}&limit=10', headers={"Authorization": f"Bearer {token['access_token']}"})
            possibleresults = response.json()
            id = str(possibleresults["data"][0]["node"]["id"])
        else:
            possibleresults = None
            id = arg
    except:
        print(traceback.format_exc())
        await error_message(ctx)
        return

    await performsearch(ctx, arg, possibleresults, id, token)

@client.command(aliases=["sid", "si"])
async def searchid(ctx, *, arg):
    token = TOKEN
    print("Recieved command searchid: " + arg)
    possibleresults = None
    id = arg

    await performsearch(ctx, arg, possibleresults, id, token)

@client.command(aliases=["sname", "sn"])
async def searchname(ctx, *, arg):
    token = TOKEN
    print("Recieved command searchname: " + arg)
    if len(arg) < 4:
        arg = arg.ljust(4, "e")

    try:
        response = requests.get(f'https://api.myanimelist.net/v2/anime?q={arg}&limit=10', headers={"Authorization": f"Bearer {token['access_token']}"})
        possibleresults = response.json()
        id = str(possibleresults["data"][0]["node"]["id"])
    except:
        print(traceback.format_exc())
        await error_message(ctx)
        return

    await performsearch(ctx, arg, possibleresults, id, token)

async def performsearch(ctx, arg, possibleresults, id, token):
    response = requests.get(f'https://api.myanimelist.net/v2/anime/{id}?fields=id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics', headers={"Authorization": f"Bearer {token['access_token']}"})
    results = response.json()

    try:
        genres = ""
        for i in results["genres"]:
            genres += i["name"] +  ", "
        genres = genres[:-2]
        synopsis = (results["synopsis"][:1021] + '...') if len(results["synopsis"]) > 1024 else results["synopsis"]
        ymhm = ""
        if possibleresults:
            for i in possibleresults["data"]:
                ymhm += "[" + i["node"]["title"] + "](https://myanimelist.net/anime/" + str(i["node"]["id"]) + ") `" + str(i["node"]["id"]) + "`\n"
        recommendations = ""
        print(results['recommendations'])
        for i in results['recommendations']:
            recommendations += "[" + i["node"]["title"] + "](https://myanimelist.net/anime/" + str(i["node"]["id"]) + ") `" + str(i["node"]["id"]) + "`\n"


        embed=discord.Embed(title=results["title"] + f" `{id}`", url="https://myanimelist.net/anime/"+str(results["id"]), description=f"{results['mean']}/10, {results['num_episodes']} episodes, {results['start_season']['season'].capitalize()} {results['start_season']['year']}\n{genres}", color=0x59278b)
        embed.set_thumbnail(url=results["main_picture"]["medium"])
        embed.add_field(name="Synopsis", value=synopsis, inline=False)
        if possibleresults:
            embed.add_field(name="You might have meant...", value=ymhm, inline=True)
        if recommendations:
            embed.add_field(name="Recommendations", value=recommendations, inline=True)
        embed.set_footer(text=f"Ranked #{results['rank']}, Popularity #{results['popularity']}\n")
        await ctx.send(embed=embed)
    except KeyError as Exception:
        print(traceback.format_exc())
        await error_message(ctx)

@client.command(aliases=["l"])
async def list(ctx, name=""):
    if name == "":
        embed=discord.Embed(title="Please send a username!", color=0xf06a85)
        await ctx.send(embed=embed)
        return
    try:
        token = TOKEN
        print("Recieved command list: " + name)

        response = requests.get(f'https://api.myanimelist.net/v2/users/{name}/animelist?fields=list_status&limit=10&sort=list_score', headers={"Authorization": f"Bearer {token['access_token']}"})
        results = response.json()
        top_shows = ""
        id = results["data"][0]["node"]["id"]
        response = requests.get(f'https://api.myanimelist.net/v2/anime/{id}?fields=id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics', headers={"Authorization": f"Bearer {token['access_token']}"})
        topshowresults = response.json()
        top_shows += f'**[{topshowresults["title"]}](https://myanimelist.net/anime/{id}) `{id}` {results["data"][0]["list_status"]["score"]}☆\n**{(topshowresults["synopsis"][:297] + "...") if len(topshowresults["synopsis"]) > 300 else topshowresults["synopsis"]}\n'

        for i in results["data"][1:]:
            entry = "**[" + i["node"]["title"] + "](https://myanimelist.net/anime/" + str(i["node"]["id"]) + ") `" + str(i["node"]["id"]) + "` " + str(i["list_status"]["score"]) + "☆**\n"
            if len(entry) + len(top_shows) < 1024:
                top_shows += entry
            else:
                break

        response = requests.get(f'https://api.myanimelist.net/v2/users/{name}/animelist?fields=list_status&limit=10&sort=list_updated_at', headers={"Authorization": f"Bearer {token['access_token']}"})
        results = response.json()
        recent_shows = ""
        id = results["data"][0]["node"]["id"]
        response = requests.get(f'https://api.myanimelist.net/v2/anime/{id}?fields=id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics', headers={"Authorization": f"Bearer {token['access_token']}"})
        topshowresults = response.json()
        recent_shows += f'**[{topshowresults["title"]}](https://myanimelist.net/anime/{id}) `{id}` {results["data"][0]["list_status"]["score"]}☆ - {statusify[results["data"][0]["list_status"]["status"]]}\n**{(topshowresults["synopsis"][:297] + "...") if len(topshowresults["synopsis"]) > 300 else topshowresults["synopsis"]}\n'

        for i in results["data"][1:]:
            entry = "**[" + i["node"]["title"] + "](https://myanimelist.net/anime/" + str(i["node"]["id"]) + ") `" + str(i["node"]["id"]) + "` " + str(i["list_status"]["score"]) + "☆ - " + statusify[i["list_status"]["status"]] + "**\n"
            if len(entry) + len(recent_shows) < 1024:
                recent_shows += entry
            else:
                break

        embed=discord.Embed(title=name + "'s list", url="https://myanimelist.net/animelist/" + name, color=0xf0d36a)
        embed.add_field(name="Top Shows", value=top_shows, inline=True)
        embed.add_field(name="Most Recent Updates", value=recent_shows, inline=True)
        embed.set_footer(text="sorry i would try to get stats for the list but the MAL API documentation is so shit there's no way to tell how to do it")
        await ctx.send(embed=embed)
    except:
        print(traceback.format_exc())
        await error_message(ctx)
        return

refresh.start()
client.run(config["token"])
