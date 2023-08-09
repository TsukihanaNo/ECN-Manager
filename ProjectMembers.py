from PySide6 import QtWidgets, QtCore, QtGui
from SignaturePanel import *
import os, sys

class ProjectMembers(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(ProjectMembers,self).__init__()
        self.windowHeight = 400
        self.windowWidth = 600
        self.doc_type = "project_member"
        self.parent = parent
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.stageDictPRQ = parent.stageDictPRQ
        self.cursor = parent.cursor
        self.db = parent.db
        self.user_info = parent.user_info
        self.doc_id = parent.doc_id
        self.access = parent.access
        self.initAtt()
        self.initUI()
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
        title = "Members"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.clicked.connect(self.save)
        self.button_add = QtWidgets.QPushButton("Add Member")
        self.button_add.clicked.connect(self.addRow)
        self.button_remove = QtWidgets.QPushButton("Remove Member")
        self.button_remove.clicked.connect(self.removeRow)
        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        if self.access == "read":
            self.button_add.setDisabled(True)
            self.button_remove.setDisabled(True)
            self.button_save.setDisabled(True)
        
        self.members = QtWidgets.QListView()
        self.members.setStyleSheet("QListView{background-color:#f0f0f0}")
        self.members.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.members.setResizeMode(QtWidgets.QListView.Adjust)
        self.members.setItemDelegate(MemberDelegate())
        
        self.model = MemberModel()
        self.members.setModel(self.model)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.members)
        self.load()
        
    def addRow(self):
        self.members_panel = SignaturePanel(self,sig_type="members")
        
    def removeRow(self):
        index = self.members.selectionModel().selectedIndexes()
        index = sorted(index, reverse=True)
        for item in index:
            row = item.row()
            self.model.removeRow(row)
                
    def rowCount(self):
        return self.model.rowCount(self.members)
                
    def save(self):
        self.clearData()
        self.parent.members = [self.parent.line_author.text()]
        for row in range(self.rowCount()):
            data = (self.doc_id,self.model.get_user(row),self.model.get_name(row),self.model.get_job_title(row))
            self.parent.members.append(self.model.get_user(row))
            self.cursor.execute("INSERT INTO PROJECT_MEMBERS(PROJECT_ID,USER_ID,USER_NAME,JOB_TITLE) VALUES(?,?,?,?)",(data))
        self.db.commit
        self.parent.members.sort()
        self.dispMsg("Saved!")
    
    def load(self):
        self.cursor.execute(f"SELECT * from PROJECT_MEMBERS where PROJECT_ID='{self.doc_id}'")
        results = self.cursor.fetchall()
        for result in results:
            self.model.add_signature(result[3],result[2],result[1])
    
    def clearData(self):
        self.cursor.execute(f"DELETE FROM PROJECT_MEMBERS WHERE PROJECT_ID = '{self.doc_id}'")
        self.db.commit()
        
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
        
PADDING = QtCore.QMargins(15, 2, 15, 2)
                
class MemberDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        
        job_title, name, user= index.model().data(index, QtCore.Qt.DisplayRole)
        
        #lineMarkedPen = QtGui.QPen(QtGui.QColor("#f0f0f0"),1,QtCore.Qt.SolidLine)
        
        r = option.rect.marginsRemoved(PADDING)
        painter.setPen(QtCore.Qt.NoPen)
        if option.state & QtWidgets.QStyle.State_Selected:
            color = QtGui.QColor("#A0C4FF")
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            color = QtGui.QColor("#BDB2FF")
        else:
            color = QtGui.QColor("#FFFFFC")
        painter.setBrush(color)
        painter.drawRoundedRect(r, 5, 5)
        
        font = painter.font()
        font.setPointSize(10)
        # font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(r.topLeft()+QtCore.QPoint(25,15),job_title)
        painter.drawText(r.topLeft()+QtCore.QPoint(375,15),name)
        
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,25)

class MemberModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(MemberModel, self).__init__(*args, **kwargs)
        self.signatures = []
        self.users = []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.signatures[index.row()]

    def setData(self, index, role, value):
        self._size[index.row()]

    def rowCount(self, index):
        return len(self.signatures)
    
    def removeRow(self, row):
        del self.signatures[row]
        del self.users[row]
        self.layoutChanged.emit()

    def clear_signatures(self):
        self.signatures = []
        self.users = []
        
    def update_signature(self,row,job_title, name, user):
        self.signatures[row]=(job_title, name, user)
        self.users[row]=user
        self.layoutChanged.emit()
        
    def get_job_title(self,row):
        return self.signatures[row][0]
    
    def get_name(self,row):
        return self.signatures[row][1]
        
    def get_user(self,row):
        return self.signatures[row][2]
    
    def get_signed_date(self,row):
        return self.signatures[row][3]

    def add_signature(self, job_title, name, user):
        # Access the list via the model.
        self.signatures.append((job_title, name, user))
        self.users.append(user)
        # Trigger refresh.
        self.layoutChanged.emit()