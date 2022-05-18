from PySide6 import QtGui, QtCore, QtWidgets
from pathlib import Path
import os, sys

class AttachmentTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(AttachmentTab,self).__init__()
        self.parent = parent
        self.files = []
        self.initAtt()
        self.initUI()
        self.generateFileList()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAcceptDrops(True)

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        #self.list_attachment = QtWidgets.QListWidget(self)
        #mainlayout.addWidget(self.list_attachment)
        
        self.button_add = QtWidgets.QPushButton("Add Files")
        self.button_add.clicked.connect(self.addFiles)
        
        self.button_remove = QtWidgets.QPushButton("Remove")
        self.button_remove.clicked.connect(self.removeRow)
        
        self.button_open = QtWidgets.QPushButton("Open")
        self.button_open.clicked.connect(self.openFile)
        
        self.button_open_loc = QtWidgets.QPushButton("Open File Location")
        self.button_open_loc.clicked.connect(self.openFileLoc)

        #self.button_gen_parts = QtWidgets.QPushButton("Autogen Parts")
        #self.button_gen_parts.clicked.connect(self.autoGenParts)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.button_add)
        hlayout.addWidget(self.button_remove)
        hlayout.addWidget(self.button_open)
        hlayout.addWidget(self.button_open_loc)
        #hlayout.addWidget(self.button_gen_parts)
        
        titles = ['File Name','File Path']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.openFile)

        
        mainlayout.addWidget(self.table)
        mainlayout.addLayout(hlayout)
        self.setLayout(mainlayout)
        

    def dropEvent(self, e):
        urlList = e.mimeData().urls()
        #self.table.setRowCount(len(urlList))
        row=self.table.rowCount()
        cfiles=[]
        for item in urlList:
            url = item.toLocalFile()
            if "C:" not in url:
                if url not in self.files:
                    self.files.append(url)
                    self.table.insertRow(row)
                    #listItem = QtWidgets.QListWidgetItem(url,self.list_attachment)
                    self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(url[url.rfind("/")+1:]))
                    self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(Path(url).resolve())))
                    row+=1
            else:
                cfiles.append(url)
        if len(cfiles)>0:
            self.dispMsg(f"The following files were not accepted as they reside on your local machine and is not accessible by other users:{cfiles}")

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
            
    def openFileLoc(self):
        row = self.table.currentRow()
        try:
            path = Path(self.table.item(row,1).text())
            os.startfile(path.parent)
        except Exception as e:
            print(e)
        
    def addFiles(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        cfiles = []
        if dialog.exec():
            fileNames = dialog.selectedFiles()
            row=self.table.rowCount()
            for url in fileNames:
                if "C:" not in url:
                    if url not in self.files:
                        self.files.append(url)
                        self.table.insertRow(row)
                        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(url[url.rfind("/")+1:]))
                        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(Path(url).resolve())))
                        row+=1
                else:
                    cfiles.append(url)
            if len(cfiles)>0:
                self.dispMsg(f"The following were files not accepted as they reside on your local machine and is not accessible by other users:{cfiles}")
                
                
    def removeRow(self):
        index = self.table.selectionModel().selectedRows()
        index = sorted(index, reverse=True)
        for item in index:
            row = item.row()
            self.files.remove(self.table.item(row, 1).text())
            self.table.removeRow(row)
        
    def generateFileList(self):
        if self.table.rowCount()>0:
            for x in range(self.table.rowCount()):
                self.files.append(self.table.item(x, 1).text())

    def autoGenParts(self):
        parts = []
        for x in range(self.table.rowCount()):
            path = Path(self.table.item(x,1).text())
            part = path.stem
            if part not in parts:
                self.parent.tab_parts.addPart(part)
                parts.append(part)
        self.dispMsg("Parts have been generated in the parts tab")
        
    def repopulateTable(self):
        command = "Select * from ATTACHMENTS where ECN_ID= '"+self.parent.ecn_id +"'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        self.table.setRowCount(len(results))
        rowcount=0
        for result in results:
            self.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['FILENAME']))
            self.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['FILEPATH']))
            rowcount+=1
    

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()

