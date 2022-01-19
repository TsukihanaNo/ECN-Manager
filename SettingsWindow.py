from PySide6 import QtWidgets, QtCore, QtGui
import os, sys
from MyTableWidget import *
from UserPanel import *
import sqlite3  


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class SettingsWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(SettingsWindow,self).__init__()
        self.windowWidth =  int(580*0.75)
        self.windowHeight = int(830*0.75)
        if parent is None:
            print("geting stuff")
            f = open(initfile,'r')
            self.settings = {}
            for line in f:
                key,value = line.split(" : ")
                self.settings[key]=value.strip()
            print(self.settings)
            f.close()
            self.db = sqlite3.connect(self.settings["DB_LOC"])
            self.cursor = self.db.cursor()
            self.cursor.row_factory = sqlite3.Row
        else:
            self.parent = parent
            self.settings = parent.settings
            self.db = self.parent.db
            self.cursor = self.parent.cursor
        self.initAtt()
        self.initUI()
        self.show()

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


    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        title = "Users Window"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        
        

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        self.label_smpt = QtWidgets.QLabel("SMPT: IP/Port")
        self.line_smpt_address = QtWidgets.QLineEdit(self)
        self.line_smpt_address.setPlaceholderText("SMPT Address")
        self.line_smpt_port = QtWidgets.QLineEdit(self)
        self.line_smpt_port.setPlaceholderText("SMPT Port")
        main_layout.addWidget(self.label_smpt)
        main_layout.addWidget(self.line_smpt_address)
        main_layout.addWidget(self.line_smpt_port)
        #main_layout.addLayout(button_layout)
        self.setLayout(main_layout)


    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()

# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    settings = SettingsWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
