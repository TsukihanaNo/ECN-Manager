import os
import re
import sys
import time
import sqlite3
from PySide import QtGui, QtCore
from LoginWindow import *
from CompletedTab import *
from MyRequestTab import *
from MyQueueTab import *
from DataBaseUpdateWindow import *
from NewDBWindow import *


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

databaseRequirements = {"ECN": ["ECN_ID TEXT", "ECN_TYPE TEXT", "ECN_TITLE TEXT", "REQ_DETAILS TEXT", "REQUESTOR TEXT", "ASSIGNED_ENG TEXT", "STATUS TEXT", "REQ_DATE DATE", "ASSIGN_DATE DATE", "COMP_DATE DATE", "ENG_DETAILS TEXT"],
                        "COMMENT": ["ECN_ID TEXT", "USER TEXT", "COMM_DATE DATE", "COMMENT TEXT"],
                        "USER": ["USER_ID TEXT", "PASSWORD TEXT", "NAME TEXT", "ROLE TEXT", "JOB_TITLE TEXT"],
                        "CHANGELOG": ["ECN_ID TEXT", "CHANGEDATE DATETIME", "NAME TEXT", "PREVDATA TEXT", "NEWDATA TEXT"],
                        }


class Manager(QtGui.QWidget):
    def __init__(self):
        super(Manager, self).__init__()
        self.windowWidth = 800
        self.windowHeight = 500
        self.startUpCheck()
        self.user_info = {}

        # self.checkDBTables()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft() - QtCore.QPoint(0, 0))

    def loginDone(self):
        self.initAtt()
        self.initUI()
        self.center()
        self.show()
        self.loadInAnim()

    def startUpCheck(self):
        if not os.path.exists(initfile):
            print("need to generate ini file")
            msgbox = QtGui.QMessageBox(self)
            msgbox.setText("No database detected, please select an existing database or ask the admin to make a new one using the included tool.")
            openbutton = msgbox.addButton("Open DB", QtGui.QMessageBox.ActionRole)
            cancelbutton = msgbox.addButton(QtGui.QMessageBox.Close)
            ret = msgbox.exec_()
            if msgbox.clickedButton() == openbutton:
                db_loc = QtGui.QFileDialog.getOpenFileName(self,self.tr("Open DB"),program_location,self.tr("DB Files (*.DB)"))[0]
                self.db = sqlite3.connect(db_loc)
                self.cursor = self.db.cursor()
                self.cursor.row_factory = sqlite3.Row
                self.loginWindow = LoginWindow(self)
                #save setting
                f = open(initfile,"w+")
                f.write("DB_LOC : "+db_loc)
                f.close()
            else:
                exit()
        else:
            #read settings
            f = open(initfile,'r')
            settings = {}
            for line in f:
                key,value = line.split(" : ")
                settings[key]=value
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
        title = "Manager - User: " + self.user_info["user"]
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def initUI(self):
        self.menubar = QtGui.QMenuBar(self)
        mainLayout = QtGui.QVBoxLayout(self)
        mainLayout.setMenuBar(self.menubar)

        self.createMenuActions()

        # mainLayout.setMenuBar(self.menubar)
        self.tabWidget = QtGui.QTabWidget(self)

        self.myRequestTab = MyRequestTab(self)
        mainLayout.addWidget(self.tabWidget)

        self.tabWidget.addTab(self.myRequestTab, "My Requests")

        if self.user_info['role'] == "Engineer":
            self.queueTab = MyQueueTab(self)
            self.tabWidget.addTab(self.queueTab, "My Queue")

        self.completedTab = CompletedTab(self)
        self.tabWidget.addTab(self.completedTab, "Completed")

    def createMenuActions(self):
        filemenu = self.menubar.addMenu("&File")
        if self.user_info['role'] == "Admin":
            newDBAction = QtGui.QAction("&New Database", self)
            newDBAction.triggered.connect(self.newDB)
            connectDBAction = QtGui.QAction(
                "&Connect to existing Database", self)
            filemenu.addAction(newDBAction)
            filemenu.addAction(connectDBAction)
        exitAction = QtGui.QAction("&Exit", self)
        exitAction.triggered.connect(self.close)
        exitAction.setShortcut("CTRL+Q")
        filemenu.addAction(exitAction)

    def dispMsg(self,msg):
        msgbox = QtGui.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec_()


    def loadInAnim(self):
        loc = self.tabWidget.pos()
        self.animation = QtCore.QPropertyAnimation(self.tabWidget, "pos")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutBack)
        self.animation.setStartValue(QtCore.QPoint(
            self.tabWidget.pos().x(), -self.windowHeight))
        self.animation.setEndValue(QtCore.QPoint(loc))

        self.animation.start()

    def closeEvent(self, event):
        for w in QtGui.qApp.allWidgets():
            w.close()

    def newDB(self):
        self.newDBWindow = NewDBWindow(self)


# execute the program
def main():
    app = QtGui.QApplication(sys.argv)
    manager = Manager()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
