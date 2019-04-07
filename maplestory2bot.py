import discord
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
import os, sys, traceback, datetime
from dbconnect import DatabaseConnection, Raid, Attendee
from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

raidDict = {}
client = discord.Client()
derogatoryList = ["whore", "nigger", "nigga", "chink", "nigguh", "niggar", "beaner"]
tokenAddress = os.environ['token']
DATABASE_URL = os.environ['DATABASE_URL']
Base = declarative_base()
engine = create_engine(DATABASE_URL)
db = DatabaseConnection(engine)
print("Set DB Connection...")


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
        try:
            if command == 'create':
                allRaids = session.query(Raid).all()
                raidNameList = [raid.raid_name for raid in allRaids]
                if msgSplit[2] in raidNameList:
                    msg = 'A raid with the name ' + msgSplit[2] + ' already exists.'
                    await client.send_message(message.channel, msg)
                elif len(msgSplit) not in [4, 5]:
                    msg = '${0.mention}, you have entered an invalid command. The raid commands it goes by the following\n\nTo create: !raid create <raid name> <time> Example: !raid create raid1 cdev 01/31-07:30PST\nTo join: !raid join <raid name> <class>'.format(message.author)
                    await client.send_message(message.channel, msg)
                else:
                    author = str(message.author)
                    time = str(msgSplit[3].lower())
                    maxPpl = msgSplit[4].lower()
                    if (len(msgSplit) == 5):
                        # Included parameter for max_ppl - overwrite default
                        session.add(Raid(raid_name=raidName, author=author, time=time, max_ppl=maxPpl))
                    else: 
                        session.add(Raid(raid_name=raidName, author=author, time=time))
                        
                        '''
                        raidDict[raidName] = {}
                        raidDict[raidName]['author'] = str(message.author)
                        raidDict[raidName]['time'] = str(msgSplit[3].lower())
                        raidDict[raidName]['attendees'] = []
                        '''
                    msg = 'A new raid has been created named: ' + raidName
                    await client.send_message(message.channel, msg)

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

