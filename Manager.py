import os
import re
import sys
import time
import sqlite3
from PySide6 import QtGui, QtCore, QtWidgets
from LoginWindow import *
#from CompletedTab import *
#from MyECNTab import *
#from MyQueueTab import *
from datetime import datetime
from ECNWindow import *
from DataBaseUpdateWindow import *
from NewDBWindow import *
from UsersWindow import *
from Hook import *
from SearchResults import *
from SettingsWindow import *
from Analytics import *
from Delegates import *
from Visual import *


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
icon = os.path.join(program_location,"icons","manager.ico")

databaseRequirements = {"ECN": ["ECN_ID TEXT", "ECN_TYPE TEXT", "ECN_TITLE TEXT", "ECN_REASON TEXT","REQUESTOR TEXT" ,"AUTHOR TEXT", "STATUS TEXT", "COMP_DATE DATE", "ECN_SUMMARY TEXT", "LAST_CHANGE_DATE DATE"],
                        "COMMENT": ["ECN_ID TEXT", "USER TEXT", "COMM_DATE DATE", "COMMENT TEXT"],
                        "USER": ["USER_ID TEXT", "PASSWORD TEXT", "NAME TEXT", "ROLE TEXT", "JOB_TITLE TEXT", "STATUS TEXT"],
                        "CHANGELOG": ["ECN_ID TEXT", "CHANGEDATE DATETIME", "NAME TEXT","DATABLOCK TEXT" ,"PREVDATA TEXT", "NEWDATA TEXT"],
                        }


