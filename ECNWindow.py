from PySide6 import QtWidgets, QtCore, QtWebEngineCore
from datetime import datetime
from AttachmentTab import *
from ECNTab import *
from PurchaserTab import *
from TasksTab import *
from ShopTab import *
from PlannerTab import *
from ChangeLogTab import *
from SignatureTab import *
from PartsTab import *
from CommentTab import *
from NotificationTab import *
from string import Template

class ECNWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, ecn_id = None):
        super(ECNWindow,self).__init__()
        self.parent = parent
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.settings = parent.settings
        self.user_info = self.parent.user_info
        self.windowWidth =  950
        self.windowHeight = 580
        self.ecn_id = ecn_id
        self.tablist = []
        #self.typeindex = {'New Part':0, 'BOM Update':1, 'Firmware Update':2, 'Configurator Update' : 3,'Product EOL':4}
        self.initAtt()
        if self.ecn_id == None:
            self.initReqUI()
            self.generateECNID()
        else:
            self.initFullUI()
            self.getCurrentValues()
            
        self.center()
        self.show()

    def initAtt(self):
        self.setWindowIcon(self.parent.ico)
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle(f"ECN-Viewer - user: {self.parent.user_info['user']}")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMinimumWidth(self.windowWidth)

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
        

    def initReqUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        
        
        self.tabwidget = QtWidgets.QTabWidget(self)
        self.tab_ecn = ECNTab(self)
        self.tab_ecn.line_author.setText(self.parent.user_info['user'])
        self.tab_ecn.box_requestor.setCurrentText(self.parent.user_info['user'])
        self.tab_ecn.line_status.setText("Draft")
        #self.tab_ecn.edit_date.setDate(QtCore.QDate.currentDate())
        #self.tab_ecn.edit_date.setMinimumDate(QtCore.QDate.currentDate())
        self.tab_parts = PartsTab(self)
        self.tab_attach = AttachmentTab(self)
        self.tab_comments = CommentTab(self)
        # self.tab_comments.enterText.setDisabled(True)
        self.tab_signature = SignatureTab(self)
        self.tab_notification = NotificationTab(self)
        #self.tab_changelog = ChangeLogTab(self,self.ecn_id)
        self.button_save = QtWidgets.QPushButton("Save",self)
        self.button_release = QtWidgets.QPushButton("Release")
        self.button_release.setDisabled(True)
        self.button_save.clicked.connect(self.save)
        self.button_release.clicked.connect(self.release)
        self.button_cancel = QtWidgets.QPushButton("Delete")
        self.button_cancel.setDisabled(True)
        self.button_cancel.clicked.connect(self.cancel)
        self.tabwidget.addTab(self.tab_ecn, "ECN")
        self.tabwidget.addTab(self.tab_parts,"Parts")
        self.tabwidget.addTab(self.tab_attach, "Attachment")
        self.tabwidget.addTab(self.tab_comments, "Comments")
        self.tabwidget.addTab(self.tab_signature, "Signatures")
        self.tabwidget.addTab(self.tab_notification, "Notification")
        #self.tabwidget.addTab(self.tab_changelog, "Change Log")
        
        self.tabwidget.setTabVisible(3, False)
        #self.tabwidget.setTabVisible(5, False)
                
        self.tab_purch = PurchaserTab(self)
        self.tab_planner = PlannerTab(self)
        self.tab_shop = ShopTab(self)
        buttonlayout = QtWidgets.QHBoxLayout()
        buttonlayout.addWidget(self.button_save)
        buttonlayout.addWidget(self.button_cancel)
        buttonlayout.addWidget(self.button_release)
        mainlayout.addWidget(self.tabwidget)
        mainlayout.addLayout(buttonlayout)
        
        #self.tab_ecn.combo_dept.currentIndexChanged.connect(self.tab_signature.prepopulateTable)
        
        #self.tab_signature.prepopulateTable()



    def initFullUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        
        self.tabwidget = QtWidgets.QTabWidget(self)
        #self.tabwidget.currentChanged.connect(self.printIndex)
        self.tab_ecn = ECNTab(self)
        self.tab_parts = PartsTab(self)
        self.tab_attach = AttachmentTab(self)
        #self.tab_task = TasksTab(self)
        self.tab_comments = CommentTab(self)
        self.tab_signature = SignatureTab(self)
        self.tab_notification = NotificationTab(self)
        #self.tab_changelog = ChangeLogTab(self,self.ecn_id)
        #self.tab_purch = PurchaserTab(self)
        #self.tab_planner = PlannerTab(self)
        #self.tab_shop = ShopTab(self)
        
        self.tabwidget.addTab(self.tab_ecn, "ECN")
        self.tabwidget.addTab(self.tab_parts, "Parts")
        self.tabwidget.addTab(self.tab_attach, "Attachment")
        #self.tabwidget.addTab(self.tab_task, "Tasks")
        self.tabwidget.addTab(self.tab_comments, "Comments")
        self.tabwidget.addTab(self.tab_signature, "Signatures")
        self.tabwidget.addTab(self.tab_notification, "Notification")
        #self.tabwidget.addTab(self.tab_changelog, "Change Log")
                    
        self.loadData()
        
        mainlayout.addWidget(self.tabwidget)
        buttonlayout = QtWidgets.QHBoxLayout()
        
        #disable signature and attachment adding if not author and completed
        if self.parent.user_info['user']==self.tab_ecn.line_author.text() and self.tab_ecn.line_status.text()!="Completed":
            self.tab_signature.button_add.setEnabled(True)
            self.tab_signature.button_remove.setEnabled(True)
            self.tab_attach.button_add.setEnabled(True)
            self.tab_attach.button_remove.setEnabled(True)
            # self.tab_comments.enterText.setEnabled(True)
            # self.tab_comments.label_enterText.setVisible(True)
            # self.tab_comments.enterText.setVisible(True)
        else:
            self.tab_signature.button_add.setDisabled(True)
            self.tab_signature.button_remove.setDisabled(True)
            self.tab_attach.button_add.setDisabled(True)
            self.tab_attach.button_remove.setDisabled(True)
            # self.tab_comments.enterText.setDisabled(True)
            # self.tab_comments.label_enterText.setVisible(False)
            # self.tab_comments.enterText.setVisible(False)
        
        if self.tab_ecn.line_status.text()!="Completed":
            if self.parent.user_info['user']==self.tab_ecn.line_author.text():
                self.button_save = QtWidgets.QPushButton("Save",self)
                self.button_cancel = QtWidgets.QPushButton("Cancel")
                if self.tab_ecn.line_status.text()=="Draft":
                    self.button_cancel.setText("Delete")
                if self.tab_ecn.line_status.text()!="Rejected" and self.tab_ecn.line_status.text()!="Draft":
                    self.button_cancel.setDisabled(True)
                self.button_release = QtWidgets.QPushButton("Release")
                self.button_save.clicked.connect(self.save)
                self.button_release.clicked.connect(self.release)
                self.button_cancel.clicked.connect(self.cancel)
                self.button_comment = QtWidgets.QPushButton("Add Comment")
                self.button_comment.clicked.connect(self.addUserComment)
                buttonlayout.addWidget(self.button_save)
                buttonlayout.addWidget(self.button_cancel)
                buttonlayout.addWidget(self.button_comment)
                buttonlayout.addWidget(self.button_release)
                if self.tab_signature.table.rowCount()==0:
                    self.button_release.setDisabled(True)
                self.tab_ecn.line_ecntitle.setReadOnly(False)
                self.tab_ecn.text_reason.setReadOnly(False)
                self.tab_ecn.text_summary.setReadOnly(False)
                if self.tab_ecn.line_status.text()=="Out For Approval":
                    self.button_release.setDisabled(True)
                    self.tab_signature.button_add.setDisabled(True)
                    self.tab_signature.button_remove.setDisabled(True)
            else:
                self.button_approve = QtWidgets.QPushButton("Approve")
                self.button_approve.clicked.connect(self.approve)
                self.button_reject = QtWidgets.QPushButton("Reject to Author",self)
                self.button_comment = QtWidgets.QPushButton("Add Comment")
                self.button_comment.clicked.connect(self.addUserComment)
                self.button_reject.clicked.connect(self.reject)
                self.button_save = QtWidgets.QPushButton("Save")
                self.button_save.clicked.connect(self.notificationSave)
                buttonlayout.addWidget(self.button_approve)
                buttonlayout.addWidget(self.button_reject)
                buttonlayout.addWidget(self.button_comment)
                buttonlayout.addWidget(self.button_save)
                self.tab_ecn.line_ecntitle.setReadOnly(True)
                self.tab_ecn.text_summary.setReadOnly(True)
                self.tab_ecn.text_reason.setReadOnly(True)
                self.tab_ecn.box_requestor.setDisabled(True)
                self.tab_ecn.combo_type.setDisabled(True)
                self.tab_parts.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
                self.tab_parts.button_remove.setDisabled(True)
                self.tab_parts.button_add.setDisabled(True)
                self.tab_signature.button_add.setDisabled(True)
                self.tab_signature.button_remove.setDisabled(True)
                if self.tab_ecn.line_status.text()=="Rejected":
                    self.button_reject.setDisabled(True)
                    self.button_approve.setDisabled(True)
                if self.isUserSignable():
                    if self.hasUserSigned():
                        self.button_approve.setDisabled(True)
                    else:
                        self.button_approve.setDisabled(False)
                else:
                    self.button_approve.setDisabled(True)
                    self.button_reject.setDisabled(True)
        self.button_exportHTML = QtWidgets.QPushButton("Export")
        self.button_exportHTML.clicked.connect(self.exportHTML)
        
        # self.button_move_stage = QtWidgets.QPushButton("Move Stage")
        # self.button_move_stage.clicked.connect(self.moveECNStage)
        buttonlayout.addWidget(self.button_exportHTML)
        # buttonlayout.addWidget(self.button_move_stage)
            
        mainlayout.addLayout(buttonlayout)
        self.setCommentCount()
        self.setPartCount()
        self.setAttachmentCount()        

    def printIndex(self):
        print(self.tabwidget.currentIndex())
        
    def togglePurchTab(self):
        if self.tab_ecn.cbpurch.isChecked():
            self.tabwidget.insertTab(len(self.tablist)+2,self.tab_purch, "Purchasing")
            self.tablist.append("purch")
        else:
            self.tabwidget.removeTab(self.tablist.index("purch")+2)
            self.tablist.remove("purch")

    def togglePlannerTab(self):
        if self.tab_ecn.cbplanner.isChecked():
            self.tabwidget.insertTab(len(self.tablist)+2,self.tab_planner, "Planner")
            self.tablist.append("planner")
        else:
            self.tabwidget.removeTab(self.tablist.index("planner")+2)
            self.tablist.remove("planner")

    def toggleShopTab(self):
        if self.tab_ecn.cbshop.isChecked():
            self.tabwidget.insertTab(len(self.tablist)+2,self.tab_shop, "Shop")
            self.tablist.append("shop")
        else:
            self.tabwidget.removeTab(self.tablist.index("shop")+2)
            self.tablist.remove("shop")

    def generateECNID(self):
        date_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.ecn_id = 'ECN-'+date_time[2:]
        self.tab_ecn.line_id.setText(self.ecn_id)

    def insertData(self):
        #inserting to ECN table
        try:
            ecn_type = self.tab_ecn.combo_type.currentText()
            author = self.tab_ecn.line_author.text()
            requestor = self.tab_ecn.box_requestor.currentText()
            status = 'Draft'
            title = self.tab_ecn.line_ecntitle.text()
            reason =self.tab_ecn.text_reason.toPlainText()
            summary = self.tab_ecn.text_summary.toPlainText()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dept = self.tab_ecn.combo_dept.currentText()

            data = (self.ecn_id,dept,ecn_type,author,requestor,status,title,reason,summary,modifieddate)
            self.cursor.execute("INSERT INTO ECN(ECN_ID,DEPARTMENT,ECN_TYPE,AUTHOR,REQUESTOR,STATUS,ECN_TITLE,ECN_REASON,ECN_SUMMARY,LAST_MODIFIED) VALUES(?,?,?,?,?,?,?,?,?,?)",(data))
            self.db.commit()
            
            if self.tab_parts.table.rowCount()>0:
                self.addParts()
                self.setPartCount()
            
            if self.tab_attach.table.rowCount()>0:
                for x in range(self.tab_attach.table.rowCount()):
                    filename = self.tab_attach.table.item(x, 0).text()
                    filepath = self.tab_attach.table.item(x, 1).text()
                    data = (self.ecn_id, filename, filepath)
                    self.cursor.execute("INSERT INTO ATTACHMENTS(ECN_ID,FILENAME,FILEPATH) VALUES(?,?,?)",(data))
                    self.db.commit()
                    self.setAttachmentCount()
            #print('data inserted')
            # if self.tab_comments.enterText.toPlainText()!="":
            #     self.addComment(ecn_id,self.tab_comments.enterText.toPlainText(),"Author")
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData)!\n Error: {e}")
        
    def approve(self):
        try:
            approvedate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = (approvedate,self.ecn_id,self.parent.user_info['user'])
            self.cursor.execute("UPDATE SIGNATURE SET SIGNED_DATE = ? WHERE ECN_ID = ? and USER_ID = ?",(data))
            self.cursor.execute(f"UPDATE ECN SET LAST_MODIFIED = '{approvedate}' where ECN_ID='{self.ecn_id}'")
            self.tab_signature.repopulateTable()
            self.dispMsg("ECN has been signed!")
            self.button_approve.setDisabled(True)
            self.checkComplete()
            self.db.commit()
            print("moving ecn stage check")
            self.moveECNStage()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (approve)!\n Error: {e}")
    
    def reject(self):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            self.addComment(self.ecn_id, comment,"Rejecting to author")
            try:
                modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = (modifieddate, "Rejected",self.ecn_id)
                self.cursor.execute("UPDATE ECN SET LAST_MODIFIED = ?, STATUS = ? WHERE ECN_ID = ?",(data))
                self.cursor.execute(f"UPDATE SIGNATURE SET SIGNED_DATE=Null where ECN_ID='{self.ecn_id}'")
                self.db.commit()
                self.setECNStage(0)
                self.parent.repopulateTable()
                self.dispMsg("Rejection successful. Setting ECN stage to 0 and all signatures have been removed.")
                self.tab_ecn.line_status.setText("Rejected")
                self.addNotification(self.ecn_id, "Rejected To Author")
                self.button_reject.setDisabled(True)
                self.button_approve.setDisabled(True)
            except Exception as e:
                print(e)
                self.dispMsg(f"Error occured during data update (reject)!\n Error: {e}")
        if ok and comment=="":
            self.dispMsg("Rejection failed: comment field was left blank.")
                  
    
    def AddSignatures(self):
        #inserting to signature table
        #SIGNATURE(ECN_ID TEXT, NAME TEXT, USER_ID TEXT, HAS_SIGNED TEXT, SIGNED_DATE TEXT)
        try:
            #get current values in db
            current_list = []
            self.cursor.execute(f"SELECT USER_ID FROM SIGNATURE WHERE ECN_ID='{self.ecn_id}' and TYPE='Signing'")
            results = self.cursor.fetchall()
            for result in results:
                current_list.append(result[0])
            #print('current list',current_list)
            #get new values
            new_list = []
            for x in range(self.tab_signature.table.rowCount()):
                if isinstance(self.tab_signature.table.item(x, 0),QtWidgets.QTableWidgetItem):
                    job_title = self.tab_signature.table.item(x, 0).text()
                    name = self.tab_signature.table.item(x,1).text()
                    user_id = self.tab_signature.table.item(x,2).text()
                else:
                    job_title = self.tab_signature.table.cellWidget(x, 0).currentText()
                    name = self.tab_signature.table.cellWidget(x,1).currentText()
                    user_id = self.tab_signature.table.cellWidget(x,2).currentText()
                new_list.append((self.ecn_id,job_title,name,user_id,"Signing"))
            #print('new list',new_list)
            
            for element in new_list:
                if element[3] not in current_list:
                    print(f'insert {element[3]} into signature db')
                    self.cursor.execute("INSERT INTO SIGNATURE(ECN_ID,JOB_TITLE,NAME,USER_ID,TYPE) VALUES(?,?,?,?,?)",(element))
            for element in current_list:
                no_match = True
                for elements in new_list:
                    if element == elements[3]:
                        no_match = False
                if no_match:
                    print(f"remove {element} from signature db")
                    self.cursor.execute(f"DELETE FROM SIGNATURE WHERE ECN_ID = '{self.ecn_id}' and USER_ID='{element}'")
                    
                    
            current_list = []
            self.cursor.execute(f"SELECT USER_ID FROM SIGNATURE WHERE ECN_ID='{self.ecn_id}' and TYPE='Notify'")
            results = self.cursor.fetchall()
            for result in results:
                current_list.append(result[0])
            
            new_list = []
            for x in range(self.tab_notification.table.rowCount()):
                if isinstance(self.tab_notification.table.item(x, 0),QtWidgets.QTableWidgetItem):
                    job_title = self.tab_notification.table.item(x, 0).text()
                    name = self.tab_notification.table.item(x,1).text()
                    user_id = self.tab_notification.table.item(x,2).text()
                else:
                    job_title = self.tab_notification.table.cellWidget(x, 0).currentText()
                    name = self.tab_notification.table.cellWidget(x,1).currentText()
                    user_id = self.tab_notification.table.cellWidget(x,2).currentText()
                new_list.append((self.ecn_id,job_title,name,user_id,"Notify"))
                
            for element in new_list:
                if element[3] not in current_list:
                    print(f'insert {element[3]} into notify db')
                    self.cursor.execute("INSERT INTO SIGNATURE(ECN_ID,JOB_TITLE,NAME,USER_ID,TYPE) VALUES(?,?,?,?,?)",(element))
            for element in current_list:
                no_match = True
                for elements in new_list:
                    if element == elements[3]:
                        no_match = False
                if no_match:
                    print(f"remove {element} from notify db")
                    self.cursor.execute(f"DELETE FROM SIGNATURE WHERE ECN_ID = '{self.ecn_id}' and USER_ID='{element}'")
            
            self.db.commit()
            print('data updated')
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (signature)!\n Error: {e}")
            
    def addParts(self):
        try:
            self.cursor.execute("DELETE FROM PARTS WHERE ECN_ID = '" + self.ecn_id + "'")
            self.db.commit()
            for x in range(self.tab_parts.table.rowCount()):
                part = self.tab_parts.table.item(x, 0).text()
                desc = self.tab_parts.table.item(x, 1).text()
                print(x,part,desc,self.tab_parts.table.item(x,2))
                if isinstance(self.tab_parts.table.item(x, 2),QtWidgets.QTableWidgetItem):
                    ptype = self.tab_parts.table.item(x, 2).text()
                    disposition = self.tab_parts.table.item(x, 3).text()
                    insp = self.tab_parts.table.item(x,8).text()
                else:
                    ptype = self.tab_parts.table.cellWidget(x, 2).currentText()
                    disposition = self.tab_parts.table.cellWidget(x, 3).currentText()
                    insp = self.tab_parts.table.cellWidget(x, 8).currentText()
                mfg = self.tab_parts.table.item(x,4).text()
                mfg_part = self.tab_parts.table.item(x,5).text()
                rep = self.tab_parts.table.item(x,6).text()
                ref = self.tab_parts.table.item(x,7).text()
                data = (self.ecn_id, part, desc,ptype,disposition,mfg,mfg_part,rep,ref,insp)
                self.cursor.execute("INSERT INTO PARTS(ECN_ID,PART_ID,DESC,TYPE,DISPOSITION,MFG,MFG_PART,REPLACING,REFERENCE,INSPEC) VALUES(?,?,?,?,?,?,?,?,?,?)",(data))
            self.db.commit()
            #self.tab_parts.repopulateTable()
            self.tab_parts.setStatusColor()
            #print('data inserted')
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (parts)!\n Error: {e}")

    def updateData(self):
        try:
            ecn_type = self.tab_ecn.combo_type.currentText()
            dept = self.tab_ecn.combo_dept.currentText()
            requestor = self.tab_ecn.box_requestor.currentText()
            title = self.tab_ecn.line_ecntitle.text()
            reason =self.tab_ecn.text_reason.toPlainText()
            summary = self.tab_ecn.text_summary.toPlainText()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = (dept,ecn_type,requestor,title,reason,summary,modifieddate,self.ecn_id)

            #data = (self.combo_type.currentText(),self.box_requestor.text(),self.date_request.date().toString("yyyy-MM-dd"),'Unassigned',self.line_ecntitle.text(),self.text_detail.toPlainText(),self.line_id.text())
            self.cursor.execute("UPDATE ECN SET DEPARTMENT = ?, ECN_TYPE = ?, REQUESTOR = ?, ECN_TITLE = ?, ECN_REASON = ?, ECN_SUMMARY = ?, LAST_MODIFIED = ? WHERE ECN_ID = ?",(data))
            self.db.commit()
            
            if self.tab_parts.table.rowCount()>0:
                self.addParts()
                self.setPartCount()
            
            if self.tab_attach.table.rowCount()>0:
                self.cursor.execute("DELETE FROM ATTACHMENTS WHERE ECN_ID = '" + self.ecn_id + "'")
                self.db.commit()
                for x in range(self.tab_attach.table.rowCount()):
                    filename = self.tab_attach.table.item(x, 0).text()
                    filepath = self.tab_attach.table.item(x, 1).text()
                    data = (self.ecn_id, filename, filepath)
                    self.cursor.execute("INSERT INTO ATTACHMENTS(ECN_ID,FILENAME,FILEPATH) VALUES(?,?,?)",(data))
                    self.db.commit()
                    self.setAttachmentCount()
                    
            # if self.tab_comments.enterText.toPlainText()!="":
            #     self.addComment(self.ecn_id,self.tab_comments.enterText.toPlainText(),"Author")
                
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (updateData)!\n Error: {e}")

    def loadData(self):
        command = "Select * from ECN where ECN_ID = '"+self.ecn_id +"'"
        self.cursor.execute(command)
        results = self.cursor.fetchone()
        self.tab_ecn.line_id.setText(results['ECN_ID'])
        #self.tab_ecn.combo_type.setCurrentIndex(self.typeindex[results['ECN_TYPE']])
        self.tab_ecn.combo_type.setCurrentText(results['ECN_TYPE'])
        self.tab_ecn.line_ecntitle.setText(results['ECN_TITLE'])
        self.tab_ecn.text_reason.setText(results['ECN_REASON'])
        self.tab_ecn.text_summary.setText(results['ECN_SUMMARY'])
        self.tab_ecn.line_author.setText(results['AUTHOR'])
        self.tab_ecn.box_requestor.setEditText(results['REQUESTOR'])
        self.tab_ecn.line_status.setText(results['STATUS'])
        if results['DEPARTMENT'] is not None:
            self.tab_ecn.combo_dept.setCurrentText(results['DEPARTMENT'])
        
        self.tab_signature.repopulateTable()
        self.tab_notification.repopulateTable()
        # command = "Select * from SIGNATURE where ECN_ID= '"+self.ecn_id +"'"
        # self.cursor.execute(command)
        # results = self.cursor.fetchall()
        # self.tab_signature.table.setRowCount(len(results))
        # rowcount=0
        # for result in results:
        #     #print(result['JOB_TITLE'],result['SIGNED_DATE'])
        #     self.tab_signature.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['JOB_TITLE']))
        #     self.tab_signature.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['NAME']))
        #     self.tab_signature.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['USER_ID']))
        #     self.tab_signature.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['SIGNED_DATE']))
        #     rowcount+=1
            
        self.tab_parts.repopulateTable()
        # command = "Select * from PARTS where ECN_ID= '"+self.ecn_id +"'"
        # self.cursor.execute(command)
        # results = self.cursor.fetchall()
        # self.tab_parts.table.setRowCount(len(results))
        # rowcount=0
        # for result in results:
        #     self.tab_parts.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['PART_ID']))
        #     self.tab_parts.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['DESC']))
        #     self.tab_parts.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['TYPE']))
        #     self.tab_parts.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['DISPOSITION']))
        #     self.tab_parts.table.setItem(rowcount, 4, QtWidgets.QTableWidgetItem(result['MFG']))
        #     self.tab_parts.table.setItem(rowcount, 5, QtWidgets.QTableWidgetItem(result['MFG_PART']))
        #     rowcount+=1
        
        self.tab_attach.repopulateTable()
        # command = "Select * from ATTACHMENTS where ECN_ID= '"+self.ecn_id +"'"
        # self.cursor.execute(command)
        # results = self.cursor.fetchall()
        # self.tab_attach.table.setRowCount(len(results))
        # rowcount=0
        # for result in results:
        #     self.tab_attach.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['FILENAME']))
        #     self.tab_attach.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['FILEPATH']))
        #     rowcount+=1
            
        self.loadComments()    
        
    def addUserComment(self):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            self.addComment(self.ecn_id, comment,"User Comment")

    def addComment(self,ecn_id,comment,commentType):
        #COMMENTS(ECN_ID TEXT, NAME TEXT, USER TEXT, COMM_DATE DATE, COMMENT TEXT
        data = (ecn_id, self.parent.user_info['user'],datetime.now().strftime('%Y-%m-%d %H:%M:%S'),comment,commentType)
        self.cursor.execute("INSERT INTO COMMENTS(ECN_ID, USER, COMM_DATE, COMMENT,TYPE) VALUES(?,?,?,?,?)",(data))
        self.db.commit()
        # self.tab_comments.enterText.clear()
        self.tab_comments.mainText.clear()
        self.loadComments()
        self.setCommentCount()
        
    def setCommentCount(self):
        self.cursor.execute(f"SELECT COUNT(COMMENT) from COMMENTS where ECN_ID='{self.ecn_id}'")
        result = self.cursor.fetchone()
        self.tabwidget.setTabText(3, "Comments ("+str(result[0])+")")
        
    def setPartCount(self):
        self.cursor.execute(f"SELECT COUNT(PART_ID) from PARTS where ECN_ID='{self.ecn_id}'")
        result = self.cursor.fetchone()
        self.tabwidget.setTabText(1, "Parts ("+str(result[0])+")")
        
    def setAttachmentCount(self):
        self.cursor.execute(f"SELECT COUNT(FILENAME) from ATTACHMENTS where ECN_ID='{self.ecn_id}'")
        result = self.cursor.fetchone()
        self.tabwidget.setTabText(2, "Attachments ("+str(result[0])+")")
            
    def loadComments(self):
            # self.tab_comments.enterText.clear()
            self.tab_comments.mainText.clear()
            command = "Select * from COMMENTS where ECN_ID = '" + self.ecn_id+"'"
            self.cursor.execute(command)
            results = self.cursor.fetchall()
            for result in results:
                # if self.tab_ecn.line_author.text() == result['USER']:
                #     self.tab_comments.mainText.setTextColor(QtGui.QColor(0,0,255))
                # else:
                if result['TYPE']=="Reject":
                    self.tab_comments.mainText.setTextColor(QtGui.QColor(255,0,0))
                else:
                    self.tab_comments.mainText.setTextColor(QtGui.QColor(0,0,255))
                self.tab_comments.mainText.append(">>  " + result['TYPE'] + " : " + result['COMMENT'] + "\r    :: " + result['USER']+ " - " + result['COMM_DATE'] +"\r\r")
                
    def cancel(self):
        if self.tab_ecn.line_status.text()=="Draft":
            self.deleteECN(self.ecn_id)
            self.close()
        else:
            self.cancelECN(self.ecn_id)
        
    def deleteECN(self,ecn_id):
        try:
            self.cursor.execute(f"DELETE FROM ECN where ECN_ID='{ecn_id}'")
            self.cursor.execute(f"DELETE FROM COMMENTS where ECN_ID='{ecn_id}'")
            self.cursor.execute(f"DELETE FROM SIGNATURE where ECN_ID='{ecn_id}'")
            self.cursor.execute(f"DELETE FROM ATTACHMENTS where ECN_ID='{ecn_id}'")
            self.cursor.execute(f"DELETE FROM CHANGELOG where ECN_ID='{ecn_id}'")
            self.db.commit()
            self.dispMsg("ECN has been deleted")
            self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Problems occured trying to delete ECN.\n Error: {e}")
        
    def cancelECN(self,ecn_id):
        try:
            self.cursor.execute(f"UPDATE ECN SET STATUS='Canceled' where ECN_ID='{ecn_id}'")
            self.db.commit()
            self.dispMsg("ECN has been canceled")
            self.tab_ecn.line_status.setText("Canceled")
            self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Problems occured trying to cancel ECN.\n Error:{e}")
        
    def release(self):
        try:
            self.save(1)
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.cursor.execute(f"SELECT FIRST_RELEASE from ECN where ECN_ID='{self.ecn_id}'")
            result = self.cursor.fetchone()
            if result[0] is None:
                self.cursor.execute(f"UPDATE ECN SET FIRST_RELEASE = '{modifieddate}' where ECN_ID='{self.ecn_id}'")
            data = (modifieddate, "Out For Approval",self.ecn_id)
            self.cursor.execute("UPDATE ECN SET LAST_MODIFIED = ?, STATUS = ? WHERE ECN_ID = ?",(data))
            self.db.commit()
            currentStage = self.getECNStage()
            if currentStage==0:
                self.setECNStage(self.getNextStage()[0])
                self.addNotification(self.ecn_id, "Stage Moved")
            self.tab_ecn.line_status.setText("Out For Approval")
            self.parent.repopulateTable()
            self.dispMsg("ECN has been saved and sent out for signing!")
            #self.addNotification(self.ecn_id, "Released")
            self.button_release.setDisabled(True)
            self.button_cancel.setText("Cancel")
            self.button_cancel.setDisabled(True)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (release)!\n Error: {e}")
            
    def getECNStage(self):
        try:
            self.cursor.execute(f"Select TEMPSTAGE from ECN where ECN_ID='{self.ecn_id}'")
            result = self.cursor.fetchone()
            print("current stage",result[0])
            if result[0] is None:
                return 0
            else:
                return result[0]
        except Exception as e:
            self.dispMsg(f"Error trying to get ECN stage. Error: {e}")
    
    def getTitlesForStage(self):
        titles = {}
        for key, value in self.parent.stageDict.items():
            if value not in titles:
                titles[value] = [key]
            else:
                titles[value].append(key)
        print("titles generated", titles)
        return titles
    
    def moveECNStage(self):
        curStage = self.getECNStage()
        titles = self.getTitlesForStage()
        titles = titles[str(curStage)]
        print("here are the titles",titles)
        move = True
        for title in titles:
            self.cursor.execute(f"Select SIGNED_DATE from SIGNATURE where ECN_ID = '{self.ecn_id}' and JOB_TITLE='{title}' and TYPE='Signing'")
            results = self.cursor.fetchall()
            for result in results:
                print(result['SIGNED_DATE'])
                if result['SIGNED_DATE'] is None:
                    move = False
                    print("not moving to next stage")
                    break
        if move:
            nextStages = self.getNextStage()
            if len(nextStages)>0:
                print("moving to stage:", nextStages[0])
                self.setECNStage(nextStages[0])
                self.addNotification(self.ecn_id, "Stage Moved")
            else:
                print("this is the last stage")
            
    def getNextStage(self):
        self.cursor.execute(f"Select JOB_TITLE from SIGNATURE where ECN_ID='{self.ecn_id}' and SIGNED_DATE is NULL and TYPE='Signing'")
        results = self.cursor.fetchall()
        stage = []
        for result in results:
            #print(result[0])
            stage.append(self.parent.stageDict[result[0]])
        stage = sorted(stage)
        print(stage)
        return stage
    
    def setECNStage(self,stage):
        try:
            print('setting ecn to ', stage)
            self.cursor.execute(f"UPDATE ECN SET STAGE ='{stage}', TEMPSTAGE = '{stage}' where ECN_ID='{self.ecn_id}'")
            self.db.commit()
        except Exception as e:
            self.dispMsg(f"Error trying to set ECN stage. Error: {e}")
            
    def resetECNStage(self):
        try:
            print('resetting ecn stage')
            self.cursor.execute(f"UPDATE ECN SET STAGE = Null, TEMPSTAGE = Null where ECN_ID='{self.ecn_id}'")
            self.db.commit()
        except Exception as e:
            self.dispMsg(f"Error trying to reset ECN stage. Error: {e}")
    
    def isUserSignable(self):
        curStage = self.getECNStage()
        print(curStage)
        if curStage == 0:
            return False
        titles = self.getTitlesForStage()
        titles = titles[str(curStage)]
        self.cursor.execute(f"SELECT USER_ID from SIGNATURE where ECN_ID='{self.ecn_id}' and USER_ID='{self.parent.user_info['user']}'")
        result = self.cursor.fetchone()
        if self.parent.user_info['title'] in titles and result is not None:
            return True
        return False
            
    def hasUserSigned(self):
        self.cursor.execute(f"SELECT SIGNED_DATE from SIGNATURE where ECN_ID='{self.ecn_id}' and USER_ID='{self.parent.user_info['user']}'")
        result = self.cursor.fetchone()
        if result is None or result[0] is None:
            print("found none returning false")
            return False
        else:
            return True
            
    def getCurrentValues(self):
        #print('getting values')
        self.now_type = self.tab_ecn.combo_type.currentText()
        self.now_title = self.tab_ecn.line_ecntitle.text()
        self.now_req_details = self.tab_ecn.text_reason.toPlainText()
        #print(self.now_type)
        #print(self.now_title)
        #print(self.now_req_details)
        
    def checkComplete(self):
        try:
            command = f"Select * from SIGNATURE where ECN_ID ='{self.ecn_id}' and TYPE='Signing'"
            self.cursor.execute(command)
            results = self.cursor.fetchall()
            completed = True
            for result in results:
                if result['SIGNED_DATE'] == None or result['SIGNED_DATE']== "":
                    completed = False
            if completed:
                completeddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute(f"select FIRST_RELEASE from ECN where ECN_ID='{self.ecn_id}'")
                result = self.cursor.fetchone()
                #print(result[0])
                #first_release = datetime.strptime(str(result[0]),'%Y-%m-%d %H:%M:%S')
                elapsed = self.getElapsedDays(result[0], completeddate)
                print(elapsed)
                #elapsed = self.getElapsedDays(first_release, completeddate)
                data = (completeddate,completeddate,elapsed, "Completed",self.ecn_id)
                self.cursor.execute("UPDATE ECN SET LAST_MODIFIED = ?,COMP_DATE = ?, COMP_DAYS = ?, STATUS = ? WHERE ECN_ID = ?",(data))
                #self.db.commit()
                self.parent.repopulateTable()
                self.dispMsg("ECN is now completed")
                self.addNotification(self.ecn_id, "Completed")
            else:
                self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during check Complete.\n Error: {e}")
            
    def getElapsedDays(self,day1,day2):
        #today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        day1 = datetime.strptime(day1,'%Y-%m-%d %H:%M:%S')
        day2 = datetime.strptime(day2,'%Y-%m-%d %H:%M:%S')
        if day2>day1:
            elapsed = day2 - day1
        else:
            elapsed = day1 - day2
        #print(elapsed.days)
        return elapsed.days + round(elapsed.seconds/86400,2)
            

    # def submitAndClose(self):
    #     self.submit()
    #     self.close()

    # def submit(self):
    #     if not self.checkEcnID():
    #         self.insertData()
    #         self.AddSignatures()
    #         self.parent.repopulateTable()
    #     else:
    #         self.dispMsg("ECN ID already exists")
    
    def checkSigNotiDuplicate(self):
        sigs = []
        for row in range(self.tab_signature.table.rowCount()):
            if isinstance(self.tab_signature.table.item(row, 2),QtWidgets.QTableWidgetItem):
                sigs.append(self.tab_signature.table.item(row, 2).text())
            else:
                sigs.append(self.tab_signature.table.cellWidget(row, 2).currentText())
        for row in range(self.tab_notification.table.rowCount()):
            if isinstance(self.tab_notification.table.item(row, 2),QtWidgets.QTableWidgetItem):
                sigs.append(self.tab_notification.table.item(row, 2).text())
            else:
                sigs.append(self.tab_notification.table.cellWidget(row, 2).currentText())
        #print(sigs)
        if len(sigs)==len(set(sigs)):
            return False
        else:
            return True
        
    def checkAllFields(self):
        if not self.tab_parts.checkFields():
            self.dispMsg("Error: Empty fields in parts tab. Please fill them in and try again.")
            return False
        if self.checkSigNotiDuplicate():
            self.dispMsg("Error: Duplicate user found in Signature and Notifications. Please remove the duplicate before trying again.")
            return False
        return True
    
    def notificationSave(self):
        if self.checkSigNotiDuplicate():
            self.dispMsg("Error: Duplicate user found in Signature and Notifications. Please remove the duplicate before trying again.")
        else:
            self.AddSignatures()
            self.dispMsg("ECN has been updated!")

    def save(self,msg = None):
        if not self.checkEcnID():
            if self.checkAllFields():
                self.insertData()
                if self.checkSigNotiDuplicate():
                    self.dispMsg("Error: Duplicate user found in Signature and Notifications. Please remove the duplicate before trying again.")
                else:
                    self.AddSignatures()
                    if not msg:
                        self.dispMsg("ECN has been saved!")
                    self.tabwidget.setTabVisible(3, True)
                    self.parent.repopulateTable()
                    if self.tab_signature.table.rowCount()>0:
                        self.button_release.setDisabled(False)
                    self.button_cancel.setDisabled(False)
        else:
            if self.checkAllFields():
                self.updateData()
                if self.checkSigNotiDuplicate():
                    self.dispMsg("Error: Duplicate user found in Signature and Notifications. Please remove the duplicate before trying again.")
                else:
                    self.AddSignatures()
                    if not msg:
                        self.dispMsg("ECN has been updated!")
                    if self.tab_signature.table.rowCount()>0:
                        self.button_release.setDisabled(False)
                    #self.getCurrentValues()
                    #self.checkDiff()
                    self.parent.repopulateTable()

    def saveAndClose(self):
        self.save()
        self.close()

    def exportHTML(self):
        try:
            foldername = QtWidgets.QFileDialog().getExistingDirectory()
            if foldername:
                template_loc = os.path.join(self.parent.programLoc,'templates','template.html')
                with open(template_loc) as f:
                    lines = f.read() 
                    #print(lines)
                    f.close()

                    t = Template(lines)
                    id = self.ecn_id
                    self.cursor.execute(f"SELECT * from ECN where ECN_ID='{self.ecn_id}'")
                    result = self.cursor.fetchone()
                    title = result['ECN_TITLE']
                    author = result['AUTHOR']
                    dept = result['DEPARTMENT']
                    requestor = result['REQUESTOR']
                    reason = result['ECN_REASON']
                    summary = result['ECN_SUMMARY']
                    # title = self.tab_ecn.line_ecntitle.text()
                    # author = self.tab_ecn.line_author.text()
                    # dept = self.tab_ecn.combo_dept.currentText()
                    # requestor = self.tab_ecn.box_requestor.currentText()
                    #316 front html wrapper characters and 14 ending html wrapper from qt.tohtml
                    # reason = self.tab_ecn.text_reason.toHtml()[330:-14]
                    # summary = self.tab_ecn.text_summary.toHtml()[330:-14]
                    signature = "<tr>"
                    attachment ="<tr>"
                    parts = ""
                    
                    #parts
                    #print('exporting parts')
                    self.cursor.execute(f"SELECT * from PARTS where ECN_ID='{self.ecn_id}'")
                    results = self.cursor.fetchall()
                    if results is not None:
                        for result in results:
                            text = f"<p> {result['PART_ID']}</p>"
                            text += "<ul>"
                            text += f"<li>Desc: {result['DESC']}</li>"
                            text += f"<li>Type: {result['TYPE']}</li>"
                            text += f"<li>Disposition: {result['DISPOSITION']}</li>"
                            text += f"<li>Inspection Req.: {result['INSPEC']}</li>"
                            text += f"<li>Mfg.: {result['MFG']}</li>"
                            text += f"<li>Mfg.#: {result['MFG_PART']}</li>"
                            text += f"<li>Replacing: {result['REPLACING']}</li>"
                            text += "</ul>"
                            parts += text
                    

                    #attachments
                    #print('exporting attachments')
                    self.cursor.execute(f"SELECT * FROM ATTACHMENTS where ECN_ID='{self.ecn_id}'")
                    results = self.cursor.fetchall()
                    if results is not None:
                        for result in results:
                            attachment += "<td>"+result['FILENAME']+"</td>"
                            attachment += "<td>"+result['FILEPATH']+"</td></tr>"
                    else:
                        attachment="<tr><td></td><td></td></tr>"

                    
                    #print('exporting signatures')
                    self.cursor.execute(f"SELECT * from SIGNATURE where ECN_ID='{self.ecn_id}' and TYPE='Signing'")
                    results = self.cursor.fetchall()
                    if results is not None:
                        for result in results:
                            signature += "<td>"+result['JOB_TITLE']+"</td>"
                            signature += "<td>"+result['NAME']+"</td>"
                            if result['SIGNED_DATE'] is not None:
                                signature += "<td>"+str(result['SIGNED_DATE'])+"</td></tr>"
                            else:
                                signature += "<td></td></tr>"
                    else:
                        signature="<tr><td></td><td></td><td></td></tr>"
                        
                    
                    #print('substituting text')
                    
                    export = t.substitute(ECNID=id,ECNTitle=title,Requestor=requestor,Department=dept,Author=author, Reason=reason,Summary=summary,Parts=parts,Attachment=attachment,Signature=signature)
                
                    with open(foldername+'\\'+id+'.html', 'w') as f:
                        f.write(export)
                        f.close()
                        
                        
                    page = QtWebEngineCore.QWebEnginePage()
                    
                    def handle_load_finished(status):
                        if status:
                            page.printToPdf(foldername+'\\'+id+'.pdf')
                            os.remove(foldername+'\\'+id+'.html')
                            
                    page.loadFinished.connect(handle_load_finished)
                    page.load(QtCore.QUrl.fromLocalFile(foldername+'\\'+id+'.html'))
                    
                    self.dispMsg("Export Completed!")
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during ecn export.\n Error: {e}")
        
    def addNotification(self,ecn_id,notificationType,userslist=None):
        if userslist is not None:
            if type(userslist)==type([]):
                users = ""
                count = 0
                for user in usersList:
                    users +=","
                    if count<len(usersList)-1:
                        users +=","
                    count+=1
            else:
                users = userslist
        if self.existNotification(ecn_id):
            if userslist is not None:
                data = (notificationType,users,ecn_id)
                self.cursor.execute("UPDATE NOTIFICATION SET TYPE = ? USERS = ? WHERE ECN_ID = ?",(data))
            else:
                data = (notificationType,ecn_id)
                self.cursor.execute("UPDATE NOTIFICATION SET TYPE = ? WHERE ECN_ID = ?",(data))
        else:
            if userslist is not None:
                data = (ecn_id,"Not Sent",notificationType, users)
                self.cursor.execute("INSERT INTO NOTIFICATION(ECN_ID, STATUS, TYPE, USERS) VALUES(?,?,?,?)",(data))
            else:
                data = (ecn_id,"Not Sent",notificationType)
                self.cursor.execute("INSERT INTO NOTIFICATION(ECN_ID, STATUS, TYPE) VALUES(?,?,?)",(data))
        self.db.commit()
        
    def existNotification(self,ecn_id):
        self.cursor.execute(f"Select * from NOTIFICATION where ECN_ID='{ecn_id}' and STATUS='Not Sent'")
        result = self.cursor.fetchone()
        if result is not None:
            return True
        else:
            return False


    def checkDiff(self):
        ecn_id = self.ecn_id
        changedate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = self.parent.user_info['user']
        prevdata = self.now_type
        newdata = self.tab_ecn.combo_type.currentText()
        if newdata != prevdata:
            data = (ecn_id,changedate,user,prevdata,newdata)
            self.cursor.execute("INSERT INTO CHANGELOG(ECN_ID, CHANGEDATE, NAME, PREVDATA, NEWDATA) VALUES(?,?,?,?,?)",(data))
            print('adding type change')
        prevdata = self.now_title
        newdata = self.tab_ecn.line_ecntitle.text()
        if newdata != prevdata:
            data = (ecn_id,changedate,user,prevdata,newdata)
            self.cursor.execute("INSERT INTO CHANGELOG(ECN_ID, CHANGEDATE, NAME, PREVDATA, NEWDATA) VALUES(?,?,?,?,?)",(data))
            print('adding title change')
        prevdata = self.now_req_details
        newdata = self.tab_ecn.text_reason.toPlainText()  
        if newdata != prevdata:
            data = (ecn_id,changedate,user,prevdata,newdata)
            self.cursor.execute("INSERT INTO CHANGELOG(ECN_ID, CHANGEDATE, NAME, PREVDATA, NEWDATA) VALUES(?,?,?,?,?)",(data))
            print('adding detail change')
        self.db.commit()
        self.tab_changelog.repopulateTable()
        


    def checkEcnID(self):
        command = "select ECN_ID from ECN where ECN_ID = '" + self.ecn_id + "'"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        if len(results)!=0:
            return True
        else:
            return False

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def closeEvent(self, event):
        self.parent.ecnWindow = None