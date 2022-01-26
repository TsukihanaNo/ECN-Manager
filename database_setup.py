import sqlite3,os, sys
if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

dbfolder = os.path.join(program_location, 'DB')
if not os.path.isdir(dbfolder):
    os.mkdir(dbfolder)

location_DB = os.path.join(dbfolder,"ECN_DB.db")

database = sqlite3.connect(location_DB)
cursor = database.cursor()
cursor.execute('CREATE TABLE ECN(ECN_ID TEXT, ECN_TYPE TEXT, ECN_TITLE TEXT, DEPARTMENT TEXT, ECN_REASON TEXT, REQUESTOR TEXT, AUTHOR TEXT, STATUS TEXT, COMP_DATE DATE, ECN_SUMMARY TEXT, LAST_MODIFIED DATE, STAGE NUMBER, TEMPSTAGE NUMBER, FIRST_RELEASE DATE, LAST_STATUS DATE, RELEASE_ELAPSE NUMBER, STATUS_ELAPSE NUMBER, LAST_NOTIFIED DATE)')
cursor.execute('CREATE TABLE COMMENTS(ECN_ID TEXT, NAME TEXT, USER TEXT, COMM_DATE DATE, COMMENT TEXT, TYPE TEXT)')
cursor.execute('CREATE TABLE PARTS(ECN_ID TEXT, PART_ID TEXT, TYPE TEXT, DESC TEXT, DISPOSITION TEXT, MFG TEXT, MFG_PART TEXT, ATTACHMENTS TEXT,REPLACING TEXT, INSPEC TEXT)')
cursor.execute('CREATE TABLE SIGNATURE(ECN_ID TEXT, NAME TEXT, USER_ID TEXT, JOB_TITLE TEXT HAS_SIGNED TEXT, SIGNED_DATE DATETIME,TYPE TEXT)')
cursor.execute('CREATE TABLE ATTACHMENTS(ECN_ID TEXT, FILENAME TEXT, FILEPATH TEXT, PART TEXT)')
cursor.execute('CREATE TABLE USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, DEPT TEXT, STATUS TEXT, EMAIL TEXT)')
cursor.execute('CREATE TABLE CHANGELOG(ECN_ID TEXT, CHANGEDATE DATETIME, NAME TEXT,DATABLOCK TEXT, PREVDATA TEXT, NEWDATA TEXT)')
cursor.execute('CREATE TABLE NOTIFICATION(ECN_ID TEXT, STATUS TEXT, TYPE TEXT)')
cursor.execute('CREATE TABLE TASKS(ECN_ID TEXT, DESC TEXT, STATUS TEXT, COMPLETED_BY TEXT, COMP_DATE DATE)')
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('admin','admin','admin','Admin','Admin','Active'))

# results = cursor.execute("Select * from ECN")
# for result in results:
#     print(result)
database.commit()
database.close()