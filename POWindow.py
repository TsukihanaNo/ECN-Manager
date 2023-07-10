from PySide6 import QtWidgets, QtCore
from datetime import datetime
from PurchReqTab import *
from ProjectScheduleTab import *
import sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))
    
class POWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, part_id = None):
        super(POWindow,self).__init__()
        self.parent = parent
        self.cursor = parent.cursor
        self.db = parent.db
        self.visual = parent.visual
        self.windowWidth =  950
        self.windowHeight = 580
        self.part_id = part_id
        self.initAtt()
        self.initUI()
        if self.part_id is not None:
            self.loadPOs()
        self.center()
        self.show()
        self.activateWindow()
        
    def initAtt(self):
        # self.setWindowIcon(self.parent.ico)
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        # self.setWindowTitle(f"Project- user: {self.parent.user_info['user']}")
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
        # self.button_save.clicked.connect(self.save)
        
        self.toolbar.addWidget(self.button_save)
        
        hlayout = QtWidgets.QHBoxLayout()
        self.po_list = QtWidgets.QListWidget()
        self.po_list.setFixedWidth(250)
        self.po_list.itemSelectionChanged.connect(self.showPoInfo)
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        hlayout.addWidget(self.po_list)
        hlayout.addWidget(self.text_edit)

        mainlayout.addWidget(self.toolbar)
        mainlayout.addLayout(hlayout)
        self.setLayout(mainlayout)
        
    def loadPOs(self):
        results = self.visual.getPurchLineInfo(self.part_id)
        for result in results:
            po_item = QtWidgets.QListWidgetItem(result[0])
            self.po_list.addItem(po_item)
            
    def showPoInfo(self):
        po_id = self.po_list.currentItem().text()
        self.text_edit.clear()
        po_info = self.visual.getPurchOrderInfo(po_id)
        self.text_edit.append(f"Vendor ID: {po_info[1]}\n")
        self.text_edit.append(f"Status: {po_info[2]}\n")
        self.text_edit.append(f"Desired Receive Date: {po_info[3]}\n")
        self.text_edit.append(f"Promise Date: {po_info[4]}\n")
        