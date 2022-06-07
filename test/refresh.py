import json
import requests
import secrets


CLIENT_ID = '1f8715ac1db9caf0d35c43809d9e02fa'
CLIENT_SECRET = '20c6696977545ee3e18baaabf0be11ebdb5406d2197561ccac413a91b67b713c'

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
response.close()
print('Token generated successfully!')

with open('token.json', 'w') as file:
    json.dump(token, file, indent = 4)
    print('Token saved in "token.json"')

print(token)
