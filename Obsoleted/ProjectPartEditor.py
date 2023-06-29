from PySide6 import QtWidgets, QtCore, QtGui
import os, sys


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class ProjectPartEditor(QtWidgets.QWidget):
    def __init__(self,parent=None,index=None):
        super(ProjectPartEditor,self).__init__()
        self.windowWidth =  400
        self.windowHeight = 550
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.parent = parent
        self.doc_id = parent.doc_id
        self.initAtt()
        self.initUI()
        if index is not None:
            self.row = index.row()
            self.loadData(index.data(QtCore.Qt.DisplayRole))
        else:
            self.row = None
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
        title = "Part Editor"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.center()

    def initUI(self):
        form_layout = QtWidgets.QFormLayout(self)
        form_layout.setLabelAlignment(QtGui.Qt.AlignRight)
        self.line_part = QtWidgets.QLineEdit()
        self.line_part.setMaxLength(30)
        self.line_desc = QtWidgets.QLineEdit()
        self.line_desc.setMaxLength(40)
        self.box_type = QtWidgets.QComboBox()
        self.box_type.addItems(["","Injection Molded","Die Casted","Off The Shelf","Machined"])
        self.box_status = QtWidgets.QComboBox()
        self.box_status.addItems(["","Designing","Quoting","Quote Review","Requisition Placed","Ordered"])
        self.line_vendor = QtWidgets.QLineEdit()
        self.line_vendor_part = QtWidgets.QLineEdit()
        self.line_tooling_cost = QtWidgets.QLineEdit()
        self.line_tooling_cost.setValidator(QtGui.QIntValidator(0,999999))
        self.line_tooling_po = QtWidgets.QLineEdit()
        self.line_cost_per = QtWidgets.QLineEdit()
        self.line_cost_per.setValidator(QtGui.QDoubleValidator(0.0,999999.99,2))
        self.text_details = QtWidgets.QTextEdit()
        self.button_save = QtWidgets.QPushButton("Add Part")
        self.button_save.clicked.connect(self.saveData)
        
        form_layout.addRow("Part ID:", self.line_part)
        form_layout.addRow("Description:", self.line_desc)
        form_layout.addRow("Type of Part:", self.box_type)
        form_layout.addRow("Status:", self.box_status)
        form_layout.addRow("Vendor:", self.line_vendor)
        form_layout.addRow("Vendor. Part ID:", self.line_vendor_part)
        form_layout.addRow("Tooling P.O:", self.line_tooling_po)
        form_layout.addRow("Tooling Cost:", self.line_tooling_cost)
        form_layout.addRow("Cost Per:", self.line_cost_per)
        form_layout.addRow("Misc Details:", self.text_details)
        form_layout.addRow(self.button_save)
                
    def loadData(self,data):
        # part_id, desc,fab_type,status,vendor, vendor_part_id,tooling_po, tooling_cost,cost_per,notes,part_po,ecn, qty_on_hand, qty_incoming
        self.line_part.setText(data[0])
        self.line_desc.setText(data[1])
        self.box_type.setCurrentText(data[2])
        self.box_status.setCurrentText(data[3])
        self.line_vendor.setText(data[4])
        self.line_vendor_part.setText(data[5])
        self.line_tooling_po.setText(data[6])
        self.line_tooling_cost.setText(data[7])
        self.line_cost_per.setText(data[8])
        self.text_details.setText(data[9])
        self.button_save.setText("Update Part")
        
    def checkEmptyFields(self,part_id,desc,fab_type):
        if part_id=="":
            return False
        if desc == "":
            return False
        if fab_type=="":
            return False
        return True
        
    def saveData(self):
        part_id = self.line_part.text()
        desc = self.line_desc.text()
        fab_type = self.box_type.currentText()
        vendor = self.line_vendor.text()
        vendor_part_id = self.line_vendor_part.text()
        status = self.box_status.currentText()
        tooling_po = self.line_tooling_po.text()
        tooling_cost = self.line_tooling_cost.text()
        cost_per = self.line_cost_per.text()
        notes = self.text_details.toPlainText()
        ecn = ""
        part_po = ""
        qty_on_hand = ""
        qty_incoming = ""
        if self.row is not None:
            if self.checkEmptyFields(part_id, desc, fab_type):
                self.parent.model.update_part_data(self.row, part_id, desc,fab_type,status,vendor, vendor_part_id,tooling_po, tooling_cost,cost_per,part_po,notes,ecn, qty_on_hand, qty_incoming)
            else:
                self.dispMsg("Update Failed. There are empty fields.")
        else:
            if not self.parent.model.exist_part(part_id):
                if self.checkEmptyFields(part_id, desc, fab_type):
                    self.parent.model.add_part(part_id, desc,fab_type,status,vendor, vendor_part_id,tooling_po, tooling_cost,cost_per,part_po,notes,ecn, qty_on_hand, qty_incoming)
                else:
                    self.dispMsg("Save Failed. There are empty fields.")
            else:
                self.dispMsg("This part has already been added to the part list!")

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()