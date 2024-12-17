from PySide6 import QtWidgets, QtCore, QtWebEngineCore
from datetime import datetime
from AttachmentTab import *
from ECRTab import *
from PurchaserTab import *
from TasksTab import *
from ShopTab import *
from PlannerTab import *
from ChangeLogTab import *
from SignatureTab import *
from PartsTab import *
from CommentTab import *
from NotificationTab import *
from WebView import *
from string import Template
import sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))
    
class ECRWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, doc_id = None):
        super(ECRWindow,self).__init__()
        self.window_id = "ECR_Window"
        self.parent = parent
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.settings = parent.settings
        self.user_info = parent.user_info
        self.visual = parent.visual
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.windowWidth =  950
        self.windowHeight = 580
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.doc_id = doc_id
        self.tablist = []
        #self.typeindex = {'New Part':0, 'BOM Update':1, 'Firmware Update':2, 'Configurator Update' : 3,'Product EOL':4}
        self.initAtt()
        if self.doc_id == None:
            self.doc_data = {"author":self.user_info["user"],"status":"Draft"}
            self.initReqUI()
            self.generateECRID()
        else:
            command = "Select * from document where doc_id = '"+self.doc_id +"'"
            self.cursor.execute(command)
            self.doc_data = self.cursor.fetchone()
            self.initFullUI()
            self.getCurrentValues()
            
        self.center()
        self.show()
        self.activateWindow()

    def initAtt(self):
        self.setWindowIcon(self.parent.ico)
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle(f"ECR-Viewer - user: {self.user_info['user']}")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMinimumWidth(self.windowWidth)
        #self.setWindowModality(QtCore.Qt.ApplicationModal)
        

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
        self.toolbar = QtWidgets.QToolBar()
        
        self.tabwidget = QtWidgets.QTabWidget(self)
        self.tab_ecr = ECRTab(self)
        self.tab_ecr.line_author.setText(self.user_info['user'])
        # self.tab_ecr.box_requestor.setCurrentText(self.user_info['user'])
        self.tab_ecr.line_status.setText("Draft")
        #self.tab_ecr.edit_date.setDate(QtCore.QDate.currentDate())
        #self.tab_ecr.edit_date.setMinimumDate(QtCore.QDate.currentDate())
        self.tab_attach = AttachmentTab(self)
        self.tab_comments = CommentTab(self)
        self.tab_signature = SignatureTab(self)


        self.button_save = QtWidgets.QPushButton("Save")
        #self.button_save.setToolTip("Save")
        icon_loc = icon = os.path.join(program_location,"icons","save.png")
        self.button_save.setIcon(QtGui.QIcon(icon_loc))
        self.button_submit = QtWidgets.QPushButton("Submit")
        #self.button_release.setToolTip("Release")
        icon_loc = icon = os.path.join(program_location,"icons","release.png")
        self.button_submit.setIcon(QtGui.QIcon(icon_loc))
        self.button_submit.setDisabled(True)
        self.button_save.clicked.connect(self.save)
        # self.button_release.clicked.connect(self.release)
        self.button_cancel = QtWidgets.QPushButton("Delete")
        self.button_cancel.setToolTip("Delete")
        icon_loc = icon = os.path.join(program_location,"icons","cancel.png")
        self.button_cancel.setIcon(QtGui.QIcon(icon_loc))
        self.button_cancel.setDisabled(True)
        # self.button_cancel.clicked.connect(self.cancel)
        
        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_cancel)
        self.toolbar.addWidget(self.button_submit)
        
        # buttonlayout = QtWidgets.QHBoxLayout()
        # buttonlayout.addWidget(self.button_save)
        # buttonlayout.addWidget(self.button_cancel)
        # buttonlayout.addWidget(self.button_release)
        
        self.tabwidget.addTab(self.tab_ecr, "ECR")
        self.tabwidget.addTab(self.tab_attach, "Attachment")
        self.tabwidget.addTab(self.tab_comments, "Comments")
        self.tabwidget.addTab(self.tab_signature, "Signatures")

            
        mainlayout.addWidget(self.toolbar)
        mainlayout.addWidget(self.tabwidget)
        
    def initFullUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        
        self.tabwidget = QtWidgets.QTabWidget(self)
        #self.tabwidget.currentChanged.connect(self.printIndex)
        self.tab_ecr = ECRTab(self)
        self.tab_attach = AttachmentTab(self)
        #self.tab_task = TasksTab(self)
        self.tab_comments = CommentTab(self)
        self.tab_signature = SignatureTab(self,"ECN",self.doc_data)
        #self.tab_changelog = ChangeLogTab(self,self.ecn_id)
        #self.tab_purch = PurchaserTab(self)
        #self.tab_planner = PlannerTab(self)
        #self.tab_shop = ShopTab(self)
        
        self.tabwidget.addTab(self.tab_ecr, "ECR")
        self.tabwidget.addTab(self.tab_attach, "Attachment")
        #self.tabwidget.addTab(self.tab_task, "Tasks")
        self.tabwidget.addTab(self.tab_comments, "Comments")
        self.tabwidget.addTab(self.tab_signature, "Signatures")
        #self.tabwidget.addTab(self.tab_changelog, "Change Log")
                    
        self.loadData()
        
        #buttonlayout = QtWidgets.QHBoxLayout()
        
        #disable signature and attachment adding if not author and completed
        if self.user_info['user']==self.doc_data['author'] and self.doc_data['status']!="Completed":
            self.tab_signature.button_add.setEnabled(True)
            #self.tab_signature.button_remove.setEnabled(True)
            self.tab_attach.button_add.setEnabled(True)
        else:
            self.tab_signature.button_add.setDisabled(True)
            #self.tab_signature.button_remove.setDisabled(True)
            self.tab_attach.button_add.setDisabled(True)
        
        if self.tab_ecr.line_status.text()!="Completed":
            if self.user_info['user']==self.tab_ecr.line_author.text():
                self.button_save = QtWidgets.QPushButton("Save")
                #self.button_save.setToolTip("Save")
                icon_loc = icon = os.path.join(program_location,"icons","save.png")
                self.button_save.setIcon(QtGui.QIcon(icon_loc))
                self.button_cancel = QtWidgets.QPushButton("Cancel")
                #self.button_cancel.setToolTip("Cancel")
                icon_loc = icon = os.path.join(program_location,"icons","cancel.png")
                self.button_cancel.setIcon(QtGui.QIcon(icon_loc))
                self.button_release = QtWidgets.QPushButton("Submit")
                icon_loc = icon = os.path.join(program_location,"icons","release.png")
                self.button_release.setIcon(QtGui.QIcon(icon_loc))
                self.button_save.clicked.connect(self.save)
                # self.button_release.clicked.connect(self.release)
                # self.button_cancel.clicked.connect(self.cancel)
                self.button_comment = QtWidgets.QPushButton("Add Comment")
                #self.button_comment.setToolTip("Add comment")
                icon_loc = icon = os.path.join(program_location,"icons","add_comment.png")
                self.button_comment.setIcon(QtGui.QIcon(icon_loc))
                # self.button_comment.clicked.connect(self.addUserComment)
                if self.tab_ecr.line_status.text()=="Draft":
                    self.button_cancel.setText("Delete")
                if self.tab_ecr.line_status.text()!="Rejected" and self.tab_ecr.line_status.text()!="Draft":
                    self.button_cancel.setDisabled(True)
                
                # buttonlayout.addWidget(self.button_save)
                # buttonlayout.addWidget(self.button_cancel)
                # buttonlayout.addWidget(self.button_comment)
                # buttonlayout.addWidget(self.button_release)
                self.toolbar.addWidget(self.button_save)
                self.toolbar.addWidget(self.button_cancel)
                self.toolbar.addWidget(self.button_comment)
                self.toolbar.addSeparator()
                self.toolbar.addWidget(self.button_release)
                if self.tab_signature.rowCount()==0:
                    self.button_release.setDisabled(True)
                self.tab_ecr.line_title.setReadOnly(False)
                self.tab_ecr.text_reason.setReadOnly(False)
                if self.tab_ecr.line_status.text()=="Out For Approval" or self.tab_ecr.line_status.text()=="Approved":
                    self.button_release.setDisabled(True)
                    #self.tab_signature.button_add.setDisabled(True)
                    #self.tab_signature.button_remove.setDisabled(True)
                if self.tab_ecr.line_status.text()=="Approved":
                    self.tab_ecr.line_title.setReadOnly(True)
                    self.tab_ecr.text_reason.setReadOnly(True)
                    self.tab_ecr.combo_type.setDisabled(True)
                    self.tab_ecr.combo_reason.setDisabled(True)
                    self.tab_ecr.combo_dept.setDisabled(True)
                    self.tab_signature.button_add.setDisabled(True)
            else:
                self.button_assign = QtWidgets.QPushButton("Assign")
                icon_loc = icon = os.path.join(program_location,"icons","approve.png")
                self.button_assign.setIcon(QtGui.QIcon(icon_loc))
                # self.button_approve.clicked.connect(self.approve)
                self.button_reject = QtWidgets.QPushButton("Reject")
                icon_loc = icon = os.path.join(program_location,"icons","reject.png")
                self.button_reject.setIcon(QtGui.QIcon(icon_loc))
                self.button_comment = QtWidgets.QPushButton("Add Comment")
                icon_loc = icon = os.path.join(program_location,"icons","add_comment.png")
                self.button_comment.setIcon(QtGui.QIcon(icon_loc))
                # self.button_comment.clicked.connect(self.addUserComment)
                # self.button_reject.clicked.connect(self.reject)
                # self.button_save = QtWidgets.QPushButton("Save")
                # icon_loc = icon = os.path.join(program_location,"icons","save.png")
                # self.button_save.setIcon(QtGui.QIcon(icon_loc))
                # self.button_save.clicked.connect(self.notificationSave)
                
                # self.toolbar.addWidget(self.button_save)
                self.toolbar.addWidget(self.button_comment)
                self.toolbar.addSeparator()
                self.toolbar.addWidget(self.button_assign)
                self.toolbar.addWidget(self.button_reject)
                
                self.tab_ecr.line_title.setReadOnly(True)
                self.tab_ecr.text_reason.setReadOnly(True)
                self.tab_ecr.combo_type.setDisabled(True)
                #self.tab_signature.button_remove.setDisabled(True)
                if self.tab_ecr.line_status.text()=="Rejected":
                    self.button_reject.setDisabled(True)
                    self.button_assign.setDisabled(True)
                if self.isUserSignable():
                    if self.hasUserSigned():
                        self.button_assign.setDisabled(True)
                    else:
                        self.button_assign.setDisabled(False)
                else:
                    self.button_assign.setDisabled(True)
                    self.button_reject.setDisabled(True)
                if self.tab_ecr.line_status.text()=="Approved":
                    self.button_reject.setDisabled(True)
        self.button_export = QtWidgets.QPushButton("Export")
        #self.button_export.setToolTip("Export ECN")
        icon_loc = icon = os.path.join(program_location,"icons","export.png")
        self.button_export.setIcon(QtGui.QIcon(icon_loc))
        # self.button_export.clicked.connect(self.exportPDF)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.button_export)
        
        self.button_preview = QtWidgets.QPushButton("Preview")
        # self.button_preview.clicked.connect(self.previewHTML)
        self.toolbar.addWidget(self.button_preview)
        
        if self.parent.user_permissions["rerouting"]=="y":
            self.button_check_stage = QtWidgets.QPushButton("Check Stage")
            # self.button_check_stage.clicked.connect(self.checkStage)
            self.toolbar.addWidget(self.button_check_stage)
        
        mainlayout.addWidget(self.toolbar)
        mainlayout.addWidget(self.tabwidget)
        
        # self.button_move_stage = QtWidgets.QPushButton("Move Stage")
        # self.button_move_stage.clicked.connect(self.moveECNStage)
        # self.toolbar.addWidget(self.button_move_stage)

        self.setCommentCount()
        self.setAttachmentCount()        
        
    def getCurrentValues(self):
        #print('getting values')
        self.now_type = self.tab_ecr.combo_type.currentText()
        self.now_title = self.tab_ecr.line_title.text()
        self.now_req_details = self.tab_ecr.text_reason.toHtml()
        #print(self.now_type)
        #print(self.now_title)
        #print(self.now_req_details)
        
    def generateECRID(self):
        date_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.doc_id = 'ECR-'+date_time[2:]
        self.tab_ecr.line_id.setText(self.doc_id)
    
    def checkEcrID(self):
        command = "select doc_id from document where doc_id = '" + self.doc_id + "'"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        if len(results)!=0:
            return True
        else:
            return False
        
    def setAttachmentCount(self):
        self.cursor.execute(f"SELECT COUNT(filename) from attachments where doc_id='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tabwidget.setTabText(1, "Attachments ("+str(result[0])+")")
        
    def setCommentCount(self):
        self.cursor.execute(f"SELECT COUNT(comment) from comments where doc_id='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tabwidget.setTabText(2, "Comments ("+str(result[0])+")")
        
    def save(self,msg = None):
        if not self.checkEcrID():
            if self.checkAllFields():
                self.insertData()
                if self.checkSigNotiDuplicate():
                    self.dispMsg("Error: Duplicate user found in Signature and Notifications. Please remove the duplicate before trying again.")
                else:
                    self.AddSignatures()
                    if not msg:
                        self.dispMsg("ECR has been saved!")
                    self.parent.repopulateTable()
                    if self.tab_signature.rowCount()>0 and self.tab_ecr.line_status.text()!="Out For Approval":
                        self.button_release.setDisabled(False)
                    self.button_cancel.setDisabled(False)
                ecn_folder = os.path.join(self.settings["ECN_Temp"],self.tab_ecr.line_id.text())
                if not os.path.exists(ecn_folder):
                    os.mkdir(ecn_folder)
        else:
            if self.checkAllFields():
                self.updateData()
                if self.checkSigNotiDuplicate():
                    self.dispMsg("Error: Duplicate user found in Signature and Notifications. Please remove the duplicate before trying again.")
                else:
                    self.AddSignatures()
                    if not msg:
                        self.dispMsg("ECR has been updated!")
                    if self.tab_signature.rowCount()>0 and self.tab_ecr.line_status.text()!="Out For Approval":
                        self.button_release.setDisabled(False)
                        
    def insertData(self):
        #inserting to ECN table
        try:
            doc_type = self.tab_ecr.combo_type.currentText()
            doc_reason = self.tab_ecr.combo_reason.currentText()
            author = self.tab_ecr.line_author.text()
            status = 'Draft'
            title = self.tab_ecr.line_title.text()
            reason =self.tab_ecr.text_reason.toHtml()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dept = self.tab_ecr.combo_dept.currentText()

            data = (self.doc_id,dept,doc_type,doc_reason,author,status,title,reason,modifieddate)
            self.cursor.execute("INSERT INTO document(doc_id,department,doc_type,doc_reason_code,author,status,doc_title,doc_reason,last_modified) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data))
            self.db.commit()
            
            if self.tab_attach.rowCount()>0:
                for x in range(self.tab_attach.rowCount()):
                    filename = self.tab_attach.model.getFileName(x)
                    filepath = self.tab_attach.model.getFilePath(x)
                    data = (self.doc_id, filename, filepath)
                    self.cursor.execute("INSERT INTO attachments(doc_id,filename,filepath) VALUES(%s,%s,%s)",(data))
                    self.db.commit()
                    self.setAttachmentCount()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData)!\n Error: {e}")
            
    def updateData(self):
        try:
            doc_type = self.tab_ecr.combo_type.currentText()
            doc_reason = self.tab_ecr.combo_reason.currentText()
            dept = self.tab_ecr.combo_dept.currentText()
            title = self.tab_ecr.line_title.text()
            reason =self.tab_ecr.text_reason.toHtml()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = (dept,doc_type,doc_reason,title,reason,modifieddate,self.doc_id)

            #data = (self.combo_type.currentText(),self.box_requestor.text(),self.date_request.date().toString("yyyy-MM-dd"),'Unassigned',self.line_ecntitle.text(),self.text_detail.toPlainText(),self.line_id.text())
            self.cursor.execute("UPDATE document SET department = %s, doc_type = %s, doc_reason_code = %s, doc_title = %s, doc_reason = %s, last_modified = %s WHERE doc_id = %s",(data))
            self.db.commit()
            
            if self.tab_attach.rowCount()>0:
                self.cursor.execute("DELETE FROM attachments WHERE doc_id = '" + self.doc_id + "'")
                self.db.commit()
                for x in range(self.tab_attach.rowCount()):
                    filename = self.tab_attach.model.getFileName(x)
                    filepath = self.tab_attach.model.getFilePath(x)
                    data = (self.doc_id, filename, filepath)
                    self.cursor.execute("INSERT INTO attachments(doc_id,filename,filepath) VALUES(%s,%s,%s)",(data))
                    self.db.commit()
                    self.setAttachmentCount()
            if self.tab_attach.rowCount()==0:
                self.cursor.execute("DELETE FROM attachments WHERE doc_id = '" + self.doc_id + "'")
                self.db.commit()
                self.setAttachmentCount()
                    
                
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (updateData)!\n Error: {e}")
            
    def loadData(self):
        self.tab_ecr.line_id.setText(self.doc_data['doc_id'])
        #self.tab_ecn.combo_type.setCurrentIndex(self.typeindex[results['ECN_TYPE']])
        self.tab_ecr.combo_type.setCurrentText(self.doc_data['doc_type'])
        self.tab_ecr.combo_reason.setCurrentText(self.doc_data['doc_reason_code'])
        self.tab_ecr.line_title.setText(self.doc_data['doc_title'])
        self.tab_ecr.text_reason.setHtml(self.doc_data['doc_reason'])
        self.tab_ecr.line_author.setText(self.doc_data['author'])
        self.tab_ecr.line_status.setText(self.doc_data['status'])
        if self.doc_data['department'] is not None:
            self.tab_ecr.combo_dept.setCurrentText(self.doc_data['department'])
        
        self.tab_signature.repopulateTable()
        self.tab_attach.repopulateTable()
        self.tab_comments.loadComments()   
                        
    def checkSigNotiDuplicate(self):
        sigs = []
        for row in range(self.tab_signature.rowCount()):
            sigs.append(self.tab_signature.model.get_user(row))
        # for row in range(self.tab_notification.rowCount()):
        #     sigs.append(self.tab_notification.model.get_user(row))
        #print(sigs)
        if len(sigs)==len(set(sigs)):
            return False
        else:
            return True
        
    def checkAllFields(self):
        if self.checkSigNotiDuplicate():
            self.dispMsg("Error: Duplicate user found in Signature and Notifications. Please remove the duplicate before trying again.")
            return False
        if not self.tab_ecr.checkFields():
            self.dispMsg("Error: Empty fields in header. Please set them and try again")
            return False
        return True
    
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
            
            self.db.commit()
            #print('data updated')
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (signature)!\n Error: {e}")
            
    def submit(self):
        try:
            self.save(1)
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.cursor.execute(f"SELECT first_release from document where doc_id='{self.doc_id}'")
            result = self.cursor.fetchone()
            if result[0] is None:
                self.cursor.execute(f"UPDATE document SET first_release = '{modifieddate}' where doc_id='{self.doc_id}'")
            data = (modifieddate, "Out For Approval",self.doc_id)
            self.cursor.execute("UPDATE document SET last_modified = %s, status = %s WHERE doc_id = %s",(data))
            self.db.commit()
            currentStage = self.getECNStage()
            if currentStage==0:
                self.setECNStage(1)
                self.addNotification(self.doc_id, "Stage Moved")
            self.tab_ecn.line_status.setText("Out For Approval")
            self.parent.repopulateTable()
            self.dispMsg("ECR has been saved and submitted!")
            #self.addNotification(self.ecn_id, "Released")
            self.button_submit.setDisabled(True)
            self.button_cancel.setText("Cancel")
            self.button_cancel.setDisabled(True)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (release)!\n Error: {e}")
            
    def setECRStage(self,stage):
        try:
            #print('setting ecn to ', stage)
            self.cursor.execute(f"UPDATE document SET stage ='{stage}', tempstage = '{stage}' where doc_id='{self.doc_id}'")
            self.db.commit()
        except Exception as e:
            self.dispMsg(f"Error trying to set ECR stage. Error: {e}")
            
    def resetECRStage(self):
        try:
            #print('resetting ecn stage')
            self.cursor.execute(f"UPDATE document SET stage = Null, tempstage = Null where doc_id='{self.doc_id}'")
            self.db.commit()
        except Exception as e:
            self.dispMsg(f"Error trying to reset ECR stage. Error: {e}")
            
    def isUserSignable(self):
        self.cursor.execute(f"SELECT user_id from signatures where doc_id='{self.doc_id}' and user_id='{self.user_info['user']}'")
        result = self.cursor.fetchone()
        if result is not None:
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
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
