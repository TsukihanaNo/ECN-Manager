from PySide6 import QtWidgets, QtCore
from datetime import datetime
from AttachmentTab import *
from ECNTab import *
from PurchaserTab import *
from TasksTab import *
from ShopTab import *
from PlannerTab import *
from ChangeLogTab import *
from SignatureTab import *
from CommentTab import *
from string import Template

class ECNWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, load_id = None):
        super(ECNWindow,self).__init__()
        self.parent = parent
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.user_info = self.parent.user_info
        self.windowWidth =  QtGui.QGuiApplication.primaryScreen().availableGeometry().width() *0.55
        self.windowHeight = self.windowWidth * 0.75
        self.load_id = load_id
        self.tablist = []
        self.typeindex = {'New Part':0, 'BOM Update':1, 'Firmware Update':2, 'Configurator Update' : 3,'Product EOL':4}
        self.initAtt()
        if self.load_id == None:
            self.initReqUI()
            self.generateECNID()
        else:
            self.initFullUI()
            self.getCurrentValues()
            
        self.center()
        self.show()

    def initAtt(self):
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
        self.tab_ecn.line_author.setText(self.parent.parent.user_info['user'])
        self.tab_ecn.line_status.setText("Draft")
        self.tab_attach = AttachmentTab(self)
        self.tab_comments = CommentTab(self)
        self.tab_comments.enterText.setDisabled(True)
        self.tab_signature = SignatureTab(self)
        self.tab_changelog = ChangeLogTab(self,self.tab_ecn.line_id.text())
        self.button_save = QtWidgets.QPushButton("Save",self)
        self.button_release = QtWidgets.QPushButton("Release")
        self.button_release.setDisabled(True)
        self.button_save.clicked.connect(self.save)
        self.button_release.clicked.connect(self.release)
        self.button_cancel = QtWidgets.QPushButton("Delete")
        self.button_cancel.setDisabled(True)
        self.button_cancel.clicked.connect(self.cancel)
        self.tabwidget.addTab(self.tab_ecn, "ECN")
        self.tabwidget.addTab(self.tab_attach, "Attachment")
        self.tabwidget.addTab(self.tab_comments, "Comments")
        self.tabwidget.addTab(self.tab_signature, "Signatures")
        self.tabwidget.addTab(self.tab_changelog, "Change Log")
        
        self.tabwidget.setTabVisible(2, False)
        self.tabwidget.setTabVisible(4, False)
                
        self.tab_purch = PurchaserTab(self)
        self.tab_planner = PlannerTab(self)
        self.tab_shop = ShopTab(self)
        buttonlayout = QtWidgets.QHBoxLayout()
        buttonlayout.addWidget(self.button_save)
        buttonlayout.addWidget(self.button_cancel)
        buttonlayout.addWidget(self.button_release)
        mainlayout.addWidget(self.tabwidget)
        mainlayout.addLayout(buttonlayout)
        
        self.tab_ecn.combo_dept.currentIndexChanged.connect(self.tab_signature.prepopulateTable)
        
        #self.tab_signature.prepopulateTable()



    def initFullUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        
        self.tabwidget = QtWidgets.QTabWidget(self)
        #self.tabwidget.currentChanged.connect(self.printIndex)
        self.tab_ecn = ECNTab(self)
        self.tab_ecn.box_requestor.setDisabled(True)
        self.tab_ecn.combo_type.setDisabled(True)
        #self.tab_eng = EngineerTab(self)
        self.tab_attach = AttachmentTab(self)
        #self.tab_task = TasksTab(self)
        self.tab_comments = CommentTab(self)
        self.tab_signature = SignatureTab(self)
        self.tab_changelog = ChangeLogTab(self,self.load_id)
        #self.tab_purch = PurchaserTab(self)
        #self.tab_planner = PlannerTab(self)
        #self.tab_shop = ShopTab(self)
        
        self.tabwidget.addTab(self.tab_ecn, "ECN")
        #self.tabwidget.addTab(self.tab_eng, "Engineer")
        self.tabwidget.addTab(self.tab_attach, "Attachment")
        #self.tabwidget.addTab(self.tab_task, "Tasks")
        self.tabwidget.addTab(self.tab_comments, "Comments")
        self.tabwidget.addTab(self.tab_signature, "Signatures")
        self.tabwidget.addTab(self.tab_changelog, "Change Log")
                    
        self.loadData()
        
        mainlayout.addWidget(self.tabwidget)
        buttonlayout = QtWidgets.QHBoxLayout()
        
        #disable signature and attachment adding if not author and completed
        if self.parent.user_info['user']==self.tab_ecn.line_author.text() and self.tab_ecn.line_status.text()!="Completed":
            self.tab_signature.button_add.setEnabled(True)
            self.tab_signature.button_remove.setEnabled(True)
            self.tab_attach.button_add.setEnabled(True)
            self.tab_attach.button_remove.setEnabled(True)
            self.tab_comments.enterText.setEnabled(True)
            self.tab_comments.label_enterText.setVisible(True)
            self.tab_comments.enterText.setVisible(True)
        else:
            self.tab_signature.button_add.setDisabled(True)
            self.tab_signature.button_remove.setDisabled(True)
            self.tab_attach.button_add.setDisabled(True)
            self.tab_attach.button_remove.setDisabled(True)
            self.tab_comments.enterText.setDisabled(True)
            self.tab_comments.label_enterText.setVisible(False)
            self.tab_comments.enterText.setVisible(False)
        
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
                buttonlayout.addWidget(self.button_save)
                buttonlayout.addWidget(self.button_cancel)
                buttonlayout.addWidget(self.button_release)
                self.tab_ecn.line_ecntitle.setReadOnly(False)
                self.tab_ecn.text_reason.setReadOnly(False)
                self.tab_ecn.text_summary.setReadOnly(False)
                if self.tab_ecn.line_status.text()=="Out For Approval":
                    self.button_release.setDisabled(True)
            else:
                self.button_approve = QtWidgets.QPushButton("Approve")
                self.button_approve.clicked.connect(self.approve)
                self.button_reject = QtWidgets.QPushButton("Reject",self)
                self.button_reject.clicked.connect(self.reject)
                buttonlayout.addWidget(self.button_approve)
                buttonlayout.addWidget(self.button_reject)
                self.tab_ecn.line_ecntitle.setReadOnly(True)
                self.tab_ecn.text_summary.setReadOnly(True)
                self.tab_ecn.text_reason.setReadOnly(True)
                if self.tab_ecn.line_status.text()=="Rejected":
                    self.button_reject.setDisabled(True)
                if self.isUserSignable():
                    if self.hasUserSigned():
                        self.button_approve.setDisabled(True)
                else:
                    self.button_approve.setDisabled(True)
                    self.button_reject.setDisabled(True)
        self.button_exportHTML = QtWidgets.QPushButton("Export")
        self.button_exportHTML.clicked.connect(self.exportHTML)
        buttonlayout.addWidget(self.button_exportHTML)
            
        mainlayout.addLayout(buttonlayout)

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
        self.tab_ecn.line_id.setText('ECN-'+date_time[2:])

    def insertData(self):
        #inserting to ECN table
        try:
            ecn_id = self.tab_ecn.line_id.text()
            ecn_type = self.tab_ecn.combo_type.currentText()
            author = self.tab_ecn.line_author.text()
            requestor = self.tab_ecn.box_requestor.currentText()
            status = 'Draft'
            title = self.tab_ecn.line_ecntitle.text()
            reason =self.tab_ecn.text_reason.toPlainText()
            summary = self.tab_ecn.text_summary.toPlainText()
            modifieddate = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')

            data = (ecn_id,ecn_type,author,requestor,status,title,reason,summary,modifieddate)
            self.cursor.execute("INSERT INTO ECN(ECN_ID,ECN_TYPE,AUTHOR,REQUESTOR,STATUS,ECN_TITLE,ECN_REASON,ECN_SUMMARY,LAST_MODIFIED) VALUES(?,?,?,?,?,?,?,?,?)",(data))
            self.db.commit()
            
            if self.tab_attach.table.rowCount()>0:
                for x in range(self.tab_attach.table.rowCount()):
                    filename = self.tab_attach.table.item(x, 0).text()
                    filepath = self.tab_attach.table.item(x, 1).text()
                    data = (ecn_id, filename, filepath)
                    self.cursor.execute("INSERT INTO ATTACHMENTS(ECN_ID,FILENAME,FILEPATH) VALUES(?,?,?)",(data))
                    self.db.commit()
            #print('data inserted')
            if self.tab_comments.enterText.toPlainText()!="":
                self.addComment(ecn_id,self.tab_comments.enterText.toPlainText(),"Author")
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData)!\n Error: {e}")
        
    def approve(self):
        try:
            approvedate = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
            data = (approvedate,self.tab_ecn.line_id.text(),self.parent.user_info['user'])
            self.cursor.execute("UPDATE SIGNATURE SET SIGNED_DATE = ? WHERE ECN_ID = ? and USER_ID = ?",(data))
            self.db.commit()
            self.cursor.execute("UPDATE ECN SET LAST_MODIFIED = '" + approvedate +"'")
            self.tab_signature.repopulateTable()
            self.dispMsg("ECN has been signed!")
            self.button_approve.setDisabled(True)
            self.checkComplete()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (approve)!\n Error: {e}")
    
    def reject(self):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            self.addComment(self.tab_ecn.line_id.text(), comment,"Reject")
        try:
            modifieddate = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
            data = (modifieddate, "Rejected",self.tab_ecn.line_id.text())
            self.cursor.execute("UPDATE ECN SET LAST_MODIFIED = ?, STATUS = ? WHERE ECN_ID = ?",(data))
            self.db.commit()
            self.parent.repopulateTable()
            self.dispMsg("ECN has been updated!")
            self.tab_ecn.line_status.setText("Rejected")
            self.addNotification(self.tab_ecn.line_id.text(), "Rejected")
            self.button_reject.setDisabled(True)
            self.button_approve.setDisabled(True)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (reject)!\n Error: {e}")
    
    def AddSignatures(self):
        #inserting to signature table
        #SIGNATURE(ECN_ID TEXT, NAME TEXT, USER_ID TEXT, HAS_SIGNED TEXT, SIGNED_DATE TEXT)
        try:
            ecn_id = self.tab_ecn.line_id.text()
            self.cursor.execute("DELETE FROM SIGNATURE WHERE ECN_ID = '" + ecn_id + "'")
            self.db.commit()
            for x in range(self.tab_signature.table.rowCount()):
                if isinstance(self.tab_signature.table.item(x, 0),QtWidgets.QTableWidgetItem):
                    job_title = self.tab_signature.table.item(x, 0).text()
                    name = self.tab_signature.table.item(x,1).text()
                    user_id = self.tab_signature.table.item(x,2).text()
                else:
                    job_title = self.tab_signature.table.cellWidget(x, 0).currentText()
                    name = self.tab_signature.table.cellWidget(x,1).currentText()
                    user_id = self.tab_signature.table.cellWidget(x,2).currentText()
                data = (ecn_id,job_title,name,user_id,)
                self.cursor.execute("INSERT INTO SIGNATURE(ECN_ID,JOB_TITLE,NAME,USER_ID) VALUES(?,?,?,?)",(data))
            self.db.commit()
            #print('data inserted')
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (signature)!\n Error: {e}")

    def updateData(self):
        try:
            ecn_id = self.tab_ecn.line_id.text()
            ecn_type = self.tab_ecn.combo_type.currentText()
            requestor = self.tab_ecn.box_requestor.currentText()
            title = self.tab_ecn.line_ecntitle.text()
            reason =self.tab_ecn.text_reason.toPlainText()
            summary = self.tab_ecn.text_summary.toPlainText()
            modifieddate = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
            data = (ecn_type,requestor,title,reason,summary,modifieddate,ecn_id)

            #data = (self.combo_type.currentText(),self.box_requestor.text(),self.date_request.date().toString("yyyy-MM-dd"),'Unassigned',self.line_ecntitle.text(),self.text_detail.toPlainText(),self.line_id.text())
            self.cursor.execute("UPDATE ECN SET ECN_TYPE = ?, REQUESTOR = ?, ECN_TITLE = ?, ECN_REASON = ?, ECN_SUMMARY = ?, LAST_MODIFIED = ? WHERE ECN_ID = ?",(data))
            self.db.commit()
            
            if self.tab_attach.table.rowCount()>0:
                self.cursor.execute("DELETE FROM ATTACHMENTS WHERE ECN_ID = '" + ecn_id + "'")
                self.db.commit()
                for x in range(self.tab_attach.table.rowCount()):
                    filename = self.tab_attach.table.item(x, 0).text()
                    filepath = self.tab_attach.table.item(x, 1).text()
                    data = (ecn_id, filename, filepath)
                    self.cursor.execute("INSERT INTO ATTACHMENTS(ECN_ID,FILENAME,FILEPATH) VALUES(?,?,?)",(data))
                    self.db.commit()
                    
            if self.tab_comments.enterText.toPlainText()!="":
                self.addComment(ecn_id,self.tab_comments.enterText.toPlainText(),"Author")
                
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (updateData)!\n Error: {e}")

    def loadData(self):
        command = "Select * from ECN where ECN_ID = '"+self.load_id +"'"
        self.cursor.execute(command)
        results = self.cursor.fetchone()
        self.tab_ecn.line_id.setText(results['ECN_ID'])
        self.tab_ecn.combo_type.setCurrentIndex(self.typeindex[results['ECN_TYPE']])
        self.tab_ecn.line_ecntitle.setText(results['ECN_TITLE'])
        self.tab_ecn.text_reason.setText(results['ECN_REASON'])
        self.tab_ecn.text_summary.setText(results['ECN_SUMMARY'])
        self.tab_ecn.line_author.setText(results['AUTHOR'])
        self.tab_ecn.box_requestor.setEditText(results['REQUESTOR'])
        self.tab_ecn.line_status.setText(results['STATUS'])
        
        command = "Select * from SIGNATURE where ECN_ID= '"+self.load_id +"'"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        self.tab_signature.table.setRowCount(len(results))
        rowcount=0
        for result in results:
            #print(result['JOB_TITLE'],result['SIGNED_DATE'])
            self.tab_signature.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['JOB_TITLE']))
            self.tab_signature.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['NAME']))
            self.tab_signature.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['USER_ID']))
            self.tab_signature.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['SIGNED_DATE']))
            rowcount+=1
            
        command = "Select * from ATTACHMENTS where ECN_ID= '"+self.load_id +"'"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        self.tab_attach.table.setRowCount(len(results))
        rowcount=0
        for result in results:
            self.tab_attach.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['FILENAME']))
            self.tab_attach.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['FILEPATH']))
            rowcount+=1
            
        self.loadComments()    

    def addComment(self,ecn_id,comment,commentType):
        #COMMENTS(ECN_ID TEXT, NAME TEXT, USER TEXT, COMM_DATE DATE, COMMENT TEXT
        data = (ecn_id, self.parent.user_info['user'],datetime.now().strftime('%Y/%m/%d-%H:%M:%S'),comment,commentType)
        self.cursor.execute("INSERT INTO COMMENTS(ECN_ID, USER, COMM_DATE, COMMENT,TYPE) VALUES(?,?,?,?,?)",(data))
        self.db.commit()
        self.tab_comments.enterText.clear()
        self.tab_comments.mainText.clear()
        self.loadComments()
            
    def loadComments(self):
            self.tab_comments.enterText.clear()
            self.tab_comments.mainText.clear()
            command = "Select * from COMMENTS where ECN_ID = '" + self.load_id+"'"
            self.cursor.execute(command)
            results = self.cursor.fetchall()
            for result in results:
                if self.tab_ecn.line_author.text() == result['USER']:
                    self.tab_comments.mainText.setTextColor(QtGui.QColor(255,0,0))
                else:
                    self.tab_comments.mainText.setTextColor(QtGui.QColor(0,0,0))
                self.tab_comments.mainText.append(">>  " + result['COMMENT'] + "\r    :: " + result['USER']+ " - " + result['COMM_DATE'] +"\r\r")
                
    def cancel(self):
        if self.tab_ecn.line_status.text()=="Draft":
            self.deleteECN(self.tab_ecn.line_id.text())
            self.close()
        else:
            self.cancelECN(self.tab_ecn.line_id.text())
        
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
            modifieddate = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
            data = (modifieddate, "Out For Approval",self.tab_ecn.line_id.text())
            self.cursor.execute("UPDATE ECN SET LAST_MODIFIED = ?, STATUS = ? WHERE ECN_ID = ?",(data))
            self.db.commit()
            self.tab_ecn.line_status.setText("Out For Approval")
            self.parent.repopulateTable()
            self.dispMsg("ECN has been saved and sent out for signing!")
            self.addNotification(self.tab_ecn.line_id.text(), "Released")
            self.button_release.setDisabled(True)
            self.button_cancel.setText("Cancel")
            self.button_cancel.setDisabled(True)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (release)!\n Error: {e}")
    
    def isUserSignable(self):
        self.cursor.execute(f"SELECT SIGNED_DATE from SIGNATURE where ECN_ID='{self.tab_ecn.line_id.text()}' and USER_ID='{self.parent.user_info['user']}'")
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True
            
    def hasUserSigned(self):
        self.cursor.execute(f"SELECT SIGNED_DATE from SIGNATURE where ECN_ID='{self.tab_ecn.line_id.text()}' and USER_ID='{self.parent.user_info['user']}'")
        result = self.cursor.fetchone()
        if result[0] is None:
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
            command = "Select * from SIGNATURE where ECN_ID ='" + self.tab_ecn.line_id.text() + "'"
            self.cursor.execute(command)
            results = self.cursor.fetchall()
            completed = True
            for result in results:
                if result['SIGNED_DATE'] == None or result['SIGNED_DATE']== "":
                    completed = False
            if completed:
                completeddate = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
                data = (completeddate, "Completed",self.tab_ecn.line_id.text())
                self.cursor.execute("UPDATE ECN SET LAST_MODIFIED = ?, STATUS = ? WHERE ECN_ID = ?",(data))
                self.db.commit()
                self.parent.repopulateTable()
                self.parent.parent.completedTab.repopulateTable()
                self.dispMsg("ECN is now completed")
                self.addNotification(self.tab_ecn.line_id.text(), "Completed")
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during check Complete.\n Error: {e}")
            

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

    def save(self,msg = None):
        if not self.checkEcnID():
            self.insertData()
            self.AddSignatures()
            if not msg:
                self.dispMsg("ECN has been saved!")
            self.tabwidget.setTabVisible(2, True)
            self.parent.repopulateTable()
            self.button_release.setDisabled(False)
            self.button_cancel.setDisabled(False)
        else:
            self.updateData()
            self.AddSignatures()
            if not msg:
                self.dispMsg("ECN has been updated!")
            self.getCurrentValues()
            self.checkDiff()
            self.parent.repopulateTable()

    def saveAndClose(self):
        self.save()
        self.close()

    def exportHTML(self):
        foldername = QtWidgets.QFileDialog().getExistingDirectory()
        if foldername:
            with open(self.parent.parent.programLoc+'\\template.html') as f:
                lines = f.read() 
                #print(lines)
                f.close()

                t = Template(lines)
                id = self.tab_ecn.line_id.text()
                title = self.tab_ecn.line_ecntitle.text()
                author = self.tab_ecn.line_author.text()
                dept = self.tab_ecn.combo_dept.currentText()
                requestor = self.tab_ecn.box_requestor.currentText()
                #316 front html wrapper characters and 14 ending html wrapper from qt.tohtml
                reason = self.tab_ecn.text_reason.toHtml()[316:-14]
                summary = self.tab_ecn.text_summary.toHtml()[316:-14]
                signature = "<tr>"
                attachment ="<tr>"

                #attachments
                if self.tab_attach.table.rowCount()>0:
                    for x in range(self.tab_attach.table.rowCount()):
                        attachment += "<td>"+self.tab_attach.table.item(x,0).text()+"</td>"
                        attachment += "<td>"+self.tab_attach.table.item(x,1).text()+"</td></tr>"
                else:
                    attachment="<tr><td></td><td></td></tr>"
                #signatures
                if self.tab_signature.table.rowCount()>0:
                    for x in range(self.tab_signature.table.rowCount()):
                        signature += "<td>"+self.tab_signature.table.item(x,0).text()+"</td>"
                        signature += "<td>"+self.tab_signature.table.item(x,1).text()+"</td>"
                        signature += "<td>"+self.tab_signature.table.item(x,3).text()+"</td></tr>"
                else:
                    signature="<tr><td></td><td></td><td></td></tr>"
                #print(id, title, author,reason,summary)
                export = t.substitute(ECNID=id,ECNTitle=title,Requestor=requestor,Department=dept,Author=author, Reason=reason,Summary=summary,Attachment=attachment,Signature=signature)
            
                with open(foldername+'\\'+id+'.html', 'w') as f:
                    f.write(export)
                    f.close()
                    
                    
                # page = QtWebEngineWidgets.QWebEnginePage()
                
                # def handle_load_finished(status):
                #     if status:
                #         page.printToPdf(foldername+'\\'+id+'.pdf')
                        
                # page.loadFinished.connect(handle_load_finished)
                # page.load(QtCore.QUrl.fromLocalFile(foldername+'\\'+id+'.html'))
                
                self.dispMsg("Export Completed!")
        
    def addNotification(self,ecn_id,notificationType):
        if self.existNotification(ecn_id):
            data = (notificationType,ecn_id)
            self.cursor.execute("UPDATE NOTIFICATION SET TYPE = ? WHERE ECN_ID = ?",(data))
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
        ecn_id = self.tab_ecn.line_id.text()
        changedate = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
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
        command = "select ECN_ID from ECN where ECN_ID = '" + self.tab_ecn.line_id.text() + "'"
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