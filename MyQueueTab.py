from PySide import QtGui, QtCore
from RequestWindow import *
import sqlite3  

class MyQueueTab(QtGui.QWidget):
    def __init__(self,parent=None):
        super(MyQueueTab,self).__init__()
        self.parent = parent
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        self.user_info = self.parent.user_info
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


    def initUI(self):
        self.initiateTable()

        self.button_open = QtGui.QPushButton("Open",self)
        self.button_open.clicked.connect(self.openRequest)

        vlayout = QtGui.QVBoxLayout(self)
        hlayout = QtGui.QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        vlayout.addWidget(self.table)
        hlayout.addWidget(self.button_open)
        vlayout.addLayout(hlayout)
        vlayout.setAlignment(QtCore.Qt.AlignCenter)

        self.button_open.setFixedWidth(200)

        self.setLayout(vlayout)


    def openRequest(self):
        row = self.table.currentRow()
        print(self.table.item(row,0).text())
        self.requestwindow = RequestWindow(self,self.table.item(row,0).text())

    def initiateTable(self):
        titles = ['ECN ID','Type', 'Title', 'Requestor', 'Status', 'Request Date','Assigned To','Assigned Date']
        self.table = QtGui.QTableWidget(1,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.repopulateTable()


    def repopulateTable(self):
        self.table.clearContents()
        command = "Select * from ECN where ASSIGNED_ENG is null"
        self.cursor.execute(command)
        test = self.cursor.fetchall()
        rowcount=0
        self.table.setRowCount(len(test))
        for item in test:
            self.table.setItem(rowcount,0,QtGui.QTableWidgetItem(item['ECN_ID']))
            self.table.setItem(rowcount,1,QtGui.QTableWidgetItem(item['ECN_TYPE']))
            self.table.setItem(rowcount,2,QtGui.QTableWidgetItem(item['ECN_TITLE']))
            self.table.setItem(rowcount,3,QtGui.QTableWidgetItem(item['STATUS']))
            self.table.setItem(rowcount,4,QtGui.QTableWidgetItem(item['ASSIGNED_ENG']))
            self.table.setItem(rowcount,5,QtGui.QTableWidgetItem(item['REQ_DATE']))
            self.table.setItem(rowcount,6,QtGui.QTableWidgetItem(item['ASSIGN_DATE']))
            rowcount+=1    
        #self.table.resizeColumnsToContents()

