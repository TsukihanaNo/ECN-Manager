from PySide import QtGui, QtCore

class AdminWindow(QtGui.QWidget):
    def __init__(self,parent=None):
        super(AdminWindow,self).__init__()
        self.parent = parent
        self.windowWidth = self.parent.windowWidth
        self.windowHeight = self.parent.windowHeight
        self.menubar = QtGui.QMenuBar(self)
        self.initUI()


    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()-QtCore.QPoint(0,0))

    def initUI(self):
        self.createAdminActions()
        mainLayout = QtGui.QVBoxLayout(self)
        mainLayout.setMenuBar(self.menubar)

        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle("Manager - Admin")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        self.show()

    def createAdminActions(self):
        settingMenu = self.menubar.addMenu("&Settings")

        newDatabaseAction = QtGui.QAction("&New Database",self)

        openDatabaseAction = QtGui.QAction("&Open Databse",self)

        usersAction = QtGui.QAction("&Users",self)

        settingMenu.addAction(newDatabaseAction)
        settingMenu.addAction(openDatabaseAction)
        settingMenu.addAction(usersAction)