from PySide6 import QtWidgets, QtCore, QtGui
import os, sys

import PySide6.QtGui
from Visual import *

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class PartImportPanel(QtWidgets.QWidget):
    def __init__(self,parent=None,index=None):
        super(PartImportPanel,self).__init__()
        self.windowWidth =  800
        self.windowHeight = 550
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.parent = parent
        self.visual = parent.visual
        self.initAtt()
        self.initUI()
        if index is not None:
            self.row = index.row()
            self.loadData(index.data(QtCore.Qt.DisplayRole))
        else:
            self.row = None
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
        title = "Part Import"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.center()

    def initUI(self):
        vlayout = QtWidgets.QVBoxLayout()
        
        search_layout= QtWidgets.QHBoxLayout()
        self.line_search = QtWidgets.QLineEdit()
        self.line_search.setPlaceholderText("Leave Blank to search all non-setup part, enter part if to search through BOM...")
        self.button_search = QtWidgets.QPushButton("Search")
        self.button_search.clicked.connect(self.search)
        search_layout.addWidget(self.line_search)
        search_layout.addWidget(self.button_search)
        
        titles = ['Select','Part','Description']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        self.button_import = QtWidgets.QPushButton("Import")
        self.button_import.setFixedWidth(200)
        vlayout.addLayout(search_layout)
        vlayout.addWidget(self.table)
        vlayout.addWidget(self.button_import)
        
        self.setLayout(vlayout)
        
    def search(self):
        if self.line_search.text() =="":
            results = self.visual.queryPartsNoStage()
        else:
            results = self.visual.queryPartsFromBOM(self.line_search.text())
        # for result in results:
        #     print(result)
        self.loadData(results)
        
    def loadData(self,data_set):
        self.table.clear()
        self.table.setRowCount(len(data_set))
        row = 0
        for data in data_set:
            checkbox_widget = QtWidgets.QWidget()
            checkbox = QtWidgets.QCheckBox()
            layout = QtWidgets.QHBoxLayout(checkbox_widget)
            layout.setAlignment(QtCore.Qt.AlignCenter)
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(checkbox)
            item = QtWidgets.QTableWidgetItem(data[0])
            item2 = QtWidgets.QTableWidgetItem(data[1])
            self.table.setCellWidget(row,0,checkbox_widget)
            self.table.setItem(row,1,item)
            self.table.setItem(row,2,item2)
            row+=1
        titles = ['Select','Part','Description']
        self.table.setHorizontalHeaderLabels(titles)
        
    def resizeEvent(self, event):
        self.table.setColumnWidth(0,self.width()*0.1)
        self.table.setColumnWidth(1,self.width()*0.4)
        self.table.setColumnWidth(2,self.width()*0.4)

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()