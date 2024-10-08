from PySide6 import QtGui, QtCore, QtWidgets
from pathlib import Path
from SignaturePanel import *
from SignatureTab import SignatureDelegate, SignatureModel
import os, sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class NotificationTab(QtWidgets.QWidget):
    def __init__(self, parent = None,doc_type="ECN",doc_data=None):
        super(NotificationTab,self).__init__()
        self.parent = parent
        self.cursor = parent.cursor
        self.user_info = parent.user_info
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.doc_type = doc_type
        self.doc_data = doc_data
        self.job_titles =[]
        self.findJobTitles()
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        mainlayout.addWidget(self.toolbar)
        
        self.signatures = QtWidgets.QListView()
        self.signatures.setStyleSheet("QListView{background-color:#f0f0f0}")
        self.signatures.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.signatures.setResizeMode(QtWidgets.QListView.Adjust)
        self.signatures.setItemDelegate(SignatureDelegate())
        self.signatures.doubleClicked.connect(self.editSignature)
        
        self.model = SignatureModel()
        self.signatures.setModel(self.model)
        
        self.signatures.selectionModel().selectionChanged.connect(self.onRowSelect)
        
        mainlayout.addWidget(self.signatures)
                
        self.button_add = QtWidgets.QPushButton("Add Notifier")
        #print(self.parent.tab_ecn.line_status.text())
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.addRow)
        self.button_remove = QtWidgets.QPushButton("Remove Notifier")
        self.button_remove.setDisabled(True)
        icon_loc = icon = os.path.join(program_location,"icons","minus.png")
        self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        self.button_remove.clicked.connect(self.removeRow)
        self.button_edit = QtWidgets.QPushButton("Edit Notifier")
        icon_loc = icon = os.path.join(program_location,"icons","edit.png")
        self.button_edit.setIcon(QtGui.QIcon(icon_loc))
        self.button_edit.setDisabled(True)
        self.button_edit.clicked.connect(self.editSignature)
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_edit)
        
        
        if self.doc_data is not None:
            if self.parent.parent.user_info['user']==self.doc_data["author"]:
                self.signatures.doubleClicked.connect(self.editSignature)
            else:
                self.button_add.setDisabled(True)

    def onRowSelect(self):
        if self.parent.parent.user_info['user']==self.parent.doc_data["author"] and self.parent.doc_data["status"]!="Completed":
            self.button_remove.setEnabled(bool(self.signatures.selectionModel().selectedIndexes()))
            self.button_edit.setEnabled(bool(self.signatures.selectionModel().selectedIndexes()))
        
    def addRow(self):
        self.signature = SignaturePanel(self)
        
    def removeRow(self):
        index = self.signatures.selectionModel().selectedIndexes()
        index = sorted(index, reverse=True)
        for item in index:
            row = item.row()
            if self.model.get_signed_date(row) is None:
                self.model.removeRow(row)
                
    def editSignature(self):
        index = self.signatures.currentIndex()
        self.sig_editor = SignaturePanel(self,index.row())
        
    def findJobTitles(self):
        self.parent.cursor.execute("Select DISTINCT job_title FROM users")
        results = self.parent.cursor.fetchall()
        for result in results:
            self.job_titles.append(result[0])
        if "Admin" in self.job_titles:
            self.job_titles.remove("Admin")
        if len(self.job_titles)==0:
            self.dispMsg("No Job Titles found, please add Jobs and Users.")
        else:
            self.job_titles.sort()
        #print(self.job_titles)
        
    def repopulateTable(self):
        self.model.clear_signatures()
        command = f"Select * from signatures where doc_id='{self.parent.doc_id}' and type='Notify'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        for result in results:
            self.model.add_signature(result['job_title'], result['name'], result['user_id'], result['signed_date'])
            
    def rowCount(self):
        return self.model.rowCount(self.signatures)
    
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
            
    def resizeEvent(self, e):
        self.model.layoutChanged.emit()