from PySide6 import QtWidgets, QtCore, QtGui
import os, sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class FileTransferWidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(FileTransferWidget,self).__init__()
        self.parent = parent
        self.windowWidth = 500
        self.windowHeight = 100
        self.can_close = True
        self.initAtt()
        self.initUI()
        self.center()
        self.show()
        
    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle(f"File Transfer")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMinimumWidth(self.windowWidth)
        
    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.label_directory = QtWidgets.QLabel("Generating")
        self.label_count = QtWidgets.QLabel("copying: 0/0")
        self.text_error = QtWidgets.QTextEdit()
        self.text_error.setReadOnly(True)
        mainlayout.addWidget(self.label_directory)
        mainlayout.addWidget(self.label_count)
        mainlayout.addWidget(self.text_error)
        
    def center(self):
        window = self.window()
        window.setGeometry(
            QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            window.size(),
            QtGui.QGuiApplication.primaryScreen().availableGeometry(),
        ),
    )
    
    def setClose(self,bool):
        self.can_close = bool
        
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def closeEvent(self,event):
        if self.can_close:
            self.close()
        else:
            self.dispMsg("File Transfer in progress, cannot close.")
            event.ignore()