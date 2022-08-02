from PySide6 import QtWidgets, QtCore, QtWidgets

class PCNTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(PCNTab,self).__init__()
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
        headerLayout = QtWidgets.QHBoxLayout()
        self.label_id = QtWidgets.QLabel("PCN ID:")
        self.line_id = QtWidgets.QLineEdit()
        self.line_id.setFixedWidth(80)
        self.line_id.setReadOnly(True)
        self.label_title = QtWidgets.QLabel("Title:")
        self.line_title = QtWidgets.QLineEdit()
        self.label_author = QtWidgets.QLabel("Author:")
        self.line_author = QtWidgets.QLineEdit()
        self.line_author.setFixedWidth(125)
        self.line_author.setReadOnly(True)
        self.label_status = QtWidgets.QLabel("Status:")
        self.line_status = QtWidgets.QLineEdit()
        self.line_status.setFixedWidth(125)
        self.line_status.setReadOnly(True)
        self.label_overview = QtWidgets.QLabel("Overview:")
        self.text_overview = QtWidgets.QTextEdit(self)
        self.label_products = QtWidgets.QLabel("Products Affected:")
        self.text_products = QtWidgets.QTextEdit(self)
        self.label_change = QtWidgets.QLabel("Change Description:")
        self.text_change = QtWidgets.QTextEdit(self)
        self.label_reason = QtWidgets.QLabel("Reason For Change:")
        self.text_reason = QtWidgets.QTextEdit(self)
        self.label_replacement = QtWidgets.QLabel("Replacement Product:")
        self.text_replacement = QtWidgets.QTextEdit(self)
        self.label_reference = QtWidgets.QLabel("Reference:")
        self.text_reference = QtWidgets.QTextEdit(self)
        self.label_response = QtWidgets.QLabel("Response:")
        self.text_response = QtWidgets.QTextEdit(self)
        self.label_web = QtWidgets.QLabel("Web Description:")
        self.line_web = QtWidgets.QLineEdit()
        self.line_web.setPlaceholderText("Format: [sales name/model] [action] [date (MM DD, YYYY)]")
        self.line_web.setMaxLength(75)
        
        headerLayout.addWidget(self.label_id)
        headerLayout.addWidget(self.line_id)
        headerLayout.addWidget(self.label_title)
        headerLayout.addWidget(self.line_title)
        headerLayout.addWidget(self.label_author)
        headerLayout.addWidget(self.line_author)
        headerLayout.addWidget(self.label_status)
        headerLayout.addWidget(self.line_status)
        mainLayout.addLayout(headerLayout)
        mainLayout.addWidget(self.label_overview)
        mainLayout.addWidget(self.text_overview)
        mainLayout.addWidget(self.label_products)
        mainLayout.addWidget(self.text_products)
        mainLayout.addWidget(self.label_change)
        mainLayout.addWidget(self.text_change)
        mainLayout.addWidget(self.label_reason)
        mainLayout.addWidget(self.text_reason)
        mainLayout.addWidget(self.label_replacement)
        mainLayout.addWidget(self.text_replacement)
        mainLayout.addWidget(self.label_reference)
        mainLayout.addWidget(self.text_reference)
        mainLayout.addWidget(self.label_response)
        mainLayout.addWidget(self.text_response)
        mainLayout.addWidget(self.label_web)
        mainLayout.addWidget(self.line_web)
        
        self.setLayout(mainLayout)
        
        
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

