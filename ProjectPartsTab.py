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

        self.button_add = QtWidgets.QPushButton("Add Row")
        icon_loc = os.path.join(program_location,"icons","add.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.addRow)
        self.button_remove = QtWidgets.QPushButton("Remove Row")
        icon_loc = os.path.join(program_location,"icons","minus.png")
        self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        self.button_remove.setDisabled(True)
        self.button_remove.clicked.connect(self.removeRow)
        self.button_po_info = QtWidgets.QPushButton("PO Info")
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_po_info)
        
        headers = ["Part ID","Description","Status","Part Type","Draw Made","Quoted","Vendor","Tooling Cost", "Tooling PO", "Product PO", "Cost Per","Qty Per", "ECN?","Qty On Hand","Notes"]
        self.parts = QtWidgets.QTableWidget(0,len(headers),self)
        self.parts.setHorizontalHeaderLabels(headers)
        self.parts.selectionModel().selectionChanged.connect(self.onRowSelect)
        mainlayout.addWidget(self.parts)
        self.addRow()
        
        self.setLayout(mainlayout)
        #self.repopulateTable()
        
    def createMenu(self):
        pass
        
    def contextMenuEvent(self,event):
        self.menu.exec_(event.globalPos())
        
    def onRowSelect(self):
        self.button_remove.setEnabled(bool(self.parts.selectionModel().selectedIndexes()))
        
    def addRow(self):
        row = self.parts.rowCount()
        self.parts.insertRow(row)

    def removeRow(self):
        current_row = self.parts.currentRow()
        self.parts.removeRow(current_row)
        
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()