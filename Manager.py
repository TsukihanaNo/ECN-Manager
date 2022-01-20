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
from SearchResults import *
from SettingsWindow import *


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")
lock_loc = r"C:\ProgramData\ECN-Manager"
lockfile = os.path.join(lock_loc, "ecn.lock")
notifier_lockfile = os.path.join(program_location, "notifier.lock")
icon = os.path.join(program_location,"ecn-icon.png")

databaseRequirements = {"ECN": ["ECN_ID TEXT", "ECN_TYPE TEXT", "ECN_TITLE TEXT", "ECN_REASON TEXT","REQUESTOR TEXT" ,"AUTHOR TEXT", "STATUS TEXT", "COMP_DATE DATE", "ECN_SUMMARY TEXT", "LAST_CHANGE_DATE DATE"],
                        "COMMENT": ["ECN_ID TEXT", "USER TEXT", "COMM_DATE DATE", "COMMENT TEXT"],
                        "USER": ["USER_ID TEXT", "PASSWORD TEXT", "NAME TEXT", "ROLE TEXT", "JOB_TITLE TEXT", "STATUS TEXT"],
                        "CHANGELOG": ["ECN_ID TEXT", "CHANGEDATE DATETIME", "NAME TEXT","DATABLOCK TEXT" ,"PREVDATA TEXT", "NEWDATA TEXT"],
                        }


class Manager(QtWidgets.QWidget):
    def __init__(self,ecn = None):
        super(Manager, self).__init__()
        self.windowWidth = 850
        self.windowHeight = 600
        self.ecn = ecn
        self.firstInstance = True
        self.checkLockLoc()
        self.checkLockFile()
        self.generateLockFile()
        self.checkNotifier()
        self.ico = QtGui.QIcon(icon)
        self.startUpCheck()
        self.getStageDict()
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
    
    def checkLockLoc(self):
        if not os.path.exists(lock_loc):
            os.makedirs(lock_loc)
        
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
        
    def checkNotifier(self):
        if not os.path.exists(notifier_lockfile):
            self.dispMsg("The Notifier is currently not running. No notifications will be sent until it is launched.")

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
                #save setting
                if db_loc!="":
                    f = open(initfile,"w")
                    data =f"DB_LOC : {db_loc}\nJob_Titles : Admin\nStage : Admin-99"
                    f.write(data)
                    f.close()
                    self.loadSettings()
                    self.checkSettings()
                self.db = sqlite3.connect(db_loc)
                self.cursor = self.db.cursor()
                self.cursor.row_factory = sqlite3.Row
                self.loginWindow = LoginWindow(self)
            elif msgbox.clickedButton() == addbutton:
                self.newDB()
            else:
                exit()
        else:
            self.loadSettings()
            self.checkSettings()
            self.db = sqlite3.connect(self.settings["DB_LOC"])
            self.cursor = self.db.cursor()
            self.cursor.row_factory = sqlite3.Row
            self.loginWindow = LoginWindow(self)
            
    def loadSettings(self):
        f = open(initfile,'r')
        self.settings = {}
        for line in f:
            key,value = line.split(" : ")
            self.settings[key]=value.strip()
        print(self.settings)
        f.close()
        
    def checkSettings(self):
        missing_keys = ""
        if "Dept" not in self.settings.keys():
            missing_keys += "Dept "
        if "SMTP" not in self.settings.keys():
            missing_keys += "SMTP "
        if "Port" not in self.settings.keys():
            missing_keys += "Port "
        if missing_keys !="":
            self.dispMsg(f"The following settings are missing: {missing_keys}. Please set them up in the settings window and set up the rest of the settings.")
        
        
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
        searchLayout = QtWidgets.QHBoxLayout()
        self.line_search = QtWidgets.QLineEdit(self)
        self.line_search.setPlaceholderText("Search here")
        self.button_search = QtWidgets.QPushButton("Search")
        self.line_search.returnPressed.connect(self.search)
        self.button_search.clicked.connect(self.search)
        searchLayout.addWidget(self.line_search)
        searchLayout.addWidget(self.button_search)
        mainLayout.addLayout(searchLayout)

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
        timer.timeout.connect(self.repopulateTable)
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
            settingAction = QtGui.QAction("&Settings",self)
            settingAction.triggered.connect(self.launchSettings)
            filemenu.addAction(settingAction)
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
        
    def HookEcn(self,ecn_id=None):
        print("info received",ecn_id)
        self.ecnWindow = ECNWindow(self,ecn_id)
        
    def repopulateTable(self):
        if self.user_info["role"]!="Signer":
            self.myECNTab.repopulateTable()
        self.queueTab.repopulateTable()
        self.completedTab.repopulateTable()


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

    def launchSettings(self):
        self.settingsWindow = SettingsWindow(self)
        
    def launchUsers(self):
        self.userWindow = UsersWindow(self)
        
    def getStageDict(self):
        self.stageDict = {}
        stages = self.settings["Stage"].split(",")
        for stage in stages:
            key,value = stage.split("-")
            self.stageDict[key.strip()] = value.strip()
        print(self.stageDict)
        
    def getNameList(self):
        command = "Select NAME from USER where STATUS ='Active'"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        for result in results:
            self.nameList.append(result[0])
        #print(self.nameList)
        
    def search(self):
        if self.line_search.text()!="":
            search = self.line_search.text()
            matches = []
            self.cursor.execute(f"Select ECN_ID from ECN where ECN_TITLE like '%{search}%' OR ECN_REASON like '%{search}%' OR ECN_SUMMARY like '%{search}%'")
            results = self.cursor.fetchall()
            for result in results:
                if result[0] not in matches:
                    matches.append(result[0])
            self.cursor.execute(f"Select ECN_ID from ATTACHMENTS where FILENAME like '%{search}%'")
            results = self.cursor.fetchall()
            for result in results:
                if result[0] not in matches:
                    matches.append(result[0])
            self.cursor.execute(f"Select ECN_ID from PARTS where PART_ID like '%{search}%' OR DESC like '%{search}%'")
            results = self.cursor.fetchall()
            for result in results:
                if result[0] not in matches:
                    matches.append(result[0])
            self.searchResult = SearchResults(self,matches)

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
