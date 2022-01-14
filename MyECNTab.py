from PySide6 import QtGui, QtCore, QtWidgets
from ECNWindow import *
from MyTableWidget import *
import sqlite3
class MyECNTab(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(MyECNTab,self).__init__()
        self.parent = parent
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.user_info = self.parent.user_info
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        self.initiateTable()

        self.button_open = QtWidgets.QPushButton("Open",self)
        self.button_new = QtWidgets.QPushButton("New ECN",self)

        vlayout = QtWidgets.QVBoxLayout(self)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        vlayout.addWidget(self.table)

        hlayout.addWidget(self.button_open)
        hlayout.addWidget(self.button_new)

        vlayout.addLayout(hlayout)
        vlayout.setAlignment(QtCore.Qt.AlignCenter)

        self.button_open.setFixedWidth(200)
        self.button_new.setFixedWidth(200)

        self.setLayout(vlayout)

        self.button_new.clicked.connect(self.newECN)
        self.button_open.clicked.connect(self.openECN)


    def newECN(self):
        self.parent.HookEcn()

    def openECN(self):
        row = self.table.currentRow()
        ecn_id=self.table.item(row,0).text()
        self.parent.HookEcn(ecn_id)

    def initiateTable(self):
        titles = ['ECN ID','Type', 'Title', 'Status', 'Last Modified']
        self.table = MyTableWidget(1,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


        self.table.doubleClicked.connect(self.openECN)
        self.repopulateTable()

    def resizeEvent(self,event):
        width = int(self.table.width()/self.table.columnCount())-3
        for x in range(self.table.columnCount()):
            self.table.setColumnWidth(x,width)


    def repopulateTable(self):
        self.table.clearContents()
        command = "Select * from ECN where AUTHOR ='" + self.user_info['user'] + "' and STATUS !='Completed'"
        self.cursor.execute(command)
        test = self.cursor.fetchall()
        rowcount=0
        self.table.setRowCount(len(test))
        for item in test:
            self.table.setItem(rowcount,0,QtWidgets.QTableWidgetItem(item['ECN_ID']))
            self.table.setItem(rowcount,1,QtWidgets.QTableWidgetItem(item['ECN_TYPE']))
            self.table.setItem(rowcount,2,QtWidgets.QTableWidgetItem(item['ECN_TITLE']))
            self.table.setItem(rowcount,3,QtWidgets.QTableWidgetItem(item['STATUS']))
            self.table.setItem(rowcount,4,QtWidgets.QTableWidgetItem(item['LAST_MODIFIED']))
            if item["STATUS"]=="Rejected":
                self.table.item(rowcount, 3).setBackground(QtGui.QColor(255,203,203))
            if item["STATUS"]=="Out For Approval":
                self.table.item(rowcount, 3).setBackground(QtGui.QColor(231,251,190))
            rowcount+=1
