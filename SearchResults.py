from PySide6 import QtWidgets, QtCore, QtGui
import os, sys
from MyTableWidget import *
import sqlite3  


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class SearchResults(QtWidgets.QWidget):
    def __init__(self,parent=None,matches = None):
        super(SearchResults,self).__init__()
        self.windowWidth =  800
        self.windowHeight = 550
        self.parent = parent
        self.matches = matches
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
        title = "Search Results"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        
        

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        searchLayout = QtWidgets.QHBoxLayout()
        self.line_search = QtWidgets.QLineEdit(self)
        self.line_search.setPlaceholderText("Search here")
        self.button_search = QtWidgets.QPushButton("Search")
        self.line_search.returnPressed.connect(self.search)
        self.button_search.clicked.connect(self.search)
        searchLayout.addWidget(self.line_search)
        searchLayout.addWidget(self.button_search)
        self.button_open = QtWidgets.QPushButton("Open")
        self.button_open.clicked.connect(self.openECN)
        self.button_open.setDisabled(True)

        #USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, DEPT TEXT, STATUS TEXT, EMAIL TEXT)
        titles = ['ECN ID','ECN Title','Status','Author']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.openECN)
        self.table.selectionModel().selectionChanged.connect(self.onRowSelect)
        main_layout.addLayout(searchLayout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.button_open)
        
        self.repopulateTable()
        
    def onRowSelect(self):
        self.button_open.setEnabled(bool(self.table.selectionModel().selectedRows()))
    
    def repopulateTable(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        rowcount=0
        for match in self.matches:
            self.parent.cursor.execute(f"Select * FROM ECN where ECN_ID ='{match}'")
            results = self.parent.cursor.fetchall()
            self.table.insertRow(rowcount)
            for result in results: #['ECN ID','ECN Title','Status','Author']
                self.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['ECN_ID']))
                self.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['ECN_TITLE']))
                self.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['STATUS']))
                self.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['AUTHOR']))

            rowcount+=1
            
    def openECN(self):
        row = self.table.currentRow()
        ecn_id =self.table.item(row,0).text()
        self.parent.HookEcn(ecn_id)
        
    def search(self):
        if self.line_search.text()!="":
            search = self.line_search.text()
            self.matches = []
            self.parent.cursor.execute(f"Select ECN_ID from ECN where ECN_TITLE like '%{search}%' OR ECN_REASON like '%{search}%' OR ECN_SUMMARY like '%{search}%'")
            results = self.parent.cursor.fetchall()
            for result in results:
                if result[0] not in self.matches:
                    self.matches.append(result[0])
            self.parent.cursor.execute(f"Select ECN_ID from ATTACHMENTS where FILENAME like '%{search}%'")
            results = self.parent.cursor.fetchall()
            for result in results:
                if result[0] not in self.matches:
                    self.matches.append(result[0])
            self.parent.cursor.execute(f"Select ECN_ID from PARTS where PART_ID like '%{search}%' OR DESC like '%{search}%'")
            results = self.parent.cursor.fetchall()
            for result in results:
                if result[0] not in self.matches:
                    self.matches.append(result[0])
            self.repopulateTable()

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
