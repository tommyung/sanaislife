import discord
import datetime
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
import os
import sys
from dbconnect import DatabaseConnection, Query
from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker

raidDict = {}
client = discord.Client()
derogatoryList = ["whore", "nigger", "nigga", "chink", "nigguh", "niggar", "beaner"]
tokenAddress = os.environ['token']
DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL)
db = DatabaseConnection(engine)
metadata = MetaData(bind=engine, reflect=True)
print("Set DB Connection...")
#tokenAddress = "MzE5MzgzNjQxMDYwODAyNTYw.XKgwvw.8RzGfkgA5QTlrR4ZJsLgX6tyBrM"

class Raid:
    def __init__(self, name, author, time, maxPpl):
        self.name = name
        self.author = author
        self.time = time
        self.maxPpl = maxPpl

    def get_column_dict(self):
        return {    
                    "name": self.name, 
                    "author": self.author, 
                    "time": self.time, 
                    "max_ppl": self.maxPpl
                }

class Attendee:
    def __init__(self, raidName, ign, ms_class):
        self.raidName = raidName
        self.ign = ign
        self.ms_class = ms_class

    def get_column_dict(self):
        return {    
                    "ign": self.ign, 
                    "ms_class": self.ms_class,
                    "raid_name": self.raidName
                }

