from PySide6 import QtGui, QtCore, QtWidgets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from string import Template
from WebView import *
from Visual import *
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
os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = "1"

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
        self.getStageDictPCN()
        self.getStageDictPRQ()
        self.getTitleStageDict()
        self.getTitleStageDictPCN()
        self.getTitleStageDictPRQ()
        if "Visual" in self.settings.keys():
            user,pw,db = self.settings['Visual'].split(',')
            ic = self.settings['Instant_Client']
            self.visual = Visual(self,user, pw , db,ic)
        else:
            self.visual = None
        self.initAtt()
        self.initUI()
        self.center()
        self.show()
        self.startTask()
        
        # self.checkDBTables()
        
    def initAtt(self):
        self.setWindowIcon(self.ico)
        self.setGeometry(100, 50, self.windowWidth, self.windowHeight)
        self.setWindowTitle("Notifier")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def initUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        
        titles = ['DOC_ID','STATUS','TYPE']
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
        self.repopulateTable()
    
    def startTask(self):
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
            #print(self.settings)
            f.close()
            self.db = sqlite3.connect(self.settings["DB_LOC"])
            self.cursor = self.db.cursor()
            self.cursor.row_factory = sqlite3.Row
            
    # def checkLockFile(self):
    #     if os.path.exists(lockfile):
    #         self.dispMsg("Another Instance is already open.")
    #         self.firstInstance = False
    #         sys.exit()
        
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
            self.emailNameList[result[0]]=result[1].split(" ")[0]
            
    def repopulateTable(self):
        self.table.clearContents()
        command = "Select * from NOTIFICATION"
        self.cursor.execute(command)
        test = self.cursor.fetchall()
        rowcount=0
        self.table.setRowCount(len(test))
        for item in test:
            self.table.setItem(rowcount,0,QtWidgets.QTableWidgetItem(item['DOC_ID']))
            self.table.setItem(rowcount,1,QtWidgets.QTableWidgetItem(item['STATUS']))
            self.table.setItem(rowcount,2,QtWidgets.QTableWidgetItem(item['TYPE']))

            rowcount+=1
            
    def getWaitingUser(self,ecn,titles):
        users = []
        usr_str = ""
        for title in titles:
            self.cursor.execute(f"select USER_ID from SIGNATURE where DOC_ID='{ecn}' and JOB_TITLE='{title}' and SIGNED_DATE is Null and TYPE='Signing'")
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
                
    def getTitleStageDictPCN(self):
        self.titleStageDictPCN = {}
        for key, value in self.stageDictPCN.items():
            if value not in self.titleStageDictPCN.keys():
                self.titleStageDictPCN[value]=[key]
            else:
                self.titleStageDictPCN[value].append(key)
                
    def getStageDict(self):
        self.stageDict = {}
        stages = self.settings["Stage"].split(",")
        for stage in stages:
            key,value = stage.split("-")
            self.stageDict[key.strip()] = value.strip()
            
    def getStageDictPCN(self):
        self.stageDictPCN = {}
        if "PCN_Stage" not in self.settings.keys():
            self.dispMsg("PCN_Stage not defined, please update your settings.")
        else:
            stages = self.settings["PCN_Stage"].split(",")
            for stage in stages:
                key,value = stage.split("-")
                self.stageDictPCN[key.strip()] = value.strip()
                
    def getStageDictPRQ(self):
        self.stageDictPRQ = {}
        if "PRQ_Stage" not in self.settings.keys():
            self.dispMsg("PRQ_Stage not defined, please update your settings.")
        else:
            stages = self.settings["PRQ_Stage"].split(",")
            for stage in stages:
                key,value = stage.split("-")
                self.stageDictPRQ[key.strip()] = value.strip()
                
    def getTitleStageDictPRQ(self):
        self.titleStageDictPRQ = {}
        for key, value in self.stageDictPRQ.items():
            if value not in self.titleStageDictPRQ.keys():
                self.titleStageDictPRQ[value]=[key]
            else:
                self.titleStageDictPRQ[value].append(key)
                
    
            
    def sendNotification(self):
        self.cursor.execute("Select * from NOTIFICATION where STATUS='Not Sent'")
        results = self.cursor.fetchall()
        
        if len(results)>0:
            for result in results:
                if result["DOC_ID"] is not None:
                    self.generateECNX(result[0])
                #self.generateHTML(result[0])
                if result['TYPE']=="Rejected To Author":
                    self.rejectNotification(result[0],result['FROM_USER'],result['MSG'])
                elif result['TYPE']=="Rejected To Signer":
                    self.rejectSignerNotification(result[0],result['FROM_USER'],result['USERS'],result['MSG'])
                elif result['TYPE']=="Approved":
                    self.ApprovedNotification(result[0])
                elif result['TYPE']=="Completed":
                    self.completionNotification(result[0])
                elif result['TYPE']=="Stage Moved":
                    self.stageReleaseNotification(result[0])
                elif result['TYPE']=="User Comment":
                    self.commentNotification(result[0],result['FROM_USER'],result['MSG'])
                elif result['TYPE']=="Canceling":
                    self.cancelNotification(result[0],result['MSG'])
                elif result['TYPE']=="User Info":
                    self.userInfoNotification(result['MSG'])
                else:
                    self.releaseNotification(result[0])
                if result["DOC_ID"] is not None:
                    self.removeECNX(result[0])
                    #self.removeHTML(result[0])
                    self.updateStatus(result[0])
        else:
            self.log_text.append("-No notifications found to be sent")
        self.repopulateTable()
                
    def updateStatus(self,doc_id):
        self.log_text.append("-updating status")
        data = ("Sent",doc_id)
        self.cursor.execute("UPDATE NOTIFICATION SET STATUS = ? WHERE DOC_ID = ?",(data))
        self.db.commit()
        now  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (now,doc_id)
        self.cursor.execute("UPDATE DOCUMENT SET LAST_NOTIFIED = ? WHERE DOC_ID = ?",(data))
        self.db.commit()
        self.log_text.append("-status updated")
        
    def rejectNotification(self,doc_id,from_user,msg):
        receivers = []
        self.cursor.execute(f"select Author from DOCUMENT where DOC_ID='{doc_id}'")
        result = self.cursor.fetchone()
        receivers.append(self.userList[result[0]])
        self.cursor.execute(f"select USER_ID from SIGNATURE where DOC_ID='{doc_id}' and TYPE='Signing'")
        results = self.cursor.fetchall()
        for result in results:
            receivers.append(self.userList[result[0]])
        from_user = self.emailNameList[self.userList[from_user]]
        message = f"<p>{doc_id} has been rejected to the author by {from_user}! All Signatures have been removed and the ECN approval will start from the beginning once the ECN is released again. See comment below.</p><p>Comment - {from_user}: {msg}</p>"
        #print(f"send email to these addresses: {receivers} notifying ecn rejection")
        #print(message)
        attach = []
        attach.append(os.path.join(program_location,doc_id+'.ecnx'))
        #attach.append(os.path.join(program_location,ecn_id+'.html'))
        self.sendEmail(doc_id,receivers, message,"Rejection",attach)
        self.log_text.append(f"-Rejection Email sent for {doc_id} to {receivers}")
        
    
    def rejectSignerNotification(self,doc_id,from_user,users,msg):
        users = users.split(',')
        receivers = []
        for user in users:
            receivers.append(self.userList[user])
        message = f"<p>{doc_id} has been rejected to : {users[0]} by {from_user}. Signatures for the following users have also been removed: {users}.See comment below.</p><p>Comment: {msg}</p>"
        #print(f"send email to these addresses: {receivers} notifying ecn completion")
        #print(message)
        attach = []
        attach.append(os.path.join(program_location,doc_id+'.ecnx'))
        #attach.append(os.path.join(program_location,ecn_id+'.html'))
        self.sendEmail(doc_id,receivers, message,"Rejection",attach)
        self.log_text.append(f"-Rejection to Signer Email sent for {doc_id} to {receivers}")
        
    def commentNotification(self,doc_id,from_user,msg):
        receivers = []
        self.cursor.execute(f"select Author from DOCUMENT where DOC_ID='{doc_id}'")
        result = self.cursor.fetchone()
        if result[0]!=from_user:
            receivers.append(self.userList[result[0]])
        self.cursor.execute(f"select USER_ID from SIGNATURE where DOC_ID='{doc_id}' and TYPE='Signing' and SIGNED_DATE!=''")
        results = self.cursor.fetchall()
        for result in results:
            if result[0]!=from_user:
                receivers.append(self.userList[result[0]])
        self.cursor.execute(f"select distinct USER from COMMENTS where DOC_ID='{doc_id}'")
        results = self.cursor.fetchall()
        for result in results:
            if self.userList[result[0]] not in receivers and result[0]!=from_user:
                receivers.append(self.userList[result[0]])
            
        from_user = self.emailNameList[self.userList[from_user]]
        message = f"<p>a comment has been added to {doc_id} by {from_user}! See comment below.</p><p>Comment - {from_user}: {msg}</p>"
        #print(f"send email to these addresses: {receivers} notifying ecn comment")
        #print(message)
        attach = []
        attach.append(os.path.join(program_location,doc_id+'.ecnx'))
        #attach.append(os.path.join(program_location,ecn_id+'.html'))
        self.sendEmail(doc_id,receivers, message,"Comment",attach)
        self.log_text.append(f"-user comment Email sent for {doc_id} to {receivers}")
        
    
    def completionNotification(self,doc_id):
        receivers = []
        self.cursor.execute(f"select Author from DOCUMENT where DOC_ID='{doc_id}'")
        result = self.cursor.fetchone()
        receivers.append(self.userList[result[0]])
        self.cursor.execute(f"select USER_ID from SIGNATURE where DOC_ID='{doc_id}'")
        results = self.cursor.fetchall()
        message = f"<p>{doc_id} has been completed!</p><p>You can now view it in the completed section of your viewer.</p>"
        for result in results:
            receivers.append(self.userList[result[0]])
        #print(f"send email to these addresses: {receivers} notifying ecn completion")
        attach = []
        attach.append(os.path.join(program_location,doc_id+'.ecnx'))
        if doc_id[:3]=="PCN":
            self.log_text.append("-exporting PCN files to server")
            filepath = os.path.join(self.settings["PCN_Export_Loc"],doc_id)
            os.mkdir(filepath)
            self.exportPDF(doc_id,filepath ,"PCN")
            self.exportHTMLPCNWeb(doc_id, filepath)
        #attach.append(os.path.join(program_location,ecn_id+'.html'))
        self.sendEmail(doc_id,receivers, message,"Completion",attach)
        self.log_text.append(f"-Completion Email sent for {doc_id} to {receivers}")
        
    def ApprovedNotification(self,doc_id):
        receivers = []
        self.cursor.execute(f"select Author from DOCUMENT where DOC_ID='{doc_id}'")
        result = self.cursor.fetchone()
        receivers.append(self.userList[result[0]])
        self.cursor.execute(f"select USER_ID from SIGNATURE where DOC_ID='{doc_id}'")
        results = self.cursor.fetchall()
        message = f"<p>{doc_id} has been Approved!</p><p>You can now view it in the Inprogress section of your viewer.</p>"
        for result in results:
            receivers.append(self.userList[result[0]])
        #print(f"send email to these addresses: {receivers} notifying ecn completion")
        attach = []
        attach.append(os.path.join(program_location,doc_id+'.ecnx'))
        if doc_id[:3]=="PCN":
            self.log_text.append("-exporting PCN files to server")
            filepath = os.path.join(self.settings["PCN_Export_Loc"],doc_id)
            os.mkdir(filepath)
            self.exportPDF(doc_id,filepath ,"PCN")
            self.exportHTMLPCNWeb(doc_id, filepath)
        #attach.append(os.path.join(program_location,ecn_id+'.html'))
        self.sendEmail(doc_id,receivers, message,"Approved",attach)
        self.log_text.append(f"-Approved Email sent for {doc_id} to {receivers}")
        
        
    def cancelNotification(self,doc_id,msg):
        self.cursor.execute(f"select USER_ID from SIGNATURE where DOC_ID='{doc_id}' and TYPE='Signing'")
        results = self.cursor.fetchall()
        receivers = []
        message = f"<p>{doc_id} has been canceled by the author! See comment below.</p><p>Comment: {msg}</p>"
        for result in results:
            receivers.append(self.userList[result[0]])
        print(f"send email these addresses: {receivers} notifying ecn cancelation")
        attach = []
        attach.append(os.path.join(program_location,doc_id+'.ecnx'))
        self.sendEmail(doc_id,receivers, message,"Cancelation",attach)
        self.log_text.append(f"-Rejection Email sent for {doc_id} to {receivers}")
        
    def releaseNotification(self,doc_id):
        self.cursor.execute(f"select USER_ID from SIGNATURE where DOC_ID='{doc_id}' and TYPE='Signing'")
        results = self.cursor.fetchall()
        receivers = []
        message = f"<p>{doc_id} has been released! You can see it in the queue section once it is your turn for approval.<\p><p>You can open the attached ECNX file to launch the ECN Manager directly to the ECN or you can view the ECN in the open section in the ECN Manager application.</p>"
        for result in results:
            receivers.append(self.userList[result[0]])
        print(f"send email these addresses: {receivers} notifying ecn release")
        attach = []
        attach.append(os.path.join(program_location,doc_id+'.ecnx'))
        self.sendEmail(doc_id,receivers, message,attach)
        self.log_text.append(f"-Release Email sent for {doc_id} to {receivers}")
        
    def stageReleaseNotification(self,doc_id):
        #get stage
        self.cursor.execute(f"Select Stage from DOCUMENT where DOC_ID='{doc_id}'")
        result = self.cursor.fetchone()
        stage = result[0]
        if doc_id[:3]=="ECN":
            users = self.getWaitingUser(doc_id, self.titleStageDict[str(stage)])
        elif doc_id[:3]=="PRQ":
            users = self.getWaitingUser(doc_id, self.titleStageDictPRQ[str(stage)])
        else:
            users = self.getWaitingUser(doc_id, self.titleStageDictPCN[str(stage)])
        receivers = []
        for user in users:
            receivers.append(self.userList[user])
        message = f"<p>{doc_id} has been released and is now awaiting for your approval!</p><p>You can open the attached ECNX file to launch the ECN Manager directly to the ECN or you can view the ECN your queue in the ECN Manager application.</p>"
        #print(f"send email these addresses: {receivers} notifying ecn release stage move")
        attach = []
        attach.append(os.path.join(program_location,doc_id+'.ecnx'))
        self.sendEmail(doc_id,receivers, message,"Awaiting Approval",attach)
        self.log_text.append(f"-Stage Release Email sent for {doc_id} to {receivers}")
        
    def userInfoNotification(self,email):
        self.cursor.execute(f"Select USER_ID, PASSWORD from USER where EMAIL='{email}'")
        result = self.cursor.fetchone()
        attach = []
        receivers = [email]
        message = f"Here is your log in information for the ECN Manager. User: {result[0]} | password: {result[1]}"
        print(f"send email to {email} with user info: {result[0]} | {result[1]}")
        self.sendEmail("", receivers, message, "User Info", attach)
        self.log_text.append(f"- user info email has been sent to {receivers}")
        self.cursor.execute(f"DELETE FROM NOTIFICATION WHERE MSG = '{email}' ")
        self.db.commit()
        self.log_text.append(f"- entry has been deleted from notifications table")
        
            
    def sendEmail(self,doc_id,receivers,message,subject,attach):
        if not isinstance(attach, list):
            attach = [attach]
        try:
            with smtplib.SMTP(self.settings["SMTP"],self.settings["Port"]) as server:
                msg = MIMEMultipart()
                msg['From'] = self.settings["From_Address"]
                msg['To'] = ", ".join(receivers)
                if subject=="User Info":
                    msg['Subject']=f"{subject} Notification for ECN Manager"
                else:
                    msg['Subject']=f"{subject} Notification for {doc_id}"
                
                message +="\n\n"
                if doc_id[:3]=="PCN":
                    html = self.generateHTMLPCN(doc_id)
                elif doc_id[:3]=="PRQ":
                    html = self.generateHTMLPRQ(doc_id)
                else:
                    html = self.generateHTML(doc_id)
                message+=html
                
                msg.attach(MIMEText(message,'html'))
                #ecnx = os.path.join(program_location,ecn_id+'.ecnx')
                #filename = f'{ecn_id}.ecnx'
                for file in attach:
                    attach_file = open(file,'rb')
                    payload = MIMEBase('application', 'octet-stream')
                    payload.set_payload(attach_file.read())
                    encoders.encode_base64(payload)
                    #print(ecnx, filename)
                    payload.add_header('Content-Disposition','attachment',filename = os.path.basename(file))
                    msg.attach(payload)
                server.sendmail(self.settings["From_Address"], receivers, msg.as_string())
                self.log_text.append(f"Successfully sent email to {receivers}")
        except Exception as e:
            print(e)
                
    def generateECNX(self,doc_id):
        self.log_text.append("-generating ecnx file")
        ecnx = os.path.join(program_location,doc_id+'.ecnx')
        f = open(ecnx,"w+")
        f.write(f"{doc_id}")
        f.close()
        self.log_text.append("-ecnx file generated")
        
    def removeECNX(self,doc_id):
        self.log_text.append("-removing ecnx file")
        ecnx = os.path.join(program_location,doc_id+'.ecnx')
        os.remove(ecnx)
        self.log_text.append("-ecnx file removed")
        
    def generateHTML(self,doc_id):
        try:
            foldername = program_location
            template_loc = os.path.join(program_location,'templates','template.html')
            with open(template_loc) as f:
                lines = f.read()
                #print(lines)
                f.close()

                t = Template(lines)
                self.cursor.execute(f"SELECT * from DOCUMENT where DOC_ID='{doc_id}'")
                result = self.cursor.fetchone()
                title = result['DOC_TITLE']
                author = result['AUTHOR']
                dept = result['DEPARTMENT']
                requestor = result['REQUESTOR']
                reason = result['DOC_REASON']
                summary = result['DOC_SUMMARY']
                signature = "<tr>"
                attachment ="<tr>"
                parts = ""
                
                #parts
                #print('exporting parts')
                self.cursor.execute(f"SELECT * from PARTS where DOC_ID='{doc_id}'")
                results = self.cursor.fetchall()
                if results is not None:
                    for result in results:
                        text = f"<p> {result['PART_ID']}</p>"
                        text += "<ul>"
                        text += f"<li>Desc: {result['DESC']}</li>"
                        text += f"<li>Type: {result['TYPE']}</li>"
                        text += f"<li>Disposition: {result['DISPOSITION']}</li>"
                        text += f"<li>Inspection Req.: {result['INSPEC']}</li>"
                        text += f"<li>Mfg.: {result['MFG']}</li>"
                        text += f"<li>Mfg.#: {result['MFG_PART']}</li>"
                        text += f"<li>Replacing: {result['REPLACING']}</li>"
                        text += "</ul>"
                        parts += text
                

                #attachments
                #print('exporting attachments')
                self.cursor.execute(f"SELECT * FROM ATTACHMENTS where DOC_ID='{doc_id}'")
                results = self.cursor.fetchall()
                if results is not None:
                    for result in results:
                        attachment += "<td>"+result['FILENAME']+"</td>"
                        attachment += "<td>"+result['FILEPATH']+"</td></tr>"
                else:
                    attachment="<tr><td></td><td></td></tr>"

                
                #print('exporting signatures')
                self.cursor.execute(f"SELECT * from SIGNATURE where DOC_ID='{doc_id}' and TYPE='Signing'")
                results = self.cursor.fetchall()
                if results is not None:
                    for result in results:
                        signature += "<td>"+result['JOB_TITLE']+"</td>"
                        signature += "<td>"+result['NAME']+"</td>"
                        if result['SIGNED_DATE'] is not None:
                            signature += "<td>"+str(result['SIGNED_DATE'])+"</td></tr>"
                        else:
                            signature += "<td></td></tr>"
                else:
                    signature="<tr><td></td><td></td><td></td></tr>"
                    
                
                export = t.substitute(ECNID=doc_id,ECNTitle=title,Requestor=requestor,Department=dept,Author=author, Reason=reason,Summary=summary,Parts=parts,Attachment=attachment,Signature=signature)
            

                self.log_text.append("generation complete")
                return export
        except Exception as e:
            print(e)
            self.log_text.append(f"Error Occured during ecn export.\n Error: {e}")
        
    def removeHTML(self,doc_id):
        self.log_text.append("-removing HTML file")
        ecnx = os.path.join(program_location,doc_id+'.html')
        os.remove(ecnx)
        self.log_text.append("-HTML file removed")
        
    def generateHTMLPCN(self,doc_id):
        template_loc = os.path.join(self.programLoc,'templates','pcn_template.html')
        with open(template_loc) as f:
            lines = f.read() 
            f.close()
            t = Template(lines)
            
            self.cursor.execute(f"SELECT * from DOCUMENT where DOC_ID='{doc_id}'")
            result = self.cursor.fetchone()
            overview = result['DOC_TEXT_1']
            products = result['DOC_TEXT_2']
            change = result['DOC_SUMMARY']
            reason = result['DOC_REASON']
            replacement = result['DOC_TEXT_3']
            reference = result['DOC_TEXT_4']
            response = result['DOC_TEXT_5']

            #print('substituting text')
            
            html = t.substitute(PCNID=doc_id,Overview=overview,Products=products,ChangeDescription=change,Reason=reason,Replacement=replacement,Reference=reference,Response=response)

            return html
        
    def generateHTMLPCNWeb(self,doc_id):
        template_loc = os.path.join(self.programLoc,'templates','pcn_web_template.html')
        with open(template_loc) as f:
            lines = f.read() 
            f.close()
            t = Template(lines)
            
            self.cursor.execute(f"SELECT * from DOCUMENT where DOC_ID='{doc_id}'")
            result = self.cursor.fetchone()
            date = result['COMP_DATE']
            date = datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
            date = date.strftime("%b %d, %Y")
            web_desc = result['DOC_TEXT_6']
            pcn_link = self.settings["PCN_Web_Href"]+doc_id+".pdf"

            #print('substituting text')
            
            html = t.substitute(PCNLink=pcn_link,PCNID=doc_id,Date=date,WebDescription=web_desc)

            return html
        
    def generateHTMLPRQ(self,doc_id):
        template_loc = os.path.join(self.programLoc,'templates','prq_template.html')
        with open(template_loc) as f:
            lines = f.read()
            f.close()
            t = Template(lines)
            
            self.cursor.execute(f"SELECT * from DOCUMENT where DOC_ID='{doc_id}'")
            result = self.cursor.fetchone()
            print("generating header 1")
            title = result["DOC_TITLE"]
            author = result["AUTHOR"]
            status = result["STATUS"]
            requisition_details = result["DOC_SUMMARY"]
            
            print("generating header 2")
            self.cursor.execute(f"SELECT * from PURCH_REQ_DOC_LINK where DOC_ID='{doc_id}'")
            result = self.cursor.fetchone()
            print(result)
            req_id = result["REQ_ID"]
            project_id = result["PROJECT_ID"]
            
            print("generating header 3")
            print(req_id)
            req_header = self.visual.getReqHeader(req_id)
            print(req_header)
            visual_status = req_header[1]
            assigned_buyer = req_header[0]
            
            print("generating header 4")
            requisitions = self.visual.getReqItems(req_id)
            req_lines = ""
            total_cost = 0
            if requisitions is not None:
                for req in requisitions:
                    line_no = str(req[0])
                    if req[2] is not None:
                        part_id = req[2]
                    else:
                        part_id = ""
                    if req[3] is not None:
                        vendor_part_id = req[3]
                    else:
                        vendor_part_id = ""
                    order_qty = str(req[4])
                    purchase_um = req[5]
                    if req[6] is not None:
                        po_num = req[6]
                    else:
                        po_num = ""
                    unit_price = req[7]
                    total_price = float(unit_price)*float(order_qty)
                    total_cost+=total_price

                    req_lines += "<tr><td>"+line_no+"</td>"
                    req_lines += "<td>"+part_id+"</td>"
                    req_lines += "<td>"+vendor_part_id+"</td>"
                    req_lines += "<td>"+order_qty+"</td>"
                    req_lines += "<td>"+purchase_um+"</td>"
                    req_lines += "<td>"+str(unit_price)+"</td>"
                    req_lines += "<td>"+str(total_price)+"</td>"
                    req_lines += "<td>"+po_num+"</td></tr>"
                    
            print("generating header 5")
            signature = "<tr>"
            self.cursor.execute(f"SELECT * from SIGNATURE where DOC_ID='{doc_id}' and TYPE='Signing'")
            results = self.cursor.fetchall()
            if results is not None:
                for result in results:
                    signature += "<td>"+result['JOB_TITLE']+"</td>"
                    signature += "<td>"+result['NAME']+"</td>"
                    if result['SIGNED_DATE'] is not None:
                        signature += "<td>"+str(result['SIGNED_DATE'])+"</td></tr>"
                    else:
                        signature += "<td></td></tr>"
            else:
                signature="<tr><td></td><td></td><td></td></tr>"
                

            print('substituting text')
            
            html = t.substitute(REQID=req_id,Title=title,AUTHOR=author,DOCID=doc_id,PRJID=project_id,ORDERSTATUS=status,VISUALSTATUS=visual_status,BUYER=assigned_buyer,TOTALCOST=total_cost,DETAILS=requisition_details,REQLINE=req_lines,Signature=signature)

            return html
        
    def exportPDF(self,doc_id,filepath,doc_type):
        try:
            if doc_type=="PCN":
                export = self.generateHTMLPCN(doc_id)
            else:
                export = self.generateHTML(doc_id)
            doc_loc = filepath+'\\'+doc_id+'.pdf'
            self.webview = WebView(msg_disable=True)
            self.webview.loadAndPrint(export,doc_loc)
        except Exception as e:
            print(e)
            self.log_text.append(f"Error Occured during document export.\n Error: {e}")
            
    def exportHTMLPCNWeb(self,doc_id,filepath):
        try:
            export = self.generateHTMLPCNWeb(doc_id)
            doc_loc = filepath+'\\'+doc_id+'.html'
            with open(doc_loc, 'w') as f:
                f.write(export)
                f.close()
            self.log_text.append(f"-PCN web HTML has been exported")
        except Exception as e:
            print(e)
            self.log_text.append(f"Error Occured during ecn export.\n Error: {e}")
        
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
        self.cursor.execute("SELECT DOC_ID, LAST_NOTIFIED, FIRST_RELEASE, LAST_MODIFIED FROM DOCUMENT WHERE STATUS !='Completed' and STATUS!='Draft' and STATUS!='Approved'and STAGE!='0'")
        results = self.cursor.fetchall()
        today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for result in results:
            if result['LAST_NOTIFIED'] is not None:
                elapsed = self.getElapsedDays(today, result["LAST_NOTIFIED"])
                #print(elapsed.days)
            else:
                elapsed = self.getElapsedDays(today, result["FIRST_RELEASE"])
                #print(elapsed.days)
            if elapsed.days >= int(self.settings['Reminder_Days']):
                doc_id = result["DOC_ID"]
                first_release = result["FIRST_RELEASE"]
                direct_receivers = []
                secondary_receivers = []
                self.cursor.execute(f"Select Stage from DOCUMENT where DOC_ID='{doc_id}'")
                result = self.cursor.fetchone()
                stage = result[0]
                if doc_id[:3]=="ECN":
                    users = self.getWaitingUser(doc_id, self.titleStageDict[str(stage)])
                elif doc_id[:3]=="PRQ":
                    users = self.getWaitingUser(doc_id, self.titleStageDictPRQ[str(stage)])
                else:
                    users = self.getWaitingUser(doc_id, self.titleStageDictPCN[str(stage)])
                for user in users:
                    direct_receivers.append(self.userList[user])
                users = self.getWaitingUser(doc_id, self.titleStageDict[str(self.settings['Reminder_Stages'])])
                for user in users:
                    secondary_receivers.append(self.userList[user])
                total_days = self.getElapsedDays(today, first_release)
                self.lateReminder(doc_id,direct_receivers,secondary_receivers, total_days)
                
                
        #check for prq reminders
        self.cursor.execute("SELECT DOC_ID, LAST_NOTIFIED, FIRST_RELEASE, LAST_MODIFIED FROM DOCUMENT WHERE STATUS ='Approved'")
        results = self.cursor.fetchall()
        today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for result in results:
            #check for prq visual status
            doc_id = result["DOC_ID"]
            self.cursor.execute(f"SELECT REQ_ID FROM PURCH_REQ_DOC_LINK WHERE DOC_ID='{doc_id}'")
            get_req = self.cursor.fetchone()
            req_id = get_req[0]
            req_status = self.visual.getReqHeader(req_id)[1]
            if req_status=="C": #Closed
                completeddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                elapsed = self.getElapsedDays(completeddate,result["FIRST_RELEASE"])
                elapsed = elapsed.days + round(elapsed.seconds/86400,2)
                data = (completeddate,completeddate,elapsed,"Completed",doc_id)
                print(data)
                self.cursor.execute("UPDATE DOCUMENT SET LAST_MODIFIED = ?,COMP_DATE = ?, COMP_DAYS = ?, STATUS = ? WHERE DOC_ID = ?",(data))
                # self.cursor.execute("UPDATE DOCUMENT SET STATUS = ? WHERE DOC_ID = ?",(data))
                self.db.commit()
                self.log_text.append(f"{doc_id} has been set as completed")
                self.generateECNX(doc_id)
                self.completionNotification(doc_id)
                self.removeECNX(doc_id)
            else:
                if result['LAST_NOTIFIED'] is not None:
                    elapsed = self.getElapsedDays(today, result["LAST_NOTIFIED"])
                    #print(elapsed.days)
                else:
                    elapsed = self.getElapsedDays(today, result["FIRST_RELEASE"])
                    #print(elapsed.days)
                if elapsed.days >= int(self.settings['Reminder_Days']):
                    # doc_id = result["DOC_ID"]
                    first_release = result["FIRST_RELEASE"]
                    direct_receivers = []
                    secondary_receivers = []
                    #users are people in the notification tab
                    direct_receivers = self.getNotificationUsers(doc_id)
                    # for user in users:
                    #     direct_receivers.append(self.userList[user])
                    # users = self.getWaitingUser(doc_id, self.titleStageDict[str(self.settings['Reminder_Stages'])])
                    # for user in users:
                    #     secondary_receivers.append(self.userList[user])
                    total_days = self.getElapsedDays(today, first_release)
                    self.lateReminder(doc_id,direct_receivers,secondary_receivers, total_days)


    def setElapsedDays(self):
        self.cursor.execute(f"Select DOC_ID, FIRST_RELEASE, LAST_STATUS from DOCUMENT where STATUS!='Completed'")
        results = self.cursor.fetchall()
        for result in results:
            today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            doc_id = result[0]
            first_release = datetime.strptime(result[1],'%Y-%m-%d %H:%M:%S')
            last_status = datetime.strptime(result[2],'%Y-%m-%d %H:%M:%S')
            release_elapse = today - first_release
            status_elapse = today - last_status
            self.cursor.execute(f"UPDATE DOCUMENT SET RELEASE_ELAPSE ='{release_elapse.day}', STATUS_ELAPSE='{status_elapse.day}' WHERE DOC_ID='{doc_id}'")
        self.db.commit()

    def lateReminder(self,doc_id,direct_receivers,secondary_receivers,total_days):
        today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        reminder_days = self.settings['Reminder_Days']
        direct = []
        for email in direct_receivers:
            direct.append(self.emailNameList[email])
        direct = ", ".join(direct)
        message = f"<p>Hello {direct}:</p><p>{doc_id} has been out for {total_days} and has not moved for {reminder_days} days or more since the last notification has been sent.</p><p> Please work on it at your earliest availability!</p><p> You can view the ECN your queue in the ECN Manager application.</p><p>You can also open the attachment file to be directed to the ECN.</p>"
        #print(message)
        #print(f"send email these addresses: {receivers} notifying ecn lateness")
        self.generateECNX(doc_id)
        #self.generateHTML(ecn_id)
        receivers = []
        for user in direct_receivers:
            receivers.append(user)
        for user in secondary_receivers:
            receivers.append(user)
        attach = []
        attach.append(os.path.join(program_location,doc_id+'.ecnx'))
        #attach.append(os.path.join(program_location,ecn_id+'.html'))
        self.sendEmail(doc_id,receivers, message,"Reminder",attach)
        data = (doc_id,"Sent","Reminder")
        self.cursor.execute("INSERT INTO NOTIFICATION(DOC_ID, STATUS, TYPE) VALUES(?,?,?)",(data))
        self.cursor.execute(f"UPDATE DOCUMENT SET LAST_NOTIFIED='{today}' WHERE DOC_ID='{doc_id}'")
        self.db.commit()
        self.log_text.append(f"-lateness Email sent for {doc_id} to {receivers}")
        self.removeECNX(doc_id)
        #self.removeHTML(ecn_id)

    def getReminderUsers(self):
        self.cursor.execute(f"select USER_ID from SIGNATURE where SIGNED_DATE is NULL")
        results = self.cursor.fetchall()
        receivers = []
        for result in results:
            receivers.append(self.userList[result[0]])
        return receivers
    
    def getNotificationUsers(self,doc_id):
        self.cursor.execute(f"select USER_ID from SIGNATURE where TYPE='Notify' and DOC_ID='{doc_id}'")
        results = self.cursor.fetchall()
        receivers = []
        for result in results:
            receivers.append(self.userList[result[0]])
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