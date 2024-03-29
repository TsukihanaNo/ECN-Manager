from PySide6 import QtWidgets, QtCore, QtWidgets
from ECNWindow import *
import sqlite3  

class ChangeLogTab(QtWidgets.QWidget):
    def __init__(self,parent=None, doc_id = None):
        super(ChangeLogTab,self).__init__()
        self.parent = parent
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        self.user_info = self.parent.user_info
        self.doc_id = doc_id
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


    def initUI(self):
        self.initiateTable()


        vlayout = QtWidgets.QVBoxLayout(self)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        vlayout.addWidget(self.table)
        vlayout.addLayout(hlayout)
        vlayout.setAlignment(QtCore.Qt.AlignCenter)


    def initiateTable(self):
        titles = ['ECN ID', 'Time Stamp', 'Name', 'Prev Data', 'New Data']
        self.table = QtWidgets.QTableWidget(1,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.repopulateTable()


    def repopulateTable(self):
        self.table.clearContents()
        if self.doc_id is not None:
            self.cursor.execute(f"Select * from CHANGELOG where DOC_ID ='{self.doc_id}'")
            results = self.cursor.fetchall()
            if results is not None:
                rowcount=0
                self.table.setRowCount(len(results))
                for item in results:
                    self.table.setItem(rowcount,0,QtWidgets.QTableWidgetItem(item['DOC_ID']))
                    self.table.setItem(rowcount,1,QtWidgets.QTableWidgetItem(item['CHANGEDATE']))
                    self.table.setItem(rowcount,2,QtWidgets.QTableWidgetItem(item['NAME']))
                    self.table.setItem(rowcount,3,QtWidgets.QTableWidgetItem(item['PREVDATA']))
                    self.table.setItem(rowcount,4,QtWidgets.QTableWidgetItem(item['NEWDATA']))
                    rowcount+=1    
        #self.table.resizeColumnsToContents()

