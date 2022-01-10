from PySide6 import QtGui, QtCore, QtWidgets
from MyTableWidget import *
import sqlite3
import os
import sys


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class Notifier(QtWidgets.QWidget):
    def __init__(self):
        super(Notifier, self).__init__()
        self.windowWidth = 1200
        self.windowHeight = 900
        self.startUpCheck()
        self.programLoc = program_location
        self.userList={}
        self.getUserList()
        self.initAtt()
        self.initUI()
        self.center()
        self.show()
        
        # self.checkDBTables()
        
    def initAtt(self):
        self.setGeometry(100, 50, self.windowWidth, self.windowHeight)
        self.setWindowTitle("Notifier")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def initUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        
        titles = ['ECN_ID','STATUS','TYPE']
        self.table = MyTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        mainLayout.addWidget(self.table)
        # mainLayout.setMenuBar(self.menubar)
        self.setLayout(mainLayout)
        self.repopulateTable()
        
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.sendNotification)
        timer.start(5000)
    
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
        
    def startUpCheck(self):
        if not os.path.exists(initfile):
            print("need to generate ini file")
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText("No database detected, please select an existing database or ask the admin to make a new one using the included tool.")
            openbutton = msgbox.addButton("Open DB", QtWidgets.QMessageBox.ActionRole)
            cancelbutton = msgbox.addButton(QtWidgets.QMessageBox.Close)
            ret = msgbox.exec()
            if msgbox.clickedButton() == openbutton:
                db_loc = QtWidgets.QFileDialog.getOpenFileName(self,self.tr("Open DB"),program_location,self.tr("DB Files (*.DB)"))[0]
                self.db = sqlite3.connect(db_loc)
                self.cursor = self.db.cursor()
                self.cursor.row_factory = sqlite3.Row
                #save setting
                if db_loc!="":
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
            
    def getUserList(self):
        self.cursor.execute("select USER_ID, EMAIL from USER where STATUS='Active'")
        results = self.cursor.fetchall()
        for result in results:
            self.userList[result[0]]=result[1]
        #print(self.userList)
            
    def repopulateTable(self):
        self.table.clearContents()
        command = "Select * from NOTIFICATION"
        self.cursor.execute(command)
        test = self.cursor.fetchall()
        rowcount=0
        self.table.setRowCount(len(test))
        for item in test:
            self.table.setItem(rowcount,0,QtWidgets.QTableWidgetItem(item['ECN_ID']))
            self.table.setItem(rowcount,1,QtWidgets.QTableWidgetItem(item['STATUS']))
            self.table.setItem(rowcount,2,QtWidgets.QTableWidgetItem(item['TYPE']))

            rowcount+=1
            
    def sendNotification(self):
        self.cursor.execute("Select * from NOTIFICATION where STATUS='Not Sent'")
        results = self.cursor.fetchall()
        
        if len(results)>0:
            for result in results:
                if result['TYPE']=="Rejected":
                    self.rejectNotification(result[0])
                elif result['TYPE']=="Completed":
                    self.completionNotification(result[0])
                else:
                    self.releaseNotification(result[0])
                self.updateStatus(result[0])
        self.repopulateTable()
                
    def updateStatus(self,ecn_id):
        data = ("Sent",ecn_id)
        # self.cursor.execute("UPDATE NOTIFICATION SET STATUS = ? WHERE ECN_ID = ?",(data))
        # self.db.commit()
        
    def rejectNotification(self,ecn_id):
        print(f"send notification to the author for ecn: {ecn_id}")
        self.cursor.execute(f"select Author from ECN where ECN_ID='{ecn_id}'")
        result = self.cursor.fetchone()
        print(f"send email to author -> user: {result[0]} @ email: {self.userList[result[0]]} for rejection")
        
        
    def completionNotification(self,ecn_id):
        print(f"send notification to author and all users on the signature block for ecn: {ecn_id}")
        self.cursor.execute(f"select Author from ECN where ECN_ID='{ecn_id}'")
        result = self.cursor.fetchone()
        print(f"send email to author -> user: {result[0]} @ email: {self.userList[result[0]]} for completion")
        self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn_id}'")
        results = self.cursor.fetchall()
        for result in results:
            print(f"send email to user: {result[0]} @ email: {self.userList[result[0]]} notifying ecn completion")
        
    def releaseNotification(self,ecn_id):
        print(f"send notification to all users on the signature block for ecn: {ecn_id}")
        self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn_id}'")
        results = self.cursor.fetchall()
        for result in results:
            print(f"send email to user: {result[0]} @ email: {self.userList[result[0]]} notifying ecn release")
            
def main():
    app = QtWidgets.QApplication(sys.argv)
    notifier = Notifier()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()