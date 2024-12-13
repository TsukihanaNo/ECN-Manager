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
        self.window_id = "ECN_Window"
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
        self.setWindowTitle(f"ECN-Viewer - user: {self.user_info['user']}")
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
        # self.button_save.clicked.connect(self.save)
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
        self.tab_parts = PartsTab(self)
        self.tab_attach = AttachmentTab(self)
        #self.tab_task = TasksTab(self)
        self.tab_comments = CommentTab(self)
        self.tab_signature = SignatureTab(self,"ECN",self.doc_data)
        #self.tab_changelog = ChangeLogTab(self,self.ecn_id)
        #self.tab_purch = PurchaserTab(self)
        #self.tab_planner = PlannerTab(self)
        #self.tab_shop = ShopTab(self)
        
        self.tabwidget.addTab(self.tab_ecr, "ECN")
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
                self.button_release.clicked.connect(self.release)
                self.button_cancel.clicked.connect(self.cancel)
                self.button_comment = QtWidgets.QPushButton("Add Comment")
                #self.button_comment.setToolTip("Add comment")
                icon_loc = icon = os.path.join(program_location,"icons","add_comment.png")
                self.button_comment.setIcon(QtGui.QIcon(icon_loc))
                self.button_comment.clicked.connect(self.addUserComment)
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
                self.tab_ecr.line_ecntitle.setReadOnly(False)
                self.tab_ecr.text_reason.setReadOnly(False)
                self.tab_ecr.text_summary.setReadOnly(False)
                if self.tab_ecr.line_status.text()=="Out For Approval" or self.tab_ecr.line_status.text()=="Approved":
                    self.button_release.setDisabled(True)
                    #self.tab_signature.button_add.setDisabled(True)
                    #self.tab_signature.button_remove.setDisabled(True)
                if self.tab_ecr.line_status.text()=="Approved":
                    self.tab_ecr.line_ecntitle.setReadOnly(True)
                    self.tab_ecr.text_summary.setReadOnly(True)
                    self.tab_ecr.text_reason.setReadOnly(True)
                    self.tab_ecr.box_requestor.setDisabled(True)
                    self.tab_ecr.combo_type.setDisabled(True)
                    self.tab_ecr.combo_reason.setDisabled(True)
                    self.tab_ecr.combo_dept.setDisabled(True)
                    self.tab_parts.button_remove.setDisabled(True)
                    self.tab_parts.button_add.setDisabled(True)
                    self.tab_parts.button_import_visual.setDisabled(True)
                    self.tab_signature.button_add.setDisabled(True)
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
                
                self.tab_ecr.line_ecntitle.setReadOnly(True)
                self.tab_ecr.text_summary.setReadOnly(True)
                self.tab_ecr.text_reason.setReadOnly(True)
                self.tab_ecr.box_requestor.setDisabled(True)
                self.tab_ecr.combo_type.setDisabled(True)
                self.tab_parts.button_remove.setDisabled(True)
                self.tab_parts.button_add.setDisabled(True)
                self.tab_signature.button_add.setDisabled(True)
                #self.tab_signature.button_remove.setDisabled(True)
                if self.tab_ecr.line_status.text()=="Rejected":
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
                if self.tab_ecr.line_status.text()=="Approved":
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
        
        
    def generateECRID(self):
        date_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.doc_id = 'ECR-'+date_time[2:]
        self.tab_ecr.line_id.setText(self.doc_id)
        
