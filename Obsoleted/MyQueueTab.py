from PySide6 import QtWidgets, QtCore
from ECNWindow import *
import sqlite3  
from MyTableWidget import *

class MyQueueTab(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(MyQueueTab,self).__init__()
        self.parent = parent
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        self.user_info = self.parent.user_info
        self.stage = self.parent.stageDict[self.user_info["title"]]
        print(self.stage)
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


    def initUI(self):
        self.initiateTable()

        self.button_open = QtWidgets.QPushButton("Open",self)
        self.button_open.clicked.connect(self.openECN)

        vlayout = QtWidgets.QVBoxLayout(self)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        vlayout.addWidget(self.table)
        hlayout.addWidget(self.button_open)
        vlayout.addLayout(hlayout)
        vlayout.setAlignment(QtCore.Qt.AlignCenter)

        self.button_open.setFixedWidth(200)

        self.setLayout(vlayout)


    def openECN(self):
        row = self.table.currentRow()
        ecn_id=self.table.item(row,0).text()
        self.parent.HookEcn(ecn_id)

    def initiateTable(self):
        titles = ['ECN ID','Type', 'Title', 'Status', 'Last Modified Date']
        self.table = MyTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


        self.table.doubleClicked.connect(self.openECN)
        self.repopulateTable()


    def repopulateTable(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        #command = "Select ECN_ID from SIGNATURE where USER_ID ='" + self.user_info['user'] + "'"
        self.cursor.execute(f"select ECN_ID from SIGNATURE where USER_ID='{self.user_info['user']}'")
        results = self.cursor.fetchall()
        ecn_id = []
        for result in results:
            ecn_id.append(result[0])
        #print(ecn_id)
        rowcount=0
        for ecn in ecn_id:
            command = f"Select * from ECN where ECN_ID ='{ecn}' and STATUS='Out For Approval' and STAGE>={self.stage}"
            self.cursor.execute(command)
            test = self.cursor.fetchall()
            for item in test:
                self.table.insertRow(rowcount)
                self.table.setItem(rowcount,0,QtWidgets.QTableWidgetItem(item['ECN_ID']))
                self.table.setItem(rowcount,1,QtWidgets.QTableWidgetItem(item['ECN_TYPE']))
                self.table.setItem(rowcount,2,QtWidgets.QTableWidgetItem(item['ECN_TITLE']))
                self.table.setItem(rowcount,3,QtWidgets.QTableWidgetItem(item['STATUS']))
                self.table.setItem(rowcount,4,QtWidgets.QTableWidgetItem(item['LAST_MODIFIED']))
                rowcount+=1

