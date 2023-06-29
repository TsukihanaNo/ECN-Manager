from PySide6 import QtGui, QtCore, QtWidgets
import sys, os

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class ProjectPartsTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ProjectPartsTab,self).__init__()
        self.parent = parent
        self.doc_id = parent.doc_id
        self.initAtt()
        self.clipboard = QtGui.QGuiApplication.clipboard()
        self.menu = QtWidgets.QMenu(self)
        self.createMenu()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self): 
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        
        mainlayout.addWidget(self.toolbar)

        self.button_add = QtWidgets.QPushButton("Add Part")
        icon_loc = os.path.join(program_location,"icons","add.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.addPart)
        self.button_remove = QtWidgets.QPushButton("Remove Part")
        icon_loc = os.path.join(program_location,"icons","minus.png")
        self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        self.button_remove.setDisabled(True)
        self.button_remove.clicked.connect(self.removeRow)
        self.button_edit = QtWidgets.QPushButton("Edit Part")
        icon_loc = os.path.join(program_location,"icons","edit.png")
        self.button_edit.setIcon(QtGui.QIcon(icon_loc))
        self.button_edit.setDisabled(True)
        self.button_edit.clicked.connect(self.editPart)
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_edit)
        
        self.parts = QtWidgets.QTableWidget()
        self.parts.setStyleSheet("QListView{background-color:#f0f0f0}")
        mainlayout.addWidget(self.parts)
        
        self.setLayout(mainlayout)              
        #self.repopulateTable()
        
    def createMenu(self):
        pass
        
    def contextMenuEvent(self,event):
        self.menu.exec_(event.globalPos())
        
    def onRowSelect(self):
        self.button_remove.setEnabled(bool(self.parts.selectionModel().selectedIndexes()))
        self.button_edit.setEnabled(bool(self.parts.selectionModel().selectedIndexes()))
        
        
    def addPart(self):
        pass
        
    def editPart(self):
        pass

    def removeRow(self):
        pass
        
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()