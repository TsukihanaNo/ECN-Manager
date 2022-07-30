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
cursor.execute('CREATE TABLE DOCUMENT(DOC_ID TEXT, DOC_TYPE TEXT, DOC_TITLE TEXT, DEPARTMENT TEXT, DOC_REASON TEXT, REQUESTOR TEXT, AUTHOR TEXT, STATUS TEXT, COMP_DATE TEXT, COMP_DAYS NUMBER , DOC_SUMMARY TEXT, LAST_MODIFIED TEXT, STAGE NUMBER, TEMPSTAGE NUMBER, FIRST_RELEASE TEXT, RELEASE_ELAPSE NUMBER, LAST_NOTIFIED TEXT, DUE_DATE TEXT, DOC_TEXT_1 TEXT,DOC_TEXT_2 TEXT,DOC_TEXT_3 TEXT,DOC_TEXT_4 TEXT,DOC_TEXT_5 TEXT)')
cursor.execute('CREATE TABLE COMMENTS(DOC_ID TEXT, NAME TEXT, USER TEXT, COMM_DATE TEXT, COMMENT TEXT, TYPE TEXT)')
cursor.execute('CREATE TABLE PARTS(DOC_ID TEXT, PART_ID TEXT, TYPE TEXT, DESC TEXT, DISPOSITION TEXT, MFG TEXT, MFG_PART TEXT, ATTACHMENTS TEXT,REPLACING TEXT, INSPEC TEXT, REFERENCE TEXT)')
cursor.execute('CREATE TABLE SIGNATURE(DOC_ID TEXT, NAME TEXT, USER_ID TEXT, JOB_TITLE TEXT, SIGNED_DATE TEXT,TYPE TEXT)')
cursor.execute('CREATE TABLE ATTACHMENTS(DOC_ID TEXT, FILENAME TEXT, FILEPATH TEXT, PART TEXT)')
cursor.execute('CREATE TABLE USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, DEPT TEXT, STATUS TEXT, EMAIL TEXT, SIGNED_IN TEXT)')
cursor.execute('CREATE TABLE CHANGELOG(DOC_ID TEXT, CHANGEDATE TEXT, NAME TEXT,DATABLOCK TEXT, PREVDATA TEXT, NEWDATA TEXT)')
cursor.execute('CREATE TABLE NOTIFICATION(DOC_ID TEXT, STATUS TEXT, TYPE TEXT, USERS TEXT, MSG TEXT, FROM_USER TEXT)')
cursor.execute('CREATE TABLE TASKS(DOC_ID TEXT, DESC TEXT, STATUS TEXT, COMPLETED_BY TEXT, COMP_DATE TEXT)')
cursor.execute('CREATE TABLE WINDOWSLOG(USER TEXT, STATUS TEXT, DATETIME TEXT)')
cursor.execute('CREATE TABLE PERMISSIONS(USER TEXT, CREATE_ECN TEXT, CREATE_PCN TEXT, CREATE_USER TEXT, REJECT_SIGNER TEXT, ACCESS_SETTINGS TEXT, VIEW_ANALYTICS TEXT)')

cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('admin','admin','admin','Admin','Admin','Active'))

# create ecn, pcn
# view analytics
# create users
# access settings
# reject to signer

# results = cursor.execute("Select * from ECN")
# for result in results:
#     print(result)
database.commit()
database.close()