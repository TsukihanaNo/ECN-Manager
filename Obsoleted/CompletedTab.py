from PySide6 import QtGui, QtCore, QtWidgets
from ECNWindow import *
class CompletedTab(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(CompletedTab,self).__init__()
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
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


        self.table.doubleClicked.connect(self.openECN)
        self.repopulateTable()


    def repopulateTable(self):
        self.table.clearContents()
        rowcount=0
        command = "Select * from ECN where STATUS='Completed'"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        self.table.setRowCount(len(results))
        for item in results:
            self.table.setItem(rowcount,0,QtWidgets.QTableWidgetItem(item['ECN_ID']))
            self.table.setItem(rowcount,1,QtWidgets.QTableWidgetItem(item['ECN_TYPE']))
            self.table.setItem(rowcount,2,QtWidgets.QTableWidgetItem(item['ECN_TITLE']))
            self.table.setItem(rowcount,3,QtWidgets.QTableWidgetItem(item['STATUS']))
            self.table.setItem(rowcount,4,QtWidgets.QTableWidgetItem(item['LAST_MODIFIED']))
            rowcount+=1