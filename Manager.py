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
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.ecnWindow = None
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
        #print("Visual" in self.settings.keys())
        if "Visual" in self.settings.keys():
            user,pw,db = self.settings['Visual'].split(',')
            ic = self.settings['Instant_Client']
            self.visual = Visual(self,user, pw , db,ic)
        else:
            self.visual = None
        #print(self.visual)
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
        
    def existsWindowsUser(self):
        user = os.getlogin()
        self.cursor.execute(f"SELECT * from WINDOWSLOG where USER='{user}'")
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True
        
    def logWindowsUser(self):
        user = os.getlogin()
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.existsWindowsUser():
            data = ("online",time,user)
            self.cursor.execute("UPDATE WINDOWSLOG SET STATUS = ?, DATETIME = ? WHERE USER = ?",(data))
        else:
            data = (user,"online",time)
            self.cursor.execute("INSERT INTO WINDOWSLOG(USER, STATUS, DATETIME) VALUES(?,?,?)",(data))
        self.db.commit()
        
    def logOutWindowsUser(self):
        #print("logging user out")
        user = os.getlogin()
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = ("offline",time,user)
        self.cursor.execute("UPDATE WINDOWSLOG SET STATUS = ?, DATETIME = ? WHERE USER = ?",(data))
        self.db.commit()
        
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
                self.logWindowsUser()
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
            self.logWindowsUser()
            self.loginWindow = LoginWindow(self)
            
            
    def loadSettings(self):
        f = open(initfile,'r')
        self.settings = {}
        for line in f:
            key,value = line.split(" : ")
            self.settings[key]=value.strip()
        #print(self.settings)
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
        self.toolbar = QtWidgets.QToolBar()
        self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.setSizeGripEnabled(False)
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setMenuBar(self.menubar)
        mainLayout.addWidget(self.toolbar)

        self.createMenuActions()
        searchLayout = QtWidgets.QHBoxLayout()
        self.line_search = QtWidgets.QLineEdit(self)
        self.line_search.setPlaceholderText("Search here")
        self.button_search = QtWidgets.QPushButton("Search")
        icon_loc = icon = os.path.join(program_location,"icons","search.png")
        self.button_search.setIcon(QtGui.QIcon(icon_loc))
        #self.button_search.setFixedWidth(25)
        self.line_search.returnPressed.connect(self.search)
        self.button_search.clicked.connect(self.search)
        #searchLayout.addWidget(self.line_search)
        #searchLayout.addWidget(self.button_search)
        #mainLayout.addLayout(searchLayout)
        
        self.label_ecn_count = QtWidgets.QLabel("ECN Count:")
        self.label_open_ecns = QtWidgets.QLabel("Open - ")
        self.label_wait_ecns = QtWidgets.QLabel("Waiting - ")
        self.label_complete_ecns = QtWidgets.QLabel("Completed - ")
        self.dropdown_type = QtWidgets.QComboBox(self)
        self.dropdown_type.setFixedWidth(100)
        self.button_refresh = QtWidgets.QPushButton("Refresh")
        #self.button_refresh.setToolTip("Refresh")
        icon_loc = icon = os.path.join(program_location,"icons","refresh.png")
        self.button_refresh.setIcon(QtGui.QIcon(icon_loc))
        #self.button_refresh.setFixedWidth(25)
        self.button_refresh.clicked.connect(self.repopulateTable)
        
        if self.user_info["role"]!="Engineer" and self.user_info['role']!="Admin":
            items = ["Queue","Open","Completed"]
        else:
            items = ["My ECNS","Queue","Open","Completed"]
        self.dropdown_type.addItems(items)
        
        self.button_open = QtWidgets.QPushButton("Open")
        self.button_open.setEnabled(False)
        #self.button_open.setToolTip("Open ECN")
        icon_loc = icon = os.path.join(program_location,"icons","open.png")
        self.button_open.setIcon(QtGui.QIcon(icon_loc))
        #self.button_open.setFixedWidth(25)
        self.button_open.clicked.connect(self.openECN)
        self.button_add = QtWidgets.QPushButton("New")
        #self.button_add.setToolTip("New ECN")
        #self.button_add.setFixedWidth(25)
        icon_loc = icon = os.path.join(program_location,"icons","new.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.newECN)
        if self.user_info['role']=="Signer":
            self.button_add.setDisabled(True)
            
        self.statusbar.addPermanentWidget(self.label_ecn_count)
        self.statusbar.addPermanentWidget(self.label_open_ecns)
        self.statusbar.addPermanentWidget(self.label_complete_ecns)
        self.statusbar.addPermanentWidget(self.label_wait_ecns)

        self.toolbar.addWidget(self.line_search)
        self.toolbar.addWidget(self.button_search)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_open)
        self.toolbar.addWidget(self.button_refresh)
        self.toolbar.addWidget(self.dropdown_type)
        
        self.ecns = QtWidgets.QListView()
        self.ecns.setStyleSheet("QListView{background-color:#f0f0f0}")
        self.ecns.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ecns.setResizeMode(QtWidgets.QListView.Adjust)
        self.ecns.setItemDelegate(ECNDelegate())
        self.ecns.doubleClicked.connect(self.openECN)
        
        
        self.model = ECNModel()
        self.ecns.setModel(self.model)
        
        self.ecns.selectionModel().selectionChanged.connect(self.onRowSelect)
        
        mainLayout.addWidget(self.ecns)
        
        mainLayout.addWidget(self.statusbar)
        
        self.dropdown_type.currentIndexChanged.connect(self.repopulateTable)
        
        self.ecns.verticalScrollBar().valueChanged.connect(self.loadMoreTable)
        
        mainLayout.setMenuBar(self.menubar)
        
        self.repopulateTable()
    
    def onRowSelect(self):
        self.button_open.setEnabled(bool(self.ecns.selectionModel().selectedIndexes()))

        
    def repopulateTable(self):
        self.getECNQty()
        self.model.clear_ecns()
        if self.ecns.verticalScrollBar().value()>0:
            self.ecns.verticalScrollBar().setValue(0)
        table_type = self.dropdown_type.currentText()
        if table_type=="My ECNS":
            command = "Select * from ECN where AUTHOR ='" + self.user_info['user'] + "' and STATUS !='Completed'"
        elif table_type=="Queue":
            command =f"Select * from SIGNATURE INNER JOIN ECN ON SIGNATURE.ECN_ID=ECN.ECN_ID WHERE ECN.STATUS='Out For Approval' and SIGNATURE.USER_ID='{self.user_info['user']}' and ECN.STAGE>={self.user_info['stage']} and SIGNATURE.SIGNED_DATE is NULL and SIGNATURE.TYPE='Signing'"
        elif table_type=="Open":
            command = "select * from ECN where STATUS!='Completed'"
        else:
            command = "select * from ECN where STATUS='Completed'"

        self.cursor.execute(command)
        self.table_data = self.cursor.fetchall()
        data_size = len(self.table_data)
        if data_size>10:
            counter = 10
        else:
            counter = data_size
        for x in range(counter):
            if self.table_data[x]['STAGE']!=0 and self.table_data[x]['STAGE'] is not None:
                users = self.getWaitingUser(self.table_data[x]['ECN_ID'], self.titleStageDict[str(self.table_data[x]['STAGE'])])
            else:
                users = ""
            if table_type!="Completed":
                if self.table_data[x]['STATUS']!="Draft":
                    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    elapsed = self.getElapsedDays(today, self.table_data[x]['FIRST_RELEASE'])
                    elapsed_days = "{:.2f}".format(elapsed.days + round(elapsed.seconds/86400,2))
                else:
                    elapsed_days =""
            else:
                elapsed_days = str(self.table_data[x]["COMP_DAYS"])
                
            self.cursor.execute(f"SELECT COUNT(COMMENT) from COMMENTS where ECN_ID='{self.table_data[x]['ECN_ID']}'")
            comment_count = self.cursor.fetchone()
            if comment_count[0]>0:
                comment_count = str(comment_count[0])
            else:
                comment_count=""
            if self.table_data[x]['STAGE'] is not None:
                status = self.table_data[x]['STAGE']
            else:
                status = ""
            self.model.add_ecn(self.table_data[x]['ECN_ID'], self.table_data[x]['ECN_TITLE'], self.table_data[x]['ECN_TYPE'], self.table_data[x]['STATUS'],self.table_data[x]['LAST_MODIFIED'], status, users, elapsed_days, comment_count)
        self.statusbar.showMessage(f"Showing {counter} of {data_size}")

    def loadMoreTable(self):
        percent = self.ecns.verticalScrollBar().value()/self.ecns.verticalScrollBar().maximum()
        rowcount = self.rowCount()
        total_count= len(self.table_data)
        table_type = self.dropdown_type.currentText()
        offset = 10
        #print(rowcount,percent)
        if percent> 0.90 and rowcount<total_count:
            diff = total_count - rowcount
            if diff>offset:
                counter = 10
            else:
                counter = diff
            for x in range(counter):
                x = x + offset
                if self.table_data[x]['STAGE']!=0 and self.table_data[x]['STAGE'] is not None:
                    users = self.getWaitingUser(self.table_data[x]['ECN_ID'], self.titleStageDict[str(self.table_data[x]['STAGE'])])
                else:
                    users = ""
                if table_type!="Completed":
                    if self.table_data[x]['STATUS']!="Draft":
                        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        elapsed = self.getElapsedDays(today, self.table_data[x]['FIRST_RELEASE'])
                        elapsed_days = "{:.2f}".format(elapsed.days + round(elapsed.seconds/86400,2))
                    else:
                        elapsed_days =""
                else:
                    elapsed_days = str(self.table_data[x]["COMP_DAYS"])
                    
                self.cursor.execute(f"SELECT COUNT(COMMENT) from COMMENTS where ECN_ID='{self.table_data[x]['ECN_ID']}'")
                comment_count = self.cursor.fetchone()
                if comment_count[0]>0:
                    comment_count = str(comment_count[0])
                else:
                    comment_count=""
                if self.table_data[x]['STAGE'] is not None:
                    status = self.table_data[x]['STAGE']
                else:
                    status = ""
                self.model.add_ecn(self.table_data[x]['ECN_ID'], self.table_data[x]['ECN_TITLE'], self.table_data[x]['ECN_TYPE'], self.table_data[x]['STATUS'],self.table_data[x]['LAST_MODIFIED'], status, users, elapsed_days, comment_count)
            self.statusbar.showMessage(f"Showing {rowcount+counter} of {total_count}")
            
    def rowCount(self):
        return self.model.rowCount(self.ecns)
        
    def setSort(self, index, order):
        self.sorting = (index,order)
        self.table.sortItems(self.sorting[0],self.sorting[1])
        
            
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
        #print(titles)
        for title in titles:
            self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn}' and JOB_TITLE='{title}' and SIGNED_DATE is Null and TYPE='Signing'")
            results = self.cursor.fetchall()
            for result in results:
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
        self.label_open_ecns.setText(f"Open - {result[0]}")
        self.cursor.execute(f"Select COUNT(ECN.ECN_ID) from SIGNATURE INNER JOIN ECN ON SIGNATURE.ECN_ID=ECN.ECN_ID WHERE ECN.STATUS='Out For Approval' and SIGNATURE.USER_ID='{self.user_info['user']}' and ECN.STAGE={self.user_info['stage']} and SIGNATURE.SIGNED_DATE is NULL")
        result = self.cursor.fetchone()
        #print("queue:",result[0])
        if result[0]>0:
            self.label_wait_ecns.setStyleSheet("Color:red;font-weight:bold")
        else:
            self.label_wait_ecns.setStyleSheet("Color:green;font-weight:bold")
        self.label_wait_ecns.setText(f"Waiting - {result[0]}")
        self.cursor.execute(f"SELECT COUNT(ECN_ID) from ECN where STATUS='Completed'")
        result = self.cursor.fetchone()
        #print("complete:",result[0])
        self.label_complete_ecns.setText(f"Completed - {result[0]}")

    def createMenuActions(self):
        filemenu = self.menubar.addMenu("&File")
        if self.user_info['role'] == "Admin":
            newDBAction = QtGui.QAction("&New Database", self)
            newDBAction.triggered.connect(self.newDB)
            connectDBAction = QtGui.QAction(
                "&Connect to existing Database", self)
            filemenu.addAction(newDBAction)
            filemenu.addAction(connectDBAction)
        if self.user_info['role']=="Admin" or self.user_info['role']=='Manager':
            filemenu.addSeparator()
            analyticsAction = QtGui.QAction("&Launch Analytics",self)
            analyticsAction.triggered.connect(self.launchAnalytics)
            filemenu.addAction(analyticsAction)
        exitAction = QtGui.QAction("&Exit", self)
        exitAction.triggered.connect(self.close)
        exitAction.setShortcut("CTRL+Q")
        filemenu.addAction(exitAction)
        setting_menu=self.menubar.addMenu("&Setting")
        if self.user_info['role']=='Admin':
            settingAction = QtGui.QAction("&Settings",self)
            settingAction.triggered.connect(self.launchSettings)
            setting_menu.addAction(settingAction)
            userAction = QtGui.QAction("&Users Window",self)
            userAction.triggered.connect(self.launchUsers)
            setting_menu.addAction(userAction)
        else:
            userAction = QtGui.QAction("&User Panel",self)
            userAction.triggered.connect(self.launchUser)
            setting_menu.addAction(userAction)
        

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def HookEcn(self,ecn_id=None):
        #print("info received",ecn_id)
        if self.ecnWindow is None:
            self.ecnWindow = ECNWindow(self,ecn_id)
        else:
            if self.ecnWindow.ecn_id !=ecn_id:
                self.ecnWindow.close()
                self.ecnWindow = ECNWindow(self,ecn_id)
            else:
                self.ecnWindow.activateWindow()
    
    def newECN(self):
        self.HookEcn()
        
    def openECN(self):
        index = self.ecns.currentIndex()
        ecn_id = index.data(QtCore.Qt.DisplayRole)[0]
        self.HookEcn(ecn_id)


    def loadInAnim(self):
        loc = self.ecns.pos()
        self.animation = QtCore.QPropertyAnimation(self.ecns, b"pos")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutBack)
        self.animation.setStartValue(QtCore.QPoint(
            -self.windowWidth, self.ecns.pos().y()))
        self.animation.setEndValue(QtCore.QPoint(loc))

        self.animation.start()

    def closeEvent(self, event):
        #print("setting things off")
        self.setUserOffline()
        self.logOutWindowsUser()
        self.db.close()
        if self.firstInstance:
            self.removeLockFile()
        for w in QtWidgets.QApplication.allWidgets():
            w.close()
            
    def setUserOffline(self):
        if 'user' in self.user_info.keys():
            self.cursor.execute(f"UPDATE USER SET SIGNED_IN ='N' where USER_ID='{self.user_info['user']}'")
            self.db.commit()

    def newDB(self):
        self.newDBWindow = NewDBWindow(self)

    def launchSettings(self):
        self.settingsWindow = SettingsWindow(self)
        
    def launchUsers(self):
        self.userWindow = UsersWindow(self)
        
    def launchAnalytics(self):
        self.analyticsWindow = AnalyticsWindow(self)
        
    def launchUser(self):
        self.userPanel = UserPanel(self,user=self.user_info['user'],func='user_edit')
        
    def getStageDict(self):
        self.stageDict = {}
        stages = self.settings["Stage"].split(",")
        for stage in stages:
            key,value = stage.split("-")
            self.stageDict[key.strip()] = value.strip()
        #print(self.stageDict)
        
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
        #print(day1, day2)
        if day2>day1:
            elapsed = day2 - day1
        else:
            elapsed = day1 - day2
        #return elapsed.days
        #print(elapsed)
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
        
