from PySide6 import QtWidgets, QtCore, QtGui
import os, sys
import sqlite3
from Delegates import *
from datetime import *


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
        self.windowWidth =  1100
        self.windowHeight = 550
        self.titleStageDict = parent.titleStageDict
        self.sorting = (0,QtCore.Qt.DescendingOrder)
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
        titles = ['ECN ID','Type', 'Title', 'Status', 'Last Modified', 'Stage','Waiting On', 'Elapsed Days']
        self.table = QtWidgets.QTableWidget(1,len(titles),self)
        delegate = AlignDelegate(self.table)
        self.table.setItemDelegate(delegate)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().sortIndicatorChanged.connect(self.setSort)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.doubleClicked.connect(self.openECN)
        self.table.selectionModel().selectionChanged.connect(self.onRowSelect)
        header = self.table.horizontalHeader()
        for x in range(self.table.columnCount()):
            if x != 2 and x!=6:
                header.setSectionResizeMode(x,QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(x,QtWidgets.QHeaderView.Stretch)
        main_layout.addLayout(searchLayout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.button_open)
        
        self.repopulateTable()
        
    def setSort(self, index, order):
        self.sorting = (index,order)
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
            for item in results: #['ECN ID','ECN Title','Status','Author']
                self.table.setItem(rowcount,0,QtWidgets.QTableWidgetItem(item['ECN_ID']))
                self.table.setItem(rowcount,1,QtWidgets.QTableWidgetItem(item['ECN_TYPE']))
                self.table.setItem(rowcount,2,QtWidgets.QTableWidgetItem(item['ECN_TITLE']))
                self.table.setItem(rowcount,3,QtWidgets.QTableWidgetItem(item['STATUS']))
                self.table.setItem(rowcount,4,QtWidgets.QTableWidgetItem(item['LAST_MODIFIED']))
                if item['STATUS']!='Draft':
                    self.table.setItem(rowcount, 5, QtWidgets.QTableWidgetItem(str(item['STAGE'])))
                    if item['STATUS']!="Completed":
                        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        elapsed = self.getElapsedDays(today, item['FIRST_RELEASE'])
                        elapsed_days = "{:.2f}".format(elapsed.days + round(elapsed.seconds/86400,2))
                        self.table.setItem(rowcount, 7, QtWidgets.QTableWidgetItem(elapsed_days))
                    else:
                        self.table.setItem(rowcount, 7, QtWidgets.QTableWidgetItem(str(item["COMP_DAYS"])))
                    if item['STAGE']!=0:
                        users = self.getWaitingUser(item['ECN_ID'], self.titleStageDict[str(item['STAGE'])])
                        self.table.setItem(rowcount, 6, QtWidgets.QTableWidgetItem(users))
                if item["STATUS"]=="Rejected":
                    self.table.item(rowcount, 3).setBackground(QtGui.QColor("#FFADAD")) #red
                if item["STATUS"]=="Out For Approval":
                    self.table.item(rowcount, 3).setBackground(QtGui.QColor("#CAFFBF")) #green
                rowcount+=1
            self.table.sortItems(self.sorting[0],self.sorting[1])

            
    def openECN(self):
        row = self.table.currentRow()
        ecn_id =self.table.item(row,0).text()
        self.parent.HookEcn(ecn_id)
        
    def getElapsedDays(self,day1,day2):
        today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        day1 = datetime.strptime(day1,'%Y-%m-%d %H:%M:%S')
        day2 = datetime.strptime(day2,'%Y-%m-%d %H:%M:%S')
        if day2>day1:
            elapsed = day2 - day1
        else:
            elapsed = day1 - day2
        #return elapsed.days
        return elapsed
    
    def getTitleStageDict(self):
        self.titleStageDict = {}
        for key, value in self.stageDict.items():
            if value not in self.titleStageDict.keys():
                self.titleStageDict[value]=[key]
            else:
                self.titleStageDict[value].append(key)
                
    def getWaitingUser(self,ecn,titles):
        users = []
        usr_str = ""
        for title in titles:
            self.parent.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn}' and JOB_TITLE='{title}' and SIGNED_DATE is Null")
            result = self.parent.cursor.fetchone()
            if result is not None:
                users.append(result[0])
        count = 0
        for user in users:
            usr_str += user
            if count<len(users)-1:
                usr_str+=","
            count+=1
        return usr_str
        
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
