from PySide6 import QtWidgets, QtCore, QtWidgets

class ECRTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ECRTab,self).__init__()
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
        headersubLayout = QtWidgets.QGridLayout()
        #headersubLayout2 = QtWidgets.QHBoxLayout()

        self.label_id = QtWidgets.QLabel("ECR ID:")
        self.label_type = QtWidgets.QLabel("ECN Type:")
        self.label_reason = QtWidgets.QLabel("ECN Reason:")
        self.label_author = QtWidgets.QLabel("Author:")
        self.label_title = QtWidgets.QLabel("ECR Title:")
        self.label_status = QtWidgets.QLabel("Status:")
        self.label_dept = QtWidgets.QLabel("Department:")
        self.label_ECN = QtWidgets.QLabel("Linked ECN:")
        self.label_assigned_to = QtWidgets.QLabel("Assigned To:")
        #self.label_due_date = QtWidgets.QLabel("Due Date:")
        #self.label_department = QtWidgets.QLabel("Department")

        self.line_id = QtWidgets.QLineEdit(self)
        self.line_id.setReadOnly(True)
        self.line_id.setFixedWidth(130)
        self.line_ECN = QtWidgets.QLineEdit(self)
        self.line_ECN.setReadOnly(True)
        self.line_ECN.setFixedWidth(130)
        self.combo_type = QtWidgets.QComboBox(self)
        ecn_types = self.parent.settings["ECN_Types"].split(",")
        ecn_types.append("")
        ecn_types.sort()
        self.combo_type.addItems(ecn_types)
        self.combo_reason = QtWidgets.QComboBox(self)
        ecn_reasons = self.parent.settings["ECN_Reasons"].split(",")
        ecn_reasons.append("")
        ecn_reasons.sort()
        self.combo_reason.addItems(ecn_reasons)
        self.combo_dept = QtWidgets.QComboBox(self)
        depts = self.parent.settings["Dept"].split(",")
        depts.append("")
        depts.sort()
        self.combo_dept.addItems(depts)
        self.line_status = QtWidgets.QLineEdit(self)
        self.line_status.setReadOnly(True)
        self.line_status.setDisabled(True)
        self.line_status.setFixedWidth(130)
        self.line_author = QtWidgets.QLineEdit(self)
        self.line_author.setReadOnly(True)
        self.line_author.setDisabled(True)
        self.line_author.setFixedWidth(150)
        
        self.line_ecn = QtWidgets.QLineEdit(self)
        self.line_ecn.setReadOnly(True)
        self.line_ecn.setDisabled(True)
        self.line_ecn.setFixedWidth(150)
        
        self.line_assigned_to = QtWidgets.QLineEdit(self)
        self.line_assigned_to.setReadOnly(True)
        self.line_assigned_to.setDisabled(True)
        self.line_assigned_to.setFixedWidth(150)

        self.line_title = QtWidgets.QLineEdit(self)

        
        headersubLayout.addWidget(self.label_id,0,0)
        headersubLayout.addWidget(self.line_id,1,0)
        headersubLayout.addWidget(self.label_status,0,1)
        headersubLayout.addWidget(self.line_status,1,1)
        headersubLayout.addWidget(self.label_author,0,2)
        headersubLayout.addWidget(self.line_author,1,2)
        headersubLayout.addWidget(self.label_assigned_to,0,3)
        headersubLayout.addWidget(self.line_assigned_to,1,3)
        headersubLayout.addWidget(self.label_type,2,0)
        headersubLayout.addWidget(self.combo_type,3,0)
        headersubLayout.addWidget(self.label_reason,2,1)
        headersubLayout.addWidget(self.combo_reason,3,1)
        headersubLayout.addWidget(self.label_dept,2,2)
        headersubLayout.addWidget(self.combo_dept,3,2)
        headersubLayout.addWidget(self.label_ECN,2,3)
        headersubLayout.addWidget(self.line_ECN,3,3)
        
        
        # headersubLayout2.addWidget(self.label_status)
        # headersubLayout2.addWidget(self.line_status)
        # headersubLayout2.addWidget(self.label_author)
        # headersubLayout2.addWidget(self.line_author)
        # headersubLayout2.addWidget(self.label_requestor)
        # headersubLayout2.addWidget(self.box_requestor)
        #headersubLayout2.addWidget(self.label_due_date)
        #headersubLayout2.addWidget(self.edit_date)

        headerMainLayout.addLayout(headersubLayout)
        #headerMainLayout.addLayout(headersubLayout2)
        headerMainLayout.addWidget(self.label_title)
        headerMainLayout.addWidget(self.line_title)

        layout_reason = QtWidgets.QVBoxLayout()
        self.label_reason = QtWidgets.QLabel("Reason for change:")
        self.text_reason = QtWidgets.QTextEdit(self)
        self.text_reason.setAcceptRichText(True)

        layout_reason.addWidget(self.label_reason)
        layout_reason.addWidget(self.text_reason)
        mainLayout.addLayout(headerMainLayout)
        mainLayout.addLayout(layout_reason)
        
    def getNameList(self):
        command = "Select name from users where status ='Active'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        for result in results:
            self.nameList.append(result[0])
        self.nameList.sort()
            
    def getUserList(self):
        command = "Select user_id from users where status ='Active'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        for result in results:
            self.userList.append(result[0])
        self.userList.sort()
        self.userList.remove("admin")
        
    def checkFields(self):
        if self.combo_dept.currentText()==" ":
            return False
        if self.combo_reason.currentText()==" ":
            return False
        if self.combo_type.currentText()==" ":
            return False
        if len(self.line_title.text())<3:
            return False
        return True

