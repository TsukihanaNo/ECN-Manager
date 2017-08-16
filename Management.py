import os, re, sys
import time, sqlite3
from PySide import QtGui, QtCore
from LoginWindow import *
from SlidingStackedWidget import *
from CompletedTab import *
from MyRequestTab import *
from QueueTab import *


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

db_loc = os.path.join(program_location, "DB","Request_DB")

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
        self.initAtt()
        self.initUI()
        self.center()
        self.show()
        self.loadInAnim()

    # def dbTest(self):
    #     print("initiating test")
    #     self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    #     test = self.cursor.fetchall()
    #     print(len(test))
    #     for item in test:
    #         print(item)

    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        title = "Manager - User: " + self.user_info["user"]
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def initUI(self):
        mainLayout = QtGui.QVBoxLayout(self)

        #mainLayout.setMenuBar(self.menubar)
        self.tabWidget = QtGui.QTabWidget(self)
        
        self.myRequestTab = MyRequestTab(self)
        mainLayout.addWidget(self.tabWidget)


        self.tabWidget.addTab(self.myRequestTab, "My Requests")
        
        if self.user_info['role']=="Engineer":
            self.queueTab = QueueTab(self)
            self.tabWidget.addTab(self.queueTab, "My Queue")

        self.completedTab = CompletedTab(self)
        self.tabWidget.addTab(self.completedTab, "Completed")
        

    def loadInAnim(self):
        loc = self.tabWidget.pos()
        self.animation = QtCore.QPropertyAnimation(self.tabWidget,"pos")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutBack)
        self.animation.setStartValue(QtCore.QPoint(self.tabWidget.pos().x(),-self.windowHeight))
        self.animation.setEndValue(QtCore.QPoint(loc))

        self.animation.start()

    def closeEvent(self, event):
        for w in QtGui.qApp.allWidgets():
            w.close()


#execute the program
def main():
    app = QtGui.QApplication(sys.argv)
    manager = Manager()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

