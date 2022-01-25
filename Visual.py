import cx_Oracle

class Visual():
    def __init__(self,user,pw,db):
        super(Visual, self).__init__()
        #try:
            #self.parent = parent
        cx_Oracle.init_oracle_client(r'F:\oracle\ora12c_64')
        #self.con = cx_Oracle.connect(user,pw,db)
        #self.cur = self.con.cursor()
        #except Exception as e:
        #    print(e)
            #self.parent.dispMsg(f"Error:{e}")

    def checkPartSetup(self,part):
        sql = f"Select PRIMARY_WHS_ID, PRIMARY_LOC_ID,UNIT_MATERIAL_COST, UNIT_LABOR_COST, UNIT_BURDEN_COST, UNIT_SERVICE_COST,ENGINEERING_MSTR,PLANNER_USER_ID,BUYER_USER_ID, SAFETY_STOCK_QTY,LEADTIME_BUFFER, STAGE_ID,STATUS, STATUS_EFF_DATE, INVENTORY_LOCKED from PART where ID='{part}'"
        self.cur.execute(sql)
        result = self.cur.fetchone()
        for item in result:
            print(item)

    def checkObsolete(self,part):
        pass

    def checkLock(self,part):
        pass

    def getPartInfo(self,part):
        pass

    def getPartQty(self,part):
        pass




    
