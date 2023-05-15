from PySide6 import QtWidgets, QtCore, QtGui
from datetime import datetime
import sys, os
from PurchReqDetailsTab import *

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
        self.db = self.parent.db
        self.settings = parent.settings
        self.user_info = self.parent.user_info
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
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.addTab(self.tab_purch_req,"Purch Reqs")
        
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
            if self.checkFields():
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
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            author = self.user_info['user']
            detail = self.tab_purch_req.text_details.toHtml()
            data = (self.project_id,self.doc_id,req_id,detail,status,author,modifieddate)
            self.cursor.execute("INSERT INTO PURCH_REQS(PROJECT_ID,DOC_ID,REQ_ID,DETAILS,STATUS,AUTHOR,LAST_MODIFIED) VALUES(?,?,?,?,?,?,?)",(data))
            self.db.commit()
            self.parent.model.add_req(self.doc_id,req_id,status)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData)!\n Error: {e}")
            
    def updateData(self):
        try:
            req_id = self.tab_purch_req.line_id.text()
            detail = self.tab_purch_req.text_details.toHtml()
            data = (req_id, detail,self.doc_id)
            status = self.tab_purch_req.line_status.text()
            self.cursor.execute("UPDATE PURCH_REQS SET REQ_ID = ?, DETAILS = ? WHERE DOC_ID = ?",(data))
            self.db.commit()
            self.parent.model.update_req_data(self.row,self.doc_id,req_id,status)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (updateData)!\n Error: {e}")
    
    def loadData(self):
        self.cursor.execute(f"select * from PURCH_REQS where DOC_ID='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tab_purch_req.line_doc_id.setText(result['DOC_ID'])
        self.tab_purch_req.line_id.setText(result["REQ_ID"])
        self.tab_purch_req.line_status.setText(result["STATUS"])
        self.tab_purch_req.text_details.setHtml(result["DETAILS"])
        self.tab_purch_req.line_author.setText(result["AUTHOR"])
        self.tab_purch_req.loadHeader()
        self.tab_purch_req.loadItems()
        
        
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def closeEvent(self, event):
        self.parent.projectWindow = None