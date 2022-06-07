import json
import re

async def refresh(client):
    with open("./config/config_test.json", "r") as data:
        config = data.read()
        config = json.loads(config)
        data.close()

    namebase = {"names": []}

    channel = client.get_channel(983803299209834566)
    messages = await channel.history(limit=5).flatten()
    for message in messages:
        text = message.clean_content
        matches = re.finditer(r"(?!.*\[left\])^~?~?@(.*?) is a?l?s?o? ?([A-Z'-][a-zA-Z'-]* [A-Z][a-zA-Z'-]*)?(?:([A-Z][a-zA-Z'-]*?)\?? )?([A-Z][a-zA-Z'-]*?\n)?", text, re.MULTILINE)
        for match in matches:
            names = []
            print(match)
            for groupNum in range(1, len(match.groups()) + 1):
                names.append(match.group(groupNum).rstrip("\n")) if match.group(groupNum) != None else False
            namebase["names"].append(names)

    with open("./config/namebase.json", "w") as data:
        data.write(json.dumps(namebase))
        data.close()
