import os, re, sys
import time
import sqlite3
from PySide6 import QtGui, QtCore, QtWidgets
from MyLineEdit import *

class LoginWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(LoginWindow,self).__init__()
        self.parent = parent
        self.windowWidth = 350
        self.windowHeight = 200
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        self.logged = False

        self.initAtt()
        self.initUI()

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

    def loginMenu(self):
        self.text_user = MyLineEdit(self)
        self.text_pass = MyLineEdit(self)
        self.button_login = QtWidgets.QPushButton("Login",self)

        self.button_login.setFixedWidth(100)
        textLayout = QtWidgets.QVBoxLayout(self)
        textLayout.setAlignment(QtCore.Qt.AlignCenter)
        buttonLayout = QtWidgets.QHBoxLayout(self)
        buttonLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.text_pass.setFixedWidth(300)
        self.text_pass.setAlignment(QtCore.Qt.AlignCenter)
        self.text_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.text_user.setFixedWidth(300)
        self.text_user.setAlignment(QtCore.Qt.AlignCenter)
        label_user = QtWidgets.QLabel("User:")
        label_pass = QtWidgets.QLabel("Password:")
        textLayout.addWidget(label_user)
        textLayout.addWidget(self.text_user)
        textLayout.addWidget(label_pass)
        textLayout.addWidget(self.text_pass)
        buttonLayout.addWidget(self.button_login)
        textLayout.addLayout(buttonLayout)

    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle("Manager")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def initUI(self):
        self.loginMenu()

        self.button_login.clicked.connect(self.checkUserPass)
        self.text_pass.returnPressed.connect(self.checkUserPass)

        self.center()
        self.show()

    def loginAnimation(self):
        # for x in range(50):
        #     QtWidgets.QApplication.processEvents()
        #     self.setWindowOpacity(1-2*x/100)
        #     time.sleep(0.01)
        #self.hide()
        self.parent.user = self.text_user.text()
        self.parent.loginDone()
        self.close()

    def checkUserPass(self):
        #print("initiating check")
        self.cursor.execute("SELECT USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE  FROM USER WHERE USER_ID=:id",{"id":self.text_user.text()})
        info = self.cursor.fetchone()
        # print(len(info))
        # for item in info:
        #     print(item)
        if info is not None:
            if self.text_pass.text()==info['PASSWORD']:
                self.parent.user_info['user'] = info['USER_ID']
                self.parent.user_info['name'] = info['NAME']
                self.parent.user_info['role'] = info['ROLE']
                self.parent.user_info['title'] = info['JOB_TITLE']
                self.parent.loginDone()
                self.logged = True
                self.close()
            else:
                self.dispMsg("Incorrect password")
        else:
            self.dispMsg("User does not exist")
            
    def closeEvent(self, event):
        if self.logged == False:
            self.parent.close()
        

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
