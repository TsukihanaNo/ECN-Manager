from PySide6 import QtWidgets, QtCore, QtGui
import os, sys


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class SignaturePanel(QtWidgets.QWidget):
    def __init__(self, parent = None, row = None, sig_type = None):
        super(SignaturePanel,self).__init__()
        self.windowWidth =  300
        self.windowHeight = 140
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.parent = parent
        self.sig_type = sig_type
        self.row = row
        self.job_titles =[]
        self.findJobTitles()
        self.initAtt()
        self.initUI()
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
        title = "Signature Editor"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.center()

    def initUI(self):
        #mainlayout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout(self)
        self.box_title = QtWidgets.QComboBox()
        self.box_title.currentIndexChanged.connect(self.setNameList)
        self.box_title.currentIndexChanged.connect(self.setUser)
        self.box_name = QtWidgets.QComboBox()
        self.box_user = QtWidgets.QComboBox()
        
        form_layout.addRow("Job Title:", self.box_title)
        form_layout.addRow("Name", self.box_name)
        form_layout.addRow("User", self.box_user)
        
        if self.row is None:
            self.setBoxJob()
            self.setBoxName()
            self.setBoxUser()
            self.button_add = QtWidgets.QPushButton("Add Signature")
            self.button_add.clicked.connect(self.addSignature)
            form_layout.addRow(self.button_add)
        else:
            self.setBoxJob(self.parent.model.get_job_title(self.row))
            self.setBoxName(self.parent.model.get_name(self.row))
            self.setBoxUser(self.parent.model.get_user(self.row))
            self.button_update = QtWidgets.QPushButton("Update Signature")
            self.button_update.clicked.connect(self.updateSignature)
            form_layout.addRow(self.button_update)
        
        #mainlayout.addLayout(form_layout)
        self.setLayout(form_layout)
        #self.setLayout(mainlayout)
        
    def addSignature(self):
        job_title = self.box_title.currentText()
        name = self.box_name.currentText()
        user = self.box_user.currentText()
        if self.checkDuplicate():
            self.dispMsg("This person already exists in list.")
        else:
            if self.sig_type=="Signing":
                if self.parent.parent.doc_id[:3]=="ECN":
                    if self.parent.parent.parent.stageDict[job_title]=="99":
                        self.dispMsg("This user is set for notification only. Please use the Notification Tab.")
                        return
                else:
                    if self.parent.parent.parent.stageDictPCN[job_title]=="99":
                        self.dispMsg("This user is set for notification only. Please use the notification Tab.")
                        return     
            self.parent.model.add_signature(job_title, name, user)
            
    def updateSignature(self):
        job_title = self.box_title.currentText()
        name = self.box_name.currentText()
        user = self.box_user.currentText()
        if self.checkDuplicate():
            self.dispMsg("This person already exists in list.")
        else:
            if self.sig_type=="Signing":
                if self.parent.parent.doc_id[:3]=="ECN":
                    if self.parent.parent.parent.stageDict[job_title]=="99":
                        self.dispMsg("This user is set for notification only.")
                        return
                else:
                    if self.parent.parent.parent.stageDictPCN[job_title]=="99":
                        self.dispMsg("This user is set for notification only.")
                        return     
            self.parent.model.add_signature(job_title, name, user)
        
    def setBoxJob(self,text=None):
        self.box_title.addItems(self.job_titles)
        if text is not None:
            self.box_title.setCurrentText(text)
        self.box_title.currentIndexChanged.connect(self.setNameList)
        self.box_title.currentIndexChanged.connect(self.setUser)
        
    def setBoxName(self,text=None):
        self.box_name.clear()
        command = "Select NAME,USER_ID from USER where JOB_TITLE = '" + self.box_title.currentText() +"'"
        self.parent.parent.cursor.execute(command)
        test = self.parent.parent.cursor.fetchall()
        names = []
        for item in test:
            if item[1]!=self.parent.parent.parent.user_info['user']:
                names.append(item[0])
        names.sort()
        self.box_name.addItems(names)
        if text is not None:
            self.box_name.setCurrentText(text)
        self.box_name.currentIndexChanged.connect(self.setUser)
        
    def setBoxUser(self, text=None):
        command = "Select USER_ID from USER where NAME = '" + self.box_name.currentText() +"'"
        self.parent.parent.cursor.execute(command)
        test = self.parent.parent.cursor.fetchall()
        names = []
        for item in test:
            names.append(item[0])
        self.box_user.addItems(names)
        if text is not None:
            self.box_user.setCurrentText(text)
            
    def setNameList(self):
        self.box_name.clear()
        command = "Select NAME from USER where JOB_TITLE = '" + self.box_title.currentText() +"' and STATUS='Active'"
        self.parent.parent.cursor.execute(command)
        test = self.parent.parent.cursor.fetchall()
        names = []
        for item in test:
            if item[0]!=self.parent.parent.parent.user_info['name']:
                names.append(item[0])
        names.sort()
        self.box_name.addItems(names)
        self.box_name.currentIndexChanged.connect(self.setUser)
        
    def setUser(self):
        self.box_user.clear()
        command = "Select USER_ID from USER where NAME = '" + self.box_name.currentText() +"'"
        self.parent.parent.cursor.execute(command)
        test = self.parent.parent.cursor.fetchall()
        users = []
        for item in test:
            users.append(item[0])
        self.box_user.addItems(users)
        
    def findJobTitles(self):
        self.parent.parent.cursor.execute("Select DISTINCT JOB_TITLE FROM USER")
        results = self.parent.parent.cursor.fetchall()
        for result in results:
            self.job_titles.append(result[0])
        if "Admin" in self.job_titles:
            self.job_titles.remove("Admin")
        if len(self.job_titles)==0:
            self.dispMsg("No Job Titles found, please add Jobs and Users.")
        else:
            self.job_titles.sort()
            
    def checkDuplicate(self):
        return self.box_user.currentText() in self.parent.model.users
        
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
