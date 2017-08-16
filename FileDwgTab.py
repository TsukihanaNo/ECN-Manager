from PySide import QtGui, QtCore

class FileDwgTab(QtGui.QWidget):
    def __init__(self, parent = None):
        super(FileDwgTab,self).__init__()
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

    def dropEvent(self, e):
        urlList = e.mimeData().urls()
        for item in urlList:
            listItem = QtGui.QListWidgetItem(item.toLocalFile(),self.list_attachment)
        print(self.list_attachment.count())


    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

