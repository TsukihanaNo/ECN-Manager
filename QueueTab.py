from PySide import QtGui, QtCore
import sqlite3  

class QueueTab(QtGui.QWidget):
    def __init__(self,parent=None):
        super(QueueTab,self).__init__()
        self.parent = parent
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.initUI()

    def initUI(self):
        titles = ['ECN ID','Type', 'Title', 'Requestor', 'Status', 'Request Date', 'Assigned Date']
        self.table = QtGui.QTableWidget(24,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.button_open = QtGui.QPushButton("Open",self)

        vlayout = QtGui.QVBoxLayout(self)
        hlayout = QtGui.QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        vlayout.addWidget(self.table)
        hlayout.addWidget(self.button_open)
        vlayout.addLayout(hlayout)
        vlayout.setAlignment(QtCore.Qt.AlignCenter)

        self.button_open.setFixedWidth(200)

        self.setLayout(vlayout)

