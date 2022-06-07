from PySide6 import QtGui, QtCore, QtWidgets
import sys, os
from SignaturePanel import *

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))


class SignatureTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(SignatureTab,self).__init__()
        self.parent = parent
        self.job_titles =[]
        self.findJobTitles()
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        mainlayout.addWidget(self.toolbar)
        
        self.signatures = QtWidgets.QListView()
        self.signatures.setStyleSheet("QListView{background-color:#f0f0f0}")
        self.signatures.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.signatures.setResizeMode(QtWidgets.QListView.Adjust)
        self.signatures.setItemDelegate(SignatureDelegate())
        
        self.model = SignatureModel()
        self.signatures.setModel(self.model)
        
        self.signatures.selectionModel().selectionChanged.connect(self.onRowSelect)
        
        mainlayout.addWidget(self.signatures)
                
        self.button_add = QtWidgets.QPushButton("Add Signature")
        print(self.parent.tab_ecn.line_status.text())
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.addRow)
        self.button_remove = QtWidgets.QPushButton("Remove Signature")
        self.button_remove.setDisabled(True)
        icon_loc = icon = os.path.join(program_location,"icons","minus.png")
        self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        self.button_remove.clicked.connect(self.removeRow)
        self.button_edit = QtWidgets.QPushButton("Edit Signature")
        icon_loc = icon = os.path.join(program_location,"icons","edit.png")
        self.button_edit.setIcon(QtGui.QIcon(icon_loc))
        self.button_edit.setDisabled(True)
        self.button_edit.clicked.connect(self.editSignature)
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_edit)
        
        
        if self.parent.ecn_data is not None:
            if self.parent.parent.user_info['user']==self.parent.ecn_data["AUTHOR"]:
                self.signatures.doubleClicked.connect(self.editSignature)
            else:
                self.button_add.setDisabled(True)
        
        if self.parent.parent.user_info['role']=="Manager":
            self.signatures.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.button_revoke = QtWidgets.QPushButton("Reject to selected")
            icon_loc = icon = os.path.join(program_location,"icons","reject.png")
            self.button_revoke.setIcon(QtGui.QIcon(icon_loc))
            self.button_revoke.setEnabled(False)
            self.button_revoke.clicked.connect(self.rejectToSelected)
            self.toolbar.addWidget(self.button_revoke)

        self.setLayout(mainlayout)       

    def onRowSelect(self):
        if self.parent.parent.user_info['role']=="Manager" and self.parent.tab_ecn.line_status.text()!="Completed":
            row = self.signatures.currentIndex().row()
            self.button_revoke.setEnabled(bool(self.signatures.selectionModel().selectedIndexes()) and self.model.get_signed_date(row) is not None)
        if self.parent.parent.user_info['user']==self.parent.tab_ecn.line_author.text() and self.parent.tab_ecn.line_status.text()!="Completed":
            self.button_remove.setEnabled(bool(self.signatures.selectionModel().selectedIndexes()))
            self.button_edit.setEnabled(bool(self.signatures.selectionModel().selectedIndexes()))
        
    def addRow(self):
        self.signature = SignaturePanel(self)
        
    def editSignature(self):
        index = self.signatures.currentIndex()
        self.sig_editor = SignaturePanel(self,index.row())
        
    def rejectToSelected(self):
        row = self.signatures.currentIndex().row()
        user = self.model.get_user(row)
        users = []
        if self.getUserRole(user)=="Signer":
            comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Rejection reason", "")
            if ok and comment!="":
                table_dict = self.getTableDict()
                for key in table_dict.keys():
                    if table_dict[key]>=table_dict[user] and key != self.parent.parent.user_info['user']:
                        self.parent.cursor.execute(f"UPDATE SIGNATURE SET SIGNED_DATE = Null where ECN_ID='{self.parent.ecn_id}' and USER_ID='{key}'")
                        users.append(key)
                if len(users)>1:
                    users = ",".join(users)
                else:
                    users = users[0]
                comment = f'For user: {user} - additionally the approval for the following users have also been resetted: {users}\n  --Reason: ' + comment
                self.parent.addComment(self.parent.ecn_id, comment, f"Rejecting to signer")
                self.parent.db.commit()
                self.parent.setECNStage(table_dict[user])
                self.dispMsg(f"Rejection successful. ECN stage has been set to {table_dict[user]}")
                # users = user+','+users
                self.parent.addNotification(self.parent.ecn_id,"Rejected To Signer",from_user=self.parent.parent.user_info['user'],userslist=users,msg=comment)
            if ok and comment=="":
                self.dispMsg("Rejection failed. Comment field was left blank.")
        else:
            self.dispMsg(f"Rejection failed: you do not have permissions to reject {user}'s approval")
        self.repopulateTable()
        
    def getTableDict(self):
        table_dict={}
        for row in range(self.rowCount()):
            user = self.model.get_user(row)
            job_title = self.model.get_job_title(row)
            stage =self.parent.parent.stageDict[job_title]
            table_dict[user]=stage
        return table_dict
        
            
    def findUserIndex(self,userList, role):
        index = 0
        try:
            for user in userList:
                if user[0]==role:
                    return index
                else:
                    index+=1
            self.dispMsg(f"No users found matching role:{role}. Please add user or remove role from requirements.")
        except Exception as e:
            print(e)

        
    def removeRow(self):
        index = self.signatures.selectionModel().selectedIndexes()
        index = sorted(index, reverse=True)
        for item in index:
            row = item.row()
            if self.model.get_signed_date(row) is None:
                self.model.removeRow(row)
        
    def findJobTitles(self):
        self.parent.cursor.execute("Select DISTINCT JOB_TITLE FROM USER")
        results = self.parent.cursor.fetchall()
        for result in results:
            self.job_titles.append(result[0])
        if "Admin" in self.job_titles:
            self.job_titles.remove("Admin")
        if len(self.job_titles)==0:
            self.dispMsg("No Job Titles found, please add Jobs and Users.")
        else:
            self.job_titles.sort()
        #print(self.job_titles)
        
    def getUserRole(self,user):
        self.parent.cursor.execute(f"select ROLE from USER where USER_ID='{user}'")
        result = self.parent.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            self.dispMsg(f"Error: no role found for {user}")
            return None

        
    def repopulateTable(self):
        self.model.clear_signatures()
        command = f"Select * from SIGNATURE where ECN_ID='{self.parent.ecn_id}' and TYPE='Signing'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        for result in results:
            self.model.add_signature(result['JOB_TITLE'], result['NAME'], result['USER_ID'], result['SIGNED_DATE'])
            
    def rowCount(self):
        return self.model.rowCount(self.signatures)
    
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
            
    def resizeEvent(self, e):
        self.model.layoutChanged.emit()
                
