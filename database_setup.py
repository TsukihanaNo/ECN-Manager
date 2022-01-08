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

location_DB = os.path.join(dbfolder,"Request_DB.db")

database = sqlite3.connect(location_DB)
cursor = database.cursor()
cursor.execute('CREATE TABLE ECN(ECN_ID TEXT, ECN_TYPE TEXT, ECN_TITLE TEXT, DEPARTMENT TEXT, ECN_REASON TEXT, REQUESTOR TEXT, AUTHOR TEXT, STATUS TEXT, COMP_DATE DATE, ECN_SUMMARY TEXT, LAST_MODIFIED DATE)')
cursor.execute('CREATE TABLE COMMENTS(ECN_ID TEXT, NAME TEXT, USER TEXT, COMM_DATE DATE, COMMENT TEXT, TYPE TEXT)')
cursor.execute('CREATE TABLE TAG_PARTS(ECN_ID TEXT, PART_ID TEXT)')
cursor.execute('CREATE TABLE TAG_PRODUCT(ECN_ID TEXT, PRODUCT TEXT)')
cursor.execute('CREATE TABLE SIGNATURE(ECN_ID TEXT, NAME TEXT, USER_ID TEXT, JOB_TITLE TEXT HAS_SIGNED TEXT, SIGNED_DATE DATETIME)')
cursor.execute('CREATE TABLE ATTACHMENTS(ECN_ID TEXT, FILENAME TEXT, FILEPATH TEXT)')
cursor.execute('CREATE TABLE USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, STATUS TEXT)')
cursor.execute('CREATE TABLE CHANGELOG(ECN_ID TEXT, CHANGEDATE DATETIME, NAME TEXT,DATABLOCK TEXT, PREVDATA TEXT, NEWDATA TEXT)')
cursor.execute('CREATE TABLE TASKS(ECN_ID TEXT, CREATEDATE DATE, DUEDATE DATE, CREATEDBY TEXT, ASSIGNTO TEXT, TASK TEXT, STATUS TEXT)')

cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('planner1','pass','P1','Signer','Planner','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('planner2','pass','P2','Signer','Planner','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('eng1','eng','E1','Engineer','Engineer','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('eng2','eng','E2','Engineer','Engineer','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('buyer1','pass','B1','Signer','Buyer','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('buyer2','pass','B2','Signer','Buyer','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('manager1','pass','Manager','Manager','Manager','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('manager2','pass','Manager2','Manager','Manager','Inactive'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('admin','admin','admin','Admin','Admin','Active'))

# results = cursor.execute("Select * from ECN")
# for result in results:
#     print(result)
database.commit()
database.close()