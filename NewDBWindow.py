from PySide6 import QtWidgets, QtCore, QtGui
import os, sys
from MyTableWidget import *
import sqlite3  

class NewDBWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(NewDBWindow,self).__init__()
        self.windowHeight = 400
        self.windowWidth = 600
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
        title = "DB Creator"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()

    def initUI(self):
        loc_layout = QtWidgets.QHBoxLayout()

        loc_label = QtWidgets.QLabel("DB Location: ")
        self.loc_line = QtWidgets.QLineEdit(self)
        self.loc_button = QtWidgets.QPushButton("Browse",self)
        self.loc_button.clicked.connect(self.getDirectory)

        loc_layout.addWidget(loc_label)
        loc_layout.addWidget(self.loc_line)
        loc_layout.addWidget(self.loc_button)

        headers = ['user','password','name','role','job title']
        self.table = MyTableWidget(1,5,self)
        self.table.setHorizontalHeaderLabels(headers)
        combo=['Admin','Engineer','Requestor']
        self.table.setCombos(3,combo)
        combo2=['Admin','Engineer','Buyer','Planner','Production Manager']
        self.table.setCombos(4,combo2)
        self.table.generateRow(True)

        self.textedit = QtWidgets.QTextEdit(self)
        self.textedit.setReadOnly(True)

        self.button = QtWidgets.QPushButton("Generate",self)
        self.button.clicked.connect(self.generateTable)

        mainlayout = QtWidgets.QVBoxLayout(self)

        mainlayout.addLayout(loc_layout)
        mainlayout.addWidget(self.table)
        mainlayout.addWidget(self.textedit)
        mainlayout.addWidget(self.button)

    def getDirectory(self):
        file_dialog = QtWidgets.QFileDialog(self)
        directory = file_dialog.getExistingDirectory()
        self.loc_line.setText(directory)

    def generateTable(self):
        if self.loc_line.text() !="":
            self.createTables()
        else:
            self.dispMsg("    Please designate a location.")


    def createTables(self):
        database = sqlite3.connect(os.path.join(self.loc_line.text(),"ECN_DB.db"))
        cur = database.cursor()
        cur.execute('CREATE TABLE ECN(ECN_ID TEXT, ECN_TYPE TEXT, ECN_TITLE TEXT, DEPARTMENT TEXT, ECN_REASON TEXT, REQUESTOR TEXT, AUTHOR TEXT, STATUS TEXT, COMP_DATE DATE, ECN_SUMMARY TEXT, LAST_MODIFIED DATE)')
        cur.execute('CREATE TABLE COMMENTS(ECN_ID TEXT, NAME TEXT, USER TEXT, COMM_DATE DATE, COMMENT TEXT, TYPE TEXT)')
        cur.execute('CREATE TABLE PARTS(ECN_ID TEXT, PART_ID TEXT, DESC TEXT, DISPOSITION TEXT, REVISION TEXT)')
        cur.execute('CREATE TABLE TAG_PARTS(ECN_ID TEXT, PART_ID TEXT)')
        cur.execute('CREATE TABLE TAG_PRODUCT(ECN_ID TEXT, PRODUCT TEXT)')
        cur.execute('CREATE TABLE SIGNATURE(ECN_ID TEXT, NAME TEXT, USER_ID TEXT, JOB_TITLE TEXT HAS_SIGNED TEXT, SIGNED_DATE DATETIME)')
        cur.execute('CREATE TABLE ATTACHMENTS(ECN_ID TEXT, FILENAME TEXT, FILEPATH TEXT)')
        cur.execute('CREATE TABLE USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, DEPT TEXT, STATUS TEXT, EMAIL TEXT)')
        cur.execute('CREATE TABLE CHANGELOG(ECN_ID TEXT, CHANGEDATE DATETIME, NAME TEXT,DATABLOCK TEXT, PREVDATA TEXT, NEWDATA TEXT)')
        cur.execute('CREATE TABLE NOTIFICATION(ECN_ID TEXT, STATUS TEXT, TYPE TEXT)')
        for rows in range(self.table.rowCount()):
            user = self.table.item(rows,0).text()
            password = self.table.item(rows,1).text()
            name = self.table.item(rows,2).text()
            role = self.table.cellWidget(rows,3).currentText()
            title = self.table.cellWidget(rows,4).currentText()
            data = (user,password,name,role,title,"Active")
            cur.execute('INSERT INTO USER(USER_ID, PASSWORD, NAME, ROLE, JOB_TITLE, Status) VALUES(?,?,?,?,?,?)',(data))
            self.textedit.append("****Created User: "+user)
            QtWidgets.QApplication.processEvents()
        self.textedit.append("Database has been created")
        database.commit()
        database.close()

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()

# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    DB = NewDBWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