class Manager(QtWidgets.QWidget):
    def __init__(self,ecn = None):
        super(Manager, self).__init__()
        self.windowWidth = 1000
        self.windowHeight = 600
        self.sorting = (0,QtCore.Qt.DescendingOrder)
        self.ecn = ecn
        self.firstInstance = True
        self.checkLockLoc()
        self.checkLockFile()
        self.generateLockFile()
        #self.checkNotifier()
        self.ico = QtGui.QIcon(icon)
        self.startUpCheck()
        self.getStageDict()
        self.getTitleStageDict()
        self.user_info = {}
        self.programLoc = program_location
        self.nameList = []
        user,pw,db = self.settings['Visual'].split(',')
        instant_Client = self.settings['Instant_Client']
        self.visual = Visual(self,user, pw , db,instant_Client)
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
        self.stage = self.stageDict[self.user_info["title"]]

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
        
        details_layout = QtWidgets.QHBoxLayout()
        self.label_ecn_count = QtWidgets.QLabel("ECNs:")
        self.label_open_ecns = QtWidgets.QLabel("Open:")
        self.label_wait_ecns = QtWidgets.QLabel("Waiting:")
        self.label_complete_ecns = QtWidgets.QLabel("Completed:")
        self.dropdown_type = QtWidgets.QComboBox(self)
        
        if self.user_info["role"]!="Engineer" and self.user_info['role']!="Admin":
            items = ["Queue","Open","Completed"]
        else:
            items = ["My ECNS","Queue","Open","Completed"]
        self.dropdown_type.addItems(items)
        details_layout.addWidget(self.label_ecn_count)
        details_layout.addWidget(self.label_open_ecns)
        details_layout.addWidget(self.label_wait_ecns)
        details_layout.addWidget(self.label_complete_ecns)
        details_layout.addWidget(self.dropdown_type)
        
        mainLayout.addLayout(details_layout)
        
        titles = ['ECN ID','Type', 'Title', 'Status', 'Last Modified', 'Stage','Waiting On', 'Elapsed Days']
        self.table = QtWidgets.QTableWidget(1,len(titles),self)
        delegate = AlignDelegate(self.table)
        self.table.setItemDelegate(delegate)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().sortIndicatorChanged.connect(self.setSort)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        #self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        header = self.table.horizontalHeader()
        for x in range(self.table.columnCount()):
            if x != 2 and x!=6:
                header.setSectionResizeMode(x,QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(x,QtWidgets.QHeaderView.Stretch)
        #self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.doubleClicked.connect(self.openECN)
        mainLayout.addWidget(self.table)
        
        self.dropdown_type.currentIndexChanged.connect(self.repopulateTable)
        
        self.button_open = QtWidgets.QPushButton("Open ECN")
        self.button_open.clicked.connect(self.openECN)
        self.button_add = QtWidgets.QPushButton("New ECN")
        self.button_add.clicked.connect(self.newECN)
        if self.user_info['role']=="Signer":
            self.button_add.setDisabled(True)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.button_open)
        hlayout.addWidget(self.button_add)
        mainLayout.addLayout(hlayout)

        mainLayout.setMenuBar(self.menubar)
        
        self.repopulateTable()

        # self.tabWidget = QtWidgets.QTabWidget(self)
        # mainLayout.addWidget(self.tabWidget)
        
        # if self.user_info["role"]!="Signer":
        #     self.myECNTab = MyECNTab(self)
        #     self.tabWidget.addTab(self.myECNTab, "My ECNs")

        # self.queueTab = MyQueueTab(self)
        # self.tabWidget.addTab(self.queueTab, "My Queue")

        # self.completedTab = CompletedTab(self)
        # self.tabWidget.addTab(self.completedTab, "Completed")

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.repopulateTable)
        timer.start(15000)
        
    def repopulateTable(self):
        self.getECNQty()
        self.table.clearContents()
        self.table.setRowCount(0)
        table_type = self.dropdown_type.currentText()
        if table_type=="My ECNS":
            command = "Select * from ECN where AUTHOR ='" + self.user_info['user'] + "' and STATUS !='Completed'"
        elif table_type=="Queue":
            command =f"Select * from SIGNATURE INNER JOIN ECN ON SIGNATURE.ECN_ID=ECN.ECN_ID WHERE ECN.STATUS='Out For Approval' and SIGNATURE.USER_ID='{self.user_info['user']}' and ECN.STAGE>={self.user_info['stage']} and SIGNATURE.SIGNED_DATE is NULL"
        elif table_type=="Open":
            command = "select * from ECN where STATUS!='Completed'"
        else:
            command = "select * from ECN where STATUS='Completed'"
        if table_type=="Completed":
            self.table.setHorizontalHeaderItem(7, QtWidgets.QTableWidgetItem("Days Taken"))
        else:
            self.table.setHorizontalHeaderItem(7, QtWidgets.QTableWidgetItem("Days Elapsed"))
        self.cursor.execute(command)
        test = self.cursor.fetchall()
        rowcount=0
        self.table.setRowCount(len(test))
        for item in test:
            self.table.setItem(rowcount,0,QtWidgets.QTableWidgetItem(item['ECN_ID']))
            self.table.setItem(rowcount,1,QtWidgets.QTableWidgetItem(item['ECN_TYPE']))
            self.table.setItem(rowcount,2,QtWidgets.QTableWidgetItem(item['ECN_TITLE']))
            self.table.setItem(rowcount,3,QtWidgets.QTableWidgetItem(item['STATUS']))
            self.table.setItem(rowcount,4,QtWidgets.QTableWidgetItem(item['LAST_MODIFIED']))
            if item['STATUS']!='Draft':
                self.table.setItem(rowcount, 5, QtWidgets.QTableWidgetItem(str(item['STAGE'])))
                if table_type!="Completed":
                    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    elapsed = self.getElapsedDays(today, item['FIRST_RELEASE'])
                    self.table.setItem(rowcount, 7, QtWidgets.QTableWidgetItem(str(round(elapsed.seconds/86400,2))))
                else:
                    self.table.setItem(rowcount, 7, QtWidgets.QTableWidgetItem(str(item["COMP_DAYS"])))
                if item['STAGE']!=0:
                    users = self.getWaitingUser(item['ECN_ID'], self.titleStageDict[str(item['STAGE'])])
                    self.table.setItem(rowcount, 6, QtWidgets.QTableWidgetItem(users))
            if item["STATUS"]=="Rejected":
                self.table.item(rowcount, 3).setBackground(QtGui.QColor(255,99,99))
            if item["STATUS"]=="Out For Approval":
                self.table.item(rowcount, 3).setBackground(QtGui.QColor(186,255,180))
            rowcount+=1
        self.table.sortItems(self.sorting[0],self.sorting[1])
        
    def setSort(self, index, order):
        self.sorting = (index,order)
        self.repopulateTable()
        
            
    def getTitleStageDict(self):
        self.titleStageDict = {}
        for key, value in self.stageDict.items():
            if value not in self.titleStageDict.keys():
                self.titleStageDict[value]=[key]
            else:
                self.titleStageDict[value].append(key)
                
    def getWaitingUser(self,ecn,titles):
        users = []
        usr_str = ""
        for title in titles:
            self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn}' and JOB_TITLE='{title}' and SIGNED_DATE is Null")
            result = self.cursor.fetchone()
            if result is not None:
                users.append(result[0])
        count = 0
        for user in users:
            usr_str += user
            if count<len(users)-1:
                usr_str+=","
            count+=1
        return usr_str
                
    def getECNQty(self):
        self.cursor.execute(f"SELECT COUNT(ECN_ID) from ECN where STATUS!='Completed'")
        result = self.cursor.fetchone()
        #print("open:",result[0])
        self.label_open_ecns.setText(f"Open: {result[0]}")
        self.cursor.execute(f"Select COUNT(ECN.ECN_ID) from SIGNATURE INNER JOIN ECN ON SIGNATURE.ECN_ID=ECN.ECN_ID WHERE ECN.STATUS='Out For Approval' and SIGNATURE.USER_ID='{self.user_info['user']}' and ECN.STAGE>={self.user_info['stage']} and SIGNATURE.SIGNED_DATE is NULL")
        result = self.cursor.fetchone()
        #print("queue:",result[0])
        if result[0]>0:
            self.label_wait_ecns.setStyleSheet("Color:red;font-weight:bold")
        else:
            self.label_wait_ecns.setStyleSheet("Color:green;font-weight:bold")
        self.label_wait_ecns.setText(f"Waiting: {result[0]}")
        self.cursor.execute(f"SELECT COUNT(ECN_ID) from ECN where STATUS='Completed'")
        result = self.cursor.fetchone()
        #print("complete:",result[0])
        self.label_complete_ecns.setText(f"Completed: {result[0]}")

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
        setting_menu=self.menubar.addMenu("&Setting")
        if self.user_info['role']=="Admin" or self.user_info['role']=='Manager':
            analyticsAction = QtGui.QAction("&Analytics",self)
            analyticsAction.triggered.connect(self.launchAnalytics)
            setting_menu.addAction(analyticsAction)

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def HookEcn(self,ecn_id=None):
        print("info received",ecn_id)
        self.ecnWindow = ECNWindow(self,ecn_id)
    
    def newECN(self):
        self.HookEcn()
        
    def openECN(self):
        row = self.table.currentRow()
        ecn_id=self.table.item(row,0).text()
        self.HookEcn(ecn_id)


    def loadInAnim(self):
        loc = self.table.pos()
        self.animation = QtCore.QPropertyAnimation(self.table, b"pos")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutBack)
        self.animation.setStartValue(QtCore.QPoint(
            self.table.pos().x(), -self.windowHeight))
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
        
    def launchAnalytics(self):
        self.analyticsWindow = AnalyticsWindow(self)
        
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
        
    def getElapsedDays(self,day1,day2):
        today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        day1 = datetime.strptime(day1,'%Y-%m-%d %H:%M:%S')
        day2 = datetime.strptime(day2,'%Y-%m-%d %H:%M:%S')
        if day2>day1:
            elapsed = day2 - day1
        else:
            elapsed = day1 - day2
        #return elapsed.days
        return elapsed
        
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
            
class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

# execute the program
def main():
    print(sys.argv)
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv)>1:
        manager=Manager(sys.argv[1])
    else:
        manager = Manager()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
