from PySide6 import QtWidgets, QtCore, QtGui
from datetime import datetime
import sys, os
from PurchReqDetailsTab import *
from SignatureTab import *
from NotificationTab import *

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class PurchReqWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, doc_id = None, row = None):
        super(PurchReqWindow,self).__init__()
        self.parent = parent
        self.cursor = parent.cursor
        self.db = parent.db
        self.settings = parent.settings
        self.user_info = parent.user_info
        self.user_permissions = parent.user_permissions
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.visual = parent.visual
        self.windowWidth =  900
        self.windowHeight = 550
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.doc_id = doc_id
        self.project_id = parent.doc_id
        self.row = row
        self.tablist = []
        self.initAtt()
        self.initUI()
        if self.doc_id is not None:
            self.loadData()
        else:
            self.doc_data = {"AUTHOR":self.user_info["user"],"STATUS":"Draft"}

            
        self.center()
        self.show()
        self.activateWindow()
        
        
    def initAtt(self):
        self.setWindowIcon(self.parent.ico)
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle(f"Purchase Requisition - user: {self.parent.user_info['user']}")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMinimumWidth(self.windowWidth)
        #self.setWindowModality(QtCore.Qt.ApplicationModal)
        
    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        
        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.clicked.connect(self.save)
        self.button_release = QtWidgets.QPushButton("Release")
        # self.button_members = QtWidgets.QPushButton("Members")
        
        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_release)
        # self.toolbar.addWidget(self.button_members)
        
        self.tab_purch_req = PurchReqDetailTab(self)
        self.tab_signature = SignatureTab(self,"PRQ")
        self.tab_notification = NotificationTab(self)
        
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.addTab(self.tab_purch_req,"Purch Reqs")
        self.tab_widget.addTab(self.tab_signature,"Signatures")
        self.tab_widget.addTab(self.tab_notification,"Notifications")
        
        mainlayout.addWidget(self.toolbar)
        mainlayout.addWidget(self.tab_widget)
        self.setLayout(mainlayout)
        
    def center(self):
        window = self.window()
        window.setGeometry(
            QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            window.size(),
            QtGui.QGuiApplication.primaryScreen().availableGeometry(),
        ),
    )
        
    def save(self, msg=None):
        if self.visual.checkReqID(self.tab_purch_req.line_id.text()):
            self.tab_purch_req.loadHeader()
            self.tab_purch_req.loadItems()
            if self.doc_id is None:
                self.generateID()
            if not self.checkID():
                self.insertData()
                if not msg:
                    self.dispMsg("Project has been saved!")
            else:
                self.updateData()
                if not msg:
                    self.dispMsg("Project has been updated!")
                        
        else:
            self.dispMsg("The purchase requisition ID does not exist in Visual. Please make sure you entered it correctly or that you have entered a purchase requisition in Visual prior to adding it here.")
        
    def AddSignatures(self):
        #inserting to signature table
        #SIGNATURE(ECN_ID TEXT, NAME TEXT, USER_ID TEXT, HAS_SIGNED TEXT, SIGNED_DATE TEXT)
        try:
            #get current values in db
            current_list = []
            self.cursor.execute(f"SELECT USER_ID FROM SIGNATURE WHERE DOC_ID='{self.doc_id}' and TYPE='Signing'")
            results = self.cursor.fetchall()
            for result in results:
                current_list.append(result[0])
            #print('current list',current_list)
            #get new values
            new_list = []
            for x in range(self.tab_signature.rowCount()):
                job_title = self.tab_signature.model.get_job_title(x)
                name = self.tab_signature.model.get_name(x)
                user_id = self.tab_signature.model.get_user(x)
                new_list.append((self.doc_id,job_title,name,user_id,"Signing"))
            #print('new list',new_list)
            
            for element in new_list:
                if element[3] not in current_list:
                    #print(f'insert {element[3]} into signature db')
                    self.cursor.execute("INSERT INTO SIGNATURE(DOC_ID,JOB_TITLE,NAME,USER_ID,TYPE) VALUES(?,?,?,?,?)",(element))
            for element in current_list:
                no_match = True
                for elements in new_list:
                    if element == elements[3]:
                        no_match = False
                if no_match:
                    #print(f"remove {element} from signature db")
                    self.cursor.execute(f"DELETE FROM SIGNATURE WHERE DOC_ID = '{self.doc_id}' and USER_ID='{element}'")
                    
                    
            current_list = []
            self.cursor.execute(f"SELECT USER_ID FROM SIGNATURE WHERE DOC_ID='{self.doc_id}' and TYPE='Notify'")
            results = self.cursor.fetchall()
            for result in results:
                current_list.append(result[0])
            
            new_list = []
            for x in range(self.tab_notification.rowCount()):
                job_title = self.tab_notification.model.get_job_title(x)
                name = self.tab_notification.model.get_name(x)
                user_id = self.tab_notification.model.get_user(x)
                new_list.append((self.doc_id,job_title,name,user_id,"Notify"))
                
            for element in new_list:
                if element[3] not in current_list:
                    #print(f'insert {element[3]} into notify db')
                    self.cursor.execute("INSERT INTO SIGNATURE(DOC_ID,JOB_TITLE,NAME,USER_ID,TYPE) VALUES(?,?,?,?,?)",(element))
            for element in current_list:
                no_match = True
                for elements in new_list:
                    if element == elements[3]:
                        no_match = False
                if no_match:
                    #print(f"remove {element} from notify db")
                    self.cursor.execute(f"DELETE FROM SIGNATURE WHERE DOC_ID = '{self.doc_id}' and USER_ID='{element}'")
            
            if self.doc_data["AUTHOR"]==self.parent.user_info["user"]:
                self.button_release.setEnabled(self.tab_signature.rowCount()>0)
            #print('data updated')
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (signature)!\n Error: {e}")
            
    def checkSigNotiDuplicate(self):
        sigs = []
        for row in range(self.tab_signature.rowCount()):
            sigs.append(self.tab_signature.model.get_user(row))
        for row in range(self.tab_notification.rowCount()):
            sigs.append(self.tab_notification.model.get_user(row))
        #print(sigs)
        if len(sigs)==len(set(sigs)):
            return False
        else:
            return True
    
    def checkID(self):
        self.cursor.execute(f"select DOC_ID from PURCH_REQS where DOC_ID='{self.tab_purch_req.line_doc_id.text()}'")
        result = self.cursor.fetchone()
        if result is not None:
            return True
        else:
            return False
        
    def checkFields(self):
        # print(self.tab_purch_req.text_details.toPlainText())
        if self.tab_purch_req.line_id.text()=="":
            self.dispMsg("Please enter the Visual Requsition ID.")
            return False
        if self.tab_purch_req.text_details.toPlainText()=="":
            self.dispMsg("Please enter a summary in the details section.")
            return False
        return True
        
    def generateID(self):
        date_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.doc_id = 'PRQ-'+date_time[2:]
        self.tab_purch_req.line_doc_id.setText(self.doc_id)

    def insertData(self):
        try:
            status = 'Draft'
            req_id = self.tab_purch_req.line_id.text()
            title = self.tab_purch_req.line_title.text()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            author = self.user_info['user']
            detail = self.tab_purch_req.text_details.toHtml()
            data = (self.project_id,self.doc_id,req_id,title,detail,status,author,modifieddate)
            self.cursor.execute("INSERT INTO PURCH_REQS(PROJECT_ID,DOC_ID,REQ_ID,DOC_TITLE,DETAILS,STATUS,AUTHOR,LAST_MODIFIED) VALUES(?,?,?,?,?,?,?,?)",(data))
            if self.checkSigNotiDuplicate():
                self.dispMsg("Duplicate signatures found")
            else:
                self.AddSignatures()
            self.db.commit()
            self.parent.model.add_req(self.doc_id,req_id,status)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData)!\n Error: {e}")
            
    def updateData(self):
        try:
            req_id = self.tab_purch_req.line_id.text()
            title = self.tab_purch_req.line_title.text()
            detail = self.tab_purch_req.text_details.toHtml()
            data = (req_id,title, detail,self.doc_id)
            status = self.tab_purch_req.line_status.text()
            self.cursor.execute("UPDATE PURCH_REQS SET REQ_ID = ?, DOC_TITLE = ?, DETAILS = ? WHERE DOC_ID = ?",(data))
            self.db.commit()
            self.parent.model.update_req_data(self.row,self.doc_id,title,req_id,status)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (updateData)!\n Error: {e}")
    
    def loadData(self):
        self.cursor.execute(f"select * from PURCH_REQS where DOC_ID='{self.doc_id}'")
        self.doc_data = self.cursor.fetchone()
        self.tab_purch_req.line_doc_id.setText(self.doc_data['DOC_ID'])
        self.tab_purch_req.line_id.setText(self.doc_data["REQ_ID"])
        self.tab_purch_req.line_title.setText(self.doc_data["DOC_TITLE"])
        self.tab_purch_req.line_status.setText(self.doc_data["STATUS"])
        self.tab_purch_req.text_details.setHtml(self.doc_data["DETAILS"])
        self.tab_purch_req.line_author.setText(self.doc_data["AUTHOR"])
        self.tab_purch_req.loadHeader()
        self.tab_purch_req.loadItems()
        
    def release(self):
        if self.checkFields():
            try:
                print("releasing")
                self.save(1)
                modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                self.cursor.execute(f"SELECT FIRST_RELEASE from DOCUMENT where DOC_ID='{self.doc_id}'")
                result = self.cursor.fetchone()
                if result[0] is None:
                    self.cursor.execute(f"UPDATE DOCUMENT SET FIRST_RELEASE = '{modifieddate}' where DOC_ID='{self.doc_id}'")
                data = (modifieddate, "Out For Approval",self.doc_id)
                self.cursor.execute("UPDATE DOCUMENT SET LAST_MODIFIED = ?, STATUS = ? WHERE DOC_ID = ?",(data))
                self.db.commit()
                currentStage = self.getPCNStage()
                if currentStage==0:
                    self.setPCNStage(self.getNextStage()[0])
                    self.addNotification(self.doc_id, "Stage Moved")
                self.tab_pcn.line_status.setText("Out For Approval")
                self.parent.repopulateTable()
                self.dispMsg("PCN has been saved and sent out for signing!")
                #self.addNotification(self.ecn_id, "Released")
                self.button_release.setDisabled(True)
                self.button_cancel.setText("Cancel")
                self.button_cancel.setDisabled(True)
            except Exception as e:
                print(e)
                self.dispMsg(f"Error occured during data update (release)!\n Error: {e}")
        else:
            self.dispMsg("There are empty Fields, cannot release.")
            
    def approve(self):
        try:
            approvedate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = (approvedate,self.doc_id,self.parent.user_info['user'])
            self.cursor.execute("UPDATE SIGNATURE SET SIGNED_DATE = ? WHERE DOC_ID = ? and USER_ID = ?",(data))
            self.cursor.execute(f"UPDATE DOCUMENT SET LAST_MODIFIED = '{approvedate}' where DOC_ID='{self.doc_id}'")
            self.tab_signature.repopulateTable()
            self.dispMsg("PCN has been signed!")
            self.button_approve.setDisabled(True)
            self.checkComplete()
            self.db.commit()
            print("moving pcn stage check")
            self.movePCNStage()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (approve)!\n Error: {e}")
    
    def reject(self):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            self.addComment(self.doc_id, comment,"Rejecting to author")
            try:
                modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = (modifieddate, "Rejected",self.doc_id)
                self.cursor.execute("UPDATE DOCUMENT SET LAST_MODIFIED = ?, STATUS = ? WHERE DOC_ID = ?",(data))
                self.cursor.execute(f"UPDATE SIGNATURE SET SIGNED_DATE=Null where DOC_ID='{self.doc_id}'")
                self.db.commit()
                self.setPCNStage(0)
                self.parent.repopulateTable()
                self.dispMsg("Rejection successful. Setting PCN stage to 0 and all signatures have been removed.")
                self.tab_pcn.line_status.setText("Rejected")
                self.addNotification(self.doc_id, "Rejected To Author",from_user=self.parent.user_info['user'],msg=comment)
                self.button_reject.setDisabled(True)
                self.button_approve.setDisabled(True)
            except Exception as e:
                print(e)
                self.dispMsg(f"Error occured during data update (reject)!\n Error: {e}")
        if ok and comment=="":
            self.dispMsg("Rejection failed: comment field was left blank.")
    
    def checkComplete(self):
        try:
            command = f"Select * from SIGNATURE where DOC_ID ='{self.doc_id}' and TYPE='Signing'"
            self.cursor.execute(command)
            results = self.cursor.fetchall()
            completed = True
            for result in results:
                if result['SIGNED_DATE'] == None or result['SIGNED_DATE']== "":
                    completed = False
            if completed:
                completeddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute(f"select FIRST_RELEASE from DOCUMENT where DOC_ID='{self.doc_id}'")
                result = self.cursor.fetchone()
                #print(result[0])
                #first_release = datetime.strptime(str(result[0]),'%Y-%m-%d %H:%M:%S')
                elapsed = self.getElapsedDays(result[0], completeddate)
                #print(elapsed)
                #elapsed = self.getElapsedDays(first_release, completeddate)
                data = (completeddate,completeddate,elapsed, "Completed",self.doc_id)
                self.cursor.execute("UPDATE DOCUMENT SET LAST_MODIFIED = ?,COMP_DATE = ?, COMP_DAYS = ?, STATUS = ? WHERE DOC_ID = ?",(data))
                #self.db.commit()
                self.parent.repopulateTable()
                self.dispMsg("PCN is now completed")
                self.addNotification(self.doc_id, "Completed")
                self.tab_signature.button_add.setDisabled(True)
                self.tab_notification.button_add.setDisabled(True)
            else:
                self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during check Complete.\n Error: {e}")
            
    def setCommentCount(self):
        self.cursor.execute(f"SELECT COUNT(COMMENT) from COMMENTS where DOC_ID='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tab_widget.setTabText(1, "Comments ("+str(result[0])+")")
    
    def existNotification(self,doc_id):
        self.cursor.execute(f"Select * from NOTIFICATION where DOC_ID='{doc_id}' and STATUS='Not Sent'")
        result = self.cursor.fetchone()
        if result is not None:
            return True
        else:
            return False
        
    def checkFields(self):
        if self.tab_purch_req.line_title.text()=="":
            return False
        if self.tab_purch_req.line_id.text()=="":
            return False
        if self.tab_purch_req.text_details.toPlainText()=="":
            return False
        return True
        
        
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def closeEvent(self, event):
        self.parent.projectWindow = None