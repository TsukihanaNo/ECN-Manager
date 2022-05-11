from PySide6 import QtWidgets, QtCore, QtWidgets

class ECNTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ECNTab,self).__init__()
        self.parent = parent
        self.nameList = []
        self.userList = []
        self.getUserList()
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


    def initUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        headerMainLayout = QtWidgets.QVBoxLayout()
        headersubLayout = QtWidgets.QHBoxLayout()
        headersubLayout2 = QtWidgets.QHBoxLayout()

        self.label_id = QtWidgets.QLabel("ECN ID:")
        self.label_type = QtWidgets.QLabel("ECN Type:")
        self.label_author = QtWidgets.QLabel("Author:")
        self.label_requestor = QtWidgets.QLabel("Requested By:")
        self.label_title = QtWidgets.QLabel("ECN Title:")
        self.label_status = QtWidgets.QLabel("Status:")
        self.label_dept = QtWidgets.QLabel("Department:")
        #self.label_due_date = QtWidgets.QLabel("Due Date:")
        #self.label_department = QtWidgets.QLabel("Department")

        self.line_id = QtWidgets.QLineEdit(self)
        self.line_id.setReadOnly(True)
        self.combo_type = QtWidgets.QComboBox(self)
        ecn_types = self.parent.settings["ECN_Types"].split(",")
        ecn_types.sort()
        self.combo_type.addItems(ecn_types)
        self.combo_dept = QtWidgets.QComboBox(self)
        depts = self.parent.settings["Dept"].split(",")
        depts.sort()
        self.combo_dept.addItems(depts)
        self.line_status = QtWidgets.QLineEdit(self)
        self.line_status.setReadOnly(True)
        self.line_status.setDisabled(True)
        self.line_author = QtWidgets.QLineEdit(self)
        self.line_author.setReadOnly(True)
        self.line_author.setDisabled(True)
        self.box_requestor = QtWidgets.QComboBox(self)
        self.box_requestor.setEditable(True)
        self.box_requestor.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.box_requestor.setMinimumWidth(200)
        self.box_requestor.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.box_requestor.addItems(self.userList) 
        self.line_ecntitle = QtWidgets.QLineEdit(self)
        #self.edit_date = QtWidgets.QDateEdit(self,calendarPopup=True)
        #self.edit_date.setMinimumWidth(200)

        #self.label_departments = QtWidgets.QLabel("Required Departments:",self)
        #self.cbpurch = QtWidgets.QCheckBox("purchasing",self)
        #self.cbplanner = QtWidgets.QCheckBox("planner",self)
        #self.cbshop = QtWidgets.QCheckBox("shop",self)
        
        layout_summary = QtWidgets.QVBoxLayout()
        self.label_summary = QtWidgets.QLabel("Summary of changes")
        self.text_summary = QtWidgets.QTextEdit(self)

        #self.cbpurch.stateChanged.connect(self.parent.togglePurchTab)
        #self.cbplanner.stateChanged.connect(self.parent.togglePlannerTab)
        #self.cbshop.stateChanged.connect(self.parent.toggleShopTab)
        
        layout_summary.addWidget(self.label_summary)
        layout_summary.addWidget(self.text_summary)

        
        headersubLayout.addWidget(self.label_id)
        headersubLayout.addWidget(self.line_id)
        headersubLayout.addWidget(self.label_type)
        headersubLayout.addWidget(self.combo_type)
        headersubLayout.addWidget(self.label_dept)
        headersubLayout.addWidget(self.combo_dept)
        
        headersubLayout2.addWidget(self.label_status)
        headersubLayout2.addWidget(self.line_status)
        headersubLayout2.addWidget(self.label_author)
        headersubLayout2.addWidget(self.line_author)
        headersubLayout2.addWidget(self.label_requestor)
        headersubLayout2.addWidget(self.box_requestor)
        #headersubLayout2.addWidget(self.label_due_date)
        #headersubLayout2.addWidget(self.edit_date)

        headerMainLayout.addLayout(headersubLayout)
        headerMainLayout.addLayout(headersubLayout2)
        headerMainLayout.addWidget(self.label_title)
        headerMainLayout.addWidget(self.line_ecntitle)

        layout_reason = QtWidgets.QVBoxLayout()
        self.label_reason = QtWidgets.QLabel("Enter reason for ECN below:")
        self.text_reason = QtWidgets.QTextEdit(self)

        layout_reason.addWidget(self.label_reason)
        layout_reason.addWidget(self.text_reason)


        groupbox_header = QtWidgets.QGroupBox("ECN Header")
        groupbox_reason = QtWidgets.QGroupBox("ECN Reason")
        groupbox_summary = QtWidgets.QGroupBox("ECN Summary")

        groupbox_header.setLayout(headerMainLayout)
        groupbox_reason.setLayout(layout_reason)
        groupbox_summary.setLayout(layout_summary)

        mainLayout.addWidget(groupbox_header)
        mainLayout.addWidget(groupbox_reason)
        mainLayout.addWidget(groupbox_summary)

        #self.line_author.setText(self.parent.parent.user_info['name'])
        
        
    def getNameList(self):
        command = "Select NAME from USER where STATUS ='Active'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        for result in results:
            self.nameList.append(result[0])
        self.nameList.sort()
            
    def getUserList(self):
        command = "Select USER_ID from USER where STATUS ='Active'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        for result in results:
            self.userList.append(result[0])
        self.userList.sort()
        self.userList.remove("admin")

