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
        scope = ['http://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('Raiding form-b21d7c952538.json', scope)
        clientName = gspread.authorize(creds)
        sheet = clientName.open("Raiding form").sheet1
        raidName = sheet.cell(1,1).value
        msgRaid = '{0.author.mention} have created a raid sign up ' + raidName
        msg = str(msgRaid).format(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
tokenAddress = os.environ['token'] 
client.run(tokenAddress)
