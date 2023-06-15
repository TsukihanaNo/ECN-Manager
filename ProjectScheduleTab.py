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
        self.button_remove.clicked.connect(self.removeTask)
        self.button_remove.setDisabled(True)
        self.button_edit = QtWidgets.QPushButton("Edit Task")
        icon_loc = icon = os.path.join(program_location,"icons","edit.png")
        self.button_edit.setIcon(QtGui.QIcon(icon_loc))
        self.button_edit.setDisabled(True)
        self.button_edit.clicked.connect(self.editTask)
        
        self.button_expand = QtWidgets.QPushButton("Expand All")
        self.button_expand.clicked.connect(self.expandAll)
        self.button_collapse = QtWidgets.QPushButton("Collapse All")
        self.button_collapse.clicked.connect(self.collapseAll)
        self.button_timeline = QtWidgets.QPushButton("Show Timeline")
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_edit)
        self.toolbar.addWidget(self.button_expand)
        self.toolbar.addWidget(self.button_collapse)
        self.toolbar.addWidget(self.button_timeline)
        
        self.tasks = QtWidgets.QTreeWidget()
        headers = ["Task", "Owner", "Start Date", "Completion Date", "Status", "Duration"]
        self.tasks.setColumnCount(len(headers))
        self.tasks.setHeaderLabels(headers)
        self.tasks.setColumnWidth(0,350)
        self.tasks.itemDoubleClicked.connect(self.editTask)
        self.tasks.selectionModel().selectionChanged.connect(self.onRowSelect)
        self.tasks.setSortingEnabled(True)

        mainlayout.addWidget(self.tasks)
        
        self.setLayout(mainlayout)              
        #self.repopulateTable()
        
    def onRowSelect(self):
        self.button_edit.setEnabled(bool(self.tasks.currentItem()))
        self.button_remove.setEnabled(bool(self.tasks.currentItem()))
        
    def addTask(self):
        self.task_editor = ScheduleTaskWindow(self)

    def editTask(self,item):
        self.task_editor = ScheduleTaskWindow(self,item)

    def removeTask(self):
        item = self.tasks.currentItem()
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            self.tasks.takeTopLevelItem(self.tasks.indexOfTopLevelItem(item))
        
    def expandAll(self):
        for x in range(self.tasks.invisibleRootItem().childCount()):
            if self.tasks.invisibleRootItem().child(x).childCount()>0:
                self.tasks.expandItem(self.tasks.invisibleRootItem().child(x))
    
    def collapseAll(self):
        for x in range(self.tasks.invisibleRootItem().childCount()):
            if self.tasks.invisibleRootItem().child(x).childCount()>0:
                self.tasks.collapseItem(self.tasks.invisibleRootItem().child(x))
                
                
    def bubbleDate(self,item):
        if item.parent() is not None:
            start_date = ""
            end_date = ""
            for x in range(item.parent().childCount()):
                if x == 0:
                    start_date = QtCore.QDate.fromString(item.parent().child(x).text(2),"MM/dd/yyyy") 
                    end_date = QtCore.QDate.fromString(item.parent().child(x).text(3),"MM/dd/yyyy") 
                else:
                    start_comp = QtCore.QDate.fromString(item.parent().child(x).text(2),"MM/dd/yyyy")
                    end_comp = QtCore.QDate.fromString(item.parent().child(x).text(3),"MM/dd/yyyy")
                    if start_comp<start_date:
                        start_date=start_comp
                    if end_comp>end_date:
                        end_date=end_comp
            item.parent().setText(2,start_date.toString("MM/dd/yyyy"))
            item.parent().setText(3,end_date.toString("MM/dd/yyyy"))
                
            self.bubbleDate(item.parent())
        
            
    def repopulateTable(self):
        pass             
                
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
