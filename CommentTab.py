from PySide2 import QtWidgets, QtGui, QtCore

class CommentTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(CommentTab,self).__init__()
        self.parent = parent
        self.initAtt()
        self.initUI()
        
    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        label_mainText = QtWidgets.QLabel("Current Comments:")
        label_enterText = QtWidgets.QLabel("Comment to be entered:")
        self.mainText = QtWidgets.QTextEdit(self)
        self.mainText.setReadOnly(True)
        self.enterText = QtWidgets.QTextEdit(self)
        self.enterText.setMaximumHeight(300)
        mainlayout.addWidget(label_mainText)
        mainlayout.addWidget(self.mainText)
        mainlayout.addWidget(label_enterText)
        mainlayout.addWidget(self.enterText)
        