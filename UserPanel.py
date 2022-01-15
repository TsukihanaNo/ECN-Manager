from PySide6 import QtWidgets, QtCore, QtGui
import os, sys
import sqlite3  


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class UserPanel(QtWidgets.QWidget):
    def __init__(self,parent=None,user=None,func=None):
        super(UserPanel,self).__init__()
        self.windowWidth =  400
        self.windowHeight = 550
        self.user = user
        self.func = func
        self.parent = parent
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        self.initAtt()
        self.initUI()
        if self.func is not None:
            if self.func != "add":
                self.loadInfo()
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
        title = "Users Panel"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        #USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, DEPT TEXT, STATUS TEXT, EMAIL TEXT)        
        label_user = QtWidgets.QLabel("User ID:")
        self.line_user = QtWidgets.QLineEdit(self)
        if self.func !="add":
            self.line_user.setDisabled(True)
        label_pass = QtWidgets.QLabel("Password:")
        self.line_pass = QtWidgets.QLineEdit(self)
        label_name = QtWidgets.QLabel("Name:")
        self.line_name = QtWidgets.QLineEdit(self)
        label_role = QtWidgets.QLabel("Role:")
        self.combo_role = QtWidgets.QComboBox(self)
        self.combo_role.addItems(['Admin','Engineer','Manager','Signer',])
        label_title = QtWidgets.QLabel("Job Title:")
        self.combo_title = QtWidgets.QComboBox(self)
        jobs = []
        for job in self.parent.settings["Job_Titles"].split(","):
            jobs.append(job.strip())
        print(jobs)
        self.combo_title.addItems(jobs)
        label_dept = QtWidgets.QLabel("Department:")
        self.combo_dept = QtWidgets.QComboBox(self)
        depts = []
        for dept in self.parent.settings["Dept"].split(","):
            depts.append(dept.strip())
        self.combo_dept.addItems(depts)
        label_status = QtWidgets.QLabel("Status:")
        self.combo_status = QtWidgets.QComboBox(self)
        self.combo_status.addItems(['Active','Inactive'])
        label_email = QtWidgets.QLabel("Email:")
        self.line_email = QtWidgets.QLineEdit(self)

        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.clicked.connect(self.save)
        
        main_layout.addWidget(label_user)
        main_layout.addWidget(self.line_user)
        main_layout.addWidget(label_pass)
        main_layout.addWidget(self.line_pass)
        main_layout.addWidget(label_name)
        main_layout.addWidget(self.line_name)
        main_layout.addWidget(label_role)
        main_layout.addWidget(self.combo_role)
        main_layout.addWidget(label_title)
        main_layout.addWidget(self.combo_title)
        main_layout.addWidget(label_dept)
        main_layout.addWidget(self.combo_dept)
        main_layout.addWidget(label_status)
        main_layout.addWidget(self.combo_status)
        main_layout.addWidget(label_email)
        main_layout.addWidget(self.line_email)
        main_layout.addWidget(self.button_save)
        
    def loadInfo(self):
        self.cursor.execute(f"Select * from USER where USER_ID='{self.user}'")
        result = self.cursor.fetchone()
        self.line_user.setText(result['USER_ID'])
        self.line_pass.setText(result['PASSWORD'])
        self.line_name.setText(result['NAME'])
        self.combo_role.setCurrentText(result['ROLE'])
        self.combo_title.setCurrentText(result['JOB_TITLE'])
        self.combo_dept.setCurrentText(result['DEPT'])
        self.combo_status.setCurrentText(result['STATUS'])
        self.line_email.setText(result['EMAIL'])
        
    def checkFields(self):
        if self.line_user.text()=="":
            return False
        if self.line_pass.text()=="":
            return False
        if self.line_name.text()=="":
            return False
        if self.line_email.text()=="":
            return False
        return True
    
    def checkPassField(self):
        if " " in self.line_pass.text():
            self.dispMsg("Please remove spaces in your password.")
            return False
        return True
    
    def checkEmailField(self):
        if "@" not in self.line_email.text():
            self.dispMsg("Email not in proper format")
            return False
        return True
    
    def existUser(self):
        self.cursor.execute(f"Select * from USER where USER_ID='{self.line_user.text()}'")
        result = self.cursor.fetchone()
        print(result)
        if result is None:
            return False
        else:
            return True

    def save(self):
        if self.checkFields():
            if self.checkPassField() and self.checkEmailField():
                if self.existUser():
                    data = (self.line_pass.text(),self.line_name.text(),self.combo_role.currentText(),self.combo_title.currentText(),self.combo_status.currentText(),self.combo_dept.currentText(),self.line_email.text(),self.line_user.text())
                    self.cursor.execute("UPDATE USER SET PASSWORD = ? , NAME = ?, ROLE = ?, JOB_TITLE = ?, STATUS = ?, DEPT = ?, EMAIL = ? WHERE USER_ID = ?",(data))
                    self.db.commit()
                    self.dispMsg("User Info has been updated!")
                else:
                    data = (self.line_user.text(),self.line_pass.text(),self.line_name.text(),self.combo_role.currentText(),self.combo_title.currentText(),self.combo_status.currentText(),self.combo_dept.currentText(),self.line_email.text())
                    self.cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, STATUS, DEPT, EMAIL) VALUES(?,?,?,?,?,?,?,?)',(data))
                    self.db.commit()
                    self.dispMsg("User has been added!")
                self.parent.repopulateTable()
        else:
            self.dispMsg("There are empty fields.")


    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()