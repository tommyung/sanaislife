import discord
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
import os, sys, traceback, datetime, re
from datetime import timedelta
from dbconnect import DatabaseConnection, Raid, Attendee
from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2

raidDict = {}
client = discord.Client()
derogatoryList = ["whore", "nigger", "nigga", "chink", "nigguh", "niggar", "beaner"]
tokenAddress = os.environ['token']
DATABASE_URL = os.environ['DATABASE_URL']
Base = declarative_base()
engine = create_engine(DATABASE_URL)
db = DatabaseConnection(engine)
print("Set DB Connection...")


def displayRaid(raid):
    returnString = '```md\n'
    returnString += raid.raid_name + '\n<' + raid.day + ' ' + raid.date + ' @ ' + raid.time + '>\n'
    count = 1
    for attendeee in raid.attendees:
        returnString += str(count) + '. ' + attendee.ign + '\n'
        count += 1
    remainingSpots = raid.max_ppl - raid.attendees_count
    if remainingSpots > 0:
        while (count <= raid.max_ppl):
            returnString += str(count) + '. \n'
            count += 1
    returnString += '```'
    return returnString

def convertToArgDict(argumentList):
    argDict = {}
    for argStr in argumentList:
        argSplit = argStr.split("=")
        key = argSplit[0]
        # Stripping quotes out of string arguments
        val = argSplit[1][1:-1] if argSplit[1].startswith('"') and argSplit[1].endswith('"') else argSplit[1]
        try:
            # Converting numeric Strings to int
            val = int(val)
        except ValueError:
            pass
        argDict[key] = val
    return argDict

