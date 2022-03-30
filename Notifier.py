from PySide6 import QtGui, QtCore, QtWidgets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
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
lockfile = os.path.join(program_location, "notifier.lock")

icon = os.path.join(program_location,"icons","notifier.ico")

class Notifier(QtWidgets.QWidget):
    def __init__(self):
        super(Notifier, self).__init__()
        self.windowWidth = 650
        self.windowHeight = 450
        self.programLoc = program_location
        self.firstInstance = True
        self.ico = QtGui.QIcon(icon)
        #self.checkLockFile()
        #self.generateLockFile()
        self.userList={}
        self.emailNameList = {}
        self.settings = {}
        self.startUpCheck()
        self.getUserList()
        self.getEmailNameDict()
        self.getStageDict()
        self.getTitleStageDict()
        self.initAtt()
        self.initUI()
        self.center()
        self.show()
        
        # self.checkDBTables()
        
    def initAtt(self):
        self.setWindowIcon(self.ico)
        self.setGeometry(100, 50, self.windowWidth, self.windowHeight)
        self.setWindowTitle("Notifier")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def initUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        
        titles = ['ECN_ID','STATUS','TYPE']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        self.log_text = QtWidgets.QTextEdit()
        
        self.button_refresh = QtWidgets.QPushButton("Refresh")
        self.button_refresh.clicked.connect(self.repopulateTable)
        
        mainLayout.addWidget(self.table)
        mainLayout.addWidget(self.log_text)
        mainLayout.addWidget(self.button_refresh)
        # mainLayout.setMenuBar(self.menubar)
        self.setLayout(mainLayout)
        self.repopulateTable()
        self.recurringTask()
        
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.recurringTask)
        timer.start(60000)
    
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
        
    def recurringTask(self):
        if len(self.log_text.toPlainText())>10000:
            self.log_text.clear()
        now  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.append(f"{now}: checking for standard and lateness notifications")
        self.checkForReminder()
        self.sendNotification()
        
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
            
    def getUserList(self):
        self.cursor.execute("select USER_ID, EMAIL from USER where STATUS='Active'")
        results = self.cursor.fetchall()
        for result in results:
            self.userList[result[0]]=result[1]
        #print(self.userList)
        
    def getEmailNameDict(self):
        self.cursor.execute("select EMAIL, NAME from USER where STATUS='Active'")
        results = self.cursor.fetchall()
        for result in results:
            self.emailNameList[result[0]]=result[1]
            
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
            
    def getWaitingUser(self,ecn,titles):
        users = []
        usr_str = ""
        for title in titles:
            self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn}' and JOB_TITLE='{title}' and SIGNED_DATE is Null and TYPE='Signing'")
            results = self.cursor.fetchall()
            for result in results:
                if result is not None:
                    users.append(result[0])
        return users
    
    def getTitleStageDict(self):
        self.titleStageDict = {}
        for key, value in self.stageDict.items():
            if value not in self.titleStageDict.keys():
                self.titleStageDict[value]=[key]
            else:
                self.titleStageDict[value].append(key)
                
    def getStageDict(self):
        self.stageDict = {}
        stages = self.settings["Stage"].split(",")
        for stage in stages:
            key,value = stage.split("-")
            self.stageDict[key.strip()] = value.strip()
            
    def sendNotification(self):
        self.cursor.execute("Select * from NOTIFICATION where STATUS='Not Sent'")
        results = self.cursor.fetchall()
        
        if len(results)>0:
            for result in results:
                self.generateECNX(result[0])
                if result['TYPE']=="Rejected To Author":
                    self.rejectNotification(result[0])
                elif result['TYPE']=="Rejected To Signer":
                    self.rejectSignerNotification(result[0],result['USERS'])
                elif result['TYPE']=="Completed":
                    self.completionNotification(result[0])
                elif result['TYPE']=="Stage Moved":
                    self.stageReleaseNotification(result[0])
                else:
                    self.releaseNotification(result[0])
                self.removeECNX(result[0])
                self.updateStatus(result[0])
        else:
            self.log_text.append("-No notifications found to be sent")
        self.repopulateTable()
                
    def updateStatus(self,ecn_id):
        self.log_text.append("-updating status")
        data = ("Sent",ecn_id)
        self.cursor.execute("UPDATE NOTIFICATION SET STATUS = ? WHERE ECN_ID = ?",(data))
        self.db.commit()
        now  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (now,ecn_id)
        self.cursor.execute("UPDATE ECN SET LAST_NOTIFIED = ? WHERE ECN_ID = ?",(data))
        self.db.commit()
        self.log_text.append("-status updated")
        
    def rejectNotification(self,ecn_id):
        receivers = []
        self.cursor.execute(f"select Author from ECN where ECN_ID='{ecn_id}'")
        result = self.cursor.fetchone()
        receivers.append(self.userList[result[0]])
        self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn_id}' and TYPE='Signing'")
        results = self.cursor.fetchall()
        for result in results:
            receivers.append(self.userList[result[0]])
        message = f"{ecn_id} has been rejected to the author! All Signatures have been removed and the ECN approval will start from the beginning once the ECN is released again.\n\n\nYou can also open the attachment file to launch to be directed to the ECN."
        print(f"send email to these addresses: {receivers} notifying ecn rejection")
        self.sendEmail(ecn_id,receivers, message,"Rejection")
        self.log_text.append(f"-Rejection Email sent for {ecn_id} to {receivers}")
        
    
    def rejectSignerNotification(self,ecn_id,users):
        receivers = users.split(',')
        message = f"{ecn_id} has been rejected to user: {receivers[0]}. Signatures for the following users has been removed: {users}.\n\n\nYou can open the attachment file to be directed to the ECN."
        print(f"send email to these addresses: {receivers} notifying ecn completion")
        self.sendEmail(ecn_id,receivers, message,"Rejection")
        self.log_text.append(f"-Rejection to Signer Email sent for {ecn_id} to {receivers}")
        
    
    def completionNotification(self,ecn_id):
        receivers = []
        self.cursor.execute(f"select Author from ECN where ECN_ID='{ecn_id}'")
        result = self.cursor.fetchone()
        receivers.append(self.userList[result[0]])
        self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn_id}'")
        results = self.cursor.fetchall()
        message = f"{ecn_id} has been completed!\n\n\n You can now view it in the completed section of your viewer.\n\n\nYou can also open the attachment file to launch to be directed to the ECN."
        for result in results:
            receivers.append(self.userList[result[0]])
        print(f"send email to these addresses: {receivers} notifying ecn completion")
        self.sendEmail(ecn_id,receivers, message,"Completion")
        self.log_text.append(f"-Completion Email sent for {ecn_id} to {receivers}")
        
    def releaseNotification(self,ecn_id):
        self.cursor.execute(f"select USER_ID from SIGNATURE where ECN_ID='{ecn_id}' and TYPE='Signing'")
        results = self.cursor.fetchall()
        receivers = []
        message = f"{ecn_id} has been released! You can see it in the queue section once it is your turn for approval. Otherwise you can view the ECN in the open section.\n\n\nYou can also open the attachment file to launch to be directed to the ECN."
        for result in results:
            receivers.append(self.userList[result[0]])
        print(f"send email these addresses: {receivers} notifying ecn release")
        self.sendEmail(ecn_id,receivers, message)
        self.log_text.append(f"-Release Email sent for {ecn_id} to {receivers}")
        
    def stageReleaseNotification(self,ecn_id):
        #get stage
        self.cursor.execute(f"Select Stage from ECN where ECN_ID='{ecn_id}'")
        result = self.cursor.fetchone()
        stage = result[0]
        users = self.getWaitingUser(ecn_id, self.titleStageDict[str(stage)])
        receivers = []
        for user in users:
            receivers.append(self.userList[user])
        message = f"{ecn_id} has been released and is now awaiting for your approval!\n\n\n. You can view the ECN your queue in the ECN Manager application.\n\n\nYou can also open the attachment file to launch to be directed to the ECN."
        print(f"send email these addresses: {receivers} notifying ecn release stage move")
        self.sendEmail(ecn_id,receivers, message,"Awaiting Approval")
        self.log_text.append(f"-Stage Release Email sent for {ecn_id} to {receivers}")
            
    def sendEmail(self,ecn_id,receivers,message,subject):
        with smtplib.SMTP(self.settings["SMTP"],self.settings["Port"]) as server:
            msg = MIMEMultipart()
            msg['From'] = self.settings["From_Address"]
            msg['To'] = ", ".join(receivers)
            msg['Subject']=f"{subject} Notification for ECN: {ecn_id}"
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
            #print(f"Successfully sent email to {receivers}")
            
    def generateECNX(self,ecn_id):
        self.log_text.append("-generating ecnx file")
        ecnx = os.path.join(program_location,ecn_id+'.ecnx')
        f = open(ecnx,"w+")
        f.write(f"{ecn_id}")
        f.close()
        self.log_text.append("-ecnx file generated")
        
    def removeECNX(self,ecn_id):
        self.log_text.append("-removing ecnx file")
        ecnx = os.path.join(program_location,ecn_id+'.ecnx')
        os.remove(ecnx)
        self.log_text.append("-ecnx file removed")
        
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
    
    def checkForReminder(self):
        self.cursor.execute("SELECT ECN_ID, LAST_NOTIFIED, FIRST_RELEASE, LAST_MODIFIED FROM ECN WHERE STATUS !='Completed' and STATUS!='Draft'")
        results = self.cursor.fetchall()
        today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for result in results:
            if result['LAST_NOTIFIED'] is not None:
                elapsed = self.getElapsedDays(today, result["LAST_NOTIFIED"])
                print(elapsed.days)
            else:
                elapsed = self.getElapsedDays(today, result["FIRST_RELEASE"])
                print(elapsed.days)
            if elapsed.days >= int(self.settings['Reminder_Days']):
                ecn_id = result["ECN_ID"]
                first_release = result["FIRST_RELEASE"]
                direct_receivers = []
                secondary_receivers = []
                self.cursor.execute(f"Select Stage from ECN where ECN_ID='{ecn_id}'")
                result = self.cursor.fetchone()
                stage = result[0]
                users = self.getWaitingUser(ecn_id, self.titleStageDict[str(stage)])
                for user in users:
                    direct_receivers.append(self.userList[user])
                users = self.getWaitingUser(ecn_id, self.titleStageDict[str(self.settings['Reminder_Stages'])])
                for user in users:
                    secondary_receivers.append(self.userList[user])
                total_days = self.getElapsedDays(today, first_release)
                self.lateReminder(ecn_id,direct_receivers,secondary_receivers, total_days)


    def setElapsedDays(self):
        self.cursor.execute(f"Select ECN_ID, FIRST_RELEASE, LAST_STATUS from ECN where STATUS!='Completed'")
        results = self.cursor.fetchall()
        for result in results:
            today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ecn = result[0]
            first_release = datetime.strptime(result[1],'%Y-%m-%d %H:%M:%S')
            last_status = datetime.strptime(result[2],'%Y-%m-%d %H:%M:%S')
            release_elapse = today - first_release
            status_elapse = today - last_status
            self.cursor.execute(f"UPDATE ECN SET RELEASE_ELAPSE ='{release_elapse.day}', STATUS_ELAPSE='{status_elapse.day}' WHERE ECN_ID='{ecn}'")
        self.db.commit()

    def lateReminder(self,ecn_id,direct_receivers,secondary_receivers,total_days):
        today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        reminder_days = self.settings['Reminder_Days']
        direct = []
        for email in direct_receivers:
            direct.append(self.emailNameList[email])
        direct = ",".join(direct)
        message = f"Hello {direct}:\n{ecn_id} has been out for {total_days} and has not moved for {reminder_days} days or more since the last notification has been sent.\n Please work on it at your earlier availability!\n\n You can view the ECN your queue in the ECN Manager application.\n\nYou can also open the attachment file to launch to be directed to the ECN."
        #print(message)
        #print(f"send email these addresses: {receivers} notifying ecn lateness")
        self.generateECNX(ecn_id)
        receivers = []
        for user in direct_receivers:
            receivers.append(user)
        for user in secondary_receivers:
            receivers.append(user)
        self.sendEmail(ecn_id,receivers, message,"Reminder")
        data = (ecn_id,"Sent","Reminder")
        self.cursor.execute("INSERT INTO NOTIFICATION(ECN_ID, STATUS, TYPE) VALUES(?,?,?)",(data))
        self.cursor.execute(f"UPDATE ECN SET LAST_NOTIFIED='{today}' WHERE ECN_ID='{ecn_id}'")
        self.db.commit()
        self.log_text.append(f"-lateness Email sent for {ecn_id} to {receivers}")
        self.removeECNX(ecn_id)

    def getReminderUsers(self):
        self.cursor.execute(f"select USER_ID from SIGNATURE where SIGNED_DATE is NULL")
        results = self.cursor.fetchall()
        receivers = []
        for result in results:
            receivers.append(self.userList(result[0]))
        return receivers
    
    def closeEvent(self, event):
        self.db.close()
        # if self.firstInstance:
        #     self.removeLockFile()

            
def main():
    app = QtWidgets.QApplication(sys.argv)
    notifier = Notifier()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()