import sqlite3,os, sys, datetime
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
#location_DB = r'T:/ecn-manager/DB/ECN_DB.db'
database = sqlite3.connect(location_DB)
cursor = database.cursor()

#results = cursor.execute(f"Select * from SIGNATURE INNER JOIN ECN ON SIGNATURE.ECN_ID=ECN.ECN_ID WHERE ECN.STATUS='Out For Approval' and SIGNATURE.USER_ID='test'")
#results = cursor.execute("UPDATE SIGNATURE SET SIGNED_DATE = NULL where ECN_ID='ECN-220126-121943' and USER_ID='lily'")
#database.commit()
# results = cursor.execute("select FIRST_RELEASE,LAST_MODIFIED,COMP_DATE from ECN where FIRST_RELEASE like '2022-01%'")
# for result in results:
#     print(result[0],result[1],result[2])
results = cursor.execute("select STAGE from ECN")
for result in results:
    print(result)
    

# cursor.execute("update NOTIFICATION set STATUS='Not Sent'")
# database.commit()
database.close()