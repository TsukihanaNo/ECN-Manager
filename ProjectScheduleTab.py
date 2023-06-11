from PySide6 import QtGui, QtCore, QtWidgets
import sys, os

from ScheduleTaskWindow import *

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class ProjectScheduleTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ProjectScheduleTab,self).__init__()
        self.parent = parent
        self.cursor = parent.cursor
        self.db = parent.db
        self.settings = parent.settings
        self.user_info = parent.user_info
        self.user_permissions = parent.user_permissions
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.stageDictPRQ = parent.stageDictPRQ
        self.ico = parent.ico
        self.visual = parent.visual
        self.doc_id = parent.doc_id
        self.initAtt()
        self.clipboard = QtGui.QGuiApplication.clipboard()
        self.menu = QtWidgets.QMenu(self)
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self): 
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        
        mainlayout.addWidget(self.toolbar)

        self.button_add = QtWidgets.QPushButton("Add Task")
        if self.doc_id is None:
            self.button_add.setDisabled(True)
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.addTask)
        self.button_remove = QtWidgets.QPushButton("Remove Task")
        icon_loc = icon = os.path.join(program_location,"icons","minus.png")
        self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        self.button_remove.setDisabled(True)
        self.button_remove.clicked.connect(self.removeRow)
        self.button_edit = QtWidgets.QPushButton("Edit Task")
        icon_loc = icon = os.path.join(program_location,"icons","edit.png")
        self.button_edit.setIcon(QtGui.QIcon(icon_loc))
        self.button_edit.setDisabled(True)
        self.button_edit.clicked.connect(self.editTask)
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_edit)
        
        self.tasks = QtWidgets.QListView()
        self.tasks.setStyleSheet("QListView{background-color:#f0f0f0}")
        self.tasks.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tasks.setResizeMode(QtWidgets.QListView.Adjust)
        self.tasks.setItemDelegate(TasksDelegate())
        self.tasks.doubleClicked.connect(self.editTask)
        # if self.parent.doc_data is not None:
        #     if self.parent.parent.user_info['user']==self.parent.doc_data["AUTHOR"]:
        #         self.tasks.doubleClicked.connect(self.editPart)
        #     else:
        #         self.button_add.setDisabled(True)
        # else:
        #     self.tasks.doubleClicked.connect(self.editPart)
        self.model = TasksModel()
        self.tasks.setModel(self.model)
        
        self.tasks.selectionModel().selectionChanged.connect(self.onRowSelect)
        
        mainlayout.addWidget(self.tasks)
        
        self.setLayout(mainlayout)              
        #self.repopulateTable()
        
        
    def onRowSelect(self):
        self.button_edit.setEnabled(bool(self.tasks.selectionModel().selectedIndexes()))
        
        
    def addTask(self):
        self.task_editor = ScheduleTaskWindow(self)

    def editTask(self):
        index = self.parts.currentIndex()
        self.task_editor = ScheduleTaskWindow(self,index)
        

    def removeRow(self):
        index = self.tasks.selectionModel().selectedIndexes()
        index = sorted(index, reverse=True)
        for item in index:
            row = item.row()
            self.model.removeRow(row)
        
            
    def repopulateTable(self):
        pass

    def rowCount(self):
        return self.model.rowCount(self.tasks)
    
                    
    def resizeEvent(self, e):
        self.model.layoutChanged.emit()
                
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()

PADDING = QtCore.QMargins(15, 2, 15, 2)

class TasksDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        
        doc_id, title,req_id,status = index.model().data(index, QtCore.Qt.DisplayRole)
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
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx2,25),"Req. ID: "+req_id)
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1,45),title)
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,55)

class TasksModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(TasksModel, self).__init__(*args, **kwargs)
        self.tasks = []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.tasks[index.row()]
        if role == QtCore.Qt.DecorationRole:
            return self.status[index.row()]

    def setData(self, index, role, value):
        self._size[index.row()]
        
    def rowCount(self, index):
        return len(self.tasks)
    
    def removeRow(self, row):
        del self.tasks[row]
        self.layoutChanged.emit()
        
    def update_req_data(self,row, doc_id,title, req_id,status):
        self.tasks[row]=(doc_id,title, req_id,status)
        self.layoutChanged.emit()
        
    def get_task_data(self,row):
        return self.tasks[row]

    def clear_tasks(self):
        self.tasks = []
    
    def add_task(self, doc_id,title, req_id,status):
        # Access the list via the model.
        self.tasks.append((doc_id,title, req_id,status))
        # Trigger refresh.
        self.layoutChanged.emit()