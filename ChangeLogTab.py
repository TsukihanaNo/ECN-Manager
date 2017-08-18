from PySide import QtGui, QtCore
from RequestWindow import *
import sqlite3  

class ChangeLogTab(QtGui.QWidget):
    def __init__(self,parent=None, ecn_id = None):
        super(ChangeLogTab,self).__init__()
        self.parent = parent
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        self.user_info = self.parent.user_info
        self.ecn_id = ecn_id
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


    def initUI(self):
        self.initiateTable()


        vlayout = QtGui.QVBoxLayout(self)
        hlayout = QtGui.QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        vlayout.addWidget(self.table)
        vlayout.addLayout(hlayout)
        vlayout.setAlignment(QtCore.Qt.AlignCenter)

        self.setLayout(vlayout)


    def initiateTable(self):
        titles = ['ECN ID', 'Time Stamp', 'Name', 'Prev Data', 'New Data']
        self.table = QtGui.QTableWidget(1,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        #self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.repopulateTable()


    def repopulateTable(self):
        self.table.clearContents()
        command = "Select * from CHANGELOG where ECN_ID ='" + self.ecn_id + "'"
        self.cursor.execute(command)
        test = self.cursor.fetchall()
        rowcount=0
        self.table.setRowCount(len(test))
        for item in test:
            self.table.setItem(rowcount,0,QtGui.QTableWidgetItem(item['ECN_ID']))
            self.table.setItem(rowcount,1,QtGui.QTableWidgetItem(item['CHANGEDATE']))
            self.table.setItem(rowcount,2,QtGui.QTableWidgetItem(item['NAME']))
            self.table.setItem(rowcount,3,QtGui.QTableWidgetItem(item['PREVDATA']))
            self.table.setItem(rowcount,4,QtGui.QTableWidgetItem(item['NEWDATA']))
            rowcount+=1    
        #self.table.resizeColumnsToContents()

