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
            print("Visual Connection Established")
            self.cur = self.con.cursor()
        except Exception as e:
            print(e)
            self.parent.dispMsg(f"Error: Connection could not be established to Visual. (error code - {e})")

    def checkPartSetup(self,part,ptype):
        #planner id, buyer id, safety stock, min-max (not required), order policy, warehouse, inspection, vendor pricing
        if ptype=="Purchased":
            command =f"Select CONSUMABLE, PURCHASED, ORDER_POLICY, PRODUCT_CODE, INSPECTION_REQD, PRIMARY_WHS_ID, PRIMARY_LOC_ID, PLANNER_USER_ID, BUYER_USER_ID, SAFETY_STOCK_QTY FROM PART WHERE ID='{part}'"
        elif ptype=="Fabricated":
            command =f"Select FABRICATED, ORDER_POLICY, ENGINEERING_MSTR, PRODUCT_CODE, PRIMARY_WHS_ID, PRIMARY_LOC_ID, PLANNER_USER_ID, SAFETY_STOCK_QTY FROM PART WHERE ID='{part}'"
        else:
            command =f"Select FABRICATED, ORDER_POLICY, ENGINEERING_MSTR, PRODUCT_CODE, PRIMARY_WHS_ID, PRIMARY_LOC_ID, PLANNER_USER_ID, SAFETY_STOCK_QTY FROM PART WHERE ID='{part}'"
        self.cur.execute(command)
        result = self.cur.fetchone()
        counter = 0
        3,5,6
        consumable = False
        for item in result:
            if counter==0 and item=="Y":
                consumable = True
            if item=="" or item is None:
                if consumable:
                    if counter==3 or counter == 5 or counter == 6:
                        pass
                    else:
                        return False
                else:
                    return False
            counter+=1
        return True
    
    def queryPartsNoStage(self):
        command = "select ID, Description, purchased, fabricated from part where stage_id is Null and inventory_locked='Y'"
        self.cur.execute(command)
        results = self.cur.fetchall()
        filtered_results = []
        for result in results:
            if result[2]=="Y":
                ptype="Purchased"
            else:
                ptype="Fabricated"
            if not self.checkPartSetup(result[0],ptype):
                filtered_results.append(result)
                
        return filtered_results
    
    def queryParts(self,search):
        command = f"select ID, Description, purchased, fabricated from part where ID like '{search}%'"
        self.cur.execute(command)
        results = self.cur.fetchall()
        filtered_results = []
        for result in results:
            # if result[2]=="Y":
            #     ptype="Purchased"
            # else:
            #     ptype="Fabricated"
            # if not self.checkPartSetup(result[0],ptype):
            filtered_results.append(result)
                
        return filtered_results
    
    def queryPartsFromBOM(self,part_id,filtered=False):
        command = f"select requirement.part_id, part.description, part.purchased, part.fabricated  from requirement left join part on part.id = requirement.part_id where workorder_type='M' and workorder_base_id='{part_id}'"
        self.cur.execute(command)
        results = self.cur.fetchall()
        
        if not filtered:
            return results
        
        filtered_results = []
        for result in results:
            # if result[2]=="Y":
            #     ptype="Purchased"
            # else:
            #     ptype="Fabricated"
            # if not self.checkPartSetup(result[0],ptype):
            filtered_results.append(result)
                
        return filtered_results

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
        # for item in result:
        #     print(item)
        return result
    
    def getPartQty(self,part):
        self.cur.execute(f"Select QTY_ON_HAND, QTY_ON_ORDER, QTY_IN_DEMAND from PART where ID='{part}'")
        result = self.cur.fetchone()
        # for item in result:
        #     print(item)
        return result

    def partExist(self,part):
        self.cur.execute(f"Select ID from PART where ID='{part}'")
        result = self.cur.fetchone()
        if result is not None:
            return True
        else:
            return False
        
    def checkReqID(self,req_id):
        self.cur.execute(f"select ID from PURC_REQUISITION where ID='{req_id}'")
        result = self.cur.fetchone()
        if result is not None:
            return True
        else:
            return False
        
    def getReqHeader(self,req_id):
        self.cur.execute(f"select ASSIGNED_TO, STATUS from PURC_REQUISITION where ID='{req_id}'")
        result = self.cur.fetchone()
        return result
    
    def getReqNotation(self,req_id):
        self.cur.execute(f"select * from NOTATION where OWNER_ID='{req_id}' and TYPE='PR'")
        results = self.cur.fetchall()
        notation = ""
        for item in results:
            # print('nonformated:',item[3].read())
            # print('formated',str(item[3].read(),"ISO-8859-1"))
            
            notation+=str(item[3].read(),"ISO-8859-1")+"\n"
            
        return notation

    def getReqItems(self,req_id):
        self.cur.execute(f"select PURC_REQ_LINE.LINE_NO, PURC_REQ_LINE.LINE_STATUS, PURC_REQ_LINE.PART_ID, PURC_REQ_LINE.VENDOR_PART_ID, PURC_REQ_LINE.ORDER_QTY, PURC_REQ_LINE.PURCHASE_UM, PURC_ORDER_REQ.PURC_ORD_ID, PURC_REQ_LINE.UNIT_PRICE, PURC_REQ_LINE.GL_EXPENSE_ACCT_ID from PURC_REQ_LINE LEFT JOIN PURC_ORDER_REQ ON PURC_REQ_LINE.PURC_REQ_ID=PURC_ORDER_REQ.PURC_REQ_ID AND PURC_REQ_LINE.LINE_NO=PURC_ORDER_REQ.PURC_REQ_LINE_NO WHERE PURC_REQ_LINE.PURC_REQ_ID='{req_id}'")
        results = self.cur.fetchall()
        # items = []
        # for result in results:
        #     items.append(result)
            
        # for item in items:
        #     print(item)
            
        # return items
        return results
    
    def getPONotation(self,PO):
        self.cur.execute(f"select NOTE from NOTATION where TYPE='PO' and OWNER_ID='{PO}'")
        result = self.cur.fetchone()
        if result is not None:
            return result[0].read().decode("ascii")  
        else:
            return None
        # print(note)
        
    def getPurchLineInfo(self,part):
        self.cur.execute(f"select PURC_ORDER_ID, LINE_NO, PART_ID, VENDOR_PART_ID, ORDER_QTY, PURCHASE_UM, UNIT_PRICE, PROMISE_DATE from PURC_ORDER_LINE where PART_ID like '%{part}%' or VENDOR_PART_ID like '%{part}%'")
        results = self.cur.fetchall()
        return results
    
    def getPurchLineInfo2(self,PO,PO_line):
        self.cur.execute(f"select PURC_ORDER_ID, LINE_NO, PART_ID, VENDOR_PART_ID, ORDER_QTY, PURCHASE_UM, UNIT_PRICE, PROMISE_DATE from PURC_ORDER_LINE where PURC_ORDER_ID='{PO}' and LINE_NO='{PO_line}'")
        result = self.cur.fetchone()
        return result
    
    def getPurchLines(self,PO):
        self.cur.execute(f"select PURC_ORDER_ID, LINE_NO, PART_ID, VENDOR_PART_ID, ORDER_QTY, PURCHASE_UM, UNIT_PRICE, LAST_RECEIVED_DATE, GL_EXPENSE_ACCT_ID from PURC_ORDER_LINE where PURC_ORDER_ID='{PO}'")
        results = self.cur.fetchall()
        return results
            
    def getPurchOrderInfo(self,PO):
        self.cur.execute(f"select ID, VENDOR_ID, STATUS,ORDER_DATE,DESIRED_RECV_DATE, PROMISE_SHIP_DATE,PROMISE_DATE,BUYER from PURCHASE_ORDER where ID='{PO}'")
        result = self.cur.fetchone()
        return result
    
    def getPurchLineDelivery(self,PO,PO_line):
        self.cur.execute(f"select PURC_ORDER_ID, PURC_ORDER_LINE_NO, DEL_SCHED_LINE_NO, DESIRED_RECV_DATE, ACTUAL_RECV_DATE, ORDER_QTY, RECEIVED_QTY FROM PURC_LINE_DEL WHERE PURC_ORDER_ID='{PO}' and PURC_ORDER_LINE_NO='{PO_line}'")
        results = self.cur.fetchall()
        return results
    
    def getPurchOrderDelivery(self,PO):
        self.cur.execute(f"select PURC_ORDER_ID, PURC_ORDER_LINE_NO, DEL_SCHED_LINE_NO, DESIRED_RECV_DATE, ACTUAL_RECV_DATE, ORDER_QTY, RECEIVED_QTY FROM PURC_LINE_DEL WHERE PURC_ORDER_ID='{PO}'")
        results = self.cur.fetchall()
        return results
    
    def getVendorName(self,vendor_id):
        self.cur.execute(f"select NAME from VENDOR where ID='{vendor_id}'")
        result = self.cur.fetchone()
        return result[0]