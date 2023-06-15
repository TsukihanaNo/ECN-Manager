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

class ScheduleTaskWindow(QtWidgets.QWidget):
    def __init__(self,parent=None,item=None):
        super(ScheduleTaskWindow,self).__init__()
        self.windowWidth =  400
        self.windowHeight = 550
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.parent = parent
        self.doc_id = parent.doc_id
        self.initAtt()
        self.initUI()
        if item is not None:
            self.item = item
            self.loadData()
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
        title = "Task Editor"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.center()

    def initUI(self):
        form_layout = QtWidgets.QFormLayout(self)
        form_layout.setLabelAlignment(QtGui.Qt.AlignRight)
        self.line_desc = QtWidgets.QLineEdit()
        self.box_status = QtWidgets.QComboBox()
        self.box_status.addItems(["","Pending","Started","Completed"])
        self.dateedit_start = QtWidgets.QDateEdit(calendarPopup=True)
        self.dateedit_start.setDate(QtCore.QDate.currentDate())
        self.dateedit_end = QtWidgets.QDateEdit(calendarPopup=True)
        self.dateedit_end.setDate(QtCore.QDate.currentDate())
        self.line_duration = QtWidgets.QLineEdit()
        self.line_duration.setValidator(QtGui.QIntValidator(1,999))
        self.box_assigned_to = QtWidgets.QComboBox()
        self.text_notes = QtWidgets.QTextEdit()
        self.button_save = QtWidgets.QPushButton("Add Task")
        self.button_save.clicked.connect(self.saveData)
        
        form_layout.addRow("Name:", self.line_desc)
        form_layout.addRow("Status:", self.box_status)
        form_layout.addRow("Start Date:", self.dateedit_start)
        form_layout.addRow("End Date:", self.dateedit_end)
        form_layout.addRow("Duration (Days):", self.line_duration)
        form_layout.addRow("Assigned To:", self.box_assigned_to)
        form_layout.addRow("Notes:", self.text_notes)
        form_layout.addRow(self.button_save)
        
    def saveData(self):
        if self.parent.tasks.currentItem() is None:
            item = QtWidgets.QTreeWidgetItem(self.parent.tasks)
        else:
            item = QtWidgets.QTreeWidgetItem(self.parent.tasks.currentItem())
            self.parent.tasks.expandItem(self.parent.tasks.currentItem())
        item.setText(0,self.line_desc.text())
        item.setText(2, self.dateedit_start.date().toString("MM/dd/yyyy"))
        item.setText(3,self.dateedit_end.date().toString("MM/dd/yyyy"))

    def updateDate(self):
        pass

    def loadData(self):
        self.line_desc.setText(self.item.text(0))
        self.dateedit_start.setDate(QtCore.QDate.fromString(self.item.text(2),"MM/dd/yyyy"))
        self.dateedit_end.setDate(QtCore.QDate.fromString(self.item.text(3),"MM/dd/yyyy"))
                