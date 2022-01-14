from PySide6 import QtGui, QtCore, QtWidgets
from MyTableWidget import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import sqlite3
import os
import sys
import smtplib

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
        self.windowWidth = 650
        self.windowHeight = 450
        self.programLoc = program_location
        self.userList={}
        self.settings = {}
        self.startUpCheck()
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
            for line in f:
                key,value = line.split(" : ")
                self.settings[key]=value.strip()
            print(self.settings)
            f.close()
            self.db = sqlite3.connect(self.settings["DB_LOC"])
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
                self.generateECNX(result[0])
                if result['TYPE']=="Rejected":
                    self.rejectNotification(result[0])
                elif result['TYPE']=="Completed":
                    self.completionNotification(result[0])
                else:
                    self.releaseNotification(result[0])
                self.updateStatus(result[0])
                self.removeECNX(result[0])
        self.repopulateTable()
                
    def updateStatus(self,ecn_id):
        data = ("Sent",ecn_id)
        self.cursor.execute("UPDATE NOTIFICATION SET STATUS = ? WHERE ECN_ID = ?",(data))
        self.db.commit()
        
    def rejectNotification(self,ecn_id):
        self.cursor.execute(f"select Author from ECN where ECN_ID='{ecn_id}'")
        result = self.cursor.fetchone()
        message = f"{ecn_id} has been rejected, please check comments and update accordingly and releasing again.\n\n\nYou can also open the attachment file to launch to be directed to the ECN."
        receivers = [self.userList[result[0]]]
        print(f"send email to these addresses: {receivers} for rejection")
        self.sendEmail(ecn_id,receivers, message)
        
        
    def completionNotification(self,ecn_id):
        receivers = []
        self.cursor.execute(f"select Author from ECN where ECN_ID='{ecn_id}'")
        result = self.cursor.fetchone()
        receivers.append(self.userList[result[0]])
        self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn_id}'")
        results = self.cursor.fetchall()
        message = f"{ecn_id} has been completed! You can now view it in the completed tab.\n\n\nYou can also open the attachment file to launch to be directed to the ECN."
        for result in results:
            receivers.append(self.userList[result[0]])
        print(f"send email to these addresses: {receivers} notifying ecn completion")
        self.sendEmail(ecn_id,receivers, message)
        
    def releaseNotification(self,ecn_id):
        self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn_id}'")
        results = self.cursor.fetchall()
        receivers = []
        message = f"{ecn_id} has been released! You can see it in the myQueueTab. Please review and approve.\n\n\nYou can also open the attachment file to launch to be directed to the ECN."
        for result in results:
            receivers.append(self.userList[result[0]])
        print(f"send email these addresses: {receivers} notifying ecn release")
        self.sendEmail(ecn_id,receivers, message)
            
    def sendEmail(self,ecn_id,receivers,message):
        with smtplib.SMTP(self.settings["SMTP"],self.settings["port"]) as server:
            
            msg = MIMEMultipart()
            msg['From'] = self.settings["From_Address"]
            msg['To'] = ", ".join(receivers)
            msg['Subject']=f"Notification for ECN: {ecn_id}"
            msg.attach(MIMEText(message,'plain'))
            ecnx = os.path.join(program_location,ecn_id+'.ecnx')
            filename = f'{ecn_id}.ecnx'
            attach_file = open(ecnx,'rb')
            payload = MIMEBase('application', 'octet-stream')
            payload.set_payload(attach_file.read())
            encoders.encode_base64(payload)
            #print(ecnx, filename)
            payload.add_header('Content-Disposition','attachment',filename = filename)
            msg.attach(payload)
            server.sendmail(self.settings["From_Address"], receivers, msg.as_string())
            print(f"Successfully sent email to {receivers}")
            
    def generateECNX(self,ecn_id):
        ecnx = os.path.join(program_location,ecn_id+'.ecnx')
        f = open(ecnx,"w+")
        f.write(f"{ecn_id}")
        f.close()
        
    def removeECNX(eslf,ecn_id):
        ecnx = os.path.join(program_location,ecn_id+'.ecnx')
        os.remove(ecnx)
            
            
def main():
    app = QtWidgets.QApplication(sys.argv)
    notifier = Notifier()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()