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
        if 'Raid master' in author.roles:
            if msgSplit[1].lower() == 'create':
                #!raid create <raidName> <boss> <time>
                raidDict[msgSplit[2].lower()] = message.author, msgSplit[3].lower(), msgSplit[4].lower()
                msg = '@🌸 A new raid has been created \nName: ' + msgSplit[2]
                await client.send_message(message.channel, msg)
            elif msgSplit[1].lower() == 'remove':
                #!raid remove <raidName>
                raidDict.pop(msgSpilt[2].lower())
            elif msgSplit[1].lower() == 'clear':
                #!raid clear
                riadDict.clear()
        else:
            if msgSplit[1].lower() == 'create':
                msg = '{0.author.mention} only those who has the role Raid master can create a listing for raids'
                await client.send_message(message.channel, msg)
            elif msgSplit[1].lower() =='join':
                #!raid join <raidName> <Class>
                appendDict = str(raidDict[msgSplit[2].lower()]) + ' ' + message.author + msgSplit[3] + ', '
                raidDict[msgSplit[2].lower()] = appendDict
    else:
        msg = '{0.author.mention, you have entered an invalid command. The raid commands it goes by the following\n\nTo create: !raid create <raid name> <boss> <time>\nTo join: !raid join <raid name> <class>'
        await client.send_message(message.channel, msg)
    for derogatoryTerms in derogatoryList:
        if derogatoryTerms in message.content:
            await client.delete_message(message)

@client.event
async def on_ready():
    print('Bot has started...')
    
tokenAddress = os.environ['token'] 
client.run(tokenAddress)
