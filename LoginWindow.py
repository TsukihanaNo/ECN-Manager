import os, re, sys
import time
import sqlite3
from PySide import QtGui, QtCore
from MyLineEdit import *

class LoginWindow(QtGui.QWidget):
    def __init__(self,parent=None):
        super(LoginWindow,self).__init__()
        self.parent = parent
        self.windowWidth = 400
        self.windowHeight = 175
        self.db = self.parent.db
        self.cursor = self.parent.cursor

        self.text_user = MyLineEdit(self)
        self.text_pass = MyLineEdit(self)
        self.button_login = QtGui.QPushButton("Login",self)
        self.initUI()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()-QtCore.QPoint(0,0))

    def loginMenu(self):
        self.button_login.setFixedWidth(100)
        textLayout = QtGui.QVBoxLayout(self)
        textLayout.setAlignment(QtCore.Qt.AlignCenter)
        buttonLayout = QtGui.QHBoxLayout(self)
        buttonLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.text_pass.setFixedWidth(300)
        self.text_pass.setAlignment(QtCore.Qt.AlignCenter)
        self.text_pass.setEchoMode(QtGui.QLineEdit.Password)
        self.text_user.setFixedWidth(300)
        self.text_user.setAlignment(QtCore.Qt.AlignCenter)
        label_user = QtGui.QLabel("User:")
        label_pass = QtGui.QLabel("Password:")
        textLayout.addWidget(label_user)
        textLayout.addWidget(self.text_user)
        textLayout.addWidget(label_pass)
        textLayout.addWidget(self.text_pass)
        buttonLayout.addWidget(self.button_login)
        textLayout.addLayout(buttonLayout)

    def initUI(self):
        self.loginMenu()

        self.button_login.clicked.connect(self.checkUserPass)
        self.text_pass.returnPressed.connect(self.checkUserPass)

        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle("Manager")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        self.show()

    def loginAnimation(self):
        # for x in range(50):
        #     QtGui.QApplication.processEvents()
        #     self.setWindowOpacity(1-2*x/100)
        #     time.sleep(0.01)
        #self.hide()
        self.parent.user = self.text_user.text()
        self.parent.loginDone()
        self.close()

    def checkUserPass(self):
        print("initiating check")
        self.cursor.execute("SELECT USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE  FROM USER WHERE USER_ID=:id",{"id":self.text_user.text()})
        info = self.cursor.fetchall()
        # print(len(info))
        # for item in info:
        #     print(item)
        if len(info)!=0:
            if self.text_pass.text()==info[0][1]:
                self.parent.user_info['user'] = info[0][0]
                self.parent.user_info['name'] = info[0][2]
                self.parent.user_info['role'] = info[0][3]
                self.parent.user_info['title'] = info[0][4]
                self.parent.loginDone()
                self.close()
            else:
                self.dispMsg("Incorrect password")
        else:
            self.dispMsg("User does not exist")
        

    def dispMsg(self,msg):
        msgbox = QtGui.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec_()
