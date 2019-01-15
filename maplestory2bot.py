import discord
import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
import os

raidDict = {}
client = discord.Client()
derogatoryList = ["whore", "nigger", "nigga", "chink", "nigguh", "niggar", "beaner"]

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, name='Interviewee')
    await client.add_roles(member,role)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!time'):
        msgTime = datetime.datetime.now().time()
        timeSplit = (str(msgTime).split(':'))
        combineTime = timeSplit[0] + ':' + timeSplit[1]
        resetHour = 23 - int(timeSplit[0])
        resetMinute = 60 - int(timeSplit[1])
        msgContent = '{0.author.mention} server time is ' + str(timeSplit[0]) + ':' + str(timeSplit[1]) + '\nServer reset in ' + str(resetHour) + ' hour(s) and ' + str(resetMinute) + ' minute(s)' 
        msg = str(msgContent).format(message)
        await client.send_message(message.channel, msg)
    if message.content.startswith('!quack'):
        msg = 'https://www.youtube.com/watch?v=QKq42dE6cvI'
        await client.send_message(message.channel, msg)
    if message.content.startswith('!raid'):
        msgContent = message.content
        msgSplit = msgContent.split()
        if msgSplit[1].lower() == 'create':
            #boss time
            raidDict[msgSplit[2].lower()] = message.author, msgSplit[3].lower(), msgSplit[4].lower()
            msg = '{0.author.mention} has created a new raid'
        elif msgSplit[1].lower() =='join':
            appendDict = str(raidDict[msgSplit[2].lower()]) + ' ' + message.author + msgSplit[3] + ', '
            raidDict[msgSplit[2].lower()] = appendDict
            
    for derogatoryTerms in derogatoryList:
        if derogatoryTerms in message.content:
            await client.delete_message(message)
    # we do not want the bot to reply to itself
#    if message.author == client.user:
#        return
#    if message.content.startswith('!raid'):
#        msgContent = message.content
#        msgSplit = msgContent.split()
        #to be determined on how its formatted
        #!raid create yourName bossName time
#        scope = ['http://spreadsheets.google.com/feeds',
#                'https://www.googleapis.com/auth/drive']
#        creds = ServiceAccountCredentials.from_json_keyfile_name('Raiding form-b21d7c952538.json', scope)
#        clientName = gspread.authorize(creds)
#        sheet = clientName.open("Raiding form").sheet1
#        if msgSplit[1].lower() == 'create':
#            row = [msgSplit[2], msgSplit[3], msgSplit[4]]
#            sheet.insert_row(row, 2)
#            raidName = sheet.cell(2,2).value
#            msgRaid = '{0.author.mention} has created a raid sign up for' + raidName
        
#        else:
#            msgRaid = '{0.author.mention}, you entered an invalid command. \nTo create a raid, type "!raid create [IGN] [Boss] [Time]"\ne.g. !raid create Sana Zakum 5:00PM_EST\n\nTo view avaliable raids, type "!raid show"'
        #elif msgSplit[1].lower() == 'list':
        #    for x in range(5):
        #        msgList = sheet.get_all_values()
        #        msgString = ''.join(msgList)
                #msgTmp = sheet.row_values(x)
                #msgList = msgList + "\n" + msgTmp
        #        msgRaid = '{0.author.mention} the list of raids: \n' + msgString
#        msg = str(msgRaid).format(message)
#        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Bot has started...')
    
tokenAddress = os.environ['token'] 
client.run(tokenAddress)
