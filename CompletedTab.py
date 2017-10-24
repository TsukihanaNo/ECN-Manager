from PySide import QtGui, QtCore
from MyTableWidget import *

class CompletedTab(QtGui.QWidget):
    def __init__(self,parent=None):
        super(CompletedTab,self).__init__()
        self.parent = parent
        self.table = MyTableWdiget(24,3,self)
        self.button_open = QtGui.QPushButton("Open",self)
        self.initUI()

    def initUI(self):
        vlayout = QtGui.QVBoxLayout(self)
        vlayout.addWidget(self.table)
        vlayout.addWidget(self.button_open)

        vlayout.setAlignment(QtCore.Qt.AlignCenter)

        self.button_open.setFixedWidth(200)


        self.setLayout(vlayout)

