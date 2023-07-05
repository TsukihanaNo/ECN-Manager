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
        self.visual = parent.visual
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
        
        self.button_check_data = QtWidgets.QPushButton("Check Data")
        self.button_check_data.clicked.connect(self.checkData)
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_po_info)
        self.toolbar.addWidget(self.button_check_data)
        
        headers = ["Part ID","Description","Status","Part Type","Draw Made","Quoted","Vendor","Tooling Cost", "Tooling PO", "ECN?","Qty On Hand","Qty On Order","Notes"]
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
        item_ecn = QtWidgets.QTableWidgetItem()
        item_qty = QtWidgets.QTableWidgetItem()
        item_qty_order = QtWidgets.QTableWidgetItem()
        item_ecn.setFlags(item_ecn.flags() & ~QtCore.Qt.ItemIsEditable)
        item_qty.setFlags(item_qty.flags() & ~QtCore.Qt.ItemIsEditable)
        item_qty_order.setFlags(item_qty_order.flags() & ~QtCore.Qt.ItemIsEditable)
        self.parts.setItem(row,9,item_ecn)
        self.parts.setItem(row,10,item_qty)
        self.parts.setItem(row,11,item_qty_order)
        combo_type = QtWidgets.QComboBox()
        part_types = ["Die-Casted","Die-Cut", "Injection Molded","Machined","Off The Shelf","PCB"]
        combo_type.addItems(part_types)
        self.parts.setCellWidget(row,3,combo_type)
        status = ["Designing","Quoting","Awaiting Sample","Evaluating","Released"]
        combo_status = QtWidgets.QComboBox()
        combo_status.addItems(status)
        combo_drawing = QtWidgets.QComboBox()
        combo_quoted = QtWidgets.QComboBox()
        yes_no = ["No","Yes"]
        combo_drawing.addItems(yes_no)
        combo_quoted.addItems(yes_no)
        self.parts.setCellWidget(row,2,combo_status)
        self.parts.setCellWidget(row,4,combo_drawing)
        self.parts.setCellWidget(row,5,combo_quoted)
        

    def removeRow(self):
        current_row = self.parts.currentRow()
        self.parts.removeRow(current_row)
        
    def checkData(self):
        row_count = self.parts.rowCount()
        for row in range(row_count):
            if self.parts.item(row,0) is not None:
                item_id = self.parts.item(row,0)
                if self.visual.partExist(item_id.text()):
                    item_id.setBackground(QtGui.QColor("#CAFFBF"))
                    part_info = self.visual.getPartQty(item_id.text())
                    self.parts.item(row,11).setText(str(part_info[0]))
                else:
                    item_id.setBackground(QtGui.QColor("#FFADAD"))
                    self.parts.item(row,11).setText("0")
            # if self.parts.item(row,8) is not None:
            #     tooling_item = self.parts.item(row,8)
            #     print(self.visual.getPONotation(tooling_item.text()))
        
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()