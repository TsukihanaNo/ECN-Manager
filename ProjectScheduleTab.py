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
        self.button_timeline = QtWidgets.QPushButton("Show Timeline")
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_edit)
        self.toolbar.addWidget(self.button_timeline)
        
        self.tasks = QtWidgets.QTreeWidget()
        headers = ["Task", "Owner", "Start Date", "Completion Date", "Status", "Duration"]
        self.tasks.setColumnCount(len(headers))
        self.tasks.setHeaderLabels(headers)
        self.tasks.setColumnWidth(0,350)
        self.tasks.itemDoubleClicked.connect(self.editTask)
        self.tasks.selectionModel().selectionChanged.connect(self.onRowSelect)

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
        
            
    def repopulateTable(self):
        pass             
                
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
