from PySide6 import QtWidgets, QtCore, QtGui
from PCNTab import *
from SignatureTab import *
from NotificationTab import *
from CommentTab import *
from WebView import *
from datetime import datetime
from string import Template
import os, sys
import sqlite3  


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class PCNWindow(QtWidgets.QWidget):
    def __init__(self,parent=None, doc_id = None):
        super(PCNWindow,self).__init__()
        self.window_id = "PCN_Window"
        self.windowWidth =  950
        self.windowHeight = 800
        self.parent = parent
        self.user_info = parent.user_info
        self.doc_id = doc_id
        self.settings = parent.settings
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        if self.doc_id is None:
            self.doc_data = {"author":self.parent.user_info["user"],"status":"Draft"}
        else:
            command = "Select * from document where doc_id = '"+self.doc_id +"'"
            self.cursor.execute(command)
            self.doc_data = self.cursor.fetchone()
        #self.getPCNCounter()
        #self.generatePCNID()
        self.initAtt()
        self.initUI()
        self.show()

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


    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        title = "PCN Window"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        
        

    def initUI(self):
        mainLayout = QtWidgets.QVBoxLayout()
        self.toolbar = QtWidgets.QToolBar()
        
        icon_loc = icon = os.path.join(program_location,"icons","export.png")
        self.button_export = QtWidgets.QPushButton("Export")
        self.button_export.setIcon(QtGui.QIcon(icon_loc))
        self.button_export.clicked.connect(self.exportPDF)
        
        icon_loc = icon = os.path.join(program_location,"icons","export.png")
        self.button_preview = QtWidgets.QPushButton("Preview")
        self.button_preview.setIcon(QtGui.QIcon(icon_loc))
        self.button_preview.clicked.connect(self.previewHTML)
        
        if self.doc_data["status"]!="Completed":
            icon_loc = icon = os.path.join(program_location,"icons","save.png")
            self.button_save = QtWidgets.QPushButton("Save")
            self.button_save.setIcon(QtGui.QIcon(icon_loc))
            self.button_save.clicked.connect(self.save)
            
            icon_loc = icon = os.path.join(program_location,"icons","add_comment.png")
            self.button_comment = QtWidgets.QPushButton("Add Comment")
            self.button_comment.setIcon(QtGui.QIcon(icon_loc))
            self.button_comment.clicked.connect(self.addUserComment)
            self.toolbar.addWidget(self.button_save)
            if self.parent.user_info["user"]==self.doc_data["author"]:
                self.button_cancel = QtWidgets.QPushButton("Delete")
                icon_loc = icon = os.path.join(program_location,"icons","cancel.png")
                self.button_cancel.setIcon(QtGui.QIcon(icon_loc))
                self.button_cancel.setEnabled(self.doc_data["status"]=="Draft" or self.doc_data["status"]=="Rejected")
                self.button_cancel.clicked.connect(self.cancel)
                
                icon_loc = icon = os.path.join(program_location,"icons","release.png")
                self.button_release = QtWidgets.QPushButton("Release")
                self.button_release.setIcon(QtGui.QIcon(icon_loc))
                self.button_release.clicked.connect(self.release)
                self.button_release.setDisabled(True)
                if self.doc_data["status"]=="Rejected":
                    self.button_cancel.setText("Cancel")
                self.toolbar.addWidget(self.button_cancel)
                self.toolbar.addWidget(self.button_release)
            if self.parent.user_info["user"]!=self.doc_data["author"] and self.doc_data["status"]=="Out For Approval":
                icon_loc = icon = os.path.join(program_location,"icons","approve.png")
                self.button_approve = QtWidgets.QPushButton("Approve")
                self.button_approve.setIcon(QtGui.QIcon(icon_loc))
                self.button_approve.clicked.connect(self.approve)
                
                icon_loc = icon = os.path.join(program_location,"icons","reject.png")
                self.button_reject = QtWidgets.QPushButton("Reject")
                self.button_reject.setIcon(QtGui.QIcon(icon_loc))
                self.button_reject.clicked.connect(self.reject)
                self.toolbar.addWidget(self.button_approve)
                self.toolbar.addWidget(self.button_reject)
                if self.isUserSignable():
                    if self.hasUserSigned():
                        self.button_approve.setDisabled(True)
                    else:
                        self.button_approve.setDisabled(False)
                else:
                    self.button_approve.setDisabled(True)
                    self.button_reject.setDisabled(True)
            self.toolbar.addWidget(self.button_comment)
        self.toolbar.addWidget(self.button_export)
        self.toolbar.addWidget(self.button_preview)
        
        if self.parent.user_permissions["rerouting"]=="y":
            self.button_check_stage = QtWidgets.QPushButton("Check Stage")
            self.button_check_stage.clicked.connect(self.checkStage)
            self.toolbar.addWidget(self.button_check_stage)
        
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_pcn = PCNTab(self)
        self.tab_comments = CommentTab(self)
        self.tab_signature = SignatureTab(self,"PCN",self.doc_data)
        self.tab_notification = NotificationTab(self,self.doc_data)
        
        self.tab_widget.addTab(self.tab_pcn,"PCN")
        self.tab_widget.addTab(self.tab_comments, "Comments")
        self.tab_widget.addTab(self.tab_signature,"Signatures")
        self.tab_widget.addTab(self.tab_notification,"Notifications")
        mainLayout.addWidget(self.toolbar)
        mainLayout.addWidget(self.tab_widget)
        self.setLayout(mainLayout)
        
        if self.doc_id is None:
            self.tab_pcn.line_id.setPlaceholderText("Save to gen.")
            self.tab_pcn.line_title.setPlaceholderText("Please enter a title")
            self.tab_pcn.line_author.setText(self.parent.user_info["user"])
            self.tab_pcn.line_status.setText("Draft")
        else:
            self.loadData()
        
    def save(self,msg=None):
        try:
            save_type = "update"
            if self.doc_id is None:
                self.generatePCNID()
                save_type = "insert"
            doc_id = self.tab_pcn.line_id.text()
            doc_type = "PCN"
            author = self.tab_pcn.line_author.text()
            #requestor = self.tab_ecn.box_requestor.currentText()
            status = self.tab_pcn.line_status.text()
            title = self.tab_pcn.line_title.text()
            overview = self.tab_pcn.text_overview.toHtml()
            reason =self.tab_pcn.text_reason.toHtml()
            change = self.tab_pcn.text_change.toHtml()
            products = self.tab_pcn.text_products.toHtml()
            replacement = self.tab_pcn.text_replacement.toHtml()
            reference = self.tab_pcn.text_reference.toHtml()
            response = self.tab_pcn.text_response.toHtml()
            web_desc = self.tab_pcn.line_web.text()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #dept = self.tab_ecn.combo_dept.currentText()
            
            #overview - text 1, products - text 2, replacement - text 3, reference - text 4, response - text 5
            if save_type == "insert":
                if self.checkSigNotiDuplicate():
                    self.dispMsg("duplicates found in signature and notification tab")
                else:
                    data = (doc_id,doc_type,author,status,title,overview,reason,change,products,replacement,reference,response,web_desc,modifieddate)
                    self.cursor.execute("INSERT INTO document(doc_id,doc_type,author,status,doc_title,doc_text_1,doc_reason,doc_summary,doc_text_2,doc_text_3,doc_text_4,doc_text_5,doc_text_6,last_modified) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data))
                    self.AddSignatures()
                    self.dispMsg("PCN Saved!")
            else:
                if self.checkSigNotiDuplicate():
                    self.dispMsg("duplicates found in signature and notification tab")
                else:
                    data = (title,overview,reason,change,products,replacement,reference,response,web_desc,modifieddate,doc_id)
                    self.cursor.execute("UPDATE document SET doc_title = %s, doc_text_1 = %s, doc_reason = %s, doc_summary = %s, doc_text_2 = %s, doc_text_3 = %s, doc_text_4 = %s, doc_text_5 = %s, doc_text_6 = %s, last_modified = %s WHERE doc_id = %s",(data))
                    self.AddSignatures()
                    if not msg:
                        self.dispMsg("PCN Updated!")
            self.db.commit()
            if status=="Out For Approval":
                print("check for signs")
                self.movePCNStage()
            self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data saving!\n Error: {e}")
            
    def isUserSignable(self):
        curStage = self.getPCNStage()
        #print(curStage)
        if curStage == 0:
            return False
        titles = self.getTitlesForStage()
        titles = titles[str(curStage)]
        self.cursor.execute(f"SELECT user_id from signatures where doc_id='{self.doc_id}' and user_id='{self.user_info['user']}'")
        result = self.cursor.fetchone()
        if self.user_info['title'] in titles and result is not None:
            return True
        return False
            
    def hasUserSigned(self):
        self.cursor.execute(f"SELECT signed_date from signatures where doc_id='{self.doc_id}' and user_id='{self.user_info['user']}'")
        result = self.cursor.fetchone()
        if result is None or result[0] is None:
            #print("found none returning false")
            return False
        else:
            return True
            
    def loadData(self):
        self.cursor.execute(f"Select * from document WHERE doc_id='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tab_pcn.line_id.setText(result["doc_id"])
        self.tab_pcn.line_title.setText(result["doc_title"])
        self.tab_pcn.line_author.setText(result["author"])
        self.tab_pcn.line_status.setText(result["status"])
        self.tab_pcn.text_overview.setHtml(result["doc_text_1"])
        self.tab_pcn.text_reason.setHtml(result["doc_reason"])
        self.tab_pcn.text_change.setHtml(result["doc_summary"])
        self.tab_pcn.text_products.setHtml(result["doc_text_2"])
        self.tab_pcn.text_replacement.setHtml(result["doc_text_3"])
        self.tab_pcn.text_reference.setHtml(result["doc_text_4"])
        self.tab_pcn.text_response.setHtml(result["doc_text_5"])
        self.tab_pcn.line_web.setText(result["doc_text_6"])
        
        self.tab_signature.repopulateTable()
        if self.doc_data["author"]==self.parent.user_info["user"] and self.doc_data["status"]!="Out For Approval" and self.doc_data["status"]!="Completed":
            self.button_release.setEnabled(self.tab_signature.rowCount()>0)
        self.tab_notification.repopulateTable()
        if self.doc_data["status"]=="Completed":
            self.tab_signature.button_add.setDisabled(True)
            self.tab_notification.button_add.setDisabled(True)
        self.tab_comments.loadComments()
        self.setCommentCount()
    
    def generatePCNID(self):
        month,counter = self.getPCNCounter()
        date_time = datetime.now().strftime('%Y%m')
        old_month = f"{month:02d}"
        #print(date_time[4:],old_month)
        if old_month == date_time[4:]:
            #print("month match")
            self.setPCNCounter(old_month, old_month, counter+1)
            self.doc_id = 'PCN'+date_time[2:]+ f"-{counter+1:02d}"
        else:
            #print("month not match")
            self.setPCNCounter(old_month, date_time[4:], 1)
            self.doc_id = 'PCN'+date_time[2:]+"-01"
        #print(self.doc_id)
        self.tab_pcn.line_id.setText(self.doc_id)
        
    def cancel(self):
        if self.tab_pcn.line_status.text()=="Draft":
            self.deletePCN(self.doc_id)
            self.close()
        else:
            self.cancelPCN(self.doc_id)
            
    def deletePCN(self,doc_id):
        try:
            self.cursor.execute(f"DELETE FROM document where doc_id='{doc_id}'")
            self.cursor.execute(f"DELETE FROM comments where doc_id='{doc_id}'")
            self.cursor.execute(f"DELETE FROM signatures where doc_id='{doc_id}'")
            self.db.commit()
            self.dispMsg("PCN has been deleted")
            self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Problems occured trying to delete PCN.\n Error: {e}")
            
    def cancelECN(self,doc_id):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            try:
                self.addComment(self.doc_id, comment,"Canceling")
                self.cursor.execute(f"UPDATE document SET status='Canceled' where doc_id='{doc_id}'")
                self.db.commit()
                self.dispMsg("PCN has been canceled")
                self.tab_pcn.line_status.setText("Canceled")
                self.parent.repopulateTable()
                self.addNotification(self.doc_id, "Canceling",from_user=self.parent.user_info['user'],msg=comment)
            except Exception as e:
                print(e)
                self.dispMsg(f"Problems occured trying to cancel PCN.\n Error:{e}")
        if ok and comment=="":
            self.dispMsg("Rejection failed: comment field was left blank.")
        
    def addUserComment(self):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            self.addComment(self.doc_id, comment,"User Comment")
            self.addNotification(self.doc_id, "User Comment",from_user=self.parent.user_info['user'], msg=comment)
            #self.dispMsg("Comment has been added!")

    def addComment(self,doc_id,comment,commentType):
        #comments(ECN_ID TEXT, name TEXT, user_id TEXT, comm_date DATE, comment TEXT
        data = (doc_id, self.parent.user_info['user'],datetime.now().strftime('%Y-%m-%d %H:%M:%S'),comment,commentType)
        self.cursor.execute("INSERT INTO comments(doc_id, user_id, comm_date, comment,type) VALUES(%s,%s,%s,%s,%s)",(data))
        self.db.commit()
        # self.tab_comments.enterText.clear()
        #self.tab_comments.mainText.clear()
        self.tab_comments.addComment(data[1], data[2], data[4], data[3])
        self.setCommentCount()
        #self.tab_widget.setCurrentIndex(3)
        
    def setCommentCount(self):
        self.cursor.execute(f"SELECT COUNT(comment) from comments where doc_id='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tab_widget.setTabText(1, "Comments ("+str(result[0])+")")
    
    def existNotification(self,doc_id):
        self.cursor.execute(f"Select * from notifications where doc_id='{doc_id}' and status='Not Sent'")
        result = self.cursor.fetchone()
        if result is not None:
            return True
        else:
            return False
        
    def addNotification(self,doc_id,notificationType,from_user=None,usersList=None,msg=""):
        print(f'adding notification: {notificationType}')
        if usersList is not None:
            if type(usersList)==type([]):
                users = ""
                count = 0
                for user in usersList:
                    users +=","
                    if count<len(usersList)-1:
                        users +=","
                    count+=1
            else:
                users = usersList
        else:
            users = ""
        if from_user is None:
            from_user = ""
                
        if self.existNotification(doc_id) and notificationType!="User Comment":
            data = (notificationType,from_user,users,msg, doc_id)
            self.cursor.execute("UPDATE notifications SET type = %s, from_user = %s, users = %s, msg = %s WHERE doc_id = %s",(data))
        else:
            data = (doc_id,"Not Sent",notificationType,from_user, users, msg)
            self.cursor.execute("INSERT INTO notifications(doc_id, status, type,from_user, users, msg) VALUES(%s,%s,%s,%s,%s,%s)",(data))
        self.db.commit()
        
        
    def getPCNCounter(self):
        self.cursor.execute("select * from pcncounter")
        result = self.cursor.fetchone()
        if result is not None:
            return (result[0],result[1])
        else:
            #print("no results")
            return (0,0)
            
    def setPCNCounter(self,old_month,new_month,counter):
        #print(old_month,new_month,counter)
        if old_month == "00":
            data = (new_month,counter)
            self.cursor.execute(f"INSERT INTO pcncounter(month,counter) VALUES(%s,%s)",(data))
            #print("inserting data")
        else:
            data = (new_month,counter,old_month)
            self.cursor.execute(f"UPDATE pcncounter SET month = %s, counter=%s where month = %s",(data))
        self.db.commit()
        
    def checkStage(self):
        try:
            self.checkComplete()
            self.db.commit()
            print("moving pcn stage check")
            self.movePCNStage()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (approve)!\n Error: {e}")
        
    def getPCNStage(self):
        try:
            self.cursor.execute(f"Select TEMPSTAGE from document where doc_id='{self.doc_id}'")
            result = self.cursor.fetchone()
            #print("current stage",result[0])
            if result[0] is None:
                return 0
            else:
                return result[0]
        except Exception as e:
            self.dispMsg(f"Error trying to get PCN stage. Error: {e}")
            
    def setPCNStage(self,stage):
        try:
            #print('setting ecn to ', stage)
            self.cursor.execute(f"UPDATE document SET stage ='{stage}', tempstage = '{stage}' where doc_id='{self.doc_id}'")
            self.db.commit()
        except Exception as e:
            self.dispMsg(f"Error trying to set PCN stage. Error: {e}")
            
    # def movePCNStage(self):
    #     curStage = self.getPCNStage()
    #     titles = self.getTitlesForStage()
    #     titles = titles[str(curStage)]
    #     #print("here are the titles",titles)
    #     move = True
    #     for title in titles:
    #         self.cursor.execute(f"Select signed_date from signatures where doc_id = '{self.doc_id}' and job_title='{title}' and type='Signing'")
    #         results = self.cursor.fetchall()
    #         for result in results:
    #             #print(result['signed_date'])
    #             if result['signed_date'] is None:
    #                 move = False
    #                 #print("not moving to next stage")
    #                 break
    #     if move:
    #         nextStages = self.getNextStage()
    #         if len(nextStages)>0:
    #             #print("moving to stage:", nextStages[0])
    #             self.setPCNStage(nextStages[0])
    #             self.addNotification(self.doc_id, "Stage Moved")
    #         # else:
    #         #     print("this is the last stage")
            
    def movePCNStage(self):
        curStage = str(self.getPCNStage())
        stages = self.getSigStages()
        print(curStage,stages)
        if stages!=[]:
            if curStage!=stages[0]:
                self.setPCNStage(stages[0])
                self.addNotification(self.doc_id, "Stage Moved")
                
    def getSigStages(self):
        self.cursor.execute(f"select job_title from signatures where doc_id='{self.doc_id}' and type='Signing' and signed_date is NULL")
        results = self.cursor.fetchall()
        stages = []
        for result in results:
            stages.append(self.stageDictPCN[result[0]])
        stages.sort()
        return stages
        # print(stages)
            
    def getNextStage(self):
        self.cursor.execute(f"Select job_title from signatures where doc_id='{self.doc_id}' and signed_date is NULL and type='Signing'")
        results = self.cursor.fetchall()
        stage = []
        for result in results:
            stage.append(self.stageDictPCN[result[0]])
        stage = sorted(stage)
        return stage
    
    def getTitlesForStage(self):
        titles = {}
        for key, value in self.stageDictPCN.items():
            if value not in titles:
                titles[value] = [key]
            else:
                titles[value].append(key)
        return titles
    
    def checkFields(self):
        if self.tab_pcn.line_title.text()=="":
            return False
        if self.tab_pcn.text_overview.toPlainText()=="":
            return False
        if self.tab_pcn.text_products.toPlainText()=="":
            return False
        if self.tab_pcn.text_change.toPlainText()=="":
            return False
        if self.tab_pcn.text_reason.toPlainText()=="":
            return False
        if self.tab_pcn.text_replacement.toPlainText()=="":
            return False
        if self.tab_pcn.text_reference.toPlainText()=="":
            return False
        if self.tab_pcn.text_response.toPlainText()=="":
            return False
        if self.tab_pcn.line_web.text()=="":
            return False
        return True
        
    def release(self):
        if self.checkFields():
            try:
                print("releasing")
                self.save(1)
                modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                self.cursor.execute(f"SELECT first_release from document where doc_id='{self.doc_id}'")
                result = self.cursor.fetchone()
                if result[0] is None:
                    self.cursor.execute(f"UPDATE document SET first_release = '{modifieddate}' where doc_id='{self.doc_id}'")
                data = (modifieddate, "Out For Approval",self.doc_id)
                self.cursor.execute("UPDATE document SET last_modified = %s, status = %s WHERE doc_id = %s",(data))
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
            self.cursor.execute("UPDATE signatures SET signed_date = %s WHERE doc_id = %s and user_id = %s",(data))
            self.cursor.execute(f"UPDATE document SET last_modified = '{approvedate}' where doc_id='{self.doc_id}'")
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
                self.cursor.execute("UPDATE document SET last_modified = %s, status = %s WHERE doc_id = %s",(data))
                self.cursor.execute(f"UPDATE signatures SET signed_date=Null where doc_id='{self.doc_id}'")
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
            command = f"Select * from signatures where doc_id ='{self.doc_id}' and type='Signing'"
            self.cursor.execute(command)
            results = self.cursor.fetchall()
            completed = True
            for result in results:
                if result['signed_date'] == None or result['signed_date']== "":
                    completed = False
            if completed:
                completeddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute(f"select first_release from document where doc_id='{self.doc_id}'")
                result = self.cursor.fetchone()
                #print(result[0])
                #first_release = datetime.strptime(str(result[0]),'%Y-%m-%d %H:%M:%S')
                elapsed = self.getElapsedDays(result[0], completeddate)
                #print(elapsed)
                #elapsed = self.getElapsedDays(first_release, completeddate)
                data = (completeddate,completeddate,elapsed, "Completed",self.doc_id)
                self.cursor.execute("UPDATE document SET last_modified = %s,comp_date = %s, comp_days = %s, status = %s WHERE doc_id = %s",(data))
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
            
    def AddSignatures(self):
        #inserting to signature table
        #signatures(ECN_ID TEXT, name TEXT, user_id TEXT, HAS_SIGNED TEXT, signed_date TEXT)
        try:
            #get current values in db
            current_list = []
            self.cursor.execute(f"SELECT user_id FROM signatures WHERE doc_id='{self.doc_id}' and type='Signing'")
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
                    self.cursor.execute("INSERT INTO signatures(doc_id,job_title,name,user_id,type) VALUES(%s,%s,%s,%s,%s)",(element))
            for element in current_list:
                no_match = True
                for elements in new_list:
                    if element == elements[3]:
                        no_match = False
                if no_match:
                    #print(f"remove {element} from signature db")
                    self.cursor.execute(f"DELETE FROM signatures WHERE doc_id = '{self.doc_id}' and user_id='{element}'")
                    
                    
            current_list = []
            self.cursor.execute(f"SELECT user_id FROM signatures WHERE doc_id='{self.doc_id}' and type='Notify'")
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
                    self.cursor.execute("INSERT INTO signatures(doc_id,job_title,name,user_id,type) VALUES(%s,%s,%s,%s,%s)",(element))
            for element in current_list:
                no_match = True
                for elements in new_list:
                    if element == elements[3]:
                        no_match = False
                if no_match:
                    #print(f"remove {element} from notify db")
                    self.cursor.execute(f"DELETE FROM signatures WHERE doc_id = '{self.doc_id}' and user_id='{element}'")
            
            self.db.commit()
            if self.doc_data["author"]==self.parent.user_info["user"]:
                self.button_release.setEnabled(self.tab_signature.rowCount()>0)
            #print('data updated')
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (signature)!\n Error: {e}")
            
    def notificationSave(self):
        if self.checkSigNotiDuplicate():
            self.dispMsg("Error: Duplicate user found in Signature and Notifications. Please remove the duplicate before trying again.")
        else:
            self.AddSignatures()
            self.dispMsg("PCN has been updated!")
            
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
        
    def previewHTML(self):
        html = self.generateHTML()
        self.webview = WebView()
        self.webview.setDocID(self.doc_id)
        self.webview.loadHtml(html)
            
    def generateHTML(self):
        template_loc = os.path.join(self.parent.programLoc,'templates','pcn_template.html')
        with open(template_loc) as f:
            lines = f.read() 
            f.close()
            t = Template(lines)
            
            self.cursor.execute(f"SELECT * from document where doc_id='{self.doc_id}'")
            result = self.cursor.fetchone()
            overview = result['doc_text_1']
            products = result['doc_text_2']
            change = result['doc_summary']
            reason = result['doc_reason']
            replacement = result['doc_text_3']
            reference = result['doc_text_4']
            response = result['doc_text_5']

            #print('substituting text')
            
            html = t.substitute(PCNID=self.doc_id,Overview=overview,Products=products,ChangeDescription=change,Reason=reason,Replacement=replacement,Reference=reference,Response=response)

            return html
        
    def exportPDF(self):
        try:
            foldername = QtWidgets.QFileDialog().getExistingDirectory()
            if foldername:
                export = self.generateHTML()
                doc_loc = foldername+'\\'+self.doc_id+'.pdf'
                self.webview = WebView()
                self.webview.loadAndPrint(export,doc_loc)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during pcn export.\n Error: {e}")
        
    def exportHTML(self):
        try:
            foldername = QtWidgets.QFileDialog().getExistingDirectory()
            if foldername:
                export = self.generateHTML()
                doc_loc = foldername+'\\'+self.doc_id+'.html'
                with open(doc_loc, 'w') as f:
                    f.write(export)
                    f.close()
                
                self.dispMsg("Export Completed!")
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during ecn export.\n Error: {e}")
        

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def closeEvent(self, event):
        self.parent.pcnWindow = None

# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    Users = PCNWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
