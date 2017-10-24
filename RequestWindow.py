from PySide import QtGui, QtCore
from datetime import datetime
from FileDwgTab import *
from RequestTab import *
from PurchaserTab import *
from TasksTab import *
from EngineerTab import *
from ShopTab import *
from PlannerTab import *
from ChangeLogTab import *

class RequestWindow(QtGui.QWidget):
    def __init__(self, parent = None, load_id = None):
        super(RequestWindow,self).__init__()
        self.parent = parent
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.user_info = self.parent.user_info
        self.windowWidth = 600
        self.windowHeight = 500
        self.load_id = load_id
        self.tablist = []
        self.typeindex = {'New Part':0, 'BOM Update':1, 'Firmware Update':2, 'Configurator Udpate' : 3,'Product EOL':4}
        self.initAtt()
        if self.load_id == None:
            self.initReqUI()
            self.generateECNID()
        else:
            self.initFullUI()
            self.loadData()
            self.getCurrentValues()
            
        self.center()
        self.show()

    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle("Manager - Request")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()-QtCore.QPoint(0,0))

    def initReqUI(self):
        mainlayout = QtGui.QVBoxLayout(self)
        
        self.tabwidget = QtGui.QTabWidget(self)

        self.tab_req = RequestTab(self)
        self.tab_attach = FileDwgTab(self)

        self.button_submit = QtGui.QPushButton("Submit",self)

        self.button_submit.clicked.connect(self.submit)

        self.tabwidget.addTab(self.tab_req, "Request")
        self.tabwidget.addTab(self.tab_attach, "Attachment")

        buttonlayout = QtGui.QHBoxLayout()
        buttonlayout.addWidget(self.button_submit)

        mainlayout.addWidget(self.tabwidget)
        mainlayout.addLayout(buttonlayout)



    def initFullUI(self):
        mainlayout = QtGui.QVBoxLayout(self)
        
        self.tabwidget = QtGui.QTabWidget(self)
        self.tabwidget.currentChanged.connect(self.printIndex)

        self.tab_req = RequestTab(self)
        self.tab_eng = EngineerTab(self)
        self.tab_attach = FileDwgTab(self)
        self.tab_task = TasksTab(self)

        self.tab_changelog = ChangeLogTab(self,self.load_id)

        self.tab_purch = PurchaserTab(self)
        self.tab_planner = PlannerTab(self)
        self.tab_shop = ShopTab(self)


        self.button_save = QtGui.QPushButton("Save",self)

        self.button_save.clicked.connect(self.save)

        self.tabwidget.addTab(self.tab_req, "Request")
        self.tabwidget.addTab(self.tab_eng, "Engineer")
        self.tabwidget.addTab(self.tab_attach, "Attachment")
        self.tabwidget.addTab(self.tab_task, "Tasks")
        self.tabwidget.addTab(self.tab_changelog, "Change Log")

        buttonlayout = QtGui.QHBoxLayout()
        buttonlayout.addWidget(self.button_save)

        mainlayout.addWidget(self.tabwidget)
        mainlayout.addLayout(buttonlayout)

    def printIndex(self):
        print(self.tabwidget.currentIndex())
        
    def togglePurchTab(self):
        if self.tab_eng.cbpurch.isChecked():
            self.tabwidget.insertTab(len(self.tablist)+2,self.tab_purch, "Purchasing")
            self.tablist.append("purch")
        else:
            self.tabwidget.removeTab(self.tablist.index("purch")+2)
            self.tablist.remove("purch")

    def togglePlannerTab(self):
        if self.tab_eng.cbplanner.isChecked():
            self.tabwidget.insertTab(len(self.tablist)+2,self.tab_planner, "Planner")
            self.tablist.append("planner")
        else:
            self.tabwidget.removeTab(self.tablist.index("planner")+2)
            self.tablist.remove("planner")

    def toggleShopTab(self):
        if self.tab_eng.cbshop.isChecked():
            self.tabwidget.insertTab(len(self.tablist)+2,self.tab_shop, "Shop")
            self.tablist.append("shop")
        else:
            self.tabwidget.removeTab(self.tablist.index("shop")+2)
            self.tablist.remove("shop")

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

    def loadData(self):
        command = "Select * from ECN where ECN_ID = '"+self.load_id +"'"
        self.cursor.execute(command)
        results = self.cursor.fetchone()
        self.tab_req.line_id.setText(results['ECN_ID'])
        self.tab_req.combo_type.setCurrentIndex(self.typeindex[results['ECN_TYPE']])
        self.tab_req.line_ecntitle.setText(results['ECN_TITLE'])
        self.tab_req.text_detail.setText(results['REQ_DETAILS'])
        self.tab_req.line_requestor.setText(results['REQUESTOR'])
        y,m,d = results['REQ_DATE'].split("-")
        self.tab_req.date_request.setDate(QtCore.QDate(int(y),int(m),int(d)))
            
    def getCurrentValues(self):
        print('getting values')
        self.now_type = self.tab_req.combo_type.currentText()
        self.now_title = self.tab_req.line_ecntitle.text()
        self.now_req_details = self.tab_req.text_detail.toPlainText()
        print(self.now_type)
        print(self.now_title)
        print(self.now_req_details)

    def submitAndClose(self):
        self.submit()
        self.close()

    def submit(self):
        if not self.checkEcnID():
            self.insertData()
            self.parent.repopulateTable()
        else:
            self.dispMsg("ECN ID already exists")

    def save(self):
        self.updateData()
        self.checkDiff()
        self.parent.repopulateTable()

    def saveAndClose(self):
        self.save()
        self.close()

    def checkDiff(self):
        ecn_id = self.tab_req.line_id.text()
        changedate = datetime.now().strftime('%Y%m%d-%H%M%S')
        user = self.parent.user_info['name']
        prevdata = self.now_type
        newdata = self.tab_req.combo_type.currentText()
        if newdata != prevdata:
            data = (ecn_id,changedate,user,prevdata,newdata)
            self.cursor.execute("INSERT INTO CHANGELOG(ECN_ID, CHANGEDATE, NAME, PREVDATA, NEWDATA) VALUES(?,?,?,?,?)",(data))
            print('adding type change')
        prevdata = self.now_title
        newdata = self.tab_req.line_ecntitle.text()
        if newdata != prevdata:
            data = (ecn_id,changedate,user,prevdata,newdata)
            self.cursor.execute("INSERT INTO CHANGELOG(ECN_ID, CHANGEDATE, NAME, PREVDATA, NEWDATA) VALUES(?,?,?,?,?)",(data))
            print('adding title change')
        prevdata = self.now_req_details
        newdata = self.tab_req.text_detail.toPlainText()  
        if newdata != prevdata:
            data = (ecn_id,changedate,user,prevdata,newdata)
            self.cursor.execute("INSERT INTO CHANGELOG(ECN_ID, CHANGEDATE, NAME, PREVDATA, NEWDATA) VALUES(?,?,?,?,?)",(data))
            print('adding detail change')
        self.db.commit()
        


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