PADDING = QtCore.QMargins(15, 2, 15, 2)
                
class SignatureDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        
        job_title, name, user, signed_date = index.model().data(index, QtCore.Qt.DisplayRole)
        
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
        
        if signed_date is not None:
            rect = QtCore.QRect(r.topRight()+QtCore.QPoint(-150,2),QtCore.QSize(130,16))
            color = QtGui.QColor("#CAFFBF")
            painter.setBrush(color)
            painter.drawRoundedRect(rect, 5, 5)
        
        font = painter.font()
        font.setPointSize(10)
        # font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(r.topLeft()+QtCore.QPoint(25,15),job_title)
        if signed_date is not None:
            painter.drawText(r.topLeft()+QtCore.QPoint(725,15),signed_date)
        painter.drawText(r.topLeft()+QtCore.QPoint(375,15),name)
        
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,25)

class SignatureModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(SignatureModel, self).__init__(*args, **kwargs)
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
        
    def update_signature(self,row,job_title, name, user,signed_date=None):
        self.signatures[row]=(job_title, name, user, signed_date)
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

    def add_signature(self, job_title, name, user,signed_date=None):
        # Access the list via the model.
        self.signatures.append((job_title, name, user, signed_date))
        self.users.append(user)
        # Trigger refresh.
        self.layoutChanged.emit()