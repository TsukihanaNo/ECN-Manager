from PySide import QtGui, QtCore

class EngineerTab(QtGui.QWidget):
    def __init__(self, parent = None):
        super(EngineerTab,self).__init__()
        self.parent = parent
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        mainlayout = QtGui.QVBoxLayout(self)

        self.cbpurch = QtGui.QCheckBox("purchasing",self)
        self.cbplanner = QtGui.QCheckBox("planner",self)
        self.cbshop = QtGui.QCheckBox("shop",self)

        self.cbpurch.stateChanged.connect(self.parent.togglePurchTab)
        self.cbplanner.stateChanged.connect(self.parent.togglePlannerTab)
        self.cbshop.stateChanged.connect(self.parent.toggleShopTab)
        mainlayout.addWidget(self.cbpurch)
        mainlayout.addWidget(self.cbplanner)
        mainlayout.addWidget(self.cbshop)


