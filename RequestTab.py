from PySide import QtGui, QtCore

class RequestTab(QtGui.QWidget):
    def __init__(self, parent = None):
        super(RequestTab,self).__init__()
        self.parent = parent

        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


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
        self.combo_type.addItems(['New Part', 'BOM Update', 'Firmware Update', 'Configurator Update', 'Product EOL'])
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
        self.label_detail = QtGui.QLabel("Enter request and additional information below:")
        self.text_detail = QtGui.QTextEdit(self)

        layout_body.addWidget(self.label_detail)
        layout_body.addWidget(self.text_detail)


        groupbox_header = QtGui.QGroupBox("ECN Header")
        groupbox_detail = QtGui.QGroupBox("ECN Request Details")

        groupbox_header.setLayout(headerMainLayout)
        groupbox_detail.setLayout(layout_body)

        mainLayout.addWidget(groupbox_header)
        mainLayout.addWidget(groupbox_detail)

        self.line_requestor.setText(self.parent.parent.user_info['name'])

