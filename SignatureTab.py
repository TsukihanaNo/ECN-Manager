from PySide2 import QtGui, QtCore, QtWidgets
from MyTableWidget import *

class SignatureTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(SignatureTab,self).__init__()
        self.parent = parent
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        self.initiateTable()
        mainlayout = QtWidgets.QVBoxLayout(self)

        self.label_signatures = QtWidgets.QLabel("Signatures",self)
        mainlayout.addWidget(self.label_signatures)
        mainlayout.addWidget(self.table)
        
        print(self.parent.user_info['name'],self.parent.tab_ecn.line_author.text())
        if self.parent.user_info['name']==self.parent.tab_ecn.line_author.text():
            hlayout = QtWidgets.QHBoxLayout(self)
            self.button_add = QtWidgets.QPushButton("Add Signature")
            self.button_add.clicked.connect(self.addRow)
            self.button_remove = QtWidgets.QPushButton("Remove Signature")
            self.button_remove.clicked.connect(self.removeRow)
            hlayout.addWidget(self.button_add)
            hlayout.addWidget(self.button_remove)
            mainlayout.addLayout(hlayout)
        
        self.setLayout(mainlayout)       

        
    def initiateTable(self):
        titles = ['Title','Name','User', 'Approval']
        self.table = MyTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        #self.repopulateTable()
        
    def addRow(self):
        self.table.insertRow(self.table.rowCount())
        box = QtWidgets.QComboBox()
        box.addItems(["Engineer","Manager","Buyer","Planner"])
        self.table.setCellWidget(self.table.rowCount()-1, 0, box)
        box.currentIndexChanged.connect(self.setNameList)
        box.currentIndexChanged.connect(self.setUser)
        
        command = "Select NAME from USER where JOB_TITLE = '" + self.table.cellWidget(self.table.rowCount()-1, 0).currentText() +"'"
        self.parent.cursor.execute(command)
        test = self.parent.cursor.fetchall()
        names = []
        for item in test:
            names.append(item[0])
        box = QtWidgets.QComboBox()
        box.addItems(names)
        box.currentIndexChanged.connect(self.setUser)
        self.table.setCellWidget(self.table.rowCount()-1, 1, box)
        
        command = "Select USER_ID from USER where NAME = '" + self.table.cellWidget(self.table.rowCount()-1, 1).currentText() +"'"
        self.parent.cursor.execute(command)
        test = self.parent.cursor.fetchall()
        names = []
        for item in test:
            names.append(item[0])
        box = QtWidgets.QComboBox()
        box.addItems(names)
        self.table.setCellWidget(self.table.rowCount()-1, 2, box)
        
        
        
        

        
    def removeRow(self):
        self.table.removeRow(self.table.currentRow())
        
    
        
    def setNameList(self):
        command = "Select NAME from USER where JOB_TITLE = '" + self.table.cellWidget(self.table.currentRow(), 0).currentText() +"' and STATUS='Active'"
        self.parent.cursor.execute(command)
        test = self.parent.cursor.fetchall()
        names = []
        for item in test:
            names.append(item[0])
        box = QtWidgets.QComboBox()
        box.addItems(names)
        self.table.setCellWidget(self.table.currentRow(), 1, box)
        box.currentIndexChanged.connect(self.setUser)

    
    def setUser(self):
        command = "Select USER_ID from USER where NAME = '" + self.table.cellWidget(self.table.currentRow(), 1).currentText() +"'"
        self.parent.cursor.execute(command)
        test = self.parent.cursor.fetchall()
        names = []
        for item in test:
            names.append(item[0])
        box = QtWidgets.QComboBox()
        box.addItems(names)
        self.table.setCellWidget(self.table.currentRow(), 2, box)
        
    def repopulateTable(self):
        self.table.clearContents()
        command = "Select * from SIGNATURE where ECN_ID= '"+self.parent.tab_ecn.line_id.text() +"'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        self.table.setRowCount(len(results))
        rowcount=0
        for result in results:
            print(result['JOB_TITLE'])
            self.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['JOB_TITLE']))
            self.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['NAME']))
            self.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['USER_ID']))
            self.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['SIGNED_DATE']))

            rowcount+=1
            
        def resizeEvent(self,event):
                width = int(self.table.width()/self.table.columnCount())-3
                for x in range(self.table.columnCount()):
                    self.table.setColumnWidth(x,width)