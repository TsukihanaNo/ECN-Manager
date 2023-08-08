from PySide6 import QtWidgets, QtCore
from datetime import datetime
from PurchReqTab import *
from ProjectPartsTab import *
from ProjectScheduleTab import *
from ProjectMembers import *
import sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class ProjectWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, doc_id = None):
        super(ProjectWindow,self).__init__()
        self.parent = parent
        self.cursor = parent.cursor
        self.db = self.parent.db
        self.settings = parent.settings
        self.user_info = self.parent.user_info
        self.user_permissions = parent.user_permissions
        self.ico = parent.ico
        self.visual = parent.visual
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.stageDictPRQ = parent.stageDictPRQ
        self.windowWidth =  950
        self.windowHeight = 580
        self.access = "write"
        # self.setFixedSize(self.windowWidth,self.windowHeight)
        self.doc_id = doc_id
        self.tablist = []
        self.initAtt()
        
        if self.doc_id is not None:
            self.getMembers()
            if self.user_info['user']!=self.getAuthor() and self.user_info['user'] not in self.members:
                self.access = "read"
            self.initUI()
            self.loadData()
        else:
            self.initUI()
            
            
        self.center()
        self.show()
        self.activateWindow()
        print(self.access)

    def initAtt(self):
        self.setWindowIcon(self.parent.ico)
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle(f"Project- user: {self.parent.user_info['user']}")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMinimumWidth(self.windowWidth)
        self.setMinimumHeight(self.windowHeight)
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
        

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        
        self.button_save = QtWidgets.QPushButton("Save")
        if self.access=="read":
            self.button_save.setDisabled(True)
        self.button_save.clicked.connect(self.save)
        self.button_members = QtWidgets.QPushButton("Members")
        self.button_members.clicked.connect(self.launchMembers)
        
        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_members)
        
        self.label_id = QtWidgets.QLabel("Project ID:")
        self.line_id = QtWidgets.QLineEdit()
        self.line_id.setFixedWidth(125)
        self.line_id.setReadOnly(True)
        self.label_title = QtWidgets.QLabel("Project Name:")
        self.line_title = QtWidgets.QLineEdit()
        self.label_status = QtWidgets.QLabel("Status:")
        self.line_status = QtWidgets.QLineEdit()
        self.line_status.setFixedWidth(125)
        self.line_status.setReadOnly(True)
        self.label_author = QtWidgets.QLabel("Author:")
        self.line_author = QtWidgets.QLineEdit()
        self.line_author.setFixedWidth(125)
        self.line_author.setReadOnly(True)
        self.line_author.setText(self.user_info['user'])
        layout_header = QtWidgets.QHBoxLayout()
        layout_header.addWidget(self.label_id)
        layout_header.addWidget(self.line_id)
        layout_header.addWidget(self.label_title)
        layout_header.addWidget(self.line_title)
        layout_header.addWidget(self.label_status)
        layout_header.addWidget(self.line_status)
        layout_header.addWidget(self.label_author)
        layout_header.addWidget(self.line_author)
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_parts = ProjectPartsTab(self)
        self.tab_purch_req = PurchReqTab(self)
        self.tab_schedule = ProjectScheduleTab(self)
        
        self.tab_widget.addTab(self.tab_parts,"Parts")
        self.tab_widget.addTab(self.tab_purch_req,"Purch Reqs")
        self.tab_widget.addTab(self.tab_schedule, "Schedule")
        
        mainlayout.addWidget(self.toolbar)
        mainlayout.addLayout(layout_header)
        mainlayout.addWidget(self.tab_widget)
        self.setLayout(mainlayout)
        
    def getMembers(self):
        self.members = []
        self.cursor.execute(f"Select * from PROJECT_MEMBERS where PROJECT_ID ='{self.doc_id}'")
        results = self.cursor.fetchall()
        for result in results:
            self.members.append(result[1])
        

    def save(self,msg = None):
        if self.checkFields():
            if self.doc_id is None:
                self.generateID()
                self.tab_purch_req.button_add.setEnabled(True)
            if not self.checkID():
                self.insertData()
                if not msg:
                    self.dispMsg("Project has been saved!")
                self.parent.repopulateTable()
            else:
                self.updateData()
                if not msg:
                    self.dispMsg("Project has been updated!")
                self.parent.repopulateTable()
            self.tab_schedule.saveData()
            
    def launchMembers(self):
        self.members_window = ProjectMembers(self)
    
    def checkID(self):
        self.cursor.execute(f"select DOC_ID from DOCUMENT where DOC_ID='{self.line_id.text()}'")
        result = self.cursor.fetchone()
        if result is not None:
            return True
        else:
            return False
        
    def checkFields(self):
        if self.line_title.text()=="":
            self.dispMsg("Please enter a title for this project.")
            return False
        return True
        
    def generateID(self):
        date_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.doc_id = 'PRJ-'+date_time[2:]
        self.line_id.setText(self.doc_id)

    def insertData(self):
        try:
            doc_type = "Project"
            status = 'Started'
            title = self.line_title.text()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            first_released = modifieddate
            author = self.user_info['user']
            data = (self.doc_id,doc_type,status,title,author,modifieddate,first_released)
            self.cursor.execute("INSERT INTO DOCUMENT(DOC_ID,DOC_TYPE,STATUS,DOC_TITLE,AUTHOR,LAST_MODIFIED,FIRST_RELEASE) VALUES(?,?,?,?,?,?,?)",(data))
            self.db.commit()
            self.tab_parts.saveData()
            self.tab_schedule.saveData()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData)!\n Error: {e}")
            
    def updateData(self):
        try:
            doc_type = "Project"
            status = self.line_status.text()
            title = self.line_title.text()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            first_released = modifieddate
            author = self.user_info['user']
            data = (self.doc_id,doc_type,status,title,author,modifieddate,first_released)
            # self.cursor.execute("INSERT INTO DOCUMENT(DOC_ID,DOC_TYPE,STATUS,DOC_TITLE,AUTHOR,LAST_MODIFIED,FIRST_RELEASE) VALUES(?,?,?,?,?,?,?)",(data))
            # self.db.commit()
            self.tab_parts.saveData()
            self.tab_schedule.saveData()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData)!\n Error: {e}")
    
    def loadData(self):
        self.cursor.execute(f"select * from DOCUMENT where DOC_ID='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.line_id.setText(result['DOC_ID'])
        self.line_title.setText(result["DOC_TITLE"])
        self.line_status.setText(result["STATUS"])
        self.line_author.setText(result['AUTHOR'])
        self.tab_purch_req.repopulateTable()
        self.tab_parts.loadData()
        self.tab_schedule.loadData()
        
    def getAuthor(self):
        self.cursor.execute(f"select author from DOCUMENT where DOC_ID='{self.doc_id}'")
        result = self.cursor.fetchone()
        return result[0]
        
    # def addParts(self):
    #     # part_id, desc,fab_type,status,vendor, vendor_part_id,tooling_po, tooling_cost,cost_per,notes,part_po,ecn, qty_on_hand, qty_incoming
    #     try:
    #         self.cursor.execute("DELETE FROM PARTS WHERE DOC_ID = '" + self.doc_id + "'")
    #         self.db.commit()
    #         for row in range(self.tab_parts.rowCount()):
    #             part_data = self.tab_parts.model.get_part_data(row)
    #             data = (self.doc_id, part, desc,ptype,disposition,mfg,mfg_part,rep,ref,insp)
    #             self.cursor.execute("INSERT INTO PROJECT_PARTS(DOC_ID,PART_ID,DESC,TYPE,DISPOSITION,MFG,MFG_PART,REPLACING,REFERENCE,INSPEC) VALUES(?,?,?,?,?,?,?,?,?,?)",(data))
                
    #         self.db.commit()
    #         #self.tab_parts.setStatusColor()
    #         #print('data inserted')
    #     except Exception as e:
    #         print(e)
    #         self.dispMsg(f"Error occured during data update (parts)!\n Error: {e}")
        

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def closeEvent(self, event):
        self.parent.projectWindow = None