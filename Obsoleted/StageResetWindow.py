from PySide6 import QtWidgets, QtCore, QtGui
import os, sys
from UserPanel import *
import sqlite3  


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class StageResetWindow(QtWidgets.QWidget):
    def __init__(self,parent=None,ecn_id = None):
        super(StageResetWindow,self).__init__()
        self.windowWidth =  400
        self.windowHeight = 600
        self.initAtt()
        self.initUI()
        self.show()

    def center(self):
        window = self.window()
        window.setGeometry(
            QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            window.size(),
            QtGui.QGuiApplication.primaryScreen().availableGeometry(),
        ),
    )


    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        title = "Stage Reset Window"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
          

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        #USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, DEPT TEXT, STATUS TEXT, EMAIL TEXT)
        titles = ['Job Title','User','Name','Stage']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.editUser)
        self.table.selectionModel().selectionChanged.connect(self.onRowSelect)
        self.button_edit.setEnabled(False)
        self.button_remove.setEnabled(False)
        self.button_select = QtWidgets.QPushButton("Set Stage")
        
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.button_select)
        
        
        self.repopulateTable()
        
    # def getStageDict(self):
    #     self.stageDict = {}
    #     print(self.settings)
    #     stages = self.settings["Stage"].split(",")
    #     for stage in stages:
    #         key,value = stage.split("-")
    #         self.stageDict[key] = value.strip()
    #     print(self.stageDict)

    
    def repopulateTable(self):
        self.table.clearContents()
        command = "Select * from USER"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        self.table.setRowCount(len(results))
        rowcount=0
        for result in results:
            self.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['USER_ID']))
            self.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['NAME']))
            self.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['JOB_TITLE']))
            self.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['ROLE']))
            self.table.setItem(rowcount, 4, QtWidgets.QTableWidgetItem(result['STATUS']))
            self.table.setItem(rowcount, 5, QtWidgets.QTableWidgetItem(result['EMAIL']))

            rowcount+=1
            

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
