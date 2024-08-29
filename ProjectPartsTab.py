import os
import sys
from POWindow import *

from PySide6 import QtCore, QtGui, QtWidgets

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
        self.cursor = parent.cursor
        self.db = parent.db
        self.access = parent.access
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
        self.button_po_info.setDisabled(True)
        self.button_po_info.clicked.connect(self.showPO)
        
        # self.button_check_data = QtWidgets.QPushButton("Check Data")
        # self.button_check_data.clicked.connect(self.checkData)
        
        self.button_export_csv = QtWidgets.QPushButton("Export CSV")
        self.button_export_csv.clicked.connect(self.export)
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_po_info)
        # self.toolbar.addWidget(self.button_check_data)
        self.toolbar.addWidget(self.button_export_csv)
        if self.access == "read":
            self.button_add.setDisabled(True)
        
        headers = ["Part ID","Description","Status","Part Type","Drawing","Quoted","Vendor","Tooling Cost", "Tooling PO", "ECN","Qty On Hand","Qty On Order","Notes"]
        self.parts = QtWidgets.QTableWidget(0,len(headers),self)
        self.parts.setHorizontalHeaderLabels(headers)
        self.parts.selectionModel().selectionChanged.connect(self.onRowSelect)
        self.sizing()
        mainlayout.addWidget(self.parts)
        # self.addRow()
        
        self.setLayout(mainlayout)
        #self.repopulateTable()
        
    def sizing(self):
        self.parts.setColumnWidth(0,150)
        self.parts.setColumnWidth(1,200)
        self.parts.setColumnWidth(2,100)
        
    def createMenu(self):
        pass
        
    def contextMenuEvent(self,event):
        self.menu.exec_(event.globalPos())
        
    def resizeEvent(self, e):        
        self.sizing()
        
    def onRowSelect(self):
        if self.access != "read":
            self.button_remove.setEnabled(bool(self.parts.selectionModel().selectedIndexes()))
        self.button_po_info.setEnabled(bool(self.parts.selectionModel().selectedIndexes()))
        
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
        if self.access=="write":
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
        else:
            for x in range(4):
                item = QtWidgets.QTableWidgetItem()
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.parts.setItem(row,2+x,item)
        

    def removeRow(self):
        current_row = self.parts.currentRow()
        self.parts.removeRow(current_row)
        
    def checkData(self):
        # self.saveData()
        row_count = self.parts.rowCount()
        for row in range(row_count):
            if self.parts.item(row,0) is not None:
                item_id = self.parts.item(row,0)
                if self.visual.partExist(item_id.text()):
                    item_id.setBackground(QtGui.QColor("#CAFFBF"))
                    part_info = self.visual.getPartQty(item_id.text())
                    self.parts.item(row,10).setText(str(part_info[0]))
                    self.parts.item(row,11).setText(str(part_info[1]))
                    if self.checkForECN(item_id.text()):
                        self.parts.item(row,9).setText("Y")
                        self.parts.item(row,9).setBackground(QtGui.QColor("#CAFFBF"))
                    else:
                        self.parts.item(row,9).setText("N")
                        self.parts.item(row,9).setBackground(QtGui.QColor("#FFADAD"))
                else:
                    item_id.setBackground(QtGui.QColor("#FFADAD"))
                    self.parts.item(row,10).setText("0")
                    self.parts.item(row,11).setText("0")
                    self.parts.item(row,9).setText("N")
                    self.parts.item(row,9).setBackground(QtGui.QColor("#FFADAD"))
            # if self.parts.item(row,8) is not None:
            #     tooling_item = self.parts.item(row,8)
            #     print(self.visual.getPONotation(tooling_item.text()))
            
    def showPO(self):
        row = self.parts.currentRow()
        part_id = self.parts.item(row,0).text()
        self.poWindow = POWindow(self,part_id)
            
    def checkForECN(self,part_id):
        self.cursor.execute(f"select count(PART_ID) from PARTS where PART_ID like '%{part_id}%'")
        result = self.cursor.fetchone()
        if result[0] > 0:
            return True
        else:
            return False
    
    def saveData(self):
        try:
            self.clearData()
            for row in range(self.parts.rowCount()):
                if self.parts.item(row,0) is None:
                    part_id = ""
                else:
                    part_id = self.parts.item(row,0).text()
                
                if self.parts.item(row,1) is None:
                    description = ""
                else:
                    description = self.parts.item(row,1).text()
                    
                status = self.parts.cellWidget(row,2).currentText()
                part_type = self.parts.cellWidget(row,3).currentText()
                drawing_made = self.parts.cellWidget(row,4).currentText()
                quoted = self.parts.cellWidget(row,5).currentText()
                
                if self.parts.item(row,6) is None:
                    vendor = ""
                else:
                    vendor = self.parts.item(row,6).text()
                    
                if self.parts.item(row,7) is None:
                    tooling_cost = ""
                else:
                    tooling_cost = self.parts.item(row,7).text()
                    
                if self.parts.item(row,8) is None:
                    tooling_po = ""
                else:
                    tooling_po = self.parts.item(row,8).text()
                    
                if self.parts.item(row,12) is None:
                    note = ""
                else:
                    note = self.parts.item(row,12).text()
                
                # print(part_id,description,status,part_type)
                data = (self.doc_id,part_id,description,status,part_type,drawing_made,quoted,vendor,tooling_cost,tooling_po,note)
                self.cursor.execute(f"INSERT INTO PROJECT_PARTS(PROJECT_ID,PART_ID,DESCRIPTION,STATUS,PART_TYPE,DRAWING_MADE,QUOTED,VENDOR,TOOLING_COST,TOOLING_PO,NOTE) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data))
            self.db.commit()
            self.checkData()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData - parts tab)!\n Error: {e}")
    
    
    def loadData(self):
        self.cursor.execute(f"select * from PROJECT_PARTS where PROJECT_ID='{self.doc_id}'")
        results = self.cursor.fetchall()
        # self.parts.setRowCount(len(results))
        row = 0
        for result in results:
            self.addRow()
            item_id = QtWidgets.QTableWidgetItem(result[1])
            # item_id.setFlags(item_id.flags() & ~QtCore.Qt.ItemIsEditable)
            self.parts.setItem(row,0,item_id)
            item_desc = QtWidgets.QTableWidgetItem(result[2])
            # item_desc.setFlags(item_desc.flags() & ~QtCore.Qt.ItemIsEditable)
            self.parts.setItem(row,1,item_desc)
            item_vendor = QtWidgets.QTableWidgetItem(result[7])
            self.parts.setItem(row,6,item_vendor)
            item_tooling_po = QtWidgets.QTableWidgetItem(result[8])
            self.parts.setItem(row,7,item_tooling_po)
            item_tooling_cost = QtWidgets.QTableWidgetItem(result[9])
            self.parts.setItem(row,8,item_tooling_cost)
            item_note = QtWidgets.QTableWidgetItem(result[10])
            # item_note.setFlags(item_note.flags() & ~QtCore.Qt.ItemIsEditable)
            self.parts.setItem(row,12,item_note)
            if self.access=="write":
                self.parts.cellWidget(row,2).setCurrentText(result[3])
                self.parts.cellWidget(row,3).setCurrentText(result[4])
                self.parts.cellWidget(row,4).setCurrentText(result[5])
                self.parts.cellWidget(row,5).setCurrentText(result[6])
            else:
                for x in range(4):
                    self.parts.item(row,2+x).setText(result[3+x])
                item_id.setFlags(item_id.flags() & ~QtCore.Qt.ItemIsEditable)
                item_desc.setFlags(item_desc.flags() & ~QtCore.Qt.ItemIsEditable)
                item_note.setFlags(item_note.flags() & ~QtCore.Qt.ItemIsEditable)
            row+=1
        self.checkData()
        
    def export(self):
        main_list = [["PART ID","Description","Status","Part Type","Drawing","Quoted","Vendor","Tooling Cost","Tooling PO","ECN","Qty On Hand","Qty On Order","Note"]]
        for row in range(self.parts.rowCount()):            
            part = self.parts.item(row,0).text()
            desc = self.parts.item(row,1).text()
            status = self.parts.cellWidget(row,2).currentText()
            part_type = self.parts.cellWidget(row,3).currentText()
            drawing = self.parts.cellWidget(row,4).currentText()
            quoted = self.parts.cellWidget(row,5).currentText()
            vendor = self.parts.item(row,6).text()
            tooling_cost = self.parts.item(row,7).text()
            tooling_po = self.parts.item(row,8).text()
            ecn = self.parts.item(row,9).text()
            qty_on_hand = self.parts.item(row,10).text()
            qty_on_order = self.parts.item(row,11).text()
            notes = self.parts.item(row,12).text()
            line = [part,desc,status,part_type,drawing,vendor,quoted,tooling_cost,tooling_po,ecn,qty_on_hand,qty_on_order,notes]
            main_list.append(line)
        f = open(f"{self.doc_id} parts.csv", "w")
        for line in main_list:
            text = ",".join(line)
            text+="\n"
            f.write(text)
        f.close()
        self.dispMsg("export completed!")
    
    def clearData(self):
        self.cursor.execute(f"DELETE FROM PROJECT_PARTS WHERE PROJECT_ID = '{self.doc_id}'")
        
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()