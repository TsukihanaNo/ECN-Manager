from PySide6 import QtWidgets, QtCore
from datetime import datetime
from PurchReqTab import *
from ProjectPartsTab import *
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
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.settings = parent.settings
        self.user_info = self.parent.user_info
        self.ico = parent.ico
        self.visual = parent.visual
        self.windowWidth =  950
        self.windowHeight = 580
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.doc_id = doc_id
        self.tablist = []
        self.initAtt()
        self.initUI()
            
        self.center()
        self.show()
        self.activateWindow()

    def initAtt(self):
        self.setWindowIcon(self.parent.ico)
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle(f"Project- user: {self.parent.user_info['user']}")
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
        

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        
        self.button_save = QtWidgets.QPushButton("Save")
        self.button_req_check = QtWidgets.QPushButton("Check For Reqs")
        # self.button_members = QtWidgets.QPushButton("Members")
        
        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_req_check)
        # self.toolbar.addWidget(self.button_members)
        
        self.label_id = QtWidgets.QLabel("Project ID:")
        self.line_id = QtWidgets.QLineEdit()
        self.label_title = QtWidgets.QLabel("Project Name:")
        self.line_title = QtWidgets.QLineEdit()
        layout_header = QtWidgets.QHBoxLayout()
        layout_header.addWidget(self.label_id)
        layout_header.addWidget(self.line_id)
        layout_header.addWidget(self.label_title)
        layout_header.addWidget(self.line_title)
        self.tab_widget = QtWidgets.QTabWidget(self)
        # self.tab_material = ProjectPartsTab(self)
        self.tab_purch_req = PurchReqTab(self)
        # self.tab_widget.addTab(self.tab_material,"Parts")
        self.tab_widget.addTab(self.tab_purch_req,"Purch Reqs")
        
        mainlayout.addWidget(self.toolbar)
        mainlayout.addLayout(layout_header)
        mainlayout.addWidget(self.tab_widget)
        self.setLayout(mainlayout)



    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def closeEvent(self, event):
        self.parent.projectWindow = None