from PySide import QtGui, QtCore
from QueueTab import *
from CompletedTab import *
import time

class EngineerWindow(QtGui.QWidget):
    def __init__(self,parent=None):
        super(EngineerWindow,self).__init__()
        self.parent = parent
        self.windowWidth = self.parent.windowWidth
        self.windowHeight = self.parent.windowHeight
        #self.menubar = QtGui.QMenuBar(self)
        self.initUI()


    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()-QtCore.QPoint(0,0))

    def initUI(self):
        mainLayout = QtGui.QVBoxLayout(self)
        #mainLayout.setMenuBar(self.menubar)
        self.tabWidget = QtGui.QTabWidget(self)
        queueTab = QueueTab(self)
        completedTab = CompletedTab(self)
        mainLayout.addWidget(self.tabWidget)
        self.tabWidget.addTab(queueTab, "Queue")
        self.tabWidget.addTab(completedTab, "Completed")


        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle("Manager - Engineer")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        self.setWindowOpacity(0)
        self.show()
        self.loadInAnimation()

    def loadInAnimation(self):
        for x in range(50):
            QtGui.QApplication.processEvents()
            self.setWindowOpacity(2*x/100)
            time.sleep(0.02)
