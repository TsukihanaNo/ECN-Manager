from PySide6 import QtWidgets, QtCore, QtGui
from datetime import datetime
import sys, os


class PurchReqDetailTab(QtWidgets.QWidget):
    def __init__(self, parent = None, doc_id = None):
        super(PurchReqDetailTab,self).__init__()
        self.parent = parent
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.settings = parent.settings
        self.visual = parent.visual
        self.user_info = self.parent.user_info
        # self.windowWidth =  self.parent.windowWidth
        # self.windowHeight = self.parent.windowHeight
        # self.setFixedSize(self.windowWidth,self.windowHeight)
        self.doc_id = doc_id
        self.tablist = []
        self.initAtt()
        self.initUI()
        
    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        self.label_id = QtWidgets.QLabel("Req ID:")
        self.line_id = QtWidgets.QLineEdit()
        self.label_status = QtWidgets.QLabel("Status:")
        self.line_status = QtWidgets.QLineEdit()
        self.line_status.setReadOnly(True)
        self.label_status_visual = QtWidgets.QLabel("Status Visual:")
        self.line_status_visual = QtWidgets.QLineEdit()
        self.line_status_visual.setReadOnly(True)
        self.label_buyer = QtWidgets.QLabel("Assigned Buyer:")
        self.line_buyer = QtWidgets.QLineEdit()
        self.line_buyer.setReadOnly(True)
        
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.label_id)
        hlayout.addWidget(self.line_id)
        hlayout.addWidget(self.label_status)
        hlayout.addWidget(self.line_status)
        hlayout.addWidget(self.label_status_visual)
        hlayout.addWidget(self.line_status_visual)
        hlayout.addWidget(self.label_buyer)
        hlayout.addWidget(self.line_buyer)
        
        self.label_details = QtWidgets.QLabel("Requisition Details:")
        self.text_details = QtWidgets.QTextEdit()
        self.label_items = QtWidgets.QLabel("Requisition Items:")
        self.list_items = QtWidgets.QListView()
        self.list_items.setStyleSheet("QListView{background-color:#f0f0f0}")
        self.list_items.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_items.setResizeMode(QtWidgets.QListView.Adjust)
        self.list_items.setItemDelegate(ItemsDelegate())
        
        self.model = ItemsModel()
        self.list_items.setModel(self.model)
        
        # self.list_items.selectionModel().selectionChanged.connect(self.onRowSelect)
        
        main_layout.addLayout(hlayout)
        
        main_layout.addWidget(self.label_details)
        main_layout.addWidget(self.text_details)
        main_layout.addWidget(self.label_items)
        main_layout.addWidget(self.list_items)
        self.setLayout(main_layout)
        
    def repopulateTable(self):
        results = self.visual.getReqItems(self.line_id.text())
        for result in results:
            #print(result['FILEPATH'])
            self.model.add_item(result[0],result[1],result[2],result[3],result[4],result[5],"")
            
    def resizeEvent(self, e):
        self.model.layoutChanged.emit()
            
        
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
        
        
PADDING = QtCore.QMargins(15, 2, 15, 2)

class ItemsDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        
        line_no, line_status, part_id, vendor_part_id,order_qty, purchase_um, purch_order = index.model().data(index, QtCore.Qt.DisplayRole)
        
        #lineMarkedPen = QtGui.QPen(QtGui.QColor("#f0f0f0"),1,QtCore.Qt.SolidLine)
        
        r = option.rect.marginsRemoved(PADDING)
        painter.setPen(QtCore.Qt.NoPen)
        if option.state & QtWidgets.QStyle.State_Selected:
            color = QtGui.QColor("#A0C4FF")
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            color = QtGui.QColor("#BDB2FF")
        else:
            color = QtGui.QColor("#FFFFFC")
        painter.setBrush(color)
        painter.drawRoundedRect(r, 5, 5)
        
        # painter.setPen(lineMarkedPen)
        # painter.drawLine(r.topLeft(),r.topRight())
        # painter.drawLine(r.topRight(),r.bottomRight())
        # painter.drawLine(r.bottomLeft(),r.bottomRight())
        # painter.drawLine(r.topLeft(),r.bottomLeft())
        
        font = painter.font()
        font.setPointSize(8)
        #font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(r.topLeft()+QtCore.QPoint(35,12),str(line_no)+".")
        # font = painter.font()
        # font.setPointSize(8)
        # font.setBold(False)
        # painter.setFont(font)
        # painter.setPen(QtCore.Qt.black)
        painter.drawText(r.topLeft()+QtCore.QPoint(45,12),"Status: " + line_status)
        # painter.drawText(r.topLeft()+QtCore.QPoint(55,12),"Part ID: " + part_id)
        painter.drawText(r.topLeft()+QtCore.QPoint(90,12),"Vendor Part ID: " + vendor_part_id)
        
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,32)

class ItemsModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(ItemsModel, self).__init__(*args, **kwargs)
        self.items = []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.items[index.row()]

    def setData(self, index, role, value):
        self._size[index.row()]

    def rowCount(self, index):
        return len(self.items)
    
    def removeRow(self, row):
        del self.items[row]
        self.layoutChanged.emit()

    def clear_items(self):
        self.items = []
        
    def getFilePath(self, row):
        return self.items[row][1]
    
    def getFileName(self, row):
        return self.items[row][0]

    def add_item(self, line_no, line_status, part_id, vendor_part_id,order_qty, purchase_um, purch_order):
        # Access the list via the model.
        self.items.append((line_no, line_status, part_id, vendor_part_id,order_qty, purchase_um, purch_order))
        # Trigger refresh.
        self.layoutChanged.emit()