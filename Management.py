import os, re, sys
import time, sqlite3
from PySide import QtGui, QtCore
from LoginWindow import *
from CompletedTab import *
from MyRequestTab import *
from QueueTab import *


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

db_loc = os.path.join(program_location, "DB\Request_DB")

class Manager(QtGui.QWidget):
    def __init__(self):
        super(Manager,self).__init__()
        self.windowWidth = 800
        self.windowHeight = 500
        self.db = sqlite3.connect(db_loc)
        self.cursor = self.db.cursor()
        self.loginWindow = LoginWindow(self)
        self.user_info = {}

        #self.dbTest()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()-QtCore.QPoint(0,0))

    def loginDone(self):
        self.initUI()

    # def dbTest(self):
    #     print("initiating test")
    #     self.cursor.execute("SELECT * FROM ECN")
    #     test = self.cursor.fetchall()
    #     print(len(test))
    #     for item in test:
    #         print(item)

    def initUI(self):
        mainLayout = QtGui.QVBoxLayout(self)
        #mainLayout.setMenuBar(self.menubar)
        self.tabWidget = QtGui.QTabWidget(self)
        myRequestTab = MyRequestTab(self)
        mainLayout.addWidget(self.tabWidget)
        self.tabWidget.addTab(myRequestTab, "My Requests")

        if self.user_info['role']=="Engineer":
            queueTab = QueueTab(self)
            self.tabWidget.addTab(queueTab, "My Queue")

        completedTab = CompletedTab(self)
        self.tabWidget.addTab(completedTab, "Completed")

        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle("Manager - Standard")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        #self.setWindowOpacity(0)
        self.show()
        #self.loadInAnimation()

    #def readUser(self):



#execute the program
def main():
    app = QtGui.QApplication(sys.argv)
    manager = Manager()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

