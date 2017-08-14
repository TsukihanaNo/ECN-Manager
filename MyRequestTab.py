from PySide import QtGui, QtCore
from NewRequestForm import *
import sqlite3
class MyRequestTab(QtGui.QWidget):
    def __init__(self,parent=None):
        super(MyRequestTab,self).__init__()
        self.parent = parent
        self.cursor = self.parent.cursor

        self.initUI()

    def initUI(self):
        self.initiateTable()

        self.button_open = QtGui.QPushButton("Open",self)
        self.button_new = QtGui.QPushButton("New Request",self)

        vlayout = QtGui.QVBoxLayout(self)
        hlayout = QtGui.QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        vlayout.addWidget(self.table)

        hlayout.addWidget(self.button_open)
        hlayout.addWidget(self.button_new)

        vlayout.addLayout(hlayout)
        vlayout.setAlignment(QtCore.Qt.AlignCenter)

        self.button_open.setFixedWidth(200)
        self.button_new.setFixedWidth(200)

        self.setLayout(vlayout)

        self.button_new.clicked.connect(self.newRequest)

    def newRequest(self):
        self.newRequestForm = NewRequestForm(self)

    def initiateTable(self):
        titles = ['ECN ID','Type', 'Title', 'Status','Assigned To', 'Request Date', 'Assigned Date']
        self.cursor.execute("SELECT * FROM ECN")
        test = self.cursor.fetchall()
        rowcount=0
        self.table = QtGui.QTableWidget(len(test),len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        for item in test:
            print(item)
            self.table.setItem(rowcount,0,QtGui.QTableWidgetItem(item[0]))
            self.table.setItem(rowcount,1,QtGui.QTableWidgetItem(item[1]))
            self.table.setItem(rowcount,2,QtGui.QTableWidgetItem(item[2]))
            self.table.setItem(rowcount,3,QtGui.QTableWidgetItem(item[6]))
            self.table.setItem(rowcount,4,QtGui.QTableWidgetItem("No One"))
            self.table.setItem(rowcount,5,QtGui.QTableWidgetItem(item[7]))
            self.table.setItem(rowcount,6,QtGui.QTableWidgetItem("Not yet!"))
            rowcount+=1    
        #self.table.resizeColumnsToContents()

    def repopulateTable(self):
        self.table.clearContents()
        self.cursor.execute("SELECT * FROM ECN")
        test = self.cursor.fetchall()
        rowcount=0
        self.table.setRowCount(len(test))
        for item in test:
            print(item)
            self.table.setItem(rowcount,0,QtGui.QTableWidgetItem(item[0]))
            self.table.setItem(rowcount,1,QtGui.QTableWidgetItem(item[1]))
            self.table.setItem(rowcount,2,QtGui.QTableWidgetItem(item[2]))
            self.table.setItem(rowcount,3,QtGui.QTableWidgetItem(item[6]))
            self.table.setItem(rowcount,4,QtGui.QTableWidgetItem("No One"))
            self.table.setItem(rowcount,5,QtGui.QTableWidgetItem(item[7]))
            self.table.setItem(rowcount,6,QtGui.QTableWidgetItem("Not yet!"))
            rowcount+=1    
        #self.table.resizeColumnsToContents()

