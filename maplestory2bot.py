import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

client = discord.Client()
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        list_of_hashes = sheet.get_all_records()
        msg = 'Hello {0.author.mention}'.format(message)
        msg = (list_of_hashes)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
tokenAddress = os.environ['token'] 
client.run(tokenAddress)

scope = ['http://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_key_name('Raiding form-b21d7c952538', scope)
client = gspread.authorize(creds)
sheet = client.open("Raiding form").sheet1
