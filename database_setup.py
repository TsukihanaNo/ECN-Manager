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

location_DB = os.path.join(dbfolder,"Request_DB")

database = sqlite3.connect(location_DB)
cursor = database.cursor()
cursor.execute('CREATE TABLE ECN(ECN_ID TEXT, ECN_TYPE TEXT, ECN_TITLE TEXT, REQ_DETAILS TEXT, REQUESTOR TEXT, ASSIGNED_ENG TEXT, STATUS TEXT, REQ_DATE DATE, ASSIGN_DATE DATE, COMP_DATE DATE, ENG_DETAILS TEXT)')
cursor.execute('CREATE TABLE COMMENT(ECN_ID TEXT, USER TEXT, COMM_DATE DATE, COMMENT TEXT)')
cursor.execute('CREATE TABLE TAG_PARTS(ECN_ID TEXT, PART_ID TEXT)')
cursor.execute('CREATE TABLE TAG_PRODUCT(ECN_ID TEXT, PRODUCT TEXT)')
cursor.execute('CREATE TABLE SIGNATURE(ECN_ID TEXT, SIGS TEXT, JOB_TITLE TEXT, HAS_SIGNED TEXT, SIGNED_DATE TEXT)')
cursor.execute('CREATE TABLE FILES(ECN_ID TEXT, FILENAME TEXT, FILE_LOC TEXT)')
cursor.execute('CREATE TABLE DRAWING(ECN_ID TEXT, DRAWING_NAME TEXT, DRAWING_LOC TEXT)')
cursor.execute('CREATE TABLE USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT)')

cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE) VALUES(?,?,?,?,?)',('std','std','standard','Requestor','Planner'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE) VALUES(?,?,?,?,?)',('eng','eng','engineer','Engineer','Engineer'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE) VALUES(?,?,?,?,?)',('admin','admin','admin','Admin','Admin'))
database.commit()
database.close()