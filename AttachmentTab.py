from PySide6 import QtGui, QtCore, QtWidgets
from pathlib import Path
import os, sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

supported_type = ["doc","docx","dwg","stl","slddrw","sldprt","stp","sldasm","ppt","pptx",""]

class AttachmentTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(AttachmentTab,self).__init__()
        self.parent = parent
        self.user_info = parent.user_info
        self.files = []
        self.initAtt()
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAcceptDrops(True)

    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        #self.list_attachment = QtWidgets.QListWidget(self)
        #mainlayout.addWidget(self.list_attachment)
        
        self.button_add = QtWidgets.QPushButton("Add Files")
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.addFiles)
        
        self.button_remove = QtWidgets.QPushButton("Remove")
        self.button_remove.setDisabled(True)
        icon_loc = icon = os.path.join(program_location,"icons","minus.png")
        self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        self.button_remove.clicked.connect(self.removeRow)
        
        self.button_open = QtWidgets.QPushButton("Open")
        self.button_open.setDisabled(True)
        icon_loc = icon = os.path.join(program_location,"icons","open.png")
        self.button_open.setIcon(QtGui.QIcon(icon_loc))
        self.button_open.clicked.connect(self.openFile)
        
        self.button_open_loc = QtWidgets.QPushButton("Open File Location")
        self.button_open_loc.setDisabled(True)
        icon_loc = icon = os.path.join(program_location,"icons","open_folder.png")
        self.button_open_loc.setIcon(QtGui.QIcon(icon_loc))
        self.button_open_loc.clicked.connect(self.openFileLoc)
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_open)
        self.toolbar.addWidget(self.button_open_loc)
        
        
        self.attachments = QtWidgets.QListView()
        self.attachments.setStyleSheet("QListView{background-color:#f0f0f0}")
        self.attachments.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.attachments.setResizeMode(QtWidgets.QListView.Adjust)
        self.attachments.setItemDelegate(AttachmentDelegate())
        self.attachments.doubleClicked.connect(self.openFile)
        
        self.model = AttachmentModel()
        self.attachments.setModel(self.model)
        
        self.attachments.selectionModel().selectionChanged.connect(self.onRowSelect)

        mainlayout.addWidget(self.toolbar)
        mainlayout.addWidget(self.attachments)

        self.setLayout(mainlayout)
        
    def onRowSelect(self):
        if self.user_info['user']==self.parent.doc_data["AUTHOR"] and self.parent.doc_data["STATUS"]!="Completed":
            self.button_remove.setEnabled(bool(self.attachments.selectionModel().selectedIndexes()))
        self.button_open.setEnabled(bool(self.attachments.selectionModel().selectedIndexes()))
        self.button_open_loc.setEnabled(bool(self.attachments.selectionModel().selectedIndexes()))


    def dropEvent(self, e):
        urlList = e.mimeData().urls()
        cfiles=[]
        for item in urlList:
            url = item.toLocalFile()
            if str(Path(url).resolve())[:2] ==r"\\":
                if str(Path(url).resolve()) not in self.files:
                    file_info = QtCore.QFileInfo(url)
                    icon_provider=QtGui.QAbstractFileIconProvider()
                    icon = icon_provider.icon(file_info)
                    self.model.add_attachment(url[url.rfind("/")+1:], str(Path(url).resolve()),icon)
                    self.files.append(str(Path(url).resolve()))
            else:
                cfiles.append(str(Path(url).resolve()))
        if len(cfiles)>0:
            self.dispMsg(f"The following files were not accepted as they reside on your local machine and is not accessible by other users:{cfiles}")

    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()
            
    def openFile(self):
        index = self.attachments.currentIndex()
        try:
            os.startfile(index.data(QtCore.Qt.DisplayRole)[1])
        except Exception as e:
            print(e)
            
    def openFileLoc(self):
        index = self.attachments.currentIndex()
        try:
            path = Path(index.data(QtCore.Qt.DisplayRole)[1])
            os.startfile(path.parent)
        except Exception as e:
            print(e)
        
    def addFiles(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        cfiles = []
        if dialog.exec():
            fileNames = dialog.selectedFiles()
            for url in fileNames:
                if str(Path(url).resolve())[:2] ==r"\\":
                    if str(Path(url).resolve()) not in self.files:
                        file_info = QtCore.QFileInfo(url)
                        icon_provider=QtGui.QAbstractFileIconProvider()
                        icon = icon_provider.icon(file_info)
                        self.model.add_attachment(url[url.rfind("/")+1:], str(Path(url).resolve()),icon)
                        self.files.append(str(Path(url).resolve()))
                else:
                    cfiles.append(str(Path(url).resolve()))
            if len(cfiles)>0:
                self.dispMsg(f"The following were files not accepted as they reside on your local machine and is not accessible by other users:{cfiles}")
                
                
    def removeRow(self):
        index = self.attachments.selectionModel().selectedIndexes()
        index = sorted(index, reverse=True)
        for item in index:
            row = item.row()
            #print(self.table.item(row, 1).text())
            #print(item.data(QtCore.Qt.DisplayRole)[1])
            #print(self.files)
            self.files.remove(item.data(QtCore.Qt.DisplayRole)[1])
            self.model.removeRow(row)
            
    def rowCount(self):
        return self.model.rowCount(self.attachments)

    def autoGenParts(self):
        parts = []
        for x in range(self.table.rowCount()):
            path = Path(self.table.item(x,1).text())
            part = path.stem
            if part not in parts:
                self.parent.tab_parts.addPart(part)
                parts.append(part)
        self.dispMsg("Parts have been generated in the parts tab")
        
    def repopulateTable(self):
        command = "Select * from ATTACHMENTS where DOC_ID= '"+self.parent.doc_id +"'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        for result in results:
            #print(result['FILEPATH'])
            file_info = QtCore.QFileInfo(result['FILEPATH'])
            icon_provider=QtGui.QAbstractFileIconProvider()
            icon = icon_provider.icon(file_info)
            self.model.add_attachment(result['FILENAME'], result['FILEPATH'],icon)
            self.files.append(result['FILEPATH'])
            
    def resizeEvent(self, e):
        self.model.layoutChanged.emit()
    

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()



PADDING = QtCore.QMargins(15, 2, 15, 2)

class AttachmentDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        
        filename, filepath, icon = index.model().data(index, QtCore.Qt.DisplayRole)
        
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
        
        # painter.setPen(lineMarkedPen)
        # painter.drawLine(r.topLeft(),r.topRight())
        # painter.drawLine(r.topRight(),r.bottomRight())
        # painter.drawLine(r.bottomLeft(),r.bottomRight())
        # painter.drawLine(r.topLeft(),r.bottomLeft())
        
        # draw filname
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(r.topLeft()+QtCore.QPoint(35,12),filename)
        # draw the filepath
        font = painter.font()
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(r.topLeft()+QtCore.QPoint(35,25),filepath)
        
        ic = QtGui.QIcon(icon)
        ic.paint(painter,r,QtCore.Qt.AlignLeft)
        
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,32)

class AttachmentModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(AttachmentModel, self).__init__(*args, **kwargs)
        self.attachments = []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.attachments[index.row()]

    def setData(self, index, role, value):
        self._size[index.row()]

    def rowCount(self, index):
        return len(self.attachments)
    
    def removeRow(self, row):
        del self.attachments[row]
        self.layoutChanged.emit()

    def clear_attachments(self):
        self.attachments = []
        
    def getFilePath(self, row):
        return self.attachments[row][1]
    
    def getFileName(self, row):
        return self.attachments[row][0]

    def add_attachment(self, filename, filepath, icon=None):
        # Access the list via the model.
        self.attachments.append((filename, filepath, icon))
        # Trigger refresh.
        self.layoutChanged.emit()