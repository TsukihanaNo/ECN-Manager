from PySide6 import QtWidgets, QtCore

class TasksTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(TasksTab,self).__init__()
        self.parent = parent
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAcceptDrops(True)

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.list_attachment = QtWidgets.QListWidget(self)
        mainlayout.addWidget(self.list_attachment)


