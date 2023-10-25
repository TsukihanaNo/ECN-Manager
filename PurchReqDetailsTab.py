from PySide6 import QtWidgets, QtCore, QtGui
from datetime import datetime
import sys, os


VISUAL_REQ_STATUS = {'V':"Approved",'I':"In Process",'C': "Closed",'X': "Canceled/Void",'T':"Draft",'O':"Ordered"}

class PurchReqDetailTab(QtWidgets.QWidget):
    def __init__(self, parent = None, doc_id = None):
        super(PurchReqDetailTab,self).__init__()
        self.parent = parent
        self.cursor = parent.cursor
        self.db = parent.db
        self.settings = parent.settings
        self.visual = parent.visual
        self.user_info = parent.user_info
        self.user_permissions = parent.user_permissions
        # self.windowWidth =  self.parent.windowWidth
        # self.windowHeight = self.parent.windowHeight
        # self.setFixedSize(self.windowWidth,self.windowHeight)
        self.doc_id = doc_id
        self.tablist = []
        self.initAtt()
        self.initUI()
        if self.doc_id is not None:
            self.line_id.setText(self.doc_id)
            self.loadHeader()
            self.loadItems()
        else:
            self.line_author.setText(self.user_info["user"])
        
    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        self.label_doc_id = QtWidgets.QLabel("Doc ID:")
        self.line_doc_id = QtWidgets.QLineEdit()
        self.line_doc_id.setDisabled(True)
        self.label_id = QtWidgets.QLabel("Visual Req. ID:")
        self.line_id = QtWidgets.QLineEdit()
        self.label_prj_id = QtWidgets.QLabel("PRJ ID:")
        self.line_prj_id = QtWidgets.QLineEdit()
        self.line_prj_id.setText(self.parent.project_id)
        self.line_prj_id.setDisabled(True)
        self.label_status = QtWidgets.QLabel("Status:")
        self.line_status = QtWidgets.QLineEdit()
        self.line_status.setText("Draft")
        self.line_status.setDisabled(True)
        self.label_status_visual = QtWidgets.QLabel("Status Visual:")
        self.line_status_visual = QtWidgets.QLineEdit()
        self.line_status_visual.setDisabled(True)
        # self.line_status_visual.setReadOnly(True)
        self.label_buyer = QtWidgets.QLabel("Assigned Buyer:")
        self.line_buyer = QtWidgets.QLineEdit()
        self.line_buyer.setDisabled(True)
        self.label_author = QtWidgets.QLabel("Author")
        self.line_author = QtWidgets.QLineEdit()
        self.line_author.setDisabled(True)
        self.label_title = QtWidgets.QLabel("Doc. Title")
        self.line_title = QtWidgets.QLineEdit()
        
        hlayout = QtWidgets.QHBoxLayout()
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.label_doc_id)
        vlayout.addWidget(self.line_doc_id)
        hlayout.addLayout(vlayout)
        vlayout1 = QtWidgets.QVBoxLayout()
        vlayout1.addWidget(self.label_id)
        vlayout1.addWidget(self.line_id)
        hlayout.addLayout(vlayout1)
        vlayout6 = QtWidgets.QVBoxLayout()
        vlayout6.addWidget(self.label_prj_id)
        vlayout6.addWidget(self.line_prj_id)
        hlayout.addLayout(vlayout6)
        vlayout2 = QtWidgets.QVBoxLayout()
        vlayout2.addWidget(self.label_status)
        vlayout2.addWidget(self.line_status)
        hlayout.addLayout(vlayout2)
        vlayout3 = QtWidgets.QVBoxLayout()
        vlayout3.addWidget(self.label_status_visual)
        vlayout3.addWidget(self.line_status_visual)
        hlayout.addLayout(vlayout3)
        vlayout4 = QtWidgets.QVBoxLayout()
        vlayout4.addWidget(self.label_buyer)
        vlayout4.addWidget(self.line_buyer)
        hlayout.addLayout(vlayout4)
        vlayout5 = QtWidgets.QVBoxLayout()
        vlayout5.addWidget(self.label_author)
        vlayout5.addWidget(self.line_author)
        hlayout.addLayout(vlayout5)

        
        self.label_details = QtWidgets.QLabel("Requisition Details:")
        self.text_details = QtWidgets.QTextEdit()
        self.text_details.setFixedHeight(80)
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
        main_layout.addWidget(self.label_title)
        main_layout.addWidget(self.line_title)
        main_layout.addWidget(self.label_details)
        main_layout.addWidget(self.text_details)
        main_layout.addWidget(self.label_items)
        main_layout.addWidget(self.list_items)
        
    def loadItems(self):
        self.model.clear_items()
        results = self.visual.getReqItems(self.line_id.text())
        for result in results:
            # print(result[0],result[1],result[2],result[3],result[4],result[5],result[6])
            self.model.add_item(result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7])
        total = self.model.get_total_cost()
        self.label_items.setText(f"Requisition Items - ${total}:")
            
    def loadHeader(self):
        result = self.visual.getReqHeader(self.line_id.text())
        self.line_status_visual.setText(VISUAL_REQ_STATUS[result[1]])
        self.line_buyer.setText(result[0])
            
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
        
        line_no, line_status, part_id, vendor_part_id,order_qty, purchase_um, purch_order, unit_price = index.model().data(index, QtCore.Qt.DisplayRole)
        
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
        
        if line_status =="C":
            color = QtGui.QColor("#CAFFBF")
            rect = QtCore.QRect(r.topLeft()+QtCore.QPoint(15+15+300+330,2),QtCore.QSize(110,15))
            painter.setBrush(color)
            painter.drawRoundedRect(rect, 5, 5)
        
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        #font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        text = str(line_no)+"."
        painter.drawText(r.topLeft()+QtCore.QPoint(15,14),text)
        text = "Part ID: "
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15,14),text)
        text = "Vendor Part ID: "
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+300,14),text)
        text = "Status: "
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+300+335,14),text)
        text = "Qty: "
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15,40),text)
        text = "UOM: "
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+100,40),text)
        text = "Unit Price: "
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+100+150,40),text)
        text = "Total: "
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+100+150+150,40),text)
        text = "P.O #: "
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+100+150+150+150,40),text)
        
        font.setBold(False)
        painter.setFont(font)
        # text = str(line_no)+"."
        # painter.drawText(r.topLeft()+QtCore.QPoint(15,14),text)
        font_metric = QtGui.QFontMetrics(painter.font())
        font_offset = font_metric.boundingRect("Part ID:").width()
        text = str(part_id)
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+font_offset+10,14),text)
        text = vendor_part_id
        font_offset=font_metric.boundingRect("Vendor Part ID:").width()
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+300+font_offset+10,14),text)
        text = VISUAL_REQ_STATUS[line_status]
        font_offset=font_metric.boundingRect("Status:").width()
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+300+335+font_offset+10,14),text)
        text = str(order_qty)
        font_offset=font_metric.boundingRect("Qty:").width()
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+font_offset+10,40),text)
        text = str(purchase_um)
        font_offset=font_metric.boundingRect("UOM:").width()
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+100+font_offset+10,40),text)
        text = "$" + str(unit_price)
        font_offset=font_metric.boundingRect("Unit Price:").width()
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+100+150+font_offset+10,40),text)
        total_price = unit_price*order_qty
        text = "$"+str(total_price)
        font_offset=font_metric.boundingRect("P.O #:").width()
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+100+150+150+font_offset+10,40),text)
        text = str(purch_order)
        font_offset=font_metric.boundingRect("P.O #:").width()
        painter.drawText(r.topLeft()+QtCore.QPoint(15+15+100+150+150+150+font_offset+10,40),text)

        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,50)

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
    
    def get_total_cost(self):
        total = 0
        for item in self.items:
            total += item[4]*item[7]
        return total

    def add_item(self, line_no, line_status, part_id, vendor_part_id,order_qty, purchase_um, purch_order,unit_price):
        # Access the list via the model.
        self.items.append((line_no, line_status, part_id, vendor_part_id,order_qty, purchase_um, purch_order,unit_price))
        # Trigger refresh.
        self.layoutChanged.emit()