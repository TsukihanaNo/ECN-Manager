import cx_Oracle

class Visual():
    def __init__(self,parent,user,pw,db):
        try:
            self.parent = parent
            self.con = cx_Oracle.connect(user,pw,db)
            self.cur = self.con.cursor()
        except Exception as e:
            print(e)
            self.parent.dispMsg(f"Error:{e}")

    def checkPartSetup(self,part):
        pass

    def checkObsolete(self,part):
        pass

    def checkLock(self,part):
        pass

    def getPartInfo(self,part):
        pass

    def getPartQty(self,part):
        pass






    
