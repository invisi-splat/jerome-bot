import discord
import json
import re

class NoMatch(Exception):
    def __init__(self, value, args=[]):
        self.value = value
        self.args = args
    pass

async def ping(client, msg):
    with open("./config/namebase.json", "r") as data:
        namebase = json.loads(data.read())
        data.close()

    matches = re.finditer(r"(?<!<)@((?:\w+ ?){1,3})", msg.content)
    hit_list = []
    for match in matches:
        for groupNum in range(1, len(match.groups()) + 1):
            search_names = match.group(groupNum).split(" ")
            try:
                name = await fulfil(search_names, namebase["names"])
                hit_list.append(name[0])
            except NoMatch as e:
                if e.value == "None found":
                    print(msg.author.name + " might have tried to ping someone with '@" + match.group(groupNum) + "'")
                elif e.value == "Duplicate":
                    names = ""
                    for i in e.args:
                        names += i[0][1] + " "
                    names.rstrip()
                    await msg.channel.send(embed=discord.Embed(title="Multiple matches", color=0xffffff).add_field(name="Your ping matched multiple names in the database:", value=names, inline=False))
                else:
                    await msg.channel.send(embed=discord.Embed(title="what the fuck did you do", description="you shouldn't be able to activate this message\nplease contact bowen immediately", color=0xff0000))
    if hit_list:
        pings = ""
        for target in hit_list:
            pings += "<@" + target[0][0] + "> "
        await msg.channel.send(pings)
        return True
    else:
        return False

async def fulfil(search_names, names):
    matched = [] # [["invisi.#0561", "Bowen"], 0]
    print("Attempting to match " + str(search_names) + "...")
    for i in range(len(names)):
        # pass 0: compare directly
        try:
            if search_names[0].lower() == names[i][1].lower():
                matched.append([names[i], 0])
                continue
            elif " ".join(search_names[:1]).lower() == names[i][1].lower():
                matched.append([names[i], 0])
                continue
            elif " ".join(search_names[:2]).lower() == names[i][1].lower():
                matched.append([names[i], 0])
                continue
        except IndexError:
            pass

        try:
            # pass 1: compare directly but reduce surnames on namebase to single letters
            if search_names[0].lower() == ((names[i][1].rsplit(" "))[0] + ((names[i][1].rsplit(" "))[1])[0]).lower():
                matched.append([names[i], 1])
                continue
            elif " ".join(search_names[:1]).lower() == ((names[i][1].rsplit(" "))[0] + ((names[i][1].rsplit(" "))[1])[0]).lower():
                matched.append([names[i], 1])
                continue
        except IndexError:
            pass

        try:
            # pass 2: compare directly but strip surnames off of namebase
            if search_names[0].lower() == (names[i][1].rsplit(" "))[0].lower():
                matched.append([names[i], 2])
                continue
            elif " ".join(search_names[:1]).lower() == (names[i][1].rsplit(" "))[0].lower():
                matched.append([names[i], 2])
                continue
        except IndexError:
            pass

        # pass 3: at this point the user's been very stupid and they probably can't spell (maya)

    if len(matched) > 1: # multiple possible names found
        raise NoMatch("Duplicate", matched)
    elif len(matched) == 0:
        raise NoMatch("None found")
    
    return matched
