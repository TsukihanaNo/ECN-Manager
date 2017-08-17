from PySide import QtGui, QtCore

class TasksTab(QtGui.QWidget):
    def __init__(self, parent = None):
        super(TasksTab,self).__init__()
        self.parent = parent
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAcceptDrops(True)

    def initUI(self):
        mainlayout = QtGui.QVBoxLayout(self)
        self.list_attachment = QtGui.QListWidget(self)
        mainlayout.addWidget(self.list_attachment)


