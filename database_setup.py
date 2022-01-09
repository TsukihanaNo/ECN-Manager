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
cursor.execute('CREATE TABLE ECN(ECN_ID TEXT, ECN_TYPE TEXT, ECN_TITLE TEXT, DEPARTMENT TEXT, ECN_REASON TEXT, REQUESTOR TEXT, AUTHOR TEXT, STATUS TEXT, COMP_DATE DATE, ECN_SUMMARY TEXT, LAST_MODIFIED DATE)')
cursor.execute('CREATE TABLE COMMENTS(ECN_ID TEXT, NAME TEXT, USER TEXT, COMM_DATE DATE, COMMENT TEXT, TYPE TEXT)')
cursor.execute('CREATE TABLE TAG_PARTS(ECN_ID TEXT, PART_ID TEXT)')
cursor.execute('CREATE TABLE TAG_PRODUCT(ECN_ID TEXT, PRODUCT TEXT)')
cursor.execute('CREATE TABLE SIGNATURE(ECN_ID TEXT, NAME TEXT, USER_ID TEXT, JOB_TITLE TEXT HAS_SIGNED TEXT, SIGNED_DATE DATETIME)')
cursor.execute('CREATE TABLE ATTACHMENTS(ECN_ID TEXT, FILENAME TEXT, FILEPATH TEXT)')
cursor.execute('CREATE TABLE USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, DEPT TEXT, STATUS TEXT)')
cursor.execute('CREATE TABLE CHANGELOG(ECN_ID TEXT, CHANGEDATE DATETIME, NAME TEXT,DATABLOCK TEXT, PREVDATA TEXT, NEWDATA TEXT)')
cursor.execute('CREATE TABLE NOTIFICATION(ECN_ID TEXT, STATUS TEXT, TYPE TEXT)')

cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS, DEPT) VALUES(?,?,?,?,?,?,?)',('plannerL','pass','Planner Lighting','Signer','Planner','Active','Lighting'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS, DEPT) VALUES(?,?,?,?,?,?,?)',('plannerE','pass','Planner Elec','Signer','Planner','Active','Elec'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS, DEPT) VALUES(?,?,?,?,?,?,?)',('plannerF','pass','Planner FoamPro','Signer','Planner','Active','FoamPro'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('eng1','eng','E1','Engineer','Engineer','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('eng2','eng','E2','Engineer','Engineer','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS, DEPT) VALUES(?,?,?,?,?,?,?)',('buyerL','pass','Buyer Lighting','Signer','Buyer','Active','Lighting'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS, DEPT) VALUES(?,?,?,?,?,?,?)',('buyerE','pass','Buyer Elec','Signer','Buyer','Active','Elec'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS, DEPT) VALUES(?,?,?,?,?,?,?)',('buyerF','pass','Buyer FoamPro','Signer','Buyer','Active','FoamPro'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('managerE','pass','Manager E','Engineering Manager','Engineering Manager','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('managerPR','pass','Manager PR','Production Manager','Production Manager','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('managerPL','pass','Manager PL','Planning Manager','Planning Manager','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('managerPU','pass','Manager PU','Purchasing Manager','Purchasing Manager','Active'))
cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS) VALUES(?,?,?,?,?,?)',('admin','admin','admin','Admin','Admin','Active'))

# results = cursor.execute("Select * from ECN")
# for result in results:
#     print(result)
database.commit()
database.close()