def raidList(raid, raidName):
    returnString = '```Raid Name: ' + raidName + ' ' + raid['time'] + ' lead by ' + raid['author'] + '\n'
    count = 1;
    for x in raid['attendees']:
        returnString += str(count) + '. ' + x + '\n'
        count += 1
    returnString += '```'
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


    if message.content.startswith('!raid') and str(message.channel) == 'raid-schedules':
        msgContent = message.content
        msgSplit = msgContent.split()
        command = msgSplit[1].lower()
        raidName = msgSplit[2].lower() if len(msgSplit) >= 3 else ''
        session = db.create_session()
        sessionQuery = Query(session, metadata)
        try:
            if 'Raid master' in [y.name for y in message.author.roles]:
                if command == 'create':
                    #!raid create <raidName> <time>
                    if msgSplit[2] in raidDict:
                        msg = 'A raid with the name ' + msgSplit[2] + ' already exists.'
                        await client.send_message(message.channel, msg)
                    elif len(msgSplit) not in [4, 5]:
                        msg = '${0.mention}, you have entered an invalid command. The raid commands it goes by the following\n\nTo create: !raid create <raid name> <time> Example: !raid create raid1 cdev 01/31-07:30PST\nTo join: !raid join <raid name> <class>'.format(message.author)
                        await client.send_message(message.channel, msg)
                    else:
                        author = str(message.author)
                        time = str(msgSplit[3].lower())
                        maxPpl = str(msgSplit[4].lower()) if len(msgSplit) > 4 else 10
                        raid = Raid(raidName, author, time, maxPpl)
                        sessionQuery.insert_raid(raid.get_column_dict())
                        '''
                        raidDict[raidName] = {}
                        raidDict[raidName]['author'] = str(message.author)
                        raidDict[raidName]['time'] = str(msgSplit[3].lower())
                        raidDict[raidName]['attendees'] = []
                        '''
                        msg = 'A new raid has been created named: ' + raidName
                        await client.send_message(message.channel, msg)
                elif command == 'join':
                    #!raid join <raidName> <Class>
                    # attendeeList = sessionQuery.select_attendees_by_raid(raidName)
                    if len(msgSplit) == 4:
                        # change if statement to check against return of attendeeList
                        if any(str(message.author.nick) in element for element in raidDict[raidName]['attendees']) or any(str(message.author) in element for element in raidDict[raidName]['attendees']):
                            msg = 'You have already signed up for that raid. If this is a mistake, contact ' + raidDict[raidName]['author'] + ' or another Raid master for any help.'
                            await client.send_message(message.channel, msg)
                        else:
                            # raidDetails = sessionQuery.select_raid_by_name(raidName)
                            
                            # if (len(attendeeList) >  raidDetails[""])
                            if len(raidDict[raidName]['attendees']) != 10:
                                attendee = message.author.nick if message.author.nick != 'None' else message.author
                                raidDict[raidName]['attendees'].append(str(attendee) + ' ' + msgSplit[3])
                                msg = raidList(raidDict[raidName], raidName)
                                await client.send_message(message.channel, msg)
                            else:
                                msg = 'That raid is full, contact ' + raidDict[raidName]['author'] + ' or another Raid master for any help.'
                                await client.send_message(message.channel, msg)
                    else:
                        msg = 'To join a raid, use the following command: !raid join <raidName> <class> \n If your class has more than one word, please abbreviate or make it one word. '
                        await client.send_message(message.channel, msg)
                elif command == 'add':
                    #!raid add <raidName> <user> <class>
                    user = msgSplit[3]
                    if len(msgSplit) == 5:
                        if any(str(user) in element for element in raidDict[raidName]['attendees']):
                            msg = 'A user by that name has already been added to ' + str(raidName)
                            await client.send_message(message.channel, msg)
                        else:
                            if len(raidDict[raidName]['attendees']) != 10:
                                raidDict[raidName]['attendees'].append(str(user) + ' ' + msgSplit[4])
                                msg = raidList(raidDict[raidName], raidName)
                                await client.send_message(message.channel, msg)
                            else:
                                msg = 'That raid is full.'
                                await client.send_message(message.channel, msg)
                    else:
                        msg = 'To manually add someone to a raid list use the following command: #!raid add <user> <raidName> <class> \n Example: !raid add Potato Horntail HeavyGunner'
                        await client.send_message(message.channel, msg)
                elif command == 'remove':
                    #!raid remove <raidName>
                    raidDict.pop(msgSplit[2].lower())
                elif command == 'list':
                    #!raid list
                    msg = '```Scheduled Raids:\n'
                    for x in raidDict.keys():
                        msg += str(x) + ' ' + raidDict[x]['time'] +'\n'
                    msg += '```'
                    await client.send_message(message.channel, msg)
                elif command == 'show':
                    #!raid join <raidName>
                    if raidName.lower() in raidDict:
                        msg = raidList(raidDict[raidName], raidName)
                        await client.send_message(message.channel, msg)
                    else:
                        msg = raidName + ' is not a scheduled raid.'
                        await client.send_message(message.channel, msg)
                elif command == 'help':
                    #!raid help
                    msg = 'Commands: \n !raid join <raidName> <class> - Join a raid specifying class. \n !raid show <raidName> - Shows the details of the specified raid. \n !raid list - Lists all the scheduled raids.'
                    await client.send_message(message.channel, msg)
                else:
                    msg = '{0.mention}, you have entered an invalid command. The raid commands it goes by the following\n\nTo create: !raid create <raid name> <MM/DD-HH:mmPST> Example: !raid create raid1 cdev 01/31-07:30PST\nTo join: !raid join <raid name> <class>'.format(message.author)
                    await client.send_message(message.channel, msg)
            else:
                if command == 'create':
                    msg = '{0.mention} only those who has the role Raid master can create a listing for raids'.format(message.author)
                    await client.send_message(message.channel, msg)
                elif command == 'join':
                    #!raid join <raidName> <Class>
                    if len(msgSplit) == 4:
                        if any(str(message.author.nick) in element for element in raidDict[raidName]['attendees']):
                            msg = 'You have already signed up for that raid. If this is a mistake, contact ' + raidDict[raidName]['author'] + ' or another Raid master for any help.'
                            await client.send_message(message.channel, msg)
                        else:
                            if len(raidDict[raidName]['attendees']) != 10:
                                attendee = message.author.nick if message.author.nick != 'None' else message.author
                                raidDict[raidName]['attendees'].append(str(attendee) + ' ' + msgSplit[3])
                                msg = raidList(raidDict[raidName], raidName)
                                await client.send_message(message.channel, msg)
                            else:
                                msg = 'That raid is full, contact ' + raidDict[raidName]['author'] + ' or another Raid master for any help.'
                                await client.send_message(message.channel, msg)
                    else:
                        msg = 'To join a raid, use the following command: !raid join <raidName> <class> \n If your class has more than one word, please abbreviate or make it one word. '
                        await client.send_message(message.channel, msg)
                    #Maybe using another key to keep tabs on the amount of people that joined the raid and cannot exceed the number the user specified?
                elif command == 'show':
                    #!raid join <raidName>
                    if msgSplit[2].lower() in raidDict:
                        msg = raidList(raidDict[raidName])
                        await client.send_message(message.channel, msg)
                    else:
                        msg = msgSplit[2] + ' is not a scheduled raid.'
                        await client.send_message(message.channel, msg)
                elif command == 'list':
                    #!raid list
                    msg = '```Scheduled Raids:\n'
                    for x in raidDict.keys():
                        msg += str(x) + ' ' + raidDict[x]['time'] +'\n'
                    msg += '```'
                    await client.send_message(message.channel, msg)
                elif command == 'help':
                    #!raid help
                    msg = 'Commands: \n !raid join <raidName> <class> - Join a raid specifying class. \n !raid show <raidName> - Shows the details of the specified raid. \n !raid list - Lists all the scheduled raids.'
                    await client.send_message(message.channel, msg)
                else:
                    msg = '{0.mention}, you have entered an invalid command. The raid commands it goes by the following\n\nTo create: !raid create <raid name> <MM/DD-HH:mmPST> Example: !raid create raid1 cdev 01/31-07:30PST\nTo join: !raid join <raid name> <class>'.format(message.author)
                    await client.send_message(message.channel, msg)
            session.commit()
        except:
            msg = sys.exc_info()[0]
            await client.send_message(message.channel, msg)
            session.rollback()
        finally:
            try:
                session.close()
            except:
                # No session to close
                pass

    for derogatoryTerms in derogatoryList:
        if derogatoryTerms in str(message.content).lower():
            await client.delete_message(message)

@client.event
async def on_ready():
    print('Bot has started...')


client.run(tokenAddress)

