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
from WebView import *
from string import Template
import sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class ECNWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, doc_id = None):
        super(ECNWindow,self).__init__()
        self.parent = parent
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.settings = parent.settings
        self.user_info = self.parent.user_info
        self.windowWidth =  950
        self.windowHeight = 580
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.doc_id = doc_id
        self.tablist = []
        #self.typeindex = {'New Part':0, 'BOM Update':1, 'Firmware Update':2, 'Configurator Update' : 3,'Product EOL':4}
        self.initAtt()
        if self.doc_id == None:
            self.doc_data = {"AUTHOR":self.parent.user_info["user"],"STATUS":"Draft"}
            self.initReqUI()
            self.generateECNID()
        else:
            command = "Select * from DOCUMENT where DOC_ID = '"+self.doc_id +"'"
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
        self.setWindowTitle(f"ECN-Viewer - user: {self.parent.user_info['user']}")
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
        self.button_save = QtWidgets.QPushButton("Save")
        #self.button_save.setToolTip("Save")
        icon_loc = icon = os.path.join(program_location,"icons","save.png")
        self.button_save.setIcon(QtGui.QIcon(icon_loc))
        self.button_release = QtWidgets.QPushButton("Release")
        #self.button_release.setToolTip("Release")
        icon_loc = icon = os.path.join(program_location,"icons","release.png")
        self.button_release.setIcon(QtGui.QIcon(icon_loc))
        self.button_release.setDisabled(True)
        self.button_save.clicked.connect(self.save)
        self.button_release.clicked.connect(self.release)
        self.button_cancel = QtWidgets.QPushButton("Delete")
        self.button_cancel.setToolTip("Delete")
        icon_loc = icon = os.path.join(program_location,"icons","cancel.png")
        self.button_cancel.setIcon(QtGui.QIcon(icon_loc))
        self.button_cancel.setDisabled(True)
        self.button_cancel.clicked.connect(self.cancel)
        
        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_cancel)
        self.toolbar.addWidget(self.button_release)
        
        # buttonlayout = QtWidgets.QHBoxLayout()
        # buttonlayout.addWidget(self.button_save)
        # buttonlayout.addWidget(self.button_cancel)
        # buttonlayout.addWidget(self.button_release)
        
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
        
        mainlayout.addWidget(self.toolbar)
        mainlayout.addWidget(self.tabwidget)
        #mainlayout.addLayout(buttonlayout)
        
        #self.tab_ecn.combo_dept.currentIndexChanged.connect(self.tab_signature.prepopulateTable)
        
        #self.tab_signature.prepopulateTable()


    def initFullUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        
        self.tabwidget = QtWidgets.QTabWidget(self)
        #self.tabwidget.currentChanged.connect(self.printIndex)
        self.tab_ecn = ECNTab(self)
        self.tab_parts = PartsTab(self)
        self.tab_attach = AttachmentTab(self)
        #self.tab_task = TasksTab(self)
        self.tab_comments = CommentTab(self)
        self.tab_signature = SignatureTab(self,"ECN",self.doc_data)
        self.tab_notification = NotificationTab(self,"ECN",self.doc_data)
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
        
        #buttonlayout = QtWidgets.QHBoxLayout()
        
        #disable signature and attachment adding if not author and completed
        if self.parent.user_info['user']==self.doc_data['AUTHOR'] and self.doc_data['STATUS']!="Completed":
            self.tab_signature.button_add.setEnabled(True)
            #self.tab_signature.button_remove.setEnabled(True)
            self.tab_attach.button_add.setEnabled(True)
            #self.tab_attach.button_remove.setEnabled(True)
            # self.tab_comments.enterText.setEnabled(True)
            # self.tab_comments.label_enterText.setVisible(True)
            # self.tab_comments.enterText.setVisible(True)
        else:
            self.tab_signature.button_add.setDisabled(True)
            #self.tab_signature.button_remove.setDisabled(True)
            self.tab_attach.button_add.setDisabled(True)
            #self.tab_attach.button_remove.setDisabled(True)
            # self.tab_comments.enterText.setDisabled(True)
            # self.tab_comments.label_enterText.setVisible(False)
            # self.tab_comments.enterText.setVisible(False)
        
        if self.tab_ecn.line_status.text()!="Completed":
            if self.parent.user_info['user']==self.tab_ecn.line_author.text():
                self.button_save = QtWidgets.QPushButton("Save")
                #self.button_save.setToolTip("Save")
                icon_loc = icon = os.path.join(program_location,"icons","save.png")
                self.button_save.setIcon(QtGui.QIcon(icon_loc))
                self.button_cancel = QtWidgets.QPushButton("Cancel")
                #self.button_cancel.setToolTip("Cancel")
                icon_loc = icon = os.path.join(program_location,"icons","cancel.png")
                self.button_cancel.setIcon(QtGui.QIcon(icon_loc))
                self.button_release = QtWidgets.QPushButton("Release")
                icon_loc = icon = os.path.join(program_location,"icons","release.png")
                self.button_release.setIcon(QtGui.QIcon(icon_loc))
                self.button_save.clicked.connect(self.save)
                self.button_release.clicked.connect(self.release)
                self.button_cancel.clicked.connect(self.cancel)
                self.button_comment = QtWidgets.QPushButton("Add Comment")
                #self.button_comment.setToolTip("Add comment")
                icon_loc = icon = os.path.join(program_location,"icons","add_comment.png")
                self.button_comment.setIcon(QtGui.QIcon(icon_loc))
                self.button_comment.clicked.connect(self.addUserComment)
                if self.tab_ecn.line_status.text()=="Draft":
                    self.button_cancel.setText("Delete")
                if self.tab_ecn.line_status.text()!="Rejected" and self.tab_ecn.line_status.text()!="Draft":
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
                self.tab_ecn.line_ecntitle.setReadOnly(False)
                self.tab_ecn.text_reason.setReadOnly(False)
                self.tab_ecn.text_summary.setReadOnly(False)
                if self.tab_ecn.line_status.text()=="Out For Approval":
                    self.button_release.setDisabled(True)
                    #self.tab_signature.button_add.setDisabled(True)
                    #self.tab_signature.button_remove.setDisabled(True)
            else:
                self.button_approve = QtWidgets.QPushButton("Approve")
                icon_loc = icon = os.path.join(program_location,"icons","approve.png")
                self.button_approve.setIcon(QtGui.QIcon(icon_loc))
                self.button_approve.clicked.connect(self.approve)
                self.button_reject = QtWidgets.QPushButton("Reject")
                icon_loc = icon = os.path.join(program_location,"icons","reject.png")
                self.button_reject.setIcon(QtGui.QIcon(icon_loc))
                self.button_comment = QtWidgets.QPushButton("Add Comment")
                icon_loc = icon = os.path.join(program_location,"icons","add_comment.png")
                self.button_comment.setIcon(QtGui.QIcon(icon_loc))
                self.button_comment.clicked.connect(self.addUserComment)
                self.button_reject.clicked.connect(self.reject)
                self.button_save = QtWidgets.QPushButton("Save")
                icon_loc = icon = os.path.join(program_location,"icons","save.png")
                self.button_save.setIcon(QtGui.QIcon(icon_loc))
                self.button_save.clicked.connect(self.notificationSave)
                
                self.toolbar.addWidget(self.button_save)
                self.toolbar.addWidget(self.button_comment)
                self.toolbar.addSeparator()
                self.toolbar.addWidget(self.button_approve)
                self.toolbar.addWidget(self.button_reject)
                
                self.tab_ecn.line_ecntitle.setReadOnly(True)
                self.tab_ecn.text_summary.setReadOnly(True)
                self.tab_ecn.text_reason.setReadOnly(True)
                self.tab_ecn.box_requestor.setDisabled(True)
                self.tab_ecn.combo_type.setDisabled(True)
                self.tab_parts.button_remove.setDisabled(True)
                self.tab_parts.button_add.setDisabled(True)
                self.tab_signature.button_add.setDisabled(True)
                #self.tab_signature.button_remove.setDisabled(True)
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
        else:
            self.tab_parts.button_add.setDisabled(True)
            self.tab_notification.button_add.setDisabled(True)
        self.button_export = QtWidgets.QPushButton("Export")
        #self.button_export.setToolTip("Export ECN")
        icon_loc = icon = os.path.join(program_location,"icons","export.png")
        self.button_export.setIcon(QtGui.QIcon(icon_loc))
        self.button_export.clicked.connect(self.exportPDF)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.button_export)
        
        self.button_preview = QtWidgets.QPushButton("Preview")
        self.button_preview.clicked.connect(self.previewHTML)
        self.toolbar.addWidget(self.button_preview)
        
        if self.parent.user_permissions["rerouting"]=="y":
            self.button_check_stage = QtWidgets.QPushButton("Check Stage")
            self.button_check_stage.clicked.connect(self.checkStage)
            self.toolbar.addWidget(self.button_check_stage)
        
        mainlayout.addWidget(self.toolbar)
        mainlayout.addWidget(self.tabwidget)
        
        # self.button_move_stage = QtWidgets.QPushButton("Move Stage")
        # self.button_move_stage.clicked.connect(self.moveECNStage)
        # self.toolbar.addWidget(self.button_move_stage)

        self.setCommentCount()
        self.setPartCount()
        self.setAttachmentCount()        
    
    def checkStage(self):
        try:
            self.checkComplete()
            self.db.commit()
            print("moving ecn stage check")
            self.moveECNStage()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (approve)!\n Error: {e}")

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
        self.doc_id = 'ECN-'+date_time[2:]
        self.tab_ecn.line_id.setText(self.doc_id)

    def insertData(self):
        #inserting to ECN table
        try:
            doc_type = self.tab_ecn.combo_type.currentText()
            author = self.tab_ecn.line_author.text()
            requestor = self.tab_ecn.box_requestor.currentText()
            status = 'Draft'
            title = self.tab_ecn.line_ecntitle.text()
            reason =self.tab_ecn.text_reason.toHtml()
            summary = self.tab_ecn.text_summary.toHtml()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dept = self.tab_ecn.combo_dept.currentText()

            data = (self.doc_id,dept,doc_type,author,requestor,status,title,reason,summary,modifieddate)
            self.cursor.execute("INSERT INTO DOCUMENT(DOC_ID,DEPARTMENT,DOC_TYPE,AUTHOR,REQUESTOR,STATUS,DOC_TITLE,DOC_REASON,DOC_SUMMARY,LAST_MODIFIED) VALUES(?,?,?,?,?,?,?,?,?,?)",(data))
            self.db.commit()
            
            if self.tab_parts.rowCount()>0:
                self.addParts()
                self.setPartCount()
            
            if self.tab_attach.rowCount()>0:
                for x in range(self.tab_attach.rowCount()):
                    filename = self.tab_attach.model.getFileName(x)
                    filepath = self.tab_attach.model.getFilePath(x)
                    data = (self.doc_id, filename, filepath)
                    self.cursor.execute("INSERT INTO ATTACHMENTS(DOC_ID,FILENAME,FILEPATH) VALUES(?,?,?)",(data))
                    self.db.commit()
                    self.setAttachmentCount()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData)!\n Error: {e}")
        
    def approve(self):
        try:
            approvedate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = (approvedate,self.doc_id,self.parent.user_info['user'])
            self.cursor.execute("UPDATE SIGNATURE SET SIGNED_DATE = ? WHERE DOC_ID = ? and USER_ID = ?",(data))
            self.cursor.execute(f"UPDATE DOCUMENT SET LAST_MODIFIED = '{approvedate}' where DOC_ID='{self.doc_id}'")
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
            self.addComment(self.doc_id, comment,"Rejecting to author")
            try:
                modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = (modifieddate, "Rejected",self.doc_id)
                self.cursor.execute("UPDATE DOCUMENT SET LAST_MODIFIED = ?, STATUS = ? WHERE DOC_ID = ?",(data))
                self.cursor.execute(f"UPDATE SIGNATURE SET SIGNED_DATE=Null where DOC_ID='{self.doc_id}'")
                self.db.commit()
                self.setECNStage(0)
                self.parent.repopulateTable()
                self.dispMsg("Rejection successful. Setting ECN stage to 0 and all signatures have been removed.")
                self.tab_ecn.line_status.setText("Rejected")
                self.addNotification(self.doc_id, "Rejected To Author",from_user=self.parent.user_info['user'],msg=comment)
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
            
            self.db.commit()
            #print('data updated')
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (signature)!\n Error: {e}")
            
    def addParts(self):
        try:
            self.cursor.execute("DELETE FROM PARTS WHERE DOC_ID = '" + self.doc_id + "'")
            self.db.commit()
            for row in range(self.tab_parts.rowCount()):
                part = self.tab_parts.model.get_part_id(row)
                desc = self.tab_parts.model.get_desc(row)
                ptype = self.tab_parts.model.get_type(row)
                disposition = self.tab_parts.model.get_disposition(row)
                insp = self.tab_parts.model.get_inspection(row)
                mfg = self.tab_parts.model.get_mfg(row)
                mfg_part = self.tab_parts.model.get_mfg_part(row)
                rep = self.tab_parts.model.get_replace(row)
                ref = self.tab_parts.model.get_reference(row)
                data = (self.doc_id, part, desc,ptype,disposition,mfg,mfg_part,rep,ref,insp)
                self.cursor.execute("INSERT INTO PARTS(DOC_ID,PART_ID,DESC,TYPE,DISPOSITION,MFG,MFG_PART,REPLACING,REFERENCE,INSPEC) VALUES(?,?,?,?,?,?,?,?,?,?)",(data))
                
            self.db.commit()
            #self.tab_parts.setStatusColor()
            #print('data inserted')
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (parts)!\n Error: {e}")

    def updateData(self):
        try:
            doc_type = self.tab_ecn.combo_type.currentText()
            dept = self.tab_ecn.combo_dept.currentText()
            requestor = self.tab_ecn.box_requestor.currentText()
            title = self.tab_ecn.line_ecntitle.text()
            reason =self.tab_ecn.text_reason.toHtml()
            summary = self.tab_ecn.text_summary.toHtml()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = (dept,doc_type,requestor,title,reason,summary,modifieddate,self.doc_id)

            #data = (self.combo_type.currentText(),self.box_requestor.text(),self.date_request.date().toString("yyyy-MM-dd"),'Unassigned',self.line_ecntitle.text(),self.text_detail.toPlainText(),self.line_id.text())
            self.cursor.execute("UPDATE DOCUMENT SET DEPARTMENT = ?, DOC_TYPE = ?, REQUESTOR = ?, DOC_TITLE = ?, DOC_REASON = ?, DOC_SUMMARY = ?, LAST_MODIFIED = ? WHERE DOC_ID = ?",(data))
            self.db.commit()
            
            if self.tab_parts.rowCount()>0:
                self.addParts()
                self.setPartCount()
            
            if self.tab_attach.rowCount()>0:
                self.cursor.execute("DELETE FROM ATTACHMENTS WHERE DOC_ID = '" + self.doc_id + "'")
                self.db.commit()
                for x in range(self.tab_attach.rowCount()):
                    filename = self.tab_attach.model.getFileName(x)
                    filepath = self.tab_attach.model.getFilePath(x)
                    data = (self.doc_id, filename, filepath)
                    self.cursor.execute("INSERT INTO ATTACHMENTS(DOC_ID,FILENAME,FILEPATH) VALUES(?,?,?)",(data))
                    self.db.commit()
                    self.setAttachmentCount()
            if self.tab_attach.rowCount()==0:
                self.cursor.execute("DELETE FROM ATTACHMENTS WHERE DOC_ID = '" + self.doc_id + "'")
                self.db.commit()
                self.setAttachmentCount()
                    
            # if self.tab_comments.enterText.toPlainText()!="":
            #     self.addComment(self.ecn_id,self.tab_comments.enterText.toPlainText(),"Author")
                
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (updateData)!\n Error: {e}")

    def loadData(self):
        self.tab_ecn.line_id.setText(self.doc_data['DOC_ID'])
        #self.tab_ecn.combo_type.setCurrentIndex(self.typeindex[results['ECN_TYPE']])
        self.tab_ecn.combo_type.setCurrentText(self.doc_data['DOC_TYPE'])
        self.tab_ecn.line_ecntitle.setText(self.doc_data['DOC_TITLE'])
        self.tab_ecn.text_reason.setHtml(self.doc_data['DOC_REASON'])
        self.tab_ecn.text_summary.setHtml(self.doc_data['DOC_SUMMARY'])
        self.tab_ecn.line_author.setText(self.doc_data['AUTHOR'])
        self.tab_ecn.box_requestor.setEditText(self.doc_data['REQUESTOR'])
        self.tab_ecn.line_status.setText(self.doc_data['STATUS'])
        if self.doc_data['DEPARTMENT'] is not None:
            self.tab_ecn.combo_dept.setCurrentText(self.doc_data['DEPARTMENT'])
        
        self.tab_signature.repopulateTable()
        self.tab_notification.repopulateTable()
        self.tab_parts.repopulateTable()
        self.tab_attach.repopulateTable()
        self.tab_comments.loadComments()    
        
    def addUserComment(self):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            self.addComment(self.doc_id, comment,"User Comment")
            self.addNotification(self.doc_id, "User Comment",from_user=self.parent.user_info['user'], msg=comment)
            #self.dispMsg("Comment has been added!")

    def addComment(self,doc_id,comment,commentType):
        #COMMENTS(ECN_ID TEXT, NAME TEXT, USER TEXT, COMM_DATE DATE, COMMENT TEXT
        data = (doc_id, self.parent.user_info['user'],datetime.now().strftime('%Y-%m-%d %H:%M:%S'),comment,commentType)
        self.cursor.execute("INSERT INTO COMMENTS(DOC_ID, USER, COMM_DATE, COMMENT,TYPE) VALUES(?,?,?,?,?)",(data))
        self.db.commit()
        # self.tab_comments.enterText.clear()
        #self.tab_comments.mainText.clear()
        self.tab_comments.addComment(data[1], data[2], data[4], data[3])
        self.setCommentCount()
        self.tabwidget.setCurrentIndex(3)
        
    def setCommentCount(self):
        self.cursor.execute(f"SELECT COUNT(COMMENT) from COMMENTS where DOC_ID='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tabwidget.setTabText(3, "Comments ("+str(result[0])+")")
        
    def setPartCount(self):
        self.cursor.execute(f"SELECT COUNT(PART_ID) from PARTS where DOC_ID='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tabwidget.setTabText(1, "Parts ("+str(result[0])+")")
        
    def setAttachmentCount(self):
        self.cursor.execute(f"SELECT COUNT(FILENAME) from ATTACHMENTS where DOC_ID='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tabwidget.setTabText(2, "Attachments ("+str(result[0])+")")
                
    def cancel(self):
        if self.tab_ecn.line_status.text()=="Draft":
            self.deleteECN(self.doc_id)
            self.close()
        else:
            self.cancelECN(self.doc_id)
        
    def deleteECN(self,doc_id):
        try:
            self.cursor.execute(f"DELETE FROM DOCUMENT where DOC_ID='{doc_id}'")
            self.cursor.execute(f"DELETE FROM COMMENTS where DOC_ID='{doc_id}'")
            self.cursor.execute(f"DELETE FROM SIGNATURE where DOC_ID='{doc_id}'")
            self.cursor.execute(f"DELETE FROM ATTACHMENTS where DOC_ID='{doc_id}'")
            self.cursor.execute(f"DELETE FROM CHANGELOG where DOC_ID='{doc_id}'")
            self.db.commit()
            self.dispMsg("ECN has been deleted")
            self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Problems occured trying to delete ECN.\n Error: {e}")
        
    def cancelECN(self,doc_id):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            try:
                self.addComment(self.doc_id, comment,"Canceling")
                self.cursor.execute(f"UPDATE DOCUMENT SET STATUS='Canceled' where DOC_ID='{doc_id}'")
                self.db.commit()
                self.dispMsg("ECN has been canceled")
                self.tab_ecn.line_status.setText("Canceled")
                self.parent.repopulateTable()
                self.addNotification(self.doc_id, "Canceling",from_user=self.parent.user_info['user'],msg=comment)
            except Exception as e:
                print(e)
                self.dispMsg(f"Problems occured trying to cancel ECN.\n Error:{e}")
        if ok and comment=="":
            self.dispMsg("Rejection failed: comment field was left blank.")
        
    def release(self):
        try:
            self.save(1)
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.cursor.execute(f"SELECT FIRST_RELEASE from DOCUMENT where DOC_ID='{self.doc_id}'")
            result = self.cursor.fetchone()
            if result[0] is None:
                self.cursor.execute(f"UPDATE DOCUMENT SET FIRST_RELEASE = '{modifieddate}' where DOC_ID='{self.doc_id}'")
            data = (modifieddate, "Out For Approval",self.doc_id)
            self.cursor.execute("UPDATE DOCUMENT SET LAST_MODIFIED = ?, STATUS = ? WHERE DOC_ID = ?",(data))
            self.db.commit()
            currentStage = self.getECNStage()
            if currentStage==0:
                self.setECNStage(self.getNextStage()[0])
                self.addNotification(self.doc_id, "Stage Moved")
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
            self.cursor.execute(f"Select TEMPSTAGE from DOCUMENT where DOC_ID='{self.doc_id}'")
            result = self.cursor.fetchone()
            #print("current stage",result[0])
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
        #print("titles generated", titles)
        return titles
    
    def moveECNStage(self):
        curStage = self.getECNStage()
        titles = self.getTitlesForStage()
        titles = titles[str(curStage)]
        #print("here are the titles",titles)
        move = True
        for title in titles:
            self.cursor.execute(f"Select SIGNED_DATE from SIGNATURE where DOC_ID = '{self.doc_id}' and JOB_TITLE='{title}' and TYPE='Signing'")
            results = self.cursor.fetchall()
            for result in results:
                #print(result['SIGNED_DATE'])
                if result['SIGNED_DATE'] is None:
                    move = False
                    #print("not moving to next stage")
                    break
        if move:
            nextStages = self.getNextStage()
            if len(nextStages)>0:
                #print("moving to stage:", nextStages[0])
                self.setECNStage(nextStages[0])
                self.addNotification(self.doc_id, "Stage Moved")
            # else:
            #     print("this is the last stage")
            
    def getNextStage(self):
        self.cursor.execute(f"Select JOB_TITLE from SIGNATURE where DOC_ID='{self.doc_id}' and SIGNED_DATE is NULL and TYPE='Signing'")
        results = self.cursor.fetchall()
        stage = []
        for result in results:
            #print(result[0])
            stage.append(self.parent.stageDict[result[0]])
        stage = sorted(stage)
        #print(stage)
        return stage
    
    def setECNStage(self,stage):
        try:
            #print('setting ecn to ', stage)
            self.cursor.execute(f"UPDATE DOCUMENT SET STAGE ='{stage}', TEMPSTAGE = '{stage}' where DOC_ID='{self.doc_id}'")
            self.db.commit()
        except Exception as e:
            self.dispMsg(f"Error trying to set ECN stage. Error: {e}")
            
    def resetECNStage(self):
        try:
            #print('resetting ecn stage')
            self.cursor.execute(f"UPDATE DOCUMENT SET STAGE = Null, TEMPSTAGE = Null where DOC_ID='{self.doc_id}'")
            self.db.commit()
        except Exception as e:
            self.dispMsg(f"Error trying to reset ECN stage. Error: {e}")
    
    def isUserSignable(self):
        curStage = self.getECNStage()
        #print(curStage)
        if curStage == 0:
            return False
        titles = self.getTitlesForStage()
        titles = titles[str(curStage)]
        self.cursor.execute(f"SELECT USER_ID from SIGNATURE where DOC_ID='{self.doc_id}' and USER_ID='{self.parent.user_info['user']}'")
        result = self.cursor.fetchone()
        if self.parent.user_info['title'] in titles and result is not None:
            return True
        return False
            
    def hasUserSigned(self):
        self.cursor.execute(f"SELECT SIGNED_DATE from SIGNATURE where DOC_ID='{self.doc_id}' and USER_ID='{self.parent.user_info['user']}'")
        result = self.cursor.fetchone()
        if result is None or result[0] is None:
            #print("found none returning false")
            return False
        else:
            return True
            
    def getCurrentValues(self):
        #print('getting values')
        self.now_type = self.tab_ecn.combo_type.currentText()
        self.now_title = self.tab_ecn.line_ecntitle.text()
        self.now_req_details = self.tab_ecn.text_reason.toHtml()
        #print(self.now_type)
        #print(self.now_title)
        #print(self.now_req_details)
        
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
                self.dispMsg("ECN is now completed")
                self.addNotification(self.doc_id, "Completed")
                self.tab_parts.button_add.setDisabled(True)
                self.tab_attach.button_add.setDisabled(True)
                self.tab_signature.button_add.setDisabled(True)
                self.tab_notification.button_add.setDisabled(True)
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
        for row in range(self.tab_signature.rowCount()):
            sigs.append(self.tab_signature.model.get_user(row))
        for row in range(self.tab_notification.rowCount()):
            sigs.append(self.tab_notification.model.get_user(row))
        #print(sigs)
        if len(sigs)==len(set(sigs)):
            return False
        else:
            return True
        
    def checkAllFields(self):
        # if not self.tab_parts.checkFields():
        #     self.dispMsg("Error: Empty fields in parts tab. Please fill them in and try again.")
        #     return False
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
                    if self.tab_signature.rowCount()>0 and self.tab_ecn.line_status.text()!="Out For Approval":
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
                    if self.tab_signature.rowCount()>0 and self.tab_ecn.line_status.text()!="Out For Approval":
                        self.button_release.setDisabled(False)
                    #self.getCurrentValues()
                    #self.checkDiff()
                    self.parent.repopulateTable()

    def saveAndClose(self):
        self.save()
        self.close()
        
    def generateHTML(self):
        template_loc = os.path.join(self.parent.programLoc,'templates','template.html')
        with open(template_loc) as f:
            lines = f.read() 
            f.close()

            t = Template(lines)
            id = self.doc_id
            self.cursor.execute(f"SELECT * from DOCUMENT where DOC_ID='{self.doc_id}'")
            result = self.cursor.fetchone()
            title = result['DOC_TITLE']
            author = result['AUTHOR']
            dept = result['DEPARTMENT']
            requestor = result['REQUESTOR']
            reason = result['DOC_REASON']
            summary = result['DOC_SUMMARY']
            signature = "<tr>"
            attachment ="<tr>"
            parts = ""
            
            #parts
            #print('exporting parts')
            self.cursor.execute(f"SELECT * from PARTS where DOC_ID='{self.doc_id}'")
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
            self.cursor.execute(f"SELECT * FROM ATTACHMENTS where DOC_ID='{self.doc_id}'")
            results = self.cursor.fetchall()
            if results is not None:
                for result in results:
                    attachment += "<td>"+result['FILENAME']+"</td>"
                    attachment += "<td>"+result['FILEPATH']+"</td></tr>"
            else:
                attachment="<tr><td></td><td></td></tr>"

            
            #print('exporting signatures')
            self.cursor.execute(f"SELECT * from SIGNATURE where DOC_ID='{self.doc_id}' and TYPE='Signing'")
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
            
            html = t.substitute(ECNID=id,ECNTitle=title,Requestor=requestor,Department=dept,Author=author, Reason=reason,Summary=summary,Parts=parts,Attachment=attachment,Signature=signature)

            return html

    def previewHTML(self):
        html = self.generateHTML()
        self.webview = WebView()
        self.webview.setDocID(self.doc_id)
        self.webview.loadHtml(html)

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
            self.dispMsg(f"Error Occured during ecn export.\n Error: {e}")
        
    def addNotification(self,doc_id,notificationType,from_user=None,userslist=None,msg=""):
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
        else:
            users = ""
        if from_user is None:
            from_user = ""
                
        if self.existNotification(doc_id) and notificationType!="User Comment":
            data = (notificationType,from_user,users,msg, doc_id)
            self.cursor.execute("UPDATE NOTIFICATION SET TYPE = ?, FROM_USER = ?, USERS = ?, MSG = ? WHERE DOC_ID = ?",(data))
        else:
            data = (doc_id,"Not Sent",notificationType,from_user, users, msg)
            self.cursor.execute("INSERT INTO NOTIFICATION(DOC_ID, STATUS, TYPE,FROM_USER, USERS, MSG) VALUES(?,?,?,?,?,?)",(data))
        self.db.commit()
        
    def existNotification(self,doc_id):
        self.cursor.execute(f"Select * from NOTIFICATION where DOC_ID='{doc_id}' and STATUS='Not Sent'")
        result = self.cursor.fetchone()
        if result is not None:
            return True
        else:
            return False


    def checkDiff(self):
        doc_id = self.doc_id
        changedate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = self.parent.user_info['user']
        prevdata = self.now_type
        newdata = self.tab_ecn.combo_type.currentText()
        if newdata != prevdata:
            data = (doc_id,changedate,user,prevdata,newdata)
            self.cursor.execute("INSERT INTO CHANGELOG(DOC_ID, CHANGEDATE, NAME, PREVDATA, NEWDATA) VALUES(?,?,?,?,?)",(data))
            print('adding type change')
        prevdata = self.now_title
        newdata = self.tab_ecn.line_ecntitle.text()
        if newdata != prevdata:
            data = (doc_id,changedate,user,prevdata,newdata)
            self.cursor.execute("INSERT INTO CHANGELOG(DOC_ID, CHANGEDATE, NAME, PREVDATA, NEWDATA) VALUES(?,?,?,?,?)",(data))
            print('adding title change')
        prevdata = self.now_req_details
        newdata = self.tab_ecn.text_reason.toHtml()  
        if newdata != prevdata:
            data = (doc_id,changedate,user,prevdata,newdata)
            self.cursor.execute("INSERT INTO CHANGELOG(DOC_ID, CHANGEDATE, NAME, PREVDATA, NEWDATA) VALUES(?,?,?,?,?)",(data))
            print('adding detail change')
        self.db.commit()
        self.tab_changelog.repopulateTable()
        


    def checkEcnID(self):
        command = "select DOC_ID from DOCUMENT where DOC_ID = '" + self.doc_id + "'"
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