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
    
    if message.content.startswith('!raid'):
        msgContent = message.content
        msgSplit = msgContent.split()
        #to be determined on how its formatted
        #!raid create yourName bossName time
        scope = ['http://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('Raiding form-b21d7c952538.json', scope)
        clientName = gspread.authorize(creds)
        sheet = clientName.open("Raiding form").sheet1
        if msgSplit[1].lower() == 'create':
             row = [msgSplit[2], msgSplit[3], msgSplit[4]]
             sheet.insert_row(row, 2)
             raidName = sheet.cell(2,2).value
             msgRaid = '{0.author.mention} has created a raid sign up for' + raidName
        
        else:
            msgRaid = '{0.author.mention}, you entered an invalid command. \nTo create a raid, type "!raid create IGN Boss Time\nTo view avaliable raids, type "!raid show"
        #elif msgSplit[1].lower() == 'list':
        #    for x in range(5):
        #        msgList = sheet.get_all_values()
        #        msgString = ''.join(msgList)
                #msgTmp = sheet.row_values(x)
                #msgList = msgList + "\n" + msgTmp
        #        msgRaid = '{0.author.mention} the list of raids: \n' + msgString
        msg = str(msgRaid).format(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Bot has started...')
    
tokenAddress = os.environ['token'] 
client.run(tokenAddress)
