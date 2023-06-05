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

class SettingsWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(SettingsWindow,self).__init__()
        self.windowWidth =  int(830*1.1)
        self.windowHeight = int(580*1.1)
        self.parent = parent
        if self.parent is None:
            f = open(initfile,'r')
            self.settings = {}
            for line in f:
                key,value = line.split(" : ")
                self.settings[key]=value.strip()
            print(self.settings)
            f.close()
            self.db = sqlite3.connect(self.settings["DB_LOC"])
            self.cursor = self.db.cursor()
            self.cursor.row_factory = sqlite3.Row
        else:
            self.settings = parent.settings
            self.db = self.parent.db
            self.cursor = self.parent.cursor
        self.initAtt()
        self.initUI()
        self.loadSettings()
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
        title = "Users Window"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        
        

    def initUI(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        layout_left = QtWidgets.QVBoxLayout()
        layout_right = QtWidgets.QVBoxLayout()
        self.label_db = QtWidgets.QLabel("DB Loc:")
        self.line_db = QtWidgets.QLineEdit(self)
        self.button_db = QtWidgets.QPushButton("Browse")
        layout_db = QtWidgets.QHBoxLayout()
        layout_db.addWidget(self.line_db)
        layout_db.addWidget(self.button_db)
        layout_left.addWidget(self.label_db)
        layout_left.addLayout(layout_db)
        self.label_visual = QtWidgets.QLabel("Visual:")
        self.label_user_v = QtWidgets.QLabel("User:")
        self.line_user_v = QtWidgets.QLineEdit(self)
        self.label_pass_v = QtWidgets.QLabel("Pass:")
        self.line_pass_v = QtWidgets.QLineEdit(self)
        self.line_pass_v.setEchoMode(QtWidgets.QLineEdit.Password)
        self.label_db_v = QtWidgets.QLabel("DB:  ")
        self.line_db_v = QtWidgets.QLineEdit(self)
        layout_user_v = QtWidgets.QHBoxLayout()
        layout_user_v.addWidget(self.label_user_v)
        layout_user_v.addWidget(self.line_user_v)
        layout_pass_v = QtWidgets.QHBoxLayout()
        layout_pass_v.addWidget(self.label_pass_v)
        layout_pass_v.addWidget(self.line_pass_v)
        layout_db_v = QtWidgets.QHBoxLayout()
        layout_db_v.addWidget(self.label_db_v)
        layout_db_v.addWidget(self.line_db_v)
        layout_left.addWidget(self.label_visual)
        layout_left.addLayout(layout_user_v)
        layout_left.addLayout(layout_pass_v)
        layout_left.addLayout(layout_db_v)
        self.label_smtp = QtWidgets.QLabel("SMTP:")
        self.label_smtp_ip = QtWidgets.QLabel("IP:   ")
        self.line_smtp_address = QtWidgets.QLineEdit(self)
        self.line_smtp_address.setPlaceholderText("SMTP Address")
        self.label_smtp_port = QtWidgets.QLabel("Port:")
        self.line_smtp_port = QtWidgets.QLineEdit(self)
        self.line_smtp_port.setPlaceholderText("SMTP Port")
        self.label_smtp_email = QtWidgets.QLabel("Email:")
        self.line_smtp_email = QtWidgets.QLineEdit(self)
        self.line_smtp_email.setPlaceholderText("Enter sent from address")
        layout_smtp_ip = QtWidgets.QHBoxLayout()
        layout_smtp_ip.addWidget(self.label_smtp_ip)
        layout_smtp_ip.addWidget(self.line_smtp_address)
        layout_smtp_port = QtWidgets.QHBoxLayout()
        layout_smtp_port.addWidget(self.label_smtp_port)
        layout_smtp_port.addWidget(self.line_smtp_port)
        layout_smtp_email = QtWidgets.QHBoxLayout()
        layout_smtp_email.addWidget(self.label_smtp_email)
        layout_smtp_email.addWidget(self.line_smtp_email)
        layout_left.addWidget(self.label_smtp)
        layout_left.addLayout(layout_smtp_ip)
        layout_left.addLayout(layout_smtp_port)
        layout_left.addLayout(layout_smtp_email)
        
        self.label_instant_client = QtWidgets.QLabel("Oracle Instant Client:")
        self.line_instant_client = QtWidgets.QLineEdit(self)
        self.line_instant_client.setPlaceholderText("Enter Location of Instant Client")
        self.button_instant_client = QtWidgets.QPushButton("Browse")
        layout_ic = QtWidgets.QHBoxLayout()
        layout_ic.addWidget(self.line_instant_client)
        layout_ic.addWidget(self.button_instant_client)
        layout_left.addWidget(self.label_instant_client)
        layout_left.addLayout(layout_ic)
        
        self.label_reminders = QtWidgets.QLabel("Reminders:")
        self.label_reminder_days = QtWidgets.QLabel("Reminder Days:")
        self.line_reminder_days = QtWidgets.QLineEdit(self)
        layout_rd = QtWidgets.QHBoxLayout()
        layout_rd.addWidget(self.label_reminder_days)
        layout_rd.addWidget(self.line_reminder_days)
        self.label_reminder_stages = QtWidgets.QLabel("Reminder Stages:")
        self.line_reminder_stages = QtWidgets.QLineEdit(self)
        self.label_PCN_export = QtWidgets.QLabel("PCN Export Loc:")
        self.line_PCN_export = QtWidgets.QLineEdit(self)
        self.button_pcn = QtWidgets.QPushButton("Browse")
        self.label_PCN_web = QtWidgets.QLabel("PCN Web HRef Path:")
        self.line_PCN_web = QtWidgets.QLineEdit()
        layout_pcn = QtWidgets.QHBoxLayout()
        layout_pcn.addWidget(self.line_PCN_export)
        layout_pcn.addWidget(self.button_pcn)
        layout_rs = QtWidgets.QHBoxLayout()
        layout_rs.addWidget(self.label_reminder_stages)
        layout_rs.addWidget(self.line_reminder_stages)
        layout_left.addWidget(self.label_reminders)
        layout_left.addLayout(layout_rd)
        layout_left.addLayout(layout_rs)
        layout_left.addWidget(self.label_PCN_export)
        layout_left.addLayout(layout_pcn)
        layout_left.addWidget(self.label_PCN_web)
        layout_left.addWidget(self.line_PCN_web)
        
        
        layout_left.addStretch()
                        
        self.label_ecn_type = QtWidgets.QLabel("ECN Types:")
        self.line_ecn_type = QtWidgets.QLineEdit(self)
        self.button_ecn_type_add = QtWidgets.QPushButton("Add")
        self.button_ecn_type_add.clicked.connect(self.addType)
        self.line_ecn_type.returnPressed.connect(self.addType)
        layout_et = QtWidgets.QHBoxLayout()
        layout_et.addWidget(self.line_ecn_type)
        layout_et.addWidget(self.button_ecn_type_add)
        self.list_ecn_type = QtWidgets.QListWidget(self)
        self.list_ecn_type.doubleClicked.connect(self.removeType)
        self.button_ecn_type_remove = QtWidgets.QPushButton("Remove")
        self.button_ecn_type_remove.clicked.connect(self.removeType)
        layout_right.addWidget(self.label_ecn_type)
        layout_right.addLayout(layout_et)
        layout_right.addWidget(self.list_ecn_type)
        layout_right.addWidget(self.button_ecn_type_remove)
        
        self.label_dept = QtWidgets.QLabel("Departments:")
        self.line_dept = QtWidgets.QLineEdit(self)
        self.line_dept.returnPressed.connect(self.addDept)
        self.button_dept_add = QtWidgets.QPushButton("Add")
        self.button_dept_add.clicked.connect(self.addDept)
        self.list_dept = QtWidgets.QListWidget(self)
        self.list_dept.doubleClicked.connect(self.removeDept)
        self.button_dept_remove = QtWidgets.QPushButton("Remove")
        self.button_dept_remove.clicked.connect(self.removeDept)
        self.label_jobs = QtWidgets.QLabel("Job Titles and stages (Set stage to 99 for notification only):")
        headers = ['Job Title','ECN Stage','PCN Stage','PRQ Stage']
        self.table_jobs = QtWidgets.QTableWidget(0,len(headers),self)
        self.table_jobs.setHorizontalHeaderLabels(headers)
        self.table_jobs.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.button_jobs_add = QtWidgets.QPushButton("Add")
        self.button_jobs_add.clicked.connect(self.addJob)
        self.button_jobs_insert = QtWidgets.QPushButton("Insert")
        self.button_jobs_insert.clicked.connect(self.insertJob)
        self.button_jobs_remove = QtWidgets.QPushButton("Remove")
        self.button_jobs_remove.clicked.connect(self.removeJob)
        self.button_save = QtWidgets.QPushButton("Save Settings")
        self.button_save.clicked.connect(self.saveSettings)
        layout_buttons_jobs = QtWidgets.QHBoxLayout()
        layout_buttons_jobs.addWidget(self.button_jobs_add)
        layout_buttons_jobs.addWidget(self.button_jobs_insert)
        layout_buttons_jobs.addWidget(self.button_jobs_remove)
        layout_dept = QtWidgets.QHBoxLayout()
        layout_dept.addWidget(self.line_dept)
        layout_dept.addWidget(self.button_dept_add)
        layout_right.addWidget(self.label_dept)
        layout_right.addLayout(layout_dept)
        layout_right.addWidget(self.list_dept)
        layout_right.addWidget(self.button_dept_remove)
        layout_right.addWidget(self.label_jobs)
        layout_right.addWidget(self.table_jobs)
        layout_right.addLayout(layout_buttons_jobs)
        layout_right.addWidget(self.button_save)
        #main_layout.addLayout(button_layout)
        main_layout.addLayout(layout_left)
        main_layout.addLayout(layout_right)
        
        self.setLayout(main_layout)

    def getStageDict(self):
        self.stageDict = {}
        stages = self.settings["Stage"].split(",")
        for stage in stages:
            key,value = stage.split("-")
            self.stageDict[key.strip()] = value.strip()
        #print(self.stageDict)
        
    def getPCNStageDict(self):
        if "PCN_Stage" in self.settings.keys():
            self.PCNstageDict = {}
            stages = self.settings["PCN_Stage"].split(",")
            for stage in stages:
                key,value = stage.split("-")
                self.PCNstageDict[key.strip()] = value.strip()
        else:
            self.PCNstageDict = None
            
    def getPRQStageDict(self):
        if "PRQ_Stage" in self.settings.keys():
            self.PCNstageDict = {}
            stages = self.settings["PRQ_Stage"].split(",")
            for stage in stages:
                key,value = stage.split("-")
                self.PRQstageDict[key.strip()] = value.strip()
        else:
            self.PRQstageDict = None


    def loadSettings(self):
        self.getStageDict()
        self.getPCNStageDict()
        self.getPRQStageDict()
        self.line_db.setText(self.settings["DB_LOC"])
        if "Visual" in self.settings.keys():
            user,pw,db = self.settings["Visual"].split(",")
            self.line_user_v.setText(user)
            self.line_pass_v.setText(pw)
            self.line_db_v.setText(db)
        if "SMTP" in self.settings.keys():
            self.line_smtp_address.setText(self.settings["SMTP"])
        if "Port" in self.settings.keys():
            self.line_smtp_port.setText(self.settings["Port"])
        if "From_Address" in self.settings.keys():
            self.line_smtp_email.setText(self.settings["From_Address"])
        if "Instant_Client" in self.settings.keys():
            self.line_instant_client.setText(self.settings["Instant_Client"])
        if "PCN_Export_Loc" in self.settings.keys():
            self.line_PCN_export.setText(self.settings["PCN_Export_Loc"])
        if "PCN_Web_Href" in self.settings.keys():
            self.line_PCN_web.setText(self.settings["PCN_Web_Href"])
        if "Reminder_Days" in self.settings.keys():
            self.line_reminder_days.setText(self.settings["Reminder_Days"])
        if "Reminder_Stages" in self.settings.keys():
            self.line_reminder_stages.setText(self.settings["Reminder_Stages"])
        if "ECN_Types" in self.settings.keys():
            types = self.settings["ECN_Types"].split(",")
            temp = []
            for item in types:
                temp.append(item.strip())
            for item in temp:
                self.list_ecn_type.addItem(item)
        if "Dept" in self.settings.keys():
            dept = self.settings["Dept"].split(",")
            temp = []
            for item in dept:
                temp.append(item.strip())
            for item in temp:
                self.list_dept.addItem(item)
        if "Job_Titles" in self.settings.keys():
            jobs = self.settings["Job_Titles"].split(",")
            temp = []
            for job in jobs:
                temp.append(job.strip())
            self.table_jobs.setRowCount(len(temp))
            row = 0
            for item in temp:
                self.table_jobs.setItem(row, 0, QtWidgets.QTableWidgetItem(item))
                self.table_jobs.setItem(row,1,QtWidgets.QTableWidgetItem(self.stageDict[item]))
                if self.PCNstageDict is not None:
                    self.table_jobs.setItem(row,2,QtWidgets.QTableWidgetItem(self.PCNstageDict[item]))
                if self.PRQstageDict is not None:
                    self.table_jobs.setItem(row,3,QtWidgets.QTableWidgetItem(self.PRQstageDict[item]))
                row+=1

    def saveSettings(self):
        data = ""
        data += "DB_LOC : " + self.line_db.text()+"\n"
        if self.line_user_v.text()!="" and self.line_pass_v.text()!= "" and self.line_db_v.text()!="":
            data+= f"Visual : {self.line_user_v.text()},{self.line_pass_v.text()},{self.line_db_v.text()}\n"
        else:
            self.dispMsg("One of the Visual fields are empty. Visual module will be disabled until fields are entered.")
        if self.line_smtp_address.text()!="" and self.line_smtp_port.text()!="" and self.line_smtp_email.text()!="":
                data += "SMTP : " + self.line_smtp_address.text() + "\n"
                data += "Port : " + self.line_smtp_port.text() +"\n"
                data += "From_Address : " + self.line_smtp_email.text() + "\n"
        else:
            self.dispMsg("One of the SMTP fields are empty.")
        data += "Instant_Client : " + self.line_instant_client.text()+"\n"
        if self.line_reminder_days.text!="":
            data+= f"Reminder_Days : {self.line_reminder_days.text()}\n"
        else:
            self.dispMsg("Reminder Days field is empty")
        data += f"Reminder_Stages : {self.line_reminder_stages.text()}\n"
        data += "ECN_Types : "
        for x in range(self.list_ecn_type.count()):
            if x < self.list_ecn_type.count()-1:
                data += self.list_ecn_type.item(x).text()+","
            else:
                data += self.list_ecn_type.item(x).text()+"\n"
        data += "Dept : "
        for x in range(self.list_dept.count()):
            if x < self.list_dept.count()-1:
                data += self.list_dept.item(x).text()+","
            else:
                data += self.list_dept.item(x).text()+"\n"
        jobs = ""
        stages = ""
        pcn_stages = ""
        prq_stages = ""
        for x in range(self.table_jobs.rowCount()):
            #print(x,self.table_jobs.item(x, 0).text(),self.table_jobs.item(x, 1).text())
            if x < self.table_jobs.rowCount()-1:
                jobs += self.table_jobs.item(x, 0).text()+","
                stages += self.table_jobs.item(x, 0).text() + "-" + self.table_jobs.item(x, 1).text() + ","
                pcn_stages += self.table_jobs.item(x, 0).text() + "-" + self.table_jobs.item(x, 2).text() + ","
                prq_stages += self.table_jobs.item(x, 0).text() + "-" + self.table_jobs.item(x, 3).text() + ","
            else:
                jobs += self.table_jobs.item(x, 0).text()+"\n"
                stages += self.table_jobs.item(x, 0).text() + "-" + self.table_jobs.item(x, 1).text() + "\n"
                pcn_stages += self.table_jobs.item(x, 0).text() + "-" + self.table_jobs.item(x, 2).text() + "\n"
                prq_stages += self.table_jobs.item(x, 0).text() + "-" + self.table_jobs.item(x, 3).text() + "\n"
        data += "Job_Titles : " + jobs
        data += "Stage : " + stages
        data += "PCN_Stage : " + pcn_stages
        data += "PRQ_Stage : " + prq_stages
        data += "PCN_Export_Loc : " + self.line_PCN_export.text()+"\n"
        data += "PCN_Web_Href : " + self.line_PCN_web.text()+"\n"
        try:
            f = open(initfile,'w')
            f.write(data)
            f.close()
            print(self.parent)
            if self.parent is not None:
                self.parent.loadSettings()
            self.dispMsg("Settings have been saved! Please restart application for settings to take effect.")
        except Exception as e:
            self.dispMsg(f"Error occured trying to save settings. Error: {e}")
        #print(data)
        
    def addDept(self):
        if self.line_dept.text()!="":
            self.list_dept.addItem(self.line_dept.text())
            self.line_dept.clear()

    def removeDept(self):
        for item in self.list_dept.selectedItems():
            self.list_dept.takeItem(self.list_dept.row(item))
            
    def addType(self):
        if self.line_ecn_type.text()!="":
            self.list_ecn_type.addItem(self.line_ecn_type.text())
            self.line_ecn_type.clear()
            
    def removeType(self):
        for item in self.list_ecn_type.selectedItems():
            self.list_ecn_type.takeItem(self.list_ecn_type.row(item))

    def addJob(self):
        self.table_jobs.insertRow(self.table_jobs.rowCount())
        
    def insertJob(self):
        self.table_jobs.insertRow(self.table_jobs.currentRow()+1)

    def removeJob(self):
        self.table_jobs.removeRow(self.table_jobs.currentRow())

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()

# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    settings = SettingsWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
