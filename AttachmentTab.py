from PySide6 import QtGui, QtCore, QtWidgets
from pathlib import Path
import os, sys, shutil
from FileTransferWidget import *

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

supported_type = ["doc","docx","dwg","stl","slddrw","sldprt","stp","sldasm","ppt","pptx",""]
maxFileLoad = 1024*15000  #restrict max size limit to 15mb 
blockSize = 1024 * 5000   #will read 5mb at a time

class AttachmentTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(AttachmentTab,self).__init__()
        self.parent = parent
        self.user_info = parent.user_info
        self.settings = parent.settings
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

        
    def onRowSelect(self):
        if self.user_info['user']==self.parent.doc_data["author"] and self.parent.doc_data["status"]!="Completed":
            self.button_remove.setEnabled(bool(self.attachments.selectionModel().selectedIndexes()))
        self.button_open.setEnabled(bool(self.attachments.selectionModel().selectedIndexes()))
        self.button_open_loc.setEnabled(bool(self.attachments.selectionModel().selectedIndexes()))


    def dropEvent(self, e):
        ecn_folder = os.path.join(self.settings["ECN_Temp"],self.parent.tab_ecn.line_id.text())
        if os.path.exists(ecn_folder):
            self.fileTransferWidget = FileTransferWidget(self)
            self.fileTransferWidget.setClose(False)
            # print(self.settings["Buffer_Path"])
            urlList = e.mimeData().urls()
            cfiles=[]
            for item in urlList:
                url = item.toLocalFile()
                url_path = str(Path(url).resolve())
                if os.path.isdir(url_path):
                # if self.settings["Buffer_Path"] in url_path:
                    if str(Path(url).resolve()) not in self.files:
                        file_info = QtCore.QFileInfo(url)
                        icon_provider=QtGui.QAbstractFileIconProvider()
                        icon = icon_provider.icon(file_info)
                        dst = os.path.join(self.settings["ECN_Temp"],self.parent.tab_ecn.line_id.text(),url[url.rfind("/")+1:])
                        self.model.add_attachment(url[url.rfind("/")+1:], dst,icon)
                        self.files.append(dst)
                        # self.model.add_attachment(url[url.rfind("/")+1:], url_path,icon)
                        # self.files.append(url_path)
                        # shutil.copytree(url_path,dst)
                        file_count = self.getFileCount(url_path)
                        self.current_count = 0 
                        os.mkdir(dst)
                        self.fileTransferWidget.label_directory.setText("Current Item:" + url_path)
                        self.fullDirCopy(url_path,dst,file_count)
                        # QtWidgets.QApplication.processEvents()
                else:
                    cfiles.append(url_path)
            self.fileTransferWidget.label_directory.setText("Completed! Please close this window.")
            self.fileTransferWidget.label_count.setText("All files have been uploaded.")
            self.fileTransferWidget.setClose(True)
            self.parent.save()
            if len(cfiles)>0:
                self.dispMsg(f"The following files were not accepted as they are not directories:{cfiles}")
                # buffer_path = self.settings["Buffer_Path"]
                # self.dispMsg(f"The following files were not accepted as they reside out of the defined file buffer Location ({buffer_path}) : {cfiles}")
        else:
            self.dispMsg("ECN has not been saved yet. Please save ECN and try again.")

    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()
            
    def upload(self):
        pass
            
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
        ecn_folder = os.path.join(self.settings["ECN_Temp"],self.parent.tab_ecn.line_id.text())
        if os.path.exists(ecn_folder):
            dialog = QtWidgets.QFileDialog(self)
            dialog.setFileMode(QtWidgets.QFileDialog.Directory)
            dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly,True)
            cfiles = []
            if dialog.exec():
                fileNames = dialog.selectedFiles()
                self.fileTransferWidget = FileTransferWidget(self)
                self.fileTransferWidget.setClose(False)
                for url in fileNames:
                    if os.path.isdir(url):
                    # if self.settings["Buffer_Path"] in url_path:
                        if str(Path(url).resolve()) not in self.files:
                            file_info = QtCore.QFileInfo(url)
                            icon_provider=QtGui.QAbstractFileIconProvider()
                            icon = icon_provider.icon(file_info)
                            dst = os.path.join(self.settings["ECN_Temp"],self.parent.tab_ecn.line_id.text(),url[url.rfind("/")+1:])
                            self.model.add_attachment(url[url.rfind("/")+1:], dst,icon)
                            self.files.append(dst)
                            # self.model.add_attachment(url[url.rfind("/")+1:], url_path,icon)
                            # self.files.append(url_path)
                            # shutil.copytree(url_path,dst)
                            file_count = self.getFileCount(url)
                            self.current_count = 0 
                            os.mkdir(dst)
                            self.fileTransferWidget.label_directory.setText("Current Item:" + url)
                            self.fullDirCopy(url,dst,file_count)
                            # QtWidgets.QApplication.processEvents()
                    else:
                        cfiles.append(url)
                self.fileTransferWidget.label_directory.setText("Completed! Please close this window.")
                self.fileTransferWidget.label_count.setText("All files have been uploaded.")
                self.fileTransferWidget.setClose(True)
                self.parent.save()
                if len(cfiles)>0:
                    self.dispMsg(f"The following files were not accepted as they are not directories:{cfiles}")
                    # buffer_path = self.settings["Buffer_Path"]
                    # self.dispMsg(f"The following files were not accepted as they reside out of the defined file buffer Location ({buffer_path}) : {cfiles}")
        else:
            self.dispMsg("ECN has not been saved yet. Please save ECN and try again.")
                
                
    def removeRow(self):
        index = self.attachments.selectionModel().selectedIndexes()
        index = sorted(index, reverse=True)
        for item in index:
            row = item.row()
            #print(self.table.item(row, 1).text())
            #print(item.data(QtCore.Qt.DisplayRole)[1])
            #print(self.files)
            shutil.rmtree(item.data(QtCore.Qt.DisplayRole)[1])
            self.files.remove(item.data(QtCore.Qt.DisplayRole)[1])
            self.model.removeRow(row)
        self.parent.save()
        
    def removeAllAttachments(self):
        for item in self.model.getAllFilePath():
            shutil.rmtree(item[1])
            
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
        command = "Select * from attachments where doc_id= '"+self.parent.doc_id +"'"
        self.parent.cursor.execute(command)
        results = self.parent.cursor.fetchall()
        for result in results:
            #print(result['filepath'])
            file_info = QtCore.QFileInfo(result['filepath'])
            icon_provider=QtGui.QAbstractFileIconProvider()
            icon = icon_provider.icon(file_info)
            self.model.add_attachment(result['filename'], result['filepath'],icon)
            self.files.append(result['filepath'])
            
    def copyFile(self,pathFrom,pathTo,maxFileLoad = maxFileLoad):
        """
        copy one file pathFrom to pathTo, byte for byte
        uses binary file modes
        """
        chunksize = 0
        if os.path.isfile(pathTo) == False:
            if os.path.getsize(pathFrom)<=maxFileLoad:
                #if file is less than 15mb
                #read the entire image file into memory
                # print('reading file')
                fileFrom = open(pathFrom,'rb')
                # print('reading bytes')
                bytesFrom = fileFrom.read()
                #write all bytes into new file
                bytesTo = open(pathTo, 'wb')
                # print('writing bytes')
                bytesTo.write(bytesFrom)
                #manual closure of file objects
                fileFrom.close()
                bytesTo.close()
                QtWidgets.QApplication.processEvents()
            else:
                #if file is bigger than 15mb
                fileFrom = open(pathFrom,'rb')
                fileTo = open(pathTo,'wb')
                # totalsize = os.path.getsize(pathFrom)
                while True:
                    QtWidgets.QApplication.processEvents()
                    #reads the data from the original file 5mb at a time into the memory
                    bytesFrom = fileFrom.read(blockSize)
                    #when there is no more data comming in from the read(), break from while loop
                    if not bytesFrom: break
                    #copy the 5mb read into memory into the new file
                    # print ('Nom nom nom...digesting byte chunks... ',100*(float(chunksize)/totalsize),'%')
                    chunksize += blockSize
                    fileTo.write(bytesFrom)
                # print ('Digesting complete... 100.0%')
                #manual closure of file objects
                fileFrom.close()
                fileTo.close()
        else:
            pass
            # dupDecision(pathFrom)
            
    def fullDirCopy(self,dirFrom,dirTo,file_count):
        for filename in os.listdir(dirFrom):
            pathFrom = os.path.join(dirFrom,filename)
            if filename[0]!="~":
                pathTo = os.path.join(dirTo,filename)
                if not os.path.isdir(pathFrom): #if the tested file is not a directory
                    try:
                        # print ('Copying: ',pathFrom,' to ',pathTo)
                        self.current_count+=1
                        # print("copying: ", pathFrom, " to ", pathTo)
                        self.copyFile(pathFrom,pathTo)
                        self.fileTransferWidget.label_count.setText(f"Uploading {self.current_count} / {file_count}")
                        # self.fileTransferWidget.text_error.append('Copying: ',pathFrom, ' to ', pathTo)
                    except:
                        self.fileTransferWidget.text_error.append('Error copying: ', pathFrom,' to ',pathTo,'--skipped')
                        self.fileTransferWidget.text_error.append(sys.exc_info()[0],sys.exc_info()[1])
                else:
                    try:
                        if not os.path.exists(pathTo):
                            os.mkdir(pathTo)
                            self.fullDirCopy(pathFrom,pathTo,file_count)
                    except:
                        self.fileTransferWidget.text_error.append('Error Diving into directory ',pathFrom)
                        self.fileTransferWidget.text_error.append(sys.exc_info()[0],sys.exc_info()[1])
            else:
                self.fileTransferWidget.text_error.append('skipping: lock file ',pathFrom)
            # QtWidgets.QApplication.processEvents()
    
    def getFileCount(self,dirFrom):
        fileCount = 0
        for filename in os.listdir(dirFrom):
            pathFrom = os.path.join(dirFrom,filename)
            # pathTo = os.path.join(dirTo,filename)
            if not os.path.isdir(pathFrom): #if the tested file is not a directory
                fileCount +=1
                # print(pathFrom)
            else:
                fileCount += self.getFileCount(pathFrom)
        return (fileCount)
            
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
    
    def getAllFilePath(self):
        return self.attachments
    
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