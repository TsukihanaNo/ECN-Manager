from PySide6 import QtWidgets, QtCore, QtWidgets

class ECNTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ECNTab,self).__init__()
        self.parent = parent
        self.nameList = []
        self.getNameList()
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


    def initUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        headerMainLayout = QtWidgets.QVBoxLayout()
        headersubLayout = QtWidgets.QHBoxLayout()
        layout_id = QtWidgets.QVBoxLayout()
        layout_type = QtWidgets.QVBoxLayout()
        layout_status = QtWidgets.QVBoxLayout()
        layout_author = QtWidgets.QVBoxLayout()
        layout_requestor = QtWidgets.QVBoxLayout()
        layout_summary = QtWidgets.QVBoxLayout()
        layout_dept = QtWidgets.QVBoxLayout()
        #layout_department = QtWidgets.QVBoxLayout()
        

        self.label_id = QtWidgets.QLabel("ECN ID")
        self.label_type = QtWidgets.QLabel("ECN Type")
        self.label_author = QtWidgets.QLabel("Author")
        self.label_requestor = QtWidgets.QLabel("Requested By")
        self.label_title = QtWidgets.QLabel("ECN Title")
        self.label_status = QtWidgets.QLabel("Status")
        self.label_dept = QtWidgets.QLabel("Dept.")
        #self.label_department = QtWidgets.QLabel("Department")

        self.line_id = QtWidgets.QLineEdit(self)
        self.line_id.setMinimumWidth(115)
        self.line_id.setReadOnly(True)
        self.line_id.setDisabled(True)
        self.combo_type = QtWidgets.QComboBox(self)
        self.combo_type.addItems(['New Part', 'BOM Update', 'Firmware Update', 'Configurator Update', 'Product EOL'])
        self.combo_dept = QtWidgets.QComboBox(self)
        self.combo_dept.addItems(self.parent.settings["Dept"].split(","))
        self.line_status = QtWidgets.QLineEdit(self)
        self.line_status.setReadOnly(True)
        self.line_status.setDisabled(True)
        self.line_author = QtWidgets.QLineEdit(self)
        self.line_author.setReadOnly(True)
        self.line_author.setDisabled(True)
        self.box_requestor = QtWidgets.QComboBox(self)
        self.box_requestor.setEditable(True)
        self.box_requestor.setMinimumWidth(100)
        self.box_requestor.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.box_requestor.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.box_requestor.addItems(self.nameList) 
        self.line_ecntitle = QtWidgets.QLineEdit(self)

        #self.label_departments = QtWidgets.QLabel("Required Departments:",self)
        #self.cbpurch = QtWidgets.QCheckBox("purchasing",self)
        #self.cbplanner = QtWidgets.QCheckBox("planner",self)
        #self.cbshop = QtWidgets.QCheckBox("shop",self)
        self.label_summary = QtWidgets.QLabel("Summary of changes")
        self.text_summary = QtWidgets.QTextEdit(self)

        #self.cbpurch.stateChanged.connect(self.parent.togglePurchTab)
        #self.cbplanner.stateChanged.connect(self.parent.togglePlannerTab)
        #self.cbshop.stateChanged.connect(self.parent.toggleShopTab)
        
        layout_summary.addWidget(self.label_summary)
        layout_summary.addWidget(self.text_summary)
        #layout_summary.addWidget(self.label_departments)
        #layout_summary.addWidget(self.cbpurch)
        #layout_summary.addWidget(self.cbplanner)
        #layout_summary.addWidget(self.cbshop)

        layout_id.addWidget(self.label_id)
        layout_id.addWidget(self.line_id)
        layout_type.addWidget(self.label_type)
        layout_type.addWidget(self.combo_type)
        layout_dept.addWidget(self.label_dept)
        layout_dept.addWidget(self.combo_dept)
        layout_status.addWidget(self.label_status)
        layout_status.addWidget(self.line_status)
        layout_author.addWidget(self.label_author)
        layout_author.addWidget(self.line_author)
        layout_requestor.addWidget(self.label_requestor)
        layout_requestor.addWidget(self.box_requestor)

        headersubLayout.addLayout(layout_id)
        headersubLayout.addLayout(layout_type)
        headersubLayout.addLayout(layout_dept)
        headersubLayout.addLayout(layout_status)
        headersubLayout.addLayout(layout_author)
        headersubLayout.addLayout(layout_requestor)

        headerMainLayout.addLayout(headersubLayout)
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

