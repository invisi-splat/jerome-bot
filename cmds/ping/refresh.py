import json
import re

async def refresh(client):
    print("Refreshing namebase...")
    with open("./config/config.json", "r") as data:
        config = data.read()
        config = json.loads(config)
        data.close()

    namebase = {"names": []}
    dupe_check = []

    channel = client.get_channel(config["whoswho"])
    messages = await channel.history(limit=5).flatten()
    for message in reversed(messages):
        text = message.content
        matches = re.finditer(r"(?!.*\[left\])^~?~?<@!?(\d*?)> is a?l?s?o? ?([A-Z'-][a-zA-Z'-]* [A-Z][a-zA-Z'-]*)?(?:([A-Z][a-zA-Z'-]*?)\?? )?([A-Z][a-zA-Z'-]*?\n)?", text, re.MULTILINE)
        for match in matches:
            names = []
            for groupNum in range(1, len(match.groups()) + 1):
                names.append(match.group(groupNum).rstrip("\n")) if match.group(groupNum) != None else False
            if [names[1:]] in dupe_check:
                pass
            else:
                dupe_check.append([names[1:]])
                namebase["names"].append(names)

    with open("./config/namebase.json", "w") as data:
        data.write(json.dumps(namebase))
        data.close()
    
    print("Refreshed namebase.")
    return True