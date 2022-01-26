from tkinter import mainloop
from wsgiref import headers
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
        self.windowWidth =  int(580*0.75)
        self.windowHeight = int(830*0.75)
        if parent is None:
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
            self.parent = parent
            self.settings = parent.settings
            self.db = self.parent.db
            self.cursor = self.parent.cursor
        self.initAtt()
        self.initUI()
        self.getStageDict()
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
        main_layout = QtWidgets.QVBoxLayout(self)
        self.label_db = QtWidgets.QLabel("DB Loc:")
        self.line_db = QtWidgets.QLineEdit(self)
        self.button_db = QtWidgets.QPushButton("Browse")
        layout_db = QtWidgets.QHBoxLayout()
        layout_db.addWidget(self.line_db)
        layout_db.addWidget(self.button_db)
        main_layout.addWidget(self.label_db)
        main_layout.addLayout(layout_db)
        self.label_smpt = QtWidgets.QLabel("SMPT: IP/Port")
        self.line_smpt_address = QtWidgets.QLineEdit(self)
        self.line_smpt_address.setPlaceholderText("SMPT Address")
        self.line_smpt_port = QtWidgets.QLineEdit(self)
        self.line_smpt_port.setPlaceholderText("SMPT Port")
        main_layout.addWidget(self.label_smpt)
        main_layout.addWidget(self.line_smpt_address)
        main_layout.addWidget(self.line_smpt_port)
        self.label_dept = QtWidgets.QLabel("Dept:")
        self.line_dept = QtWidgets.QLineEdit(self)
        self.line_dept.returnPressed.connect(self.addDept)
        self.button_dept_add = QtWidgets.QPushButton("Add")
        self.button_dept_add.clicked.connect(self.addDept)
        self.list_dept = QtWidgets.QListWidget(self)
        self.list_dept.doubleClicked.connect(self.removeDept)
        self.button_dept_remove = QtWidgets.QPushButton("Remove")
        self.button_dept_remove.clicked.connect(self.removeDept)
        self.label_jobs = QtWidgets.QLabel("Job Titles:")
        headers = ['Job Title','Stage']
        self.table_jobs = QtWidgets.QTableWidget(0,len(headers),self)
        self.table_jobs.setHorizontalHeaderLabels(headers)
        self.table_jobs.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.button_jobs_add = QtWidgets.QPushButton("Add")
        self.button_jobs_add.clicked.connect(self.addJob)
        self.button_jobs_remove = QtWidgets.QPushButton("Remove")
        self.button_jobs_remove.clicked.connect(self.removeJob)
        self.button_save = QtWidgets.QPushButton("Save Settings")
        self.button_save.clicked.connect(self.saveSettings)
        layout_buttons_jobs = QtWidgets.QHBoxLayout()
        layout_buttons_jobs.addWidget(self.button_jobs_add)
        layout_buttons_jobs.addWidget(self.button_jobs_remove)
        layout_dept = QtWidgets.QHBoxLayout()
        layout_dept.addWidget(self.line_dept)
        layout_dept.addWidget(self.button_dept_add)
        main_layout.addWidget(self.label_dept)
        main_layout.addLayout(layout_dept)
        main_layout.addWidget(self.list_dept)
        main_layout.addWidget(self.button_dept_remove)
        main_layout.addWidget(self.label_jobs)
        main_layout.addWidget(self.table_jobs)
        main_layout.addLayout(layout_buttons_jobs)
        main_layout.addWidget(self.button_save)
        #main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def getStageDict(self):
        self.stageDict = {}
        stages = self.settings["Stage"].split(",")
        for stage in stages:
            key,value = stage.split("-")
            self.stageDict[key.strip()] = value.strip()
        #print(self.stageDict)


    def loadSettings(self):
        self.line_db.setText(self.settings["DB_LOC"])
        if "SMPT" in self.settings.keys():
            self.line_smpt_address.setText(self.settings["SMTP"])
        if "Port" in self.settings.keys():
            self.line_smpt_port.setText(self.settings["Port"])
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
                row+=1

    def saveSettings(self):
        data = ""
        data += "DB_LOC : " + self.line_db.text()+"\n"
        if self.line_smpt_address.text()!="":
            if self.line_smpt_port.text()!="":
                data += "SMTP : " + self.line_smpt_address.text() + "\n"
                data += "Port : " + self.line_smpt_port.text() +"\n"
            else:
                self.dispMsg("Missing SMTP Port.")
        data += "Dept : "
        for x in range(self.list_dept.count()):
            if x < self.list_dept.count()-1:
                data += self.list_dept.item(x).text()+","
            else:
                data += self.list_dept.item(x).text()+"\n"
        jobs = ""
        stages = ""
        for x in range(self.table_jobs.rowCount()):
            #print(x,self.table_jobs.item(x, 0).text(),self.table_jobs.item(x, 1).text())
            if x < self.table_jobs.rowCount()-1:
                jobs += self.table_jobs.item(x, 0).text()+","
                stages += self.table_jobs.item(x, 0).text() + "-" + self.table_jobs.item(x, 1).text() + ","
            else:
                jobs += self.table_jobs.item(x, 0).text()+"\n"
                stages += self.table_jobs.item(x, 0).text() + "-" + self.table_jobs.item(x, 1).text() + "\n"
        data += "Job_Titles : " + jobs
        data += "Stage : " + stages
        try:
            f = open(initfile,'w')
            f.write(data)
            f.close()
            if self.parent is not None:
                self.parent.loadSettings()
            self.dispMsg("Settings have been saved!")
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

    def addJob(self):
        self.table_jobs.insertRow(self.table_jobs.rowCount())

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
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
