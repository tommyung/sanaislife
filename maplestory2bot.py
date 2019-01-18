import discord
import datetime
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
import os

os.environ["token"] = "NDQ0MjY5MzExOTM1MzgxNTI1.DdZd_g.r1Q3qZkNF6ai0fl_vEWfMoEqNBg"

raidDict = {}
client = discord.Client()
derogatoryList = ["whore", "nigger", "nigga", "chink", "nigguh", "niggar", "beaner"]

def raidList(raid, raidName):
    returnString = 'Raid Name: ' + raidName + ' ' + raid['time'] + ' lead by ' + raid['author'] + '\n'
    count = 1;
    for x in raid['attendees']:
        returnString += str(count) + '. ' + x + '\n'
        count += 1
    return returnString

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
        command = msgSplit[1].lower()
        raidName = msgSplit[2].lower()
        if 'Raid master' in [y.name for y in message.author.roles]:
            if command == 'create':
                #!raid create <raidName> <boss> <time>
                if msgSplit[2] in raidDict:
                    msg = 'A raid with the name ' + msgSplit[2] + ' already exists.'
                    await client.send_message(message.channel, msg)
                elif len(msgSplit) != 5:
                    msg = '${0.mention}, you have entered an invalid command. The raid commands it goes by the following\n\nTo create: !raid create <raid name> <boss> <time> Example: !raid create raid1 cdev 01/31-07:30PST\nTo join: !raid join <raid name> <class>'.format(message.author)
                    await client.send_message(message.channel, msg)
                else:
                    raidDict[raidName] = {}
                    raidDict[raidName]['author'] = str(message.author)
                    raidDict[raidName]['boss'] = str(msgSplit[3].lower())
                    raidDict[raidName]['time'] = str(msgSplit[4].lower())
                    raidDict[raidName]['attendees'] = []
                    msg = 'A new raid has been created \nName: ' + raidName
                    await client.send_message(message.channel, msg)
            elif command == 'join':
                #!raid join <raidName> <Class>
                if len(raidDict[raidName]['attendees']) != 10:
                    raidDict[raidName]['attendees'].append(str(message.author.nick) + ' ' + msgSplit[3])
                    msg = raidList(raidDict[raidName], raidName)
                    await client.send_message(message.channel, msg)
                else:
                    msg = 'That raid is full, contact ' + raidDict[raidName]['author'] + ' or another Raid master for any help.'
                    await client.send_message(message.channel, msg)
            elif command == 'remove':
                #!raid remove <raidName>
                raidDict.pop(msgSpilt[2].lower())
            elif command == 'clear':
                #!raid clear
                raidDict.clear()
            elif command == 'show':
                #!raid join <raidName>
                if msgSplit[2].lower() in raidDict:
                    msg = raidList(raidDict[raidName])
                    await client.send_message(message.channel, msg)
                else:
                    msg = msgSplit[2] + ' is not a scheduled raid.'
                    await client.send_message(message.channel, msg)
        else:
            if command == 'create':
                msg = '{0.mention} only those who has the role Raid master can create a listing for raids'.format(message.author)
                await client.send_message(message.channel, msg)
            elif command == 'join':
                #!raid join <raidName> <Class>
                if len(raidDict[raidName]['attendees']) != 10:
                    raidDict[raidName]['attendees'].append(str(message.author.nick) + ' ' + msgSplit[3])
                    msg = raidList(raidDict[raidName])
                    await client.send_message(message.channel, msg)
                else:
                    msg = 'That raid is full, contact ' + raidDict[raidname]['author'].mention + ' or another Raid master for any help.'
                #Maybe using another key to keep tabs on the amount of people that joined the raid and cannot exceed the number the user specified?
            elif command == 'show':
                #!raid join <raidName>
                if msgSplit[2].lower() in raidDict:
                    msg = raidList(raidDict[raidName])
                    await client.send_message(message.channel, msg)
                else:
                    msg = msgSplit[2] + ' is not a scheduled raid.'
                    await client.send_message(message.channel, msg)
            else:
                msg = '{0.mention}, you have entered an invalid command. The raid commands it goes by the following\n\nTo create: !raid create <raid name> <boss> <MM/DD-HH:mmPST> Example: !raid create raid1 cdev 01/31-07:30PST\nTo join: !raid join <raid name> <class>'.format(message.author)
                await client.send_message(message.channel, msg)
    for derogatoryTerms in derogatoryList:
        if derogatoryTerms in message.content:
            await client.delete_message(message)

@client.event
async def on_ready():
    print('Bot has started...')

tokenAddress = os.environ['token']
client.run(tokenAddress)
