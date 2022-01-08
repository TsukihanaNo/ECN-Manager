from PySide2 import QtWidgets, QtCore, QtWidgets

class PurchaserTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(PurchaserTab,self).__init__()
        self.parent = parent
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)


