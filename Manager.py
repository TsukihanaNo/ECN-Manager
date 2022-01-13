import os
import re
import sys
import time
import sqlite3
from PySide6 import QtGui, QtCore, QtWidgets
from LoginWindow import *
from CompletedTab import *
from MyECNTab import *
from MyQueueTab import *
from DataBaseUpdateWindow import *
from NewDBWindow import *
from UsersWindow import *
from Hook import *


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")
lockfile = os.path.join(r"C:\temp", "ecn.lock")
icon = os.path.join(program_location,"ecn-icon.png")

databaseRequirements = {"ECN": ["ECN_ID TEXT", "ECN_TYPE TEXT", "ECN_TITLE TEXT", "ECN_REASON TEXT","REQUESTOR TEXT" ,"AUTHOR TEXT", "STATUS TEXT", "COMP_DATE DATE", "ECN_SUMMARY TEXT", "LAST_CHANGE_DATE DATE"],
                        "COMMENT": ["ECN_ID TEXT", "USER TEXT", "COMM_DATE DATE", "COMMENT TEXT"],
                        "USER": ["USER_ID TEXT", "PASSWORD TEXT", "NAME TEXT", "ROLE TEXT", "JOB_TITLE TEXT", "STATUS TEXT"],
                        "CHANGELOG": ["ECN_ID TEXT", "CHANGEDATE DATETIME", "NAME TEXT","DATABLOCK TEXT" ,"PREVDATA TEXT", "NEWDATA TEXT"],
                        }


