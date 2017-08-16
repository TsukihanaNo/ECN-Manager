from PySide import QtGui, QtCore
from datetime import datetime
from FileDwgTab import *
from RequestTab import *

class RequestWindow(QtGui.QWidget):
    def __init__(self, parent = None, load_id = None):
        super(RequestWindow,self).__init__()
        self.parent = parent
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.windowWidth = 600
        self.windowHeight = 500
        self.load_id = load_id
        self.initAtt()
        self.initUI()
        self.center()
        self.show()

    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle("Manager - New Request")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()-QtCore.QPoint(0,0))

    def initUI(self):
        mainlayout = QtGui.QVBoxLayout(self)
        
        self.tabwidget = QtGui.QTabWidget(self)

        self.tab_req = RequestTab(self)
        self.tab_attach = FileDwgTab(self)

        self.button_submit = QtGui.QPushButton("Submit",self)
        self.button_submitandclose = QtGui.QPushButton("Submit & Close",self)

        self.button_submit.clicked.connect(self.submit)
        self.button_submitandclose.clicked.connect(self.submitAndClose)

        self.tabwidget.addTab(self.tab_req, "Request")
        self.tabwidget.addTab(self.tab_attach, "Attachment")

        buttonlayout = QtGui.QHBoxLayout()
        buttonlayout.addWidget(self.button_submit)
        buttonlayout.addWidget(self.button_submitandclose)
        mainlayout.addWidget(self.tabwidget)
        mainlayout.addLayout(buttonlayout)

        if self.load_id == None:
            self.generateECNID()
        
        

    def generateECNID(self):
        date_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.tab_req.line_id.setText('ECN-'+date_time[2:])

    def insertData(self):
        try:
            ecn_id = self.tab_req.line_id.text()
            ecn_type = self.tab_req.combo_type.currentText()
            requestor = self.tab_req.line_requestor.text()
            req_date = self.tab_req.date_request.date().toString("yyyy-MM-dd")
            status = 'Unassigned'
            title = self.tab_req.line_ecntitle.text()
            detail =self.tab_req.text_detail.toPlainText()
            #data = (self.line_id.text(),self.combo_type.currentText(),self.line_requestor.text(),self.date_request.date().toString("yyyy-MM-dd"),'Unassigned',self.line_ecntitle.text(),self.text_detail.toPlainText())
            data = (ecn_id,ecn_type,requestor,req_date,status,title,detail)
            self.cursor.execute("INSERT INTO ECN(ECN_ID,ECN_TYPE,REQUESTOR,REQ_DATE,STATUS,ECN_TITLE,REQ_DETAILS) VALUES(?,?,?,?,?,?,?)",(data))
            self.db.commit()
            print('data inserted')    
        except Exception as e:
            print(e)
            self.dispMsg("Error occured during data insertion!")

    def updateData(self):
        try:
            ecn_id = self.tab_req.line_id.text()
            ecn_type = self.tab_req.combo_type.currentText()
            requestor = self.tab_req.line_requestor.text()
            req_date = self.tab_req.date_request.date().toString("yyyy-MM-dd")
            status = 'Unassigned'
            title = self.tab_req.line_ecntitle.text()
            detail =self.tab_req.text_detail.toPlainText()
            data = (ecn_type,requestor,req_date,status,title,detail,ecn_id)

            #data = (self.combo_type.currentText(),self.line_requestor.text(),self.date_request.date().toString("yyyy-MM-dd"),'Unassigned',self.line_ecntitle.text(),self.text_detail.toPlainText(),self.line_id.text())
            self.cursor.execute("UPDATE ECN SET ECN_TYPE = ?, REQUESTOR = ?, REQ_DATE = ?, STATUS = ?, ECN_TITLE = ?, REQ_DETAILS = ? WHERE ECN_ID = ?",(data))
            self.db.commit()
            print('data updated')    
        except Exception as e:
            print(e)
            self.dispMsg("Error occured during data update!")

    def submitAndClose(self):
        self.submit()
        self.close()

    def submit(self):
        if self.checkEcnID():
            self.updateData()
        else:
            self.insertData()
        self.parent.repopulateTable()

    def checkEcnID(self):
        command = "select ECN_ID from ECN where ECN_ID = '" + self.tab_req.line_id.text() + "'"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        if len(results)!=0:
            return True
        else:
            return False

    def dispMsg(self,msg):
        msgbox = QtGui.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec_()