from PySide6 import QtWidgets, QtCore, QtGui
import os, sys
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

class PermissionsWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(PermissionsWindow,self).__init__()
        self.windowWidth =  int(400)
        self.windowHeight = int(600)
        self.parent = parent
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
        title = "User Permissions Window - u"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        
        

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.toolbar = QtWidgets.QToolBar()
        self.button_save = QtWidgets.QPushButton("Save")
        self.toolbar.addWidget(self.button_save)
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_general = GeneralTab(self)
        self.tab_widget.addTab(self.tab_general,"General")
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)


class GeneralTab(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(GeneralTab,self).__init__()
        self.parent = parent
        self.initUI()
        self.show()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()
        self.check_ecn = QtWidgets.QCheckBox()
        self.check_pcn = QtWidgets.QCheckBox()
        self.check_create_user = QtWidgets.QCheckBox()
        self.check_view_analytics = QtWidgets.QCheckBox()
        self.check_reject_signer = QtWidgets.QCheckBox()
        self.check_settings = QtWidgets.QCheckBox()
        form_layout.addRow("Allow user to create ECNs:",self.check_ecn)
        form_layout.addRow("Allow user to create PCNs:",self.check_pcn)
        form_layout.addRow("Allow user to reject to signer:",self.check_reject_signer)
        form_layout.addRow("Allow user to access settings:", self.check_settings)
        form_layout.addRow("Allow user to create users:", self.check_create_user)
        form_layout.addRow("Allow user to view Analytics:",self.check_view_analytics)

        main_layout.addLayout(form_layout)

        self.setLayout(main_layout)

#permissions listing
# create ecn, pcn
# view analytics
# create users
# access settings
# reject to signer



# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    settings = PermissionsWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()