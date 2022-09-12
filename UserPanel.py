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
        main_layout = QtWidgets.QVBoxLayout()
        self.toolbar = QtWidgets.QToolBar(self)
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_general = GeneralTab(self)
        self.tab_permissions = PermissionsTab(self)
        self.tab_widget.addTab(self.tab_general, "General")
        self.tab_widget.addTab(self.tab_permissions, "Permissions")
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.tab_widget)

        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.clicked.connect(self.save)
        self.button_clear = QtWidgets.QPushButton("Clear")
        self.button_clear.clicked.connect(self.clearFields)
        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_clear)
        
        if self.func=="user_edit":
            self.button_clear.setEnabled(False)
            self.tab_general.line_name.setEnabled(False)
            self.tab_general.combo_dept.setEnabled(False)
            self.tab_general.combo_title.setEnabled(False)
            self.tab_general.combo_status.setEnabled(False)
            self.tab_widget.setTabVisible(1, False)
        self.setLayout(main_layout)
        
    def loadInfo(self):
        self.cursor.execute(f"Select * from USER where USER_ID='{self.user}'")
        result = self.cursor.fetchone()
        self.tab_general.line_user.setText(result['USER_ID'])
        self.tab_general.line_pass.setText(result['PASSWORD'])
        self.tab_general.line_name.setText(result['NAME'])
        self.tab_general.combo_title.setCurrentText(result['JOB_TITLE'])
        self.tab_general.combo_dept.setCurrentText(result['DEPT'])
        self.tab_general.combo_status.setCurrentText(result['STATUS'])
        self.tab_general.line_email.setText(result['EMAIL'])
        self.cursor.execute(f"Select * from PERMISSIONS where USER_ID='{self.user}'")
        result = self.cursor.fetchone()
        check_dict = {"y":QtCore.Qt.Checked,"n":QtCore.Qt.Unchecked, None : QtCore.Qt.Unchecked}
        if result is not None:
            self.tab_permissions.check_ecn.setCheckState(check_dict[result["CREATE_ECN"]])
            self.tab_permissions.check_pcn.setCheckState(check_dict[result["CREATE_PCN"]])
            self.tab_permissions.check_create_user.setCheckState(check_dict[result["CREATE_USER"]])
            self.tab_permissions.check_settings.setCheckState(check_dict[result["ACCESS_SETTINGS"]])
            self.tab_permissions.check_view_analytics.setCheckState(check_dict[result["VIEW_ANALYTICS"]])
            self.tab_permissions.check_reject_signer.setCheckState(check_dict[result["REJECT_SIGNER"]])
            self.tab_permissions.check_rerouting.setCheckState(check_dict[result["REROUTING"]])
        
    def checkFields(self):
        if self.tab_general.line_user.text()=="":
            return False
        if self.tab_general.line_pass.text()=="":
            return False
        if self.tab_general.line_name.text()=="":
            return False
        if self.tab_general.line_email.text()=="":
            return False
        return True
    
    def checkPassField(self):
        if " " in self.tab_general.line_pass.text():
            self.dispMsg("Please remove spaces in your password.")
            return False
        return True
    
    def checkEmailField(self):
        if "@" not in self.tab_general.line_email.text():
            self.dispMsg("Email not in proper format")
            return False
        return True
    
    def existUser(self):
        self.cursor.execute(f"Select * from USER where USER_ID='{self.tab_general.line_user.text()}'")
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
                    data = (self.tab_general.line_pass.text(),self.tab_general.line_name.text(),self.tab_general.combo_title.currentText(),self.tab_general.combo_status.currentText(),self.tab_general.combo_dept.currentText(),self.tab_general.line_email.text(),self.tab_general.line_user.text())
                    self.cursor.execute("UPDATE USER SET PASSWORD = ? , NAME = ?, JOB_TITLE = ?, STATUS = ?, DEPT = ?, EMAIL = ? WHERE USER_ID = ?",(data))
                    self.db.commit()
                    if self.func != "user_edit":
                        self.savePermissions()
                    self.dispMsg("User Info has been updated!")
                else:
                    data = (self.tab_general.line_user.text(),self.tab_general.line_pass.text(),self.tab_general.line_name.text(),self.tab_general.combo_title.currentText(),self.tab_general.combo_status.currentText(),self.tab_general.combo_dept.currentText(),self.tab_general.line_email.text())
                    self.cursor.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, JOB_TITLE, STATUS, DEPT, EMAIL) VALUES(?,?,?,?,?,?,?)',(data))
                    self.db.commit()
                    if self.func != "user_edit":
                        self.savePermissions()
                    self.dispMsg("User has been added!")
                self.parent.repopulateTable()
        else:
            self.dispMsg("There are empty fields.")
            
    def savePermissions(self):
        self.cursor.execute(f"select * from PERMISSIONS where USER_ID='{self.user}'")
        result = self.cursor.fetchone()
        check_dict = {QtCore.Qt.Checked:"y",QtCore.Qt.Unchecked:"n"}
        if result is not None:
            data = (check_dict[self.tab_permissions.check_ecn.checkState()],check_dict[self.tab_permissions.check_pcn.checkState()],check_dict[self.tab_permissions.check_create_user.checkState()],check_dict[self.tab_permissions.check_reject_signer.checkState()],check_dict[self.tab_permissions.check_settings.checkState()],check_dict[self.tab_permissions.check_view_analytics.checkState()],check_dict[self.tab_permissions.check_rerouting.checkState()],self.tab_general.line_user.text())
            self.cursor.execute(f"UPDATE PERMISSIONS SET CREATE_ECN = ?, CREATE_PCN = ?, CREATE_USER = ?, REJECT_SIGNER = ?, ACCESS_SETTINGS = ?, VIEW_ANALYTICS = ?, REROUTING = ? WHERE USER_ID = ?", (data))
        else:
            data = (self.tab_general.line_user.text(),check_dict[self.tab_permissions.check_ecn.checkState()],check_dict[self.tab_permissions.check_pcn.checkState()],check_dict[self.tab_permissions.check_create_user.checkState()],check_dict[self.tab_permissions.check_reject_signer.checkState()],check_dict[self.tab_permissions.check_settings.checkState()],check_dict[self.tab_permissions.check_view_analytics.checkState()],check_dict[self.tab_permissions.check_rerouting.checkState()])
            self.cursor.execute(f"INSERT INTO PERMISSIONS(USER_ID,CREATE_ECN, CREATE_PCN, CREATE_USER, REJECT_SIGNER, ACCESS_SETTINGS, VIEW_ANALYTICS, REROUTING) VALUES (?,?,?,?,?,?,?,?)",(data))
        self.db.commit()
            
