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

class PartEditor(QtWidgets.QWidget):
    def __init__(self,parent=None,index=None):
        super(PartEditor,self).__init__()
        self.windowWidth =  400
        self.windowHeight = 550
        self.parent = parent
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
        self.box_type.addItems(["","Fabricated","Purchased","Outside Service"])
        self.box_dispo = QtWidgets.QComboBox()
        self.box_dispo.addItems(["","Deplete","New","Scrap","Rework"])
        self.line_mfg = QtWidgets.QLineEdit()
        self.line_mfg_part = QtWidgets.QLineEdit()
        self.text_replace = QtWidgets.QTextEdit()
        self.text_reference = QtWidgets.QTextEdit()
        self.box_inspec = QtWidgets.QComboBox()
        self.box_inspec.addItems(["","N","Y"])
        self.button_save = QtWidgets.QPushButton("Add Part")
        self.button_save.clicked.connect(self.saveData)
        
        form_layout.addRow("Part ID:", self.line_part)
        form_layout.addRow("Description:", self.line_desc)
        form_layout.addRow("Type:", self.box_type)
        form_layout.addRow("Disposition:", self.box_dispo)
        form_layout.addRow("Manufacturer:", self.line_mfg)
        form_layout.addRow("Mfg. Part ID:", self.line_mfg_part)
        form_layout.addRow("Reference:", self.text_reference)
        form_layout.addRow("Replacing", self.text_replace)
        form_layout.addRow("Inspection:", self.box_inspec)
        form_layout.addRow(self.button_save)
        
        self.setLayout(form_layout)
        
    def loadData(self,data):
        self.line_part.setText(data[0])
        self.line_desc.setText(data[1])
        self.box_type.setCurrentText(data[2])
        self.box_dispo.setCurrentText(data[3])
        self.line_mfg.setText(data[4])
        self.line_mfg_part.setText(data[5])
        self.text_reference.setText(data[6])
        self.text_replace.setText(data[7])
        self.box_inspec.setCurrentText(data[8])
        self.button_save.setText("Update Part")
        
    def checkEmptyFields(self,part_id,desc,part_type,disposition,inspection):
        if part_id=="":
            return False
        if desc == "":
            return False
        if part_type=="":
            return False
        if disposition=="":
            return False
        if inspection=="":
            return False
        return True
        
    def saveData(self):
        part_id = self.line_part.text()
        desc = self.line_desc.text()
        part_type = self.box_type.currentText()
        disposition = self.box_dispo.currentText()
        mfg = self.line_mfg.text()
        mfg_part_id = self.line_mfg_part.text()
        replacing = self.text_replace.toPlainText()
        reference = self.text_reference.toPlainText()
        inspection = self.box_inspec.currentText()
        if self.row is not None:
            if self.checkEmptyFields(part_id, desc, part_type, disposition, inspection):
                self.parent.model.update_part_data(self.row, part_id, desc, part_type, disposition, mfg, mfg_part_id, reference,replacing, inspection)
                if self.parent.parent.parent.visual is not None:
                    status = self.parent.getStatus(part_id, part_type)
                    self.parent.model.update_status(self.row, status)
            else:
                self.dispMsg("Update Failed. There are empty fields.")
        else:
            if not self.parent.model.exist_part(part_id):
                if self.checkEmptyFields(part_id, desc, part_type, disposition, inspection):
                    if self.parent.parent.parent.visual is not None:
                        status = self.parent.getStatus(part_id, part_type)
                    else:
                        status = "NA"
                    self.parent.model.add_part(part_id, desc, part_type, disposition, mfg, mfg_part_id,reference,replacing, inspection,status)
                else:
                    self.dispMsg("Save Failed. There are empty fields.")
            else:
                self.dispMsg("This part has already been added to the part list!")

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()