def mapArgToCol(argDict, mappingDict):
    mappedArgDict = {}
    for key, value in argDict.items():
        if (key in mappingDict.keys()):
            mappedKey = mappingDict[key]
            mappedArgDict[mappedKey] = value
        else:
            mappedArgDict[key] = value
    return mappedArgDict


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
        # Example Content: '!raid create --raidname="7 man cdev" --day="Saturday" --date="April 6" --time="7 PM" --max_ppl=10'
        # Example Split: ['!raid create', 'raidname="7 man cdev"', 'day="Saturday"', 'date="April 6"', 'time="7 PM"', 'max_ppl=10']
        msgContent = message.content
        msgSplit = msgContent.split(" --")
        commandRe = re.compile("!raid (.+)")
        command = commandRe.match(msgSplit[0]).group(1)
        argumentList = msgSplit[1:]
        argDict = convertToArgDict(argumentList)
        print(msgContent)
        print("Command: ", command)
        print("Argument List: ", argumentList)
        print("Argument Dictionary: ", argDict)
        session = db.create_session()
        try:
            if command == 'create':
                # !raid create --raidname="7 man cdev" --day="Saturday" --date="April 6" --time="7 PM" --max_ppl=10
                acceptableArgs = ["raidname", "day", "date", "time", "max_ppl"]
                allRaids = session.query(Raid).all()
                raidNameList = [raid.raid_name for raid in allRaids]
                print (raidNameList)
                if len(argumentList) not in [4, 5] or any([key not in acceptableArgs for key in argDict.keys()]):
                    # Invalid arguments
                    msg = ('${0.mention}, you have entered an invalid command. To create a raid, follow this format:' +
                            '\n !raid create --raidname="7 man cdev" --day="Saturday" --date="April 6" --time="7 PM" --max_ppl=7' +
                            '\n The "--max_ppl" is optional and can be left off to default to 10.')
                    await client.send_message(message.channel, msg)
                elif argDict["raidname"] in raidNameList:
                    # Raid name already exists
                    msg = 'A raid with the name ' + argDict["raidname"] + ' already exists.'
                    await client.send_message(message.channel, msg)
                elif len(argumentList) == 5 and (argDict["max_ppl"] > 10 or argDict["max_ppl"] < 4):
                    # Invalid max_ppl ( 4 <= max_ppl <= 10)
                    msg = "Sorry. You can't create a raids with more than 10 or less than 4 members."
                    await client.send_message(message.channel, msg)
                else:
                    # Creating the raid
                    try:
                        if (len(argumentList) == 5):
                            # Included parameter for max_ppl - overwrite default of 10
                            raid = Raid(raid_name=argDict["raidname"], day=argDict["day"], date=argDict["date"], time=argDict["time"], max_ppl=argDict["max_ppl"], created_by=str(message.author))
                            session.add(raid)
                        else: 
                            raid = Raid(raid_name=argDict["raidname"], day=argDict["day"], date=argDict["date"], time=argDict["time"], created_by=str(message.author))
                            session.add(raid)
                    except:
                        print(traceback.format_exc())
                        msg = "Couldn't save to the database... Ionno what to say."
                        await client.send_message(message.channel, msg)
                    else:
                        msg = "Raid '" + argDict["raidname"] + "' was created:\n"
                        msg += displayRaid(raid)
                        await client.send_message(message.channel, msg)

            elif command == "updateRaid":
                # !raid updateRaid --oldRaidname="7 man cdev" --raidname="4 man cdev" --day="Sunday" --date="April 7" --time="8 PM" --max_ppl=4
                acceptableArgs = ["oldRaidname", "raidname", "day", "date", "time", "max_ppl"] 
                if (len(argumentList) < 1) or ("oldRaidname" not in argDict.keys()) or (any([key not in acceptableArgs for key in argDict.keys()])):
                    # Invalid arguments
                    msg = ('${0.mention}, you have entered an invalid command. To update a raid, follow this format:' +
                            '\n !raid updateRaid --oldRaidname="7 man cdev" --raidname="4 man cdev" --day="Sunday" --date="April 7" --time="8 PM" --max_ppl=4' +
                            "\n oldRaidname and one other option is required. If you leave out an optional value, it'll stay the same as the old value.")
                    await client.send_message(message.channel, msg)
                else:
                    # For parameter to column mapping
                    colMapping = {"raidname" : "raid_name"}
                    remappedArgDict = mapArgToCol(argDict, colMapping)
                    # Updating the values that were listed
                    oldRaidname = remappedArgDict.pop("oldRaidname")
                    session.query(Raid).filter_by(raid_name=oldRaidname).update(remappedArgDict, synchronize_session="fetch")

            elif command == 'delete':
                # !raid delete --raidname="7 man cdev"
                acceptableArgs = ["raidname"]
                if len(argumentList) != 1 or any([key not in acceptableArgs for key in argDict.keys()]):
                    # Invalid arguments
                    msg = ('${0.mention}, you have entered an invalid command. To delete a raid, follow this format:' +
                            '\n !raid delete --raidname="7 man cdev"')
                    await client.send_message(message.channel, msg)
                else:
                    try:
                        raidDetails = session.query(Raid).filter_by(raid_name=argDict["raidname"]).one()
                    except NoResultFound:
                        print(traceback.format_exc())
                        msg = "I couldn't find your raid. Ionno what to say."
                        await client.send_message(message.channel, msg)
                    else:
                        if str(message.author) != raidDetails.created_by:
                            # Unauthorized delete. The person trying to delete the raid is not the same as the person who created it
                            msg = "Oooo. " +  raidDetails.created_by + " isn't going to like that you're trying to delete their raid... COT"
                            await client.send_message(message.channel, msg)
                        else:
                            # Deleting the raid -  this wil also delete the associated attendees
                            session.query(Raid).filter_by(raid_name=argDict["raidname"]).delete()
                            msg = "Deleted the raid: " + argDict["raidname"]
                            await client.send_message(message.channel, msg)

            elif command == "help":
                # !raid help
                await client.send_message(message.channel, raidHelpStr1)
                await client.send_message(message.channel, raidHelpStr2)
                await client.send_message(message.channel, raidHelpStr3)

            else:
                msg = "We aren't speaking the same language. Please use '!raid help' for a list of commands and format."
                await client.send_message(message.channel, msg)
        except:
            print(traceback.format_exc())
            msg = sys.exc_info()[0]
            await client.send_message(message.channel, msg)
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()

    if message.content.startswith('!raid') and (str(message.channel) == 'clear-runs' or str(message.channel) == 'practice-runs'):
        # Example Content: !raid join --raidname="7 man cdev" --ign="Zukoori" --class="runeblader"
        # Example Split: ['!raid join', 'raidname="7 man cdev"', 'ign="Zukoori"', 'class="runeblader"']
        msgContent = message.content
        msgSplit = msgContent.split(" --")
        commandRe = re.compile("!raid (.+)")
        command = commandRe.match(msgSplit[0]).group(1)
        argumentList = msgSplit[1:]
        argDict = convertToArgDict(argumentList)
        print(argDict)
        session = db.create_session()
        try:
            if command == "join":
                # !raid join --raidname="7 man cdev" --ign="Zukoori" --class="runeblader"
                acceptableArgs = ["raidname", "ign", "class"]
                if len(argumentList) != 3 or any([key not in acceptableArgs for key in argDict.keys()]):
                    # Invalid arguments
                    msg = ('${0.mention}, you have entered an invalid command. To join a raid, follow this format:' +
                            '\n !raid join --raidname="7 man cdev" --ign="Zukoori" --class="runeblader"')
                    await client.send_message(message.channel, msg)
                else:
                    try:
                        raidDetails = session.query(Raid).filter_by(raid_name=argDict["raidname"]).one()
                    except NoResultFound:
                        print(traceback.format_exc())
                        msg = "Couldn't find that raid. Tiff, check your typos."
                        await client.send_message(message.channel, msg)   
                    else:
                        attendeesList = [attendee.ign.lower() for attendee in raidDetails.attendees]
                        if (argDict["ign"].lower() in attendeesList):
                            # Attendee already listed
                            msg = "[Tiff Voice] Hello?? " + argDict["ign"] + " is already signed up for the raid."
                            await client.send_message(message.channel, msg)
                        elif raidDetails.attendees_count >= raidDetails.max_ppl:
                            # Number of attendees is more than allowed
                            msg = "The raid is full. The max number of attendees set was " +  raidDetails.max_ppl + "."
                            await client.send_message(message.channel, msg)
                        else:
                            # Adding attendee
                            session.add(Attendee(raid_name=argDict["raidname"], ign=argDict["ign"], ms_class=argDict["class"], added_by=str(message.author)))
                            msg = "Added you to the raid: " + argDict["raidname"]
                            await client.send_message(message.channel, msg)

            elif command == "updatePerson":
                #!raid updatePerson --raidname="7 man cdev" --oldIgn="Liatris" --ign="Calendula" --class="calendar"
                acceptableArgs = ["raidname", "oldIgn", "ign", "class"]
                if (len(argumentList) < 1) or ("oldRaidname" not in argDict.keys()) or (any([key not in acceptableArgs for key in argDict.keys()])):
                    # Invalid arguments
                    msg = ('${0.mention}, you have entered an invalid command. To update a raid, follow this format:' +
                            '\n !raid updateRaid --oldRaidname="7 man cdev" --raidname="4 man cdev" --day="Sunday" --date="April 7" --time="8 PM" --max_ppl=4' +
                            "\n oldRaidname and one other option is required. If you leave out an optional value, it'll stay the same as the old value.")
                    await client.send_message(message.channel, msg)
                else:
                    # For parameter to column mapping
                    colMapping = {      "raidname" : "raid_name",
                                        "class" : "ms_class"        }
                    remappedArgDict = mapArgToCol(argDict, colMapping)
                    # Updating the values that were listed
                    oldIgn = remappedArgDict.pop("oldIgn")
                    session.query(Attendee).filter_by(ign=oldIgn).update(remappedArgDict, synchronize_session="fetch")
                                        
            elif command == "byebye":
                # !raid byebye --raidname="7 man cdev" --ign="Zukoori"
                acceptableArgs = ["raidname", "ign"]
                if 'Raid master' not in [y.name for y in message.author.roles]:
                    msg = "New phone... who dis? You can only remove an attendee if you're a raid master... and you aren't... spits."
                    await client.send_message(message.channel, msg)
                elif len(argumentList) != 2  or any([key not in acceptableArgs for key in argDict.keys()]):
                    # Invalid arguments
                    msg = ('${0.mention}, you have entered an invalid command. To remove a person from the raid, follow this format:' +
                            '\n !raid byebye --raidname="7 man cdev" --ign="Zukoori"')
                    await client.send_message(message.channel, msg)
                else:
                    # Removing the attendee from the raid
                    session.query(Attendee).filter_by(raid_name=argDict["raidname"], ign=argDict["ign"]).delete()
                    msg = "Bye bye " + argDict["ign"] + ". You've been removed from the raid: " + argDict["raidname"]
                    await client.send_message(message.channel, msg)

            elif command == "show":
                # !raid show --raidname="cdev 7 man"
                acceptableArgs = ["raidname"]
                if len(argumentList) != 1 or any([key not in acceptableArgs for key in argDict.keys()]):
                    # Invalid arguments
                    msg = ('${0.mention}, you have entered an invalid command. To show a raid, follow this format:' +
                            '\n !raid show --raidname="cdev 7 man"')
                    await client.send_message(message.channel, msg)
                else:
                    try:
                        raid = session.query(Raid).filter_by(raid_name=argDict["raidname"]).one()
                    except NoResultFound:
                        print(traceback.format_exc())
                        msg = argDict["raidname"] + " is not a scheduled raid."
                        await client.send_message(message.channel, msg)
                    else:
                        msg += displayRaid(raid)
                        await client.send_message(message.channel, msg)

            elif command == "list":
                # !raid list
                # Lists raids that were created in the past week.
                fromLastWeek = datetime.datetime.now() - timedelta(weeks=1)
                newerRaidList = session.query(Raid).filter(Raid.created_datetime > fromLastWeek).all()
                msg = '```md\nScheduled Raids:\n'
                for raid in newerRaidList:
                    msg += raid.raid_name + " - " + raid.day + ", " + raid.date + " @ " + raid.time + '\n'
                msg += '```'
                await client.send_message(message.channel, msg)

            elif command == "help":
                # !raid help
                await client.send_message(message.channel, raidHelpStr1)
                await client.send_message(message.channel, raidHelpStr2)
                await client.send_message(message.channel, raidHelpStr3)

            else:
                msg = "We aren't speaking the same language. Please use '!raid help' for a list of commands and format."
                await client.send_message(message.channel, msg)
        except:
            print(traceback.format_exc())
            msg = sys.exc_info()[0]
            await client.send_message(message.channel, msg)
            session.rollback()
        else:
            session.commit()
        finally:            
            session.close()

    for derogatoryTerms in derogatoryList:
        if derogatoryTerms in str(message.content).lower():
            await client.delete_message(message)