#cursor.execute('CREATE TABLE PERMISSIONS(USER_ID TEXT, CREATE_ECN TEXT, CREATE_PCN TEXT, CREATE_USER TEXT, REJECT_SIGNER TEXT, ACCESS_SETTINGS TEXT, VIEW_ANALYTICS TEXT)')
    def clearFields(self):
        self.tab_general.line_user.clear()
        self.tab_general.line_pass.clear()
        self.tab_general.line_name.clear()
        self.tab_general.line_email.clear()

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
        
class PermissionsTab(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(PermissionsTab,self).__init__()
        self.parent = parent
        self.initUI()
        #self.show()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()
        self.check_ecn = QtWidgets.QCheckBox()
        self.check_pcn = QtWidgets.QCheckBox()
        self.check_project = QtWidgets.QCheckBox()
        self.check_create_user = QtWidgets.QCheckBox()
        self.check_view_analytics = QtWidgets.QCheckBox()
        self.check_reject_signer = QtWidgets.QCheckBox()
        self.check_settings = QtWidgets.QCheckBox()
        self.check_rerouting = QtWidgets.QCheckBox()
        form_layout.addRow("Allow user to create ECNs:",self.check_ecn)
        form_layout.addRow("Allow user to create PCNs:",self.check_pcn)
        form_layout.addRow("Allow user to create Projects:",self.check_project)
        form_layout.addRow("Allow user to reject to signer:",self.check_reject_signer)
        form_layout.addRow("Allow user to access settings:", self.check_settings)
        form_layout.addRow("Allow user to create users:", self.check_create_user)
        form_layout.addRow("Allow user to view Analytics:",self.check_view_analytics)
        form_layout.addRow("Allow user to check for rerouting:",self.check_rerouting)

        main_layout.addLayout(form_layout)

        self.setLayout(main_layout)
        

class GeneralTab(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(GeneralTab,self).__init__()
        self.parent = parent
        self.initUI()
        #self.show()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        #USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, DEPT TEXT, STATUS TEXT, EMAIL TEXT)        
        label_user = QtWidgets.QLabel("User ID:")
        self.line_user = QtWidgets.QLineEdit(self)
        label_pass = QtWidgets.QLabel("Password:")
        self.line_pass = QtWidgets.QLineEdit(self)
        self.line_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        label_name = QtWidgets.QLabel("Name:")
        self.line_name = QtWidgets.QLineEdit(self)
        label_title = QtWidgets.QLabel("Job Title:")
        self.combo_title = QtWidgets.QComboBox(self)
        jobs = []
        for job in self.parent.parent.settings["Job_Titles"].split(","):
            jobs.append(job.strip())
        print(jobs)
        self.combo_title.addItems(jobs)
        label_dept = QtWidgets.QLabel("Department:")
        self.combo_dept = QtWidgets.QComboBox(self)
        depts = []
        for dept in self.parent.parent.settings["Dept"].split(","):
            depts.append(dept.strip())
        self.combo_dept.addItems(depts)
        label_status = QtWidgets.QLabel("Status:")
        self.combo_status = QtWidgets.QComboBox(self)
        self.combo_status.addItems(['Active','Inactive'])
        label_email = QtWidgets.QLabel("Email:")
        self.line_email = QtWidgets.QLineEdit(self)
        main_layout.addWidget(label_user)
        main_layout.addWidget(self.line_user)
        main_layout.addWidget(label_pass)
        main_layout.addWidget(self.line_pass)
        main_layout.addWidget(label_name)
        main_layout.addWidget(self.line_name)
        main_layout.addWidget(label_title)
        main_layout.addWidget(self.combo_title)
        main_layout.addWidget(label_dept)
        main_layout.addWidget(self.combo_dept)
        main_layout.addWidget(label_status)
        main_layout.addWidget(self.combo_status)
        main_layout.addWidget(label_email)
        main_layout.addWidget(self.line_email)
