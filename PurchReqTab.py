from PySide6 import QtGui, QtCore, QtWidgets
import sys, os
from PartEditor import *
from PurchReqWindow import *

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class PurchReqTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(PurchReqTab,self).__init__()
        self.parent = parent
        self.cursor = parent.cursor
        self.db = parent.db
        self.settings = parent.settings
        self.user_info = parent.user_info
        self.user_permissions = parent.user_permissions
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.ico = parent.ico
        self.visual = parent.visual
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

        self.button_add = QtWidgets.QPushButton("Add Requisition")
        if self.doc_id is None:
            self.button_add.setDisabled(True)
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.addReq)
        # self.button_remove = QtWidgets.QPushButton("Remove Requisition")
        # icon_loc = icon = os.path.join(program_location,"icons","minus.png")
        # self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        # self.button_remove.setDisabled(True)
        # self.button_remove.clicked.connect(self.removeRow)
        self.button_edit = QtWidgets.QPushButton("Edit Requisition")
        icon_loc = icon = os.path.join(program_location,"icons","edit.png")
        self.button_edit.setIcon(QtGui.QIcon(icon_loc))
        self.button_edit.setDisabled(True)
        self.button_edit.clicked.connect(self.editReq)
        
        self.toolbar.addWidget(self.button_add)
        # self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_edit)
        
        self.reqs = QtWidgets.QListView()
        self.reqs.setStyleSheet("QListView{background-color:#f0f0f0}")
        self.reqs.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.reqs.setResizeMode(QtWidgets.QListView.Adjust)
        self.reqs.setItemDelegate(ReqsDelegate())
        self.reqs.doubleClicked.connect(self.editReq)
        # if self.parent.doc_data is not None:
        #     if self.parent.parent.user_info['user']==self.parent.doc_data["AUTHOR"]:
        #         self.reqs.doubleClicked.connect(self.editPart)
        #     else:
        #         self.button_add.setDisabled(True)
        # else:
        #     self.reqs.doubleClicked.connect(self.editPart)
        self.model = ReqsModel()
        self.reqs.setModel(self.model)
        
        self.reqs.selectionModel().selectionChanged.connect(self.onRowSelect)
        
        mainlayout.addWidget(self.reqs)
        
        self.setLayout(mainlayout)              
        #self.repopulateTable()
        
    def createMenu(self):
        copy_part_action = QtGui.QAction("Copy Part ID",self)
        copy_mfg_action = QtGui.QAction("Copy Manufacturer",self)
        copy_mfg_part_action = QtGui.QAction("Copy Mfg. Part",self)
        copy_reference_action = QtGui.QAction("Copy Reference",self)
        copy_replace_action = QtGui.QAction("Copy Replacing",self)
        copy_part_action.triggered.connect(self.copyPartID)
        copy_mfg_action.triggered.connect(self.copyMFG)
        copy_mfg_part_action.triggered.connect(self.copyMFGPart)
        copy_reference_action.triggered.connect(self.copyReference)
        copy_replace_action.triggered.connect(self.copyReplace)
        self.menu.addAction(copy_part_action)
        self.menu.addAction(copy_mfg_action)
        self.menu.addAction(copy_mfg_part_action)
        self.menu.addAction(copy_reference_action)
        self.menu.addAction(copy_replace_action)
        
    def copyPartID(self):
        index = self.reqs.currentIndex()
        self.clipboard.setText(self.model.get_part_id(index.row()))
        
    def copyMFG(self):
        index = self.reqs.currentIndex()
        self.clipboard.setText(self.model.get_mfg(index.row()))
        
    def copyMFGPart(self):
        index = self.reqs.currentIndex()
        self.clipboard.setText(self.model.get_mfg_part(index.row()))
        
    def copyReference(self):
        index = self.reqs.currentIndex()
        self.clipboard.setText(self.model.get_reference(index.row()))
        
    def copyReplace(self):
        index = self.reqs.currentIndex()
        self.clipboard.setText(self.model.get_replace(index.row()))
        
    def contextMenuEvent(self,event):
        self.menu.exec_(event.globalPos())
        
    def onRowSelect(self):
        self.button_edit.setEnabled(bool(self.reqs.selectionModel().selectedIndexes()))
        
        
    def addReq(self):
        self.req_editor = PurchReqWindow(self)
        
    def editReq(self):
        index = self.reqs.currentIndex()
        print(index.data(QtCore.Qt.DisplayRole))
        doc_id = index.data(QtCore.Qt.DisplayRole)[0]
        row = index.row()
        self.part_editor = PurchReqWindow(self,doc_id,row)

    def removeRow(self):
        index = self.reqs.selectionModel().selectedIndexes()
        index = sorted(index, reverse=True)
        for item in index:
            row = item.row()
            self.model.removeRow(row)
        
            
    def repopulateTable(self):
        self.parent.cursor.execute(f"select * from PURCH_REQS where PROJECT_ID='{self.doc_id}'")
        results = self.parent.cursor.fetchall()
        for result in results:
            # if self.parent.parent.visual is not None:
            #     status = self.getStatus(result['PART_ID'], result['TYPE'])
            # else:
            #     status = "NA"
            self.model.add_req(result['DOC_ID'], result['REQ_ID'],result['STATUS'])
            
    def rowCount(self):
        return self.model.rowCount(self.reqs)
    
    def getStatus(self,part,part_type):
        if self.parent.parent.visual.partExist(part):
            if self.parent.parent.visual.checkPartSetup(part,part_type):
                return "Completed"
            else: 
                return "Incomplete"
        else:
            return "Not Found"
            
    def updateStatusColor(self):
        for row in range(self.rowCount()):
            part = self.model.get_part_id(row)
            part_type = self.model.get_type(row)
            if self.parent.parent.visual is not None:
                if self.parent.parent.visual.partExist(part):
                    if self.parent.parent.visual.checkPartSetup(part,part_type):
                        self.model.update_status(row, "Complete")
                    else: 
                        self.model.update_status(row, "Incomplete")
                else:
                    self.model.update_status(row, "Not Found")
                    
    def resizeEvent(self, e):
        self.model.layoutChanged.emit()
                
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
            
                
PADDING = QtCore.QMargins(15, 2, 15, 2)

class ReqsDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        
        doc_id, req_id,status = index.model().data(index, QtCore.Qt.DisplayRole)
        # status = index.model().data(index, QtCore.Qt.DecorationRole)
        
        lineMarkedPen = QtGui.QPen(QtGui.QColor("#f0f0f0"),1,QtCore.Qt.SolidLine)
        
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
        
        if status !="NA":
            rect = QtCore.QRect(r.topRight()+QtCore.QPoint(-150,12),QtCore.QSize(110,25))
            if status =="Completed":
                color = QtGui.QColor("#CAFFBF")
            elif status =="Incomplete":
                color = QtGui.QColor("#FDFFB6")
            else:
                color = QtGui.QColor("#FFADAD")
            painter.setBrush(color)
            painter.drawRoundedRect(rect, 5, 5)
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            painter.setPen(QtCore.Qt.black)
            painter.drawText(r.topRight()+QtCore.QPoint(-145,28),f"Status: {status}")
        
        painter.setPen(lineMarkedPen)
        painter.drawLine(r.topLeft()+QtCore.QPoint(0,50),r.topRight()+QtCore.QPoint(0,50))

        
        text_offsetx1 = 15
        text_offsetx2 = r.width()/2+10
        
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1,25),doc_id)
        font.setPointSize(12)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1,45),req_id)
        font.setPointSize(8)
        painter.setFont(font)
        # painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx2,15),f"Type: {part_type}")
        # painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx2,30),f"Disposition: {disposition}")
        # painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx2,45),f"Inspection: {Inspection}")
        # painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1,65),f"Manufacturer: {mfg}")
        # painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx2,65),f"Mfg. Part: {mfg_part_id}")
        # if reference is not None:
        #     if len(reference)>50:
        #         reference = reference[:50] +" ..."
        # painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1,80),f"Reference: {reference}")
        # if replacing is not None:
        #     if len(replacing)>100:
        #         replacing = replacing[:100] +" ..."
        # painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1,95),f"Replacing: {replacing}")
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,55)

class ReqsModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(ReqsModel, self).__init__(*args, **kwargs)
        self.reqs = []
        self.status = []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.reqs[index.row()]
        if role == QtCore.Qt.DecorationRole:
            return self.status[index.row()]

    def setData(self, index, role, value):
        self._size[index.row()]
        
    def rowCount(self, index):
        return len(self.reqs)
    
    def removeRow(self, row):
        del self.reqs[row]
        self.layoutChanged.emit()
        
    def update_req_data(self,row, doc_id, req_id,status):
        self.reqs[row]=(doc_id, req_id,status)
        self.layoutChanged.emit()
        
    def update_status(self,row,status):
        self.status[row]=status
        self.layoutChange.emit()
        
    def get_req_data(self,row):
        return self.reqs[row]

    def clear_reqs(self):
        self.reqs = []
        
    # def exist_part(self,part):
    #     for data in self.reqs:
    #         if data[0]==part:
    #             return True
    #     return False
        
    # def get_part_id(self, row):
    #     return self.reqs[row][0]

    # def get_desc(self,row):
    #     return self.reqs[row][1]

    # def get_type(self,row):
    #     return self.reqs[row][2]
    
    # def get_disposition(self,row):
    #     return self.reqs[row][3]
    
    # def get_mfg(self,row):
    #     return self.reqs[row][4]
    
    # def get_mfg_part(self,row):
    #     return self.reqs[row][5]
    
    # def get_reference(self,row):
    #     return self.reqs[row][6]
    
    # def get_replace(self,row):
    #     return self.reqs[row][7]
    
    # def get_inspection(self,row):
    #     return self.reqs[row][8]
    
    def add_req(self, doc_id, req_id,status):
        # Access the list via the model.
        self.reqs.append((doc_id, req_id,status))
        self.status.append(status)
        # Trigger refresh.
        self.layoutChanged.emit()