@client.event
async def on_ready():
    print('Bot has started...')

raidHelpStr1 = ('```python\n' +
                "Raid bot says use the '!raid' command prefix.\n" +
                "```\n" +
                "**help!!!!**\n" +
                "```md\n" +
                "Uhh... you're lookin' at it already.\n" +
                "\nChannel and role restrictions: \n" +
                "[#raid-schedules, #clear-runs, #practice-runs][any role]\n" +
                "```\n" +
                "**show raid details**\n" +
                "```md\n" +
                "Examples:\n" + 
                '!raid show --raidname="cdev 7 man"\n' +
                "\nChannel and role restrictions: \n" +
                "[#clear-runs, #practice-runs][any role]\n" +
                "\nRequired Options:\n" +
                "[--raidname]\n" +
                "----\n" +
                "```\n" +
                "**list raids created in the past week**\n" +
                "```md\n" +
                "Examples:\n" +
                "!raid list\n" +
                "\nChannel and role restrictions: \n" +
                "[#clear-runs, #practice-runs][any role]\n" +
                "```\n")

raidHelpStr2 = ("**create a raid**\n" +
                "```md\n" +
                "Examples:\n" +
                '!raid create --raidname="7 man cdev" --day="Saturday" --date="April 6" --time="7 PM" --max_ppl=7\n' +
                '!raid create --raidname="CPAP" --day="Saturday" --date="April 6" --time="7 PM"\n' +
                "\nChannel and role restrictions: \n" +
                "[#raid-schedules][Raid master]\n" +
                "\nRequired Options:\n" +
                "[--raidname][--day][--date][--time]\n" +
                "----\n" +
                "\nOptional:\n" +
                "[--max_ppl]\n" +
                "----\n" +
                "```\n" +
                "**update your raid details**\n" +
                "```md\n" +
                "Examples:\n" +
                '!raid updateRaid --oldRaidname="7 man cdev" --raidname="4 man cdev" --day="Sunday" --date="April 7" --time="8 PM" --max_ppl=4\n' +
                "\nChannel and role restrictions: \n" +
                "[#clear-runs, #practice-runs][Raid master]\n" +
                "\nRequired Options (Will keep old values if not provided):\n" +
                "[--oldRaidname] & at least one of the following: [--raidname][--day][--date][--time]\n" +
                "----\n" +
                "```\n" +
                "**delete a raid**\n" +
                "```md\n" +
                "Examples:\n" +
                '!raid delete --raidname="7 man cdev"\n' +
                "\nChannel and role restrictions: \n" +
                "[#raid-schedules][Raid master - must be the person who created it]\n" +
                "\nRequired Options:\n" +
                "[--raidname]\n" +
                "----\n" +
                "```\n")

