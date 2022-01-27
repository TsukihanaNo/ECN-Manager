from PySide6 import QtGui, QtCore, QtWidgets

class SignatureTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(SignatureTab,self).__init__()
        self.parent = parent
        self.job_titles =[]
        self.findJobTitles()
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)

        self.label_signatures = QtWidgets.QLabel("Signatures",self)
        mainlayout.addWidget(self.label_signatures)
        
        titles = ['Title','Name','User', 'Approval']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.selectionModel().selectionChanged.connect(self.onRowSelect)
        mainlayout.addWidget(self.table)
                
        hlayout = QtWidgets.QHBoxLayout(self)
        self.button_add = QtWidgets.QPushButton("Add Signature")
        self.button_add.clicked.connect(self.addRow)
        self.button_remove = QtWidgets.QPushButton("Remove Signature")
        self.button_remove.setEnabled(False)
        self.button_remove.clicked.connect(self.removeRow)
        hlayout.addWidget(self.button_add)
        hlayout.addWidget(self.button_remove)
        if self.parent.parent.user_info['role']=="Manager":
            self.button_revoke = QtWidgets.QPushButton("Revoke")
            self.button_revoke.setEnabled(False)
            self.button_revoke.clicked.connect(self.revokeApproval)
            hlayout.addWidget(self.button_revoke)
        mainlayout.addLayout(hlayout)

        self.setLayout(mainlayout)       

    def onRowSelect(self):
        if self.parent.parent.user_info['role']=="Manager":
            self.button_revoke.setEnabled(bool(self.table.selectionModel().selectedRows()))
        if self.parent.parent.user_info['user']==self.parent.tab_ecn.line_author.text():
            self.button_remove.setEnabled(bool(self.table.selectionModel().selectedRows()))
        
    def addRow(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.setBoxJob(row)
        self.setBoxName(row)
        self.setBoxUser(row)
    
    def setBoxJob(self,row,text=None):
        box = QtWidgets.QComboBox()
        box.addItems(self.job_titles)
        if text is not None:
            box.setCurrentText(text)
        box.currentIndexChanged.connect(self.setNameList)
        box.currentIndexChanged.connect(self.setUser)
        self.table.setCellWidget(row, 0, box)
        
    def setBoxName(self,row,text=None):
        command = "Select NAME from USER where JOB_TITLE = '" + self.table.cellWidget(row, 0).currentText() +"'"
        self.parent.cursor.execute(command)
        test = self.parent.cursor.fetchall()
        names = []
        for item in test:
            names.append(item[0])
        box = QtWidgets.QComboBox()
        box.addItems(names)
        if text is not None:
            box.setCurrentText(text)
        box.currentIndexChanged.connect(self.setUser)
        self.table.setCellWidget(row, 1, box)
        
    def setBoxUser(self,row, text=None):
        command = "Select USER_ID from USER where NAME = '" + self.table.cellWidget(row, 1).currentText() +"'"
        self.parent.cursor.execute(command)
        test = self.parent.cursor.fetchall()
        names = []
        for item in test:
            names.append(item[0])
        box = QtWidgets.QComboBox()
        box.addItems(names)
        if text is not None:
            box.setCurrentText(text)
        self.table.setCellWidget(row, 2, box)
        
    def revokeApproval(self):
        index = self.table.selectionModel().selectedRows()
        for item in index:
            row = item.row()
            user = self.table.item(row, 2).text()
            self.parent.cursor.execute(f"UPDATE SIGNATURE SET SIGNED_DATE = NULL where ECN_ID='{self.parent.ecn_id}' and USER_ID='{user}'")
        self.parent.db.commit()
        self.repopulateTable()
        
    def prepopulateTable(self):
        #department specific roles are: buyer, planner, supervisor
        #non-specific roles are: engineer (author), engineering manager, purchasing manager, production manager, planning manager
        self.table.clearContents()
        self.table.setRowCount(0)
        dept = self.parent.tab_ecn.combo_dept.currentText()
        command = f"Select JOB_TITLE, NAME, USER_ID from USER where STATUS='Active' and (DEPT is NULL OR DEPT='{dept}')"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        userList =[]
        for result in results:
            userList.append([result[0],result[1],result[2]])
        print(userList)
        #setting on specifics
        sigs = ["Engineering Manager","Purchasing Manager","Production Manager","Planning Manager","Buyer","Planner"]
        rowcount=0
        for role in sigs:
            info = userList[self.findUserIndex(userList, role)]
            #print(info)
            self.table.insertRow(rowcount)
            self.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(info[0]))
            self.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(info[1]))
            self.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(info[2]))
            rowcount+=1
        #pass
            
    def findUserIndex(self,userList, role):
        index = 0
        try:
            for user in userList:
                if user[0]==role:
                    return index
                else:
                    index+=1
            self.dispMsg(f"No users found matching role:{role}. Please add user or remove role from requirements.")
        except Exception as e:
            print(e)

        
    def removeRow(self):
        self.table.removeRow(self.table.currentRow())
        
    def findJobTitles(self):
        self.parent.cursor.execute("Select DISTINCT JOB_TITLE FROM USER")
        results = self.parent.cursor.fetchall()
        for result in results:
            self.job_titles.append(result[0])
        if "Admin" in self.job_titles:
            self.job_titles.remove("Admin")
        if len(self.job_titles)==0:
            self.dispMsg("No Job Titles found, please add Jobs and Users.")
        print(self.job_titles)
    
        
    def setNameList(self):
        command = "Select NAME from USER where JOB_TITLE = '" + self.table.cellWidget(self.table.currentRow(), 0).currentText() +"' and STATUS='Active'"
        self.parent.cursor.execute(command)
        test = self.parent.cursor.fetchall()
        names = []
        for item in test:
            names.append(item[0])
        box = QtWidgets.QComboBox()
        box.addItems(names)
        self.table.setCellWidget(self.table.currentRow(), 1, box)
        box.currentIndexChanged.connect(self.setUser)

    
    def setUser(self):
        command = "Select USER_ID from USER where NAME = '" + self.table.cellWidget(self.table.currentRow(), 1).currentText() +"'"
        self.parent.cursor.execute(command)
        test = self.parent.cursor.fetchall()
        names = []
        for item in test:
            names.append(item[0])
        box = QtWidgets.QComboBox()
        box.addItems(names)
        self.table.setCellWidget(self.table.currentRow(), 2, box)
        
    def repopulateTable(self):
        self.table.clearContents()
        command = "Select * from SIGNATURE where ECN_ID= '"+self.parent.ecn_id +"'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        self.table.setRowCount(len(results))
        rowcount=0
        for result in results:
            print(result['JOB_TITLE'])
            if self.parent.parent.user_info['user']!=self.parent.tab_ecn.line_author.text():
                self.table.setItem(rowcount, 0, QtWidgets.QTableWidgetItem(result['JOB_TITLE']))
                self.table.setItem(rowcount, 1, QtWidgets.QTableWidgetItem(result['NAME']))
                self.table.setItem(rowcount, 2, QtWidgets.QTableWidgetItem(result['USER_ID']))
            else:
                self.setBoxJob(rowcount,result['JOB_TITLE'])
                self.setBoxName(rowcount,result['NAME'])
                self.setBoxUser(rowcount,result['USER_ID'])
            self.table.setItem(rowcount, 3, QtWidgets.QTableWidgetItem(result['SIGNED_DATE']))

            rowcount+=1
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
            
    def resizeEvent(self,event):
            width = int(self.table.width()/self.table.columnCount())-3
            for x in range(self.table.columnCount()):
                self.table.setColumnWidth(x,width)