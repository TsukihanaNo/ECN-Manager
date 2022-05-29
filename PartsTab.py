from PySide6 import QtGui, QtCore, QtWidgets
import sys, os

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class PartsTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(PartsTab,self).__init__()
        self.parent = parent
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self): 
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()

        # self.label_parts = QtWidgets.QLabel("Parts",self)
        
        titles = ['Part ID','Description','Type','Disposition','Manufacturer','Mfg. #','Replacing','Reference','Inspection Req.']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        #self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.selectionModel().selectionChanged.connect(self.onRowSelect)
        
        #mainlayout.addWidget(self.label_parts)
        mainlayout.addWidget(self.toolbar)
        mainlayout.addWidget(self.table)
                
        #hlayout = QtWidgets.QHBoxLayout(self)
        self.button_add = QtWidgets.QPushButton("Add Part")
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.addRow)
        self.button_remove = QtWidgets.QPushButton("Remove Part")
        icon_loc = icon = os.path.join(program_location,"icons","minus.png")
        self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        self.button_remove.setDisabled(True)
        self.button_remove.clicked.connect(self.removeRow)
        #hlayout.addWidget(self.button_add)
        #hlayout.addWidget(self.button_remove)
        #mainlayout.addLayout(hlayout)
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
                
        self.setLayout(mainlayout)              
        self.repopulateTable()
        
    def onRowSelect(self):
        if self.parent.parent.user_info['user']==self.parent.tab_ecn.line_author.text():
            self.button_remove.setEnabled(bool(self.table.selectionModel().selectedRows()))
        
        
    def addRow(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        box_type = QtWidgets.QComboBox()
        box_type.addItems(["","Fabricated","Purchased","Outside Service"])
        self.table.setCellWidget(row, 2, box_type)
        box_dispo = QtWidgets.QComboBox()
        box_dispo.addItems(["","Deplete","New","Scrap","Rework"])
        self.table.setCellWidget(row, 3, box_dispo)
        self.table.setItem(row, 4, QtWidgets.QTableWidgetItem("NA"))
        self.table.setItem(row, 5, QtWidgets.QTableWidgetItem("NA"))
        self.table.setItem(row, 6, QtWidgets.QTableWidgetItem("NA"))
        self.table.setItem(row, 7, QtWidgets.QTableWidgetItem("NA"))
        box_inspec = QtWidgets.QComboBox()
        box_inspec.addItems(["","N","Y"])
        self.table.setCellWidget(row, 8, box_inspec)

    
    def removeRow(self):
        index = self.table.selectionModel().selectedRows()
        for item in sorted(index,reverse=True):
            self.table.removeRow(item.row())
        
        
    def repopulateTable(self):
        self.table.clearContents()
        self.parent.cursor.execute(f"select * from PARTS where ECN_ID='{self.parent.tab_ecn.line_id.text()}'")
        results = self.parent.cursor.fetchall()
        self.table.setRowCount(len(results))
        rowcount=0
        for result in results:
            part_id = QtWidgets.QTableWidgetItem(result['PART_ID'])
            part_id.setToolTip(result['PART_ID'])
            self.table.setItem(rowcount, 0, part_id)
            desc = QtWidgets.QTableWidgetItem(result['DESC'])
            desc.setToolTip(result['DESC'])
            self.table.setItem(rowcount, 1, desc)
            if self.parent.parent.user_info['user']!=self.parent.tab_ecn.line_author.text():
                self.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['TYPE']))
                self.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['DISPOSITION']))
                if isinstance(self.table.item(rowcount, 3),QtWidgets.QTableWidgetItem):
                    if result['DISPOSITION']=="New":
                        self.table.item(rowcount, 3).setBackground(QtGui.QColor(186,255,180))
                    if result['DISPOSITION']=="SCrap":
                        self.table.item(rowcount, 3).setBackground(QtGui.QColor(255,99,99))
                    if result['DISPOSITION']=="Deplete":
                        self.table.item(rowcount, 3).setBackground(QtGui.QColor(255,253,162))
                self.table.setItem(rowcount, 8, QtWidgets.QTableWidgetItem(result['INSPEC']))
            else:
                box_type = QtWidgets.QComboBox()
                box_type.addItems(["","Fabricated","Purchased","Outside Service"])
                box_type.setCurrentText(result['TYPE'])
                self.table.setCellWidget(rowcount, 2, box_type)
                box_dispo = QtWidgets.QComboBox()
                box_dispo.addItems(["","Deplete","New","Scrap","Rework"])
                box_dispo.setCurrentText(result['DISPOSITION'])
                self.table.setCellWidget(rowcount, 3, box_dispo)
                box_inspec = QtWidgets.QComboBox()
                box_inspec.addItems(["","N","Y"])
                box_inspec.setCurrentText(result['INSPEC'])
                self.table.setCellWidget(rowcount, 8, box_inspec)
            self.table.setItem(rowcount, 4, QtWidgets.QTableWidgetItem(result['MFG']))
            self.table.setItem(rowcount, 5, QtWidgets.QTableWidgetItem(result['MFG_PART']))
            self.table.setItem(rowcount, 6, QtWidgets.QTableWidgetItem(result['REPLACING']))
            self.table.setItem(rowcount, 7, QtWidgets.QTableWidgetItem(result['REFERENCE']))
            if self.parent.parent.visual is not None:
                if self.parent.parent.visual.partExist(result['PART_ID']):
                    if self.parent.parent.visual.checkPartSetup(result['PART_ID'], result['TYPE']):
                        self.table.item(rowcount, 0).setBackground(QtGui.QColor(186,255,180))
                    else:
                        self.table.item(rowcount, 0).setBackground(QtGui.QColor(255,253,162))
                else:
                    self.table.item(rowcount, 0).setBackground(QtGui.QColor(255,99,99))
            
            # if self.parent.parent.user_info['user']!=self.parent.tab_ecn.line_author.text():
            #     self.table.item(rowcount,2).

            rowcount+=1
            
    def setStatusColor(self):
        for x in range(self.table.rowCount()):
            part = self.table.item(x,0).text()
            if isinstance(self.table.item(x, 2),QtWidgets.QTableWidgetItem):
                part_type = self.table.item(x,2).text()
            else:
                part_type = self.table.cellWidget(x, 2).currentText()
            if self.parent.parent.visual is not None:
                if self.parent.parent.visual.partExist(part):
                    if self.parent.parent.visual.checkPartSetup(part,part_type):
                        self.table.item(x, 0).setBackground(QtGui.QColor(186,255,180))
                    else: 
                        self.table.item(x, 0).setBackground(QtGui.QColor(255,253,162))
                else:
                    self.table.item(x, 0).setBackground(QtGui.QColor(255,99,99))
                
    # def addPart(self,part):
    #     row = self.table.rowCount()
    #     self.table.insertRow(row)
    #     box_type = QtWidgets.QComboBox()
    #     box_type.addItems([" ","Fabricated","Purchased","Outside Service"])
    #     self.table.setCellWidget(row, 2, box_type)
    #     box_dispo = QtWidgets.QComboBox()
    #     box_dispo.addItems([" ","Deplete","New","Scrap","Rework"])
    #     self.table.setCellWidget(row, 3, box_dispo)
    #     self.table.setItem(row,0,QtWidgets.QTableWidgetItem(part))
        
    def checkFields(self):
        for x in range(self.table.rowCount()):
            print(f"checking row {x}")
            for y in range(self.table.columnCount()):
                if isinstance(self.table.item(x, y),QtWidgets.QTableWidgetItem):
                    if self.table.item(x, y).text() is None or self.table.item(x,y).text()=="":
                        return False
                else:
                    if self.table.cellWidget(x, y) is None:
                        return False
                    else:
                        if self.table.cellWidget(x,y).currentText()=="":
                            return False
        return True
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
            
    def resizeEvent(self,event):
            width = int(self.table.width()/self.table.columnCount())-3
            for x in range(self.table.columnCount()):
                self.table.setColumnWidth(x,width)