import cx_Oracle
import os, sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class Visual():
    def __init__(self,parent,user,pw,db,instantclient_dir):
        super(Visual, self).__init__()
        try:
            self.parent = parent
            os.environ['PATH'] = instantclient_dir + os.path.pathsep + os.environ['PATH']
            cx_Oracle.init_oracle_client(instantclient_dir)
            self.con = cx_Oracle.connect(user,pw,db)
            self.cur = self.con.cursor()
        except Exception as e:
           print(e)

    def checkPartSetup(self,part,ptype):
        #planner id, buyer id, safety stock, min-max (not required), order policy, warehouse, inspection, vendor pricing
        if ptype=="Purchased":
            command =f"Select PURCHASED, ORDER_POLICY, PRODUCT_CODE, INSPECTION_REQD, PRIMARY_WHS_ID, PRIMARY_LOC_ID, PLANNER_USER_ID, BUYER_USER_ID, SAFETY_STOCK_QTY FROM PART WHERE ID='{part}'"
        elif ptype=="Fabricated":
            command =f"Select FABRICATED, ORDER_POLICY, ENGINEERING_MSTR, PRODUCT_CODE, PRIMARY_WHS_ID, PRIMARY_LOC_ID, PLANNER_USER_ID, SAFETY_STOCK_QTY FROM PART WHERE ID='{part}'"
        else:
            command =f"Select FABRICATED, ORDER_POLICY, ENGINEERING_MSTR, PRODUCT_CODE, PRIMARY_WHS_ID, PRIMARY_LOC_ID, PLANNER_USER_ID, SAFETY_STOCK_QTY FROM PART WHERE ID='{part}'"
        self.cur.execute(command)
        result = self.cur.fetchone()
        for item in result:
            if item=="" or item is None:
                return False
        return True

    def checkObsolete(self,part):
        self.cur.execute(f"select STATUS from PART where ID='{part}'")
        result = self.cur.fetchone()
        if result[0]=="O":
            return True
        else:
            return False

    def checkLock(self,part):
        self.cur.execute(f"Select INVENTORY_LOCKED from PART where ID='{part}")
        result = self.cur.fetchone()
        print(result[0])

    def getPartInfo(self,part):
        self.cur.execute(f"Select * from PART where ID='{part}'")
        result = self.cur.fetchone()
        for item in result:
            print(item)

    def partExist(self,part):
        self.cur.execute(f"Select ID from PART where ID='{part}'")
        result = self.cur.fetchone()
        if result is not None:
            return True
        else:
            return False

    
