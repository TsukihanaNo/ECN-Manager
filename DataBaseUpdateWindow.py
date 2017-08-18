import os, re, sys
import sqlite3
from PySide import QtGui, QtCore

class DataBaseUpdateWindow(QtGui.QWidget):
    def __init__(self,parent=None, addtables = None, removetables = None, addcolumns = None):
        super(DataBaseUpdateWindow,self).__init__()
        self.parent = parent
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        self.windowHeight = 300
        self.windowWidth = 400
        self.addtables = addtables
        self.removetables = removetables
        self.addcolumns = addcolumns

        self.initAtt()
        self.initUI()
        self.center()
        self.show()
        self.initiateUpdate()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()-QtCore.QPoint(0,0))

    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle("Manager - Database Update")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def initUI(self):
        mainlayout = QtGui.QVBoxLayout(self)
        self.text_update = QtGui.QTextEdit(self)
        self.text_update.setReadOnly(True)
        self.button_close = QtGui.QPushButton("Close",self)
        self.button_close.clicked.connect(self.close)
        mainlayout.addWidget(self.text_update)
        mainlayout.addWidget(self.button_close)

    def initiateUpdate(self):
        self.text_update.append('Initing Update...')
        self.text_update.append('* Number of Tables to add: ' + str(len(self.addtables)))
        self.text_update.append('* Number of Tables to remove: ' + str(len(self.removetables)))
        self.text_update.append('* Number of Columns to add: ' + str(len(self.addcolumns)))

        for item in self.removetables:
            command = "DROP TABLE IF EXISTS " + item
            QtGui.QApplication.processEvents()
            self.text_update.append("-- Dropping the following tables: " + item)
            self.text_update.append("    ** executing command: " + command)
            self.cursor.execute(command)

        for key in self.addtables.keys():
            tableinfo = "("
            for item in self.addtables[key]:
                tableinfo = tableinfo + item
            command = "CREATE TABLE " + key + tableinfo + ")"
            QtGui.QApplication.processEvents()
            self.text_update.append("-- Creating the following tables: " + item)
            self.text_update.append("    ** executing command: " + command)
            self.cursor.execute(command)

        for key in self.addcolumns.keys():
            #print(key)
            #print(self.addcolumns[key])
            for item in self.addcolumns[key]:
                command = "ALTER TABLE " + key + " ADD COLUMN " + item
                QtGui.QApplication.processEvents()
                self.text_update.append("-- Creating the following Table : Column: " + key + " : " + item)
                self.text_update.append("    ** executing command: " + command)
                self.cursor.execute(command)

        self.text_update.append("Update completed!")
        self.text_update.append("You can close this window now.")

            #self.db.commit()
