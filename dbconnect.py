import os, sys, datetime, traceback
from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
import psycopg2


DATABASE_URL = os.environ['DATABASE_URL']
Base = declarative_base()

class Raid(Base):
    __tablename__ = "raids"
    raid_name = Column("raid_name", String, primary_key=True, nullable=False)
    time = Column("time", String, nullable=False)
    day = Column("day", String, nullable=False)
    date = Column("date", String, nullable=False)
    max_ppl = Column("max_ppl", Integer, nullable=False, default=10)
    attendees = relationship("Attendee", cascade="all, delete-orphan", passive_deletes=True)
    created_by = Column("created_by", String, nullable=False)
    created_datetime = Column("created_datetime", DateTime, nullable=False, default=datetime.datetime.now())

    @property
    def attendees_count(self):
        return len(self.attendees)

    def __repr__(self):
        return "<Raid( raid_name='%s',\n\ttime='%s',\n\tday='%s',\n\tdate='%s',\n\tmax_ppl='%d',\n\tattendees='%s',\n\tcreated_by='%s',\n\tcreated_datetime='%s')>" % (
                    self.raid_name, self.time, self.day, self.date, self.max_ppl, str(self.attendees), self.created_by, self.created_datetime)


class Attendee(Base):
    __tablename__ = "raidAttendance"
    unique_id = Column("unique_id", Integer, primary_key=True, autoincrement=True)
    raid_name = Column("raid_name", String, ForeignKey(Raid.raid_name, ondelete="CASCADE"), nullable=False)
    ign = Column("ign", String, nullable=False)
    ms_class = Column("ms_class", String, nullable=False)
    added_by = Column("added_by", String, nullable=False)

    def __repr__(self):
        return "\n<Attendee(unique_id='%d', raid_name='%s', ign='%s', ms_class='%s', added_by='%s')>" % (
                    self.unique_id, self.raid_name, self.ign, self.ms_class, self.added_by)

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

# You can run dbconnect.py on it's own with "initTables" argument to initialize creation of tables
# or put any queries in the else statement that you want to test.
# NOTE: DO NOT RUN dbconnect.py AS ITS OWN SCRIPT ON LIVE SERVER - it'll wipe the data and then run these example queries
def main(args):
    engine = create_engine(DATABASE_URL)
    if (len(args) > 0):
        if (args[0] == "initTables"):
            print("Creating tables")
            init_tables(engine)
        elif (args[0] == "reinitTables"):
            print("TO DO: Deleting tables & data & reinitializing")
            reinit_tables(engine)
    else:
        confirmContinue = input("This script run on its own will wipe the data, and run the example queries." +
                                "\nAre you sure you want to run this script on it's own? (Y/N): ")
        if (confirmContinue == "Y"):
            db = DatabaseConnection(engine)
            session = db.create_session()
            try: 
                ''' WIPING THE DB Data - not dropping the tables: Attendees will delete by cascade on deletion of raid '''
                session.query(Raid).delete()

                ''' 
                EXAMPLE USAGE OF QUERIES I THINK WE'LL NEED
                Reference for available Query methods: https://docs.sqlalchemy.org/en/latest/orm/query.html
                '''
                print("Creating raids: '7man cdev' and 'CPAP'\n")
                session.add(Raid(raid_name="7man cdev", day="Saturday", date="April 5", time="~5PM CST", max_ppl="7", created_by="kerro"))
                session.add(Raid(raid_name="CPAP", day="Sunday", date="April 6", time="TBD", created_by="kerro"))

                print("Adding attendee, Zukoori and Calendar, to raid: '7man cdev'\n")
                session.add(Attendee(raid_name="7man cdev", ign="Zukoori", ms_class="rb", added_by="kerro"))
                session.add(Attendee(raid_name="7man cdev", ign="Calendar", ms_class="priest", added_by="kerro"))
                print("Adding attendee, kerro, to raid: 'CPAP'\n")
                session.add(Attendee(raid_name="CPAP", ign="kerro", ms_class="archer", added_by="kerro"))

                print("Updating attendee ign and class: Zukoori - rb --> kerro - archer\n")
                session.query(Attendee)\
                        .filter_by(raid_name="7man cdev", ign="Zukoori")\
                        .update({"ign": "kerro", "ms_class":"archer"}, synchronize_session="fetch")

                print("Select for all raids")
                allRaids = session.query(Raid).all()
                print(allRaids, "\n")

                print("Printing all raid names from this query")
                allRaidNames = [raid.raid_name for raid in allRaids]
                print(allRaidNames, "\n")


                print("Select for raid details: '7man cdev'")
                # The attendees attribute will be a list of Attendees so can use the same query to get a list of everyone who's going
                raidDetailsExample = session.query(Raid)\
                                       .filter_by(raid_name="7man cdev")\
                                       .one()
                print(raidDetailsExample, "\n")

                print("Who's going to '7man cdev'?")
                attendeesList = [" - ".join([attendee.ign, attendee.ms_class]) for attendee in raidDetailsExample.attendees]
                print(attendeesList, "\n")
                print("How many people are going to '7man cdev' so far?")
                print(raidDetailsExample.attendees_count, "\n")

                print("Select for one attendee's details: 'kerro - 7man cdev'\n")
                attendeeDetailsExample = session.query(Attendee)\
                                       .filter_by(raid_name="7man cdev", ign="kerro")\
                                       .one()
                print(attendeeDetailsExample)

                print("Deleting an attendee from a raid: no kerro you can't go CPAP\n")
                session.query(Attendee)\
                        .filter_by(raid_name="CPAP", ign="kerro")\
                        .delete()

                print("Deleting raid '7man cdev' - should delete associated attendees automatically\n")
                session.query(Raid).filter_by(raid_name="7man cdev").delete()
                session.query(Raid).filter_by(raid_name="CPAP").delete()

                session.commit()
            except: 
                print(traceback.format_exc())
                session.rollback()
            else:
                session.close()
                db.close()
        else:
            print("Goodbye.")
            sys.exit()

# Creates table definitions if not already created
def init_tables(engine):
    Base.metadata.create_all(engine)
    for _t in Base.metadata.tables:
        print("Exists Table: ", _t)

def reinit_tables(engine):
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