raidHelpStr3 = ("**join a raid**\n" +
                "```md\n" +
                "Examples:\n" +
                '!raid join --raidname="7 man cdev" --ign="Stronk Oolong" --class="DPS Priest"\n' +
                "\nChannel and role restrictions: \n" +
                "[#clear-runs, #practice-runs][any role]\n" +
                "\nRequired Options:\n" +
                "[--raidname][--ign][--class]\n" +
                "----\n" +
                "```\n" +
                "**update your class details**\n" +
                "```md\n" +
                "Examples:\n" +
                '!raid updatePerson --raidname="7 man cdev" --oldIgn="Liatris" --ign="Calendula" --class="calendar"\n' +
                "\nChannel and role restrictions: \n" +
                "[#clear-runs, #practice-runs][any role - must be the same person who used the !raid join]\n" +
                "\nRequired Options (Will keep old values if not provided):\n" +
                "[--raidname][--oldIgn] & at least one of the following: [--ign][--class]\n" +
                "----\n" +
                "```\n" +
                "**remove someone from a raid**\n" +
                "```md\n" +
                "Examples:\n" +
                '!raid byebye --raidname="7 man cdev" --ign="SenjiNO"\n' +
                "\nChannel and role restrictions: \n" +
                "[#clear-runs, #practice-runs][Raid master]\n" +
                "\nRequired Options:\n" +
                "[--raidname][--ign]\n" +
                "----\n" +
                "```")

client.run(tokenAddress)


