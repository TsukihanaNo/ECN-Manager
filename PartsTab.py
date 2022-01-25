from PySide6 import QtGui, QtCore, QtWidgets
from MyTableWidget import *

class PartsTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(PartsTab,self).__init__()
        self.parent = parent
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        self.initiateTable()
        mainlayout = QtWidgets.QVBoxLayout(self)

        self.label_parts = QtWidgets.QLabel("Parts",self)
        mainlayout.addWidget(self.label_parts)
        mainlayout.addWidget(self.table)
                
        hlayout = QtWidgets.QHBoxLayout(self)
        self.button_add = QtWidgets.QPushButton("Add Part")
        self.button_add.clicked.connect(self.addRow)
        self.button_remove = QtWidgets.QPushButton("Remove Part")
        self.button_remove.clicked.connect(self.removeRow)
        hlayout.addWidget(self.button_add)
        hlayout.addWidget(self.button_remove)
        mainlayout.addLayout(hlayout)
        
        self.setLayout(mainlayout)       

        
    def initiateTable(self):
        titles = ['Part ID','Desc','Type','Disposition','Mfg.','Mfg. #']
        self.table = MyTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        self.repopulateTable()
        
    def addRow(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        box_type = QtWidgets.QComboBox()
        box_type.addItems([" ","Fabricated","Purchased","Outside Service"])
        self.table.setCellWidget(row, 2, box_type)
        box_dispo = QtWidgets.QComboBox()
        box_dispo.addItems([" ","Deplete","New","Scrap","Rework"])
        self.table.setCellWidget(row, 3, box_dispo)
        self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(""))
        self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(""))
    
        
    def removeRow(self):
        self.table.removeRow(self.table.currentRow())
        
        
    def repopulateTable(self):
        self.table.clearContents()
        self.parent.cursor.execute(f"select * from PARTS where ECN_ID='{self.parent.tab_ecn.line_id.text()}'")
        results = self.parent.cursor.fetchall()
        self.table.setRowCount(len(results))
        rowcount=0
        for result in results:
            self.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['PART_ID']))
            self.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['DESC']))
            self.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['TYPE']))
            self.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['DISPOSITION']))
            self.table.setItem(rowcount, 4, QtWidgets.QTableWidgetItem(result['MFG']))
            self.table.setItem(rowcount, 5, QtWidgets.QTableWidgetItem(result['MFG_PART']))

            rowcount+=1

    def addPart(self,part):
        row = self.table.rowCount()
        self.table.insertRow(row)
        box_type = QtWidgets.QComboBox()
        box_type.addItems([" ","Fabricated","Purchased","Outside Service"])
        self.table.setCellWidget(row, 2, box_type)
        box_dispo = QtWidgets.QComboBox()
        box_dispo.addItems([" ","Deplete","New","Scrap","Rework"])
        self.table.setCellWidget(row, 3, box_dispo)
        self.table.setItem(row,0,QtWidgets.QTableWidgetItem(part))
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
            
    def resizeEvent(self,event):
            width = int(self.table.width()/self.table.columnCount())-3
            for x in range(self.table.columnCount()):
                self.table.setColumnWidth(x,width)