import os
import sys
from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2


DATABASE_URL = os.environ['DATABASE_URL']

class DatabaseConnection:
    # Connect to DB on initialization
    def __init__(self, engine):
        #self.dbConnection = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.engine = engine
        self.conn = engine.connect()
        init_tables(engine)

    def create_session(self):
        return scoped_session(sessionmaker(bind=self.engine))

    def close(self):
        self.conn.close()


class Query:
    def __init__(self, session, metadata):
        self.session = session
        self.metadata = metadata

   	# --------------------------------- #
    #        CRUD FOR TABLE: RAID       #
   	# --------------------------------- #
    def insert_raid(self, raidDict):
    	''' SQL STATEMENT
        insert into raids (name, author, time, max_ppl) 
        values (VARCHAR, VARCHAR, VARCHAR, NUMBER)
    	'''
        t_raids = self.metadata.tables["raids"]
        self.session.execute(t_raids.insert(), [raidDict])
    
    def update_raid(self, newRaidDict):
    	''' SQL STATEMENT
        update raids set author = VARCHAR, time= VARCHAR, max_ppl = NUMBER
        where name = VARCHAR
    	'''
        t_raids = self.metadata.tables["raids"]
        self.session.execute(t_raids.update().\
            where(t_raids.c.name == newRaidDict["name"]).\
            values (    author = newRaidDict["author"], 
                        time = newRaidDict["time"],
                        max_ppl = newRaidDict["max_ppl"]
                    )
        )

    def delete_raid(self):
    	''' SQL STATEMENT
        delete from raids where name = VARCHAR
    	'''
        t_raids = self.metadata.tables["raids"]

    def select_raid_by_name(self, raidName):
        t_raids = self.metadata.tables["raids"]


   	# --------------------------------- #
    #   CRUD FOR TABLE: RAIDATTENDANCE  #
    # --------------------------------- #
    def insert_attendee(self, attendeeDict):
    	''' SQL STATEMENT
        insert into raidAttendance (raid_name, ign, ms_class) 
        values (VARCHAR, VARCHAR, VARCHAR)
    	'''
        t_raidAttendance = self.metadata.tables["raidAttendance"]
        self.session.execute(t_raidAttendance.insert(), [attendeeDict])
        
    def update_attendee(self, newAttendeeDict):
    	''' SQL STATEMENT
        update raidAttendance set ign = VARCHAR, ms_class = VARCHAR
        where raid_name = VARCHAR
    	'''
        t_raidAttendance = self.metadata.tables["raidAttendance"]
        self.session.execute(t_raidAttendance.update().\
            where(t_raidAttendance.c.raid_name == newAttendeeDict["raid_name"]).\
            values (    ign = newAttendeeDict["ign"], 
                        ms_class = newAttendeeDict["ms_class"]
                    )
        )

    def delete_attendee(self):
    	''' SQL STATEMENT
        delete from raidAttendance where raid_name = VARCHAR and ign = VARCHAR
    	'''
        t_raidAttendance = self.metadata.tables["raidAttendance"]
    def select_attendees_by_raid(self):
        t_raidAttendance = self.metadata.tables["raidAttendance"]



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

    

# You can run dbconnect.py on it's own with "initTables" argument to initialize creation of tables
# or put any queries in the else statement that you want to test.
def main(args):
    engine = create_engine(DATABASE_URL)
    if (len(args) > 0 and args[0] == "initTables"):
        print("init tables")
        init_tables(engine)
    else :
        db = DatabaseConnection(engine)
        metadata = MetaData(bind=engine, reflect=True)
        session = db.create_session()
        sessionQuery = Query(session, metadata)
        '''   
        # Raid Test Queries
        raid = Raid("imsquibbo2", "me", "7pm", 7)
        sessionQuery.insert_raid(raid.get_column_dict())
        raid = Raid("name", "me2", "5pm", 7)
        sessionQuery.update_raid(raid.get_column_dict())
        session.execute(t_raids.insert(), [raid.get_column_dict()])
        '''

        '''
        # Attendee Test Queries
        attendee = Attendee("imsquibbo2", "kerro", "archer")
        sessionQuery.insert_attendee(attendee.get_column_dict())
        '''
        attendee = Attendee("imsquibbo2", "Zukoori", "rb")
        sessionQuery.update_attendee(attendee.get_column_dict())
        session.commit()
        session.close()
        db.close()


# Creates table definitions if not already created
def init_tables(engine):
    metadata = MetaData(engine)
    
    if not engine.has_table(engine, "raids"):
    # One to one
        raids = Table("raids", metadata,
            Column("name", String, primary_key=True, nullable=False),
            Column("author", String, nullable=False),
            Column("time", String, nullable=False),
            Column("max_ppl", Integer, nullable=False)
        )

    if not engine.has_table(engine, "raidAttendance"):
        # One raid to many attendees
        raidAttendance = Table("raidAttendance", metadata,
            Column("raid_name", String, ForeignKey("raids.name"), nullable=False),
            Column("ign", String, nullable=False),
            Column("ms_class", String, nullable=False)
        )

    metadata.create_all()
    for _t in metadata.tables:
        print("Created Table: ", _t)



if __name__ == "__main__":
    main(sys.argv[1:])