PADDING = QtCore.QMargins(15, 2, 15, 2)

class ECNDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        
        ecn_id, title, ecn_type, status, last_modified, stage, waiting_on, elapsed_days, comment_count = index.model().data(index, QtCore.Qt.DisplayRole)
        
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
        
        
        if status !="Completed":
            rect = QtCore.QRect(r.topRight()+QtCore.QPoint(-150,2),QtCore.QSize(125,20))
            if status =="Out For Approval":
                color = QtGui.QColor("#CAFFBF")
            elif status =="Rejected":
                color = QtGui.QColor("#FFADAD")
            else:
                color = QtGui.QColor("#FDFFB6")
            painter.setBrush(color)
            painter.drawRoundedRect(rect, 5, 5)
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            painter.setPen(QtCore.Qt.black)
            painter.drawText(r.topRight()+QtCore.QPoint(-145,16),status)
        
        painter.setPen(lineMarkedPen)
        painter.drawLine(r.topLeft()+QtCore.QPoint(0,25),r.topRight()+QtCore.QPoint(0,25))

        
        text_offsetx1 = 15
        text_offsetx2 = r.width()/2+10
        
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1,20),ecn_id)
        if len(title)>75:
            title = title[:75] + "..."
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(r.topLeft()+QtCore.QPoint(175,20),title)
        font.setPointSize(10)
        font.setBold(False)
        painter.setFont(font)
        #ecn_id, title, ecn_type, status, last_modified, stage, waiting_on, elapsed_days, comment_count
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1,45),f"Type: {ecn_type}")
        painter.drawText(r.topLeft()+QtCore.QPoint(175,45),f"Last Modified: {last_modified}")
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1+375,45),f"Stage: {stage}")
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1+450,45),f"Elapsed: {elapsed_days}")
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1+550,45),f"💬: {comment_count}")
        if len(waiting_on)>25:
            waiting_on = waiting_on[:25] + "..."
        painter.drawText(r.topLeft()+QtCore.QPoint(text_offsetx1+610,45),f"Waiting On: {waiting_on}")
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,55)

class ECNModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(ECNModel, self).__init__(*args, **kwargs)
        self.ecns = []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.ecns[index.row()]

    def setData(self, index, role, value):
        self._size[index.row()]
        
    def rowCount(self, index):
        return len(self.ecns)
    
    def removeRow(self, row):
        del self.ecns[row]
        self.layoutChanged.emit()
        
    def get_ecn_data(self,row):
        return self.ecns[row]

    def clear_ecns(self):
        self.ecns = []
    
    def add_ecn(self, ecn_id, title, ecn_type, status, last_modified, stage, waiting_on, elapsed_days, comment_count):
        # Access the list via the model.
        self.ecns.append((ecn_id, title, ecn_type, status, last_modified, stage, waiting_on, elapsed_days, comment_count))
        # Trigger refresh.
        self.layoutChanged.emit()

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
