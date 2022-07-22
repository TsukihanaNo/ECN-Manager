from PySide import QtGui, QtCore
from datetime import datetime

class NewRequestForm(QtGui.QWidget):
    def __init__(self, parent = None):
        super(NewRequestForm,self).__init__()
        self.parent = parent
        self.cursor = self.parent.parent.cursor
        self.db = self.parent.parent.db
        self.windowWidth = 600
        self.windowHeight = 500

        self.setAcceptDrops(True)

        self.initUI()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()-QtCore.QPoint(0,0))

    def initUI(self):
        mainLayout = QtGui.QVBoxLayout(self)
        headerMainLayout = QtGui.QVBoxLayout()
        headersubLayout = QtGui.QHBoxLayout()
        layout_id = QtGui.QVBoxLayout()
        layout_type = QtGui.QVBoxLayout()
        layout_requestor = QtGui.QVBoxLayout()
        layout_date = QtGui.QVBoxLayout()

        self.label_id = QtGui.QLabel("ECN ID")
        self.label_type = QtGui.QLabel("ECN Type")
        self.label_requestor = QtGui.QLabel("Requestor")
        self.label_requestdate = QtGui.QLabel("Request Date")
        self.label_title = QtGui.QLabel("ECN Title")

        self.line_id = QtGui.QLineEdit(self)
        self.combo_type = QtGui.QComboBox(self)
        self.combo_type.addItems(['New Part', 'BOM Update', 'Firmware Update', 'Product EOL'])
        self.line_requestor = QtGui.QLineEdit(self)
        self.date_request = QtGui.QDateTimeEdit(QtCore.QDate.currentDate())
        self.date_request.setDisplayFormat("MM.dd.yyyy")
        self.line_ecntitle = QtGui.QLineEdit(self)

        layout_id.addWidget(self.label_id)
        layout_id.addWidget(self.line_id)
        layout_type.addWidget(self.label_type)
        layout_type.addWidget(self.combo_type)
        layout_requestor.addWidget(self.label_requestor)
        layout_requestor.addWidget(self.line_requestor)
        layout_date.addWidget(self.label_requestdate)
        layout_date.addWidget(self.date_request)

        headersubLayout.addLayout(layout_id)
        headersubLayout.addLayout(layout_type)
        headersubLayout.addLayout(layout_requestor)
        headersubLayout.addLayout(layout_date)

        headerMainLayout.addLayout(headersubLayout)
        headerMainLayout.addWidget(self.label_title)
        headerMainLayout.addWidget(self.line_ecntitle)

        layout_body = QtGui.QVBoxLayout()
        self.label_detail = QtGui.QLabel("Details")
        self.text_detail = QtGui.QTextEdit(self)

        layout_body.addWidget(self.label_detail)
        layout_body.addWidget(self.text_detail)

        layout_attachment = QtGui.QHBoxLayout()
        layout_attachment_button = QtGui.QVBoxLayout()
        self.list_attachment = QtGui.QListWidget(self)
        self.button_attachment_add = QtGui.QPushButton("Add",self)
        self.button_attachment_remove = QtGui.QPushButton("Remove",self)

        layout_attachment.addWidget(self.list_attachment)
        layout_attachment_button.addWidget(self.button_attachment_add)
        layout_attachment_button.addWidget(self.button_attachment_remove)
        layout_attachment.addLayout(layout_attachment_button)

        groupbox_header = QtGui.QGroupBox("ECN Header")
        groupbox_detail = QtGui.QGroupBox("ECN Details")
        self.groupbox_attachment = QtGui.QGroupBox("ECN Attachments")
        self.groupbox_attachment.setCheckable(True)
        self.groupbox_attachment.setChecked(False)
        self.groupbox_attachment.setMaximumHeight(20)

        self.groupbox_attachment.toggled.connect(self.toggleGroup)

        groupbox_header.setLayout(headerMainLayout)
        groupbox_detail.setLayout(layout_body)
        self.groupbox_attachment.setLayout(layout_attachment)

        layout_submit = QtGui.QHBoxLayout()
        layout_submit.setAlignment(QtCore.Qt.AlignCenter)
        self.button_submit = QtGui.QPushButton("Submit",self)
        self.button_submit.setFixedWidth(200)
        self.button_submitandclose = QtGui.QPushButton("Submit and Close",self)
        self.button_submitandclose.setFixedWidth(200)

        layout_submit.addWidget(self.button_submit)
        layout_submit.addWidget(self.button_submitandclose)

        mainLayout.addWidget(groupbox_header)
        mainLayout.addWidget(groupbox_detail)
        mainLayout.addWidget(self.groupbox_attachment)
        mainLayout.addLayout(layout_submit)

        self.line_requestor.setText(self.parent.parent.user_info['user'])

        self.button_submit.clicked.connect(self.submit)
        self.button_submitandclose.clicked.connect(self.submitAndClose)

        self.generateECNID()

        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle("Manager - New Request")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        self.show()

    def generateECNID(self):
        date_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.line_id.setText('ECN-'+date_time[2:])

    def insertData(self):
        try:
            data = (self.line_id.text(),self.combo_type.currentText(),self.line_requestor.text(),self.date_request.date().toString("yyyy-MM-dd"),'Unassigned',self.line_ecntitle.text(),self.text_detail.toPlainText())
            self.cursor.execute("INSERT INTO ECN(ECN_ID,ECN_TYPE,REQUESTOR,REQ_DATE,STATUS,ECN_TITLE,REQ_DETAILS) VALUES(?,?,?,?,?,?,?)",(data))
            self.db.commit()
            print('data inserted')    
        except Exception as e:
            print(e)
            self.dispMsg("Error occured during data insertion!")

    def updateData(self):
        try:
            data = (self.combo_type.currentText(),self.line_requestor.text(),self.date_request.date().toString("yyyy-MM-dd"),'Unassigned',self.line_ecntitle.text(),self.text_detail.toPlainText(),self.line_id.text())
            self.cursor.execute("UPDATE DOCUMENT SET ECN_TYPE = ?, REQUESTOR = ?, REQ_DATE = ?, STATUS = ?, ECN_TITLE = ?, REQ_DETAILS = ? WHERE DOC_ID = ?",(data))
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
        command = "select ECN_ID from DOCUMENT where ECN_ID = '" + self.line_id.text() + "'"
        self.cursor.execute(command)
        results = self.cursor.fetchall()
        if len(results)!=0:
            return True
        else:
            return False

    def dispMsg(self,msg):
        msgbox = QtGui.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()

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

    def toggleGroup(self):
        if self.groupbox_attachment.isChecked():
            self.animation = QtCore.QPropertyAnimation(self.groupbox_attachment,"maximumHeight")
            self.animation.setDuration(600)
            self.animation.setStartValue(20)
            self.animation.setEndValue(300)
            self.animation.setEasingCurve(QtCore.QEasingCurve.Linear)
            self.animation.start()
        else:
            self.animation = QtCore.QPropertyAnimation(self.groupbox_attachment,"maximumHeight")
            self.animation.setDuration(600)
            self.animation.setStartValue(300)
            self.animation.setEndValue(20)
            self.animation.setEasingCurve(QtCore.QEasingCurve.Linear)
            self.animation.start()

