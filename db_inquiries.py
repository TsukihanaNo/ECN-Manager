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
#location_DB = r'T:/ecn-manager/DB/ECN_DB.db'
database = sqlite3.connect(location_DB)
cursor = database.cursor()

results = cursor.execute(f"Select ECN_ID from ECN where ECN_TITLE like '%safelink%'")
for result in results:
    print(result)

# cursor.execute("update NOTIFICATION set STATUS='Not Sent'")
# database.commit()
database.close()