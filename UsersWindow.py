from PySide6 import QtWidgets, QtCore, QtGui
import os, sys
from MyTableWidget import *
from UserPanel import *
from Hook import *
import sqlite3  


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class UsersWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(UsersWindow,self).__init__()
        self.windowWidth =  int(830*0.9)
        self.windowHeight = int(580*0.90)
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
        button_layout = QtWidgets.QHBoxLayout()
        self.button_add = QtWidgets.QPushButton("Add User")
        self.button_add.clicked.connect(self.addUser)
        self.button_remove = QtWidgets.QPushButton("Remove User")
        self.button_remove.clicked.connect(self.removeUser)
        self.button_edit = QtWidgets.QPushButton("Edit User")
        self.button_edit.clicked.connect(self.editUser)
        button_layout.addWidget(self.button_add)
        button_layout.addWidget(self.button_remove)
        button_layout.addWidget(self.button_edit)
        #USER(USER_ID TEXT, PASSWORD TEXT, NAME TEXT, ROLE TEXT, JOB_TITLE TEXT, DEPT TEXT, STATUS TEXT, EMAIL TEXT)
        titles = ['User ID','Name','Job Title','Role','Status','Email']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.editUser)
        self.table.selectionModel().selectionChanged.connect(self.onRowSelect)
        self.button_edit.setEnabled(False)
        self.button_remove.setEnabled(False)
        main_layout.addWidget(self.table)
        main_layout.addLayout(button_layout)
        
        self.repopulateTable()
        
    def onRowSelect(self):
        self.button_edit.setEnabled(bool(self.table.selectionModel().selectedRows()))
        self.button_remove.setEnabled(bool(self.table.selectionModel().selectedRows()))
    
    def repopulateTable(self):
        self.table.clearContents()
        command = "Select * from USER"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        self.table.setRowCount(len(results))
        rowcount=0
        for result in results:
            self.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['USER_ID']))
            self.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['NAME']))
            self.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['JOB_TITLE']))
            self.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['ROLE']))
            self.table.setItem(rowcount, 4, QtWidgets.QTableWidgetItem(result['STATUS']))
            self.table.setItem(rowcount, 5, QtWidgets.QTableWidgetItem(result['EMAIL']))

            rowcount+=1
            
    
    def addUser(self):
        self.userPanel = UserPanel(self,func="add")

    
    def removeUser(self):
        row = self.table.currentRow()
        if row:
            user = self.table.item(row,0).text()
            status = self.table.item(row, 4).text()
            if self.checkRemovable(user, status):
                self.cursor.execute(f"DELETE from USER where USER_ID='{user}'")
                self.db.commit()
                self.dispMsg(f"{user} has been removed.")
                self.repopulateTable()
            else:
                self.dispMsg("Cannot remove. User is either currently active or has records already.")
        else:
            self.dispMsg("No row selected, please pick a row")
            
            
    def checkRemovable(self,user,status):
        if status=="Active":
            return False
        self.cursor.execute(f"Select * from ECN where AUTHOR='{user}'")
        result = self.cursor.fetchone()
        if result is not None:
            return False
        self.cursor.execute(f"Select * from SIGNATURE where USER_ID='{user}'")
        result = self.cursor.fetchone()
        if result is not None:
            return False
        self.cursor.execute(f"Select * from COMMENTS where USER='{user}'")
        result = self.cursor.fetchone()
        if result is not None:
            return False
        return True
        
    
    def editUser(self):
        row = self.table.currentRow()
        user = self.table.item(row,0).text()
        self.userPanel = UserPanel(self,user,"edit")


    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()

# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    Users = UsersWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
