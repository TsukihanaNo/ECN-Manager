from PySide6 import QtWidgets, QtCore, QtGui
import os, sys

import PySide6.QtGui
from Visual import *

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class PartImportPanel(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(PartImportPanel,self).__init__()
        self.windowWidth =  800
        self.windowHeight = 550
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.parent = parent
        self.visual = parent.visual
        self.initAtt()
        self.initUI()
        self.show()

    def center(self):
        window = self.window()
        window.setGeometry(
            QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            window.size(),
            QtGui.QGuiApplication.primaryScreen().availableGeometry(),
        ),
    )


    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        title = "Part Import"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.center()

    def initUI(self):
        vlayout = QtWidgets.QVBoxLayout()
        
        search_layout= QtWidgets.QHBoxLayout()
        self.line_search = QtWidgets.QLineEdit()
        self.line_search.setPlaceholderText("Leave blank to search all non-setup part, enter part id to search for part...")
        self.line_search.returnPressed.connect(self.search)
        self.checkbox_filter = QtWidgets.QCheckBox()
        self.label_fiflter = QtWidgets.QLabel("BOM Search")
        self.button_search = QtWidgets.QPushButton("Search")
        self.button_search.clicked.connect(self.search)
        search_layout.addWidget(self.line_search)
        search_layout.addWidget(self.checkbox_filter)
        search_layout.addWidget(self.label_fiflter)
        search_layout.addWidget(self.button_search)
        
        titles = ['Select','Part','Description']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        self.button_import = QtWidgets.QPushButton("Import")
        self.button_import.clicked.connect(self.importSelection)
        self.button_import.setFixedWidth(200)
        
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.button_import)
        vlayout.addLayout(search_layout)
        vlayout.addWidget(self.table)
        vlayout.addLayout(hlayout)
        
        self.setLayout(vlayout)
        
    def search(self):
        if self.line_search.text() =="":
            self.results = self.visual.queryPartsNoStage()
        else:
            search_string = self.line_search.text().upper()
            if self.checkbox_filter.checkState()==QtCore.Qt.CheckState.Checked:
                self.results = self.visual.queryPartsFromBOM(search_string)
            else:
                self.results = self.visual.queryParts(search_string)
        # for result in results:
        #     print(result)
        self.results.sort(key=self.sortData)
        self.loadData()
        
    def sortData(self,e):
        return e[0]
        
    def loadData(self):
        self.table.clear()
        self.table.setRowCount(len(self.results))
        row = 0
        for data in self.results:
            checkbox_widget = QtWidgets.QWidget()
            checkbox = QtWidgets.QCheckBox()
            layout = QtWidgets.QHBoxLayout(checkbox_widget)
            layout.setAlignment(QtCore.Qt.AlignCenter)
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(checkbox)
            item = QtWidgets.QTableWidgetItem(data[0])
            item2 = QtWidgets.QTableWidgetItem(data[1])
            self.table.setCellWidget(row,0,checkbox_widget)
            self.table.setItem(row,1,item)
            self.table.setItem(row,2,item2)
            row+=1
        titles = ['Select','Part','Description']
        self.table.setHorizontalHeaderLabels(titles)
        
    def getSelection(self):
        rows = []
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row,0).layout().itemAt(0).widget().checkState()==QtCore.Qt.CheckState.Checked:
                rows.append(row)
        return rows
        
    def importSelection(self):
        rows = self.getSelection()
        for row in rows:
            part_id = self.results[row][0]
            if not self.parent.model.exist_part(part_id):
                desc = self.results[row][1]
                if self.results[row][2]=="N":
                    part_type = "Fabricated"
                else:
                    part_type = "Purchased"
                    
                status = self.parent.getStatus(part_id,part_type)
                self.parent.model.add_part(part_id, desc, part_type,"", "", "","","", "",status)
            
        
    def resizeEvent(self, event):
        self.table.setColumnWidth(0,self.width()*0.1)
        self.table.setColumnWidth(1,self.width()*0.4)
        self.table.setColumnWidth(2,self.width()*0.4)

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()