class Manager(QtWidgets.QWidget):
    def __init__(self,ecn = None):
        super(Manager, self).__init__()
        self.windowWidth = QtGui.QGuiApplication.primaryScreen().availableGeometry().width() *0.5
        self.windowHeight = self.windowWidth *.75
        self.ecn = ecn
        self.firstInstance = True
        self.checkLockFile()
        self.generateLockFile()
        self.ico = QtGui.QIcon(icon)
        self.startUpCheck()
        self.user_info = {}
        self.programLoc = program_location
        
        self.nameList = []

        # self.checkDBTables()

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
        
    def checkLockFile(self):
        if os.path.exists(lockfile):
            self.dispMsg("Another Instance is already open.")
            self.firstInstance = False
            sys.exit()
        
    def generateLockFile(self):
        f = open(lockfile,"w+")
        f.write("program started, lock trigger")
        f.close()
        
    def removeLockFile(self):
        os.remove(lockfile)

    def loginDone(self):
        self.initAtt()
        self.initUI()
        self.center()
        self.show()
        self.loadInAnim()
        try:
            self.thread = QtCore.QThread()
            self.worker = Hook()
            self.worker.launch.connect(self.HookEcn)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.thread.start()
        except Exception as e:
            print(e)
            self.dispMsg("Port already in use.")
        
        if self.ecn is not None:
            self.HookEcn(self.ecn)

    def startUpCheck(self):
        if not os.path.exists(initfile):
            print("need to generate ini file")
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText("No database detected, please select an existing database or ask the admin to make a new one using the included tool.")
            openbutton = msgbox.addButton("Open DB", QtWidgets.QMessageBox.ActionRole)
            addbutton = msgbox.addButton("Add DB", QtWidgets.QMessageBox.ActionRole)
            cancelbutton = msgbox.addButton(QtWidgets.QMessageBox.Close)
            ret = msgbox.exec()
            if msgbox.clickedButton() == openbutton:
                db_loc = QtWidgets.QFileDialog.getOpenFileName(self,self.tr("Open DB"),program_location,self.tr("DB Files (*.DB)"))[0]
                self.db = sqlite3.connect(db_loc)
                self.cursor = self.db.cursor()
                self.cursor.row_factory = sqlite3.Row
                self.loginWindow = LoginWindow(self)
                #save setting
                if db_loc!="":
                    f = open(initfile,"w+")
                    f.write("DB_LOC : "+db_loc)
                    f.close()
            elif msgbox.clickedButton() == addbutton:
                self.newDB()
            else:
                exit()
        else:
            #read settings
            f = open(initfile,'r')
            settings = {}
            for line in f:
                key,value = line.split(" : ")
                settings[key]=value.strip()
            print(settings)
            f.close()
            self.db = sqlite3.connect(settings["DB_LOC"])
            self.cursor = self.db.cursor()
            self.cursor.row_factory = sqlite3.Row
            self.loginWindow = LoginWindow(self)


    def checkDBTables(self):
        addtable = {}
        addcolumns = {}
        removetables = []
        checkedtable = []
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")
        test = self.cursor.fetchall()
        for item in test:
            for key in item.keys():
                if item[key] in databaseRequirements.keys():
                    checkedtable.append(item[key])
                    command = "PRAGMA table_info(" + item[key] + ")"
                    self.cursor.execute(command)
                    columns = self.cursor.fetchall()
                    missingcol = []
                    colcheck = []
                    for colname in columns:
                        col = colname[1] + ' ' + colname[2]
                        colcheck.append(col)
                    for col in databaseRequirements[item[key]]:
                        if col not in colcheck:
                            missingcol.append(col)
                    if len(missingcol) > 0:
                        addcolumns[item[key]] = missingcol
                else:
                    removetables.append(item[key])
        for item in databaseRequirements.keys():
            if item not in checkedtable:
                addtable[item] = databaseRequirements[item]
        if len(addtable) != 0 or len(removetables) != 0 or len(addcolumns) != 0:
            self.databaseupdate = DataBaseUpdateWindow(
                self, addtable, removetables, addcolumns)

    # def dbTest(self):
    #     print("initiating test")
    #     #self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    #     self.cursor.execute("select * from CHANGELOG")
    #     test = self.cursor.fetchall()
    #     print(len(test))
    #     for item in test:
    #         for key in item.keys():
    #             print(item[key])

    def initAtt(self):
        self.setGeometry(100, 50, self.windowWidth, self.windowHeight)
        title = "ECN-Manager - User: " + self.user_info["user"]
        self.setWindowIcon(self.ico)
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.getNameList()

    def initUI(self):
        self.menubar = QtWidgets.QMenuBar(self)
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setMenuBar(self.menubar)

        self.createMenuActions()

        # mainLayout.setMenuBar(self.menubar)
        self.tabWidget = QtWidgets.QTabWidget(self)
        mainLayout.addWidget(self.tabWidget)
        
        if self.user_info["role"]!="Signer":
            self.myECNTab = MyECNTab(self)
            self.tabWidget.addTab(self.myECNTab, "My ECNs")

        self.queueTab = MyQueueTab(self)
        self.tabWidget.addTab(self.queueTab, "My Queue")

        self.completedTab = CompletedTab(self)
        self.tabWidget.addTab(self.completedTab, "Completed")

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.updateQueue)
        timer.start(15000)

    def createMenuActions(self):
        filemenu = self.menubar.addMenu("&File")
        if self.user_info['role'] == "Admin":
            newDBAction = QtGui.QAction("&New Database", self)
            newDBAction.triggered.connect(self.newDB)
            connectDBAction = QtGui.QAction(
                "&Connect to existing Database", self)
            filemenu.addAction(newDBAction)
            filemenu.addAction(connectDBAction)
            userAction = QtGui.QAction("&Users Window",self)
            userAction.triggered.connect(self.launchUsers)
            filemenu.addAction(userAction)
        exitAction = QtGui.QAction("&Exit", self)
        exitAction.triggered.connect(self.close)
        exitAction.setShortcut("CTRL+Q")
        filemenu.addAction(exitAction)

    def updateQueue(self):
        if self.user_info["role"]!="Signer":
            self.myECNTab.repopulateTable()
        self.queueTab.repopulateTable()
        self.completedTab.repopulateTable()

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def HookEcn(self,ecn_id):
        print("info received",ecn_id)
        self.ecnWindow = ECNWindow(self,ecn_id)


    def loadInAnim(self):
        loc = self.tabWidget.pos()
        self.animation = QtCore.QPropertyAnimation(self.tabWidget, b"pos")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutBack)
        self.animation.setStartValue(QtCore.QPoint(
            self.tabWidget.pos().x(), -self.windowHeight))
        self.animation.setEndValue(QtCore.QPoint(loc))

        self.animation.start()

    def closeEvent(self, event):
        self.db.close()
        if self.firstInstance:
            self.removeLockFile()
        for w in QtWidgets.QApplication.allWidgets():
            w.close()

    def newDB(self):
        self.newDBWindow = NewDBWindow(self)
        
    def launchUsers(self):
        self.userWindow = UsersWindow(self)
        
    def getNameList(self):
        command = "Select NAME from USER where STATUS ='Active'"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        for result in results:
            self.nameList.append(result[0])
        #print(self.nameList)


# execute the program
def main():
    print(sys.argv)
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv)>1:
        manager=Manager(sys.argv[1])
    else:
        manager = Manager()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
