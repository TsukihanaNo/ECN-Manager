from PySide6 import QtGui, QtCore, QtWidgets
from MyTableWidget import *
import os, sys

class AttachmentTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(AttachmentTab,self).__init__()
        self.parent = parent
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAcceptDrops(True)

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        #self.list_attachment = QtWidgets.QListWidget(self)
        #mainlayout.addWidget(self.list_attachment)
        self.initiateTable()
        self.table.doubleClicked.connect(self.openFile)
        
        self.button_add = QtWidgets.QPushButton("Add Files")
        self.button_add.clicked.connect(self.addFiles)
        
        self.button_remove = QtWidgets.QPushButton("Remove")
        self.button_remove.clicked.connect(self.removeRow)
        
        self.button_open = QtWidgets.QPushButton("Open")
        self.button_open.clicked.connect(self.openFile)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.button_add)
        hlayout.addWidget(self.button_remove)
        hlayout.addWidget(self.button_open)
        
        mainlayout.addWidget(self.table)
        mainlayout.addLayout(hlayout)
        self.setLayout(mainlayout)
        
    def initiateTable(self):
        titles = ['File Name','File Path']
        self.table = MyTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def dropEvent(self, e):
        urlList = e.mimeData().urls()
        #self.table.setRowCount(len(urlList))
        row=self.table.rowCount()
        for item in urlList:
            url = item.toLocalFile()
            self.table.insertRow(row)
            #listItem = QtWidgets.QListWidgetItem(url,self.list_attachment)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(url[url.rfind("/")+1:]))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(url))
            row+=1


    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()
            
    def openFile(self):
        row = self.table.currentRow()
        try:
            os.startfile(self.table.item(row,1).text())
        except Exception as e:
            print(e)
        
    def addFiles(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            row=self.table.rowCount()
            for url in fileNames:
                self.table.insertRow(row)
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(url[url.rfind("/")+1:]))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(url))
                row+=1
                
    def removeRow(self):
        self.table.removeRow(self.table.currentRow())

