from PySide6 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets, QtPrintSupport

import os, sys
from UserPanel import *
import sqlite3  


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class WebView(QtWidgets.QWidget):
    def __init__(self,parent=None, msg_disable=False):
        super(WebView,self).__init__()
        self.windowWidth =  900
        self.windowHeight = 600
        self.filepath = None
        self.doc_id = None
        self.msg_disable = msg_disable
        self.initAtt()
        self.initUI()
        #self.show()

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
        title = "Web View"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        
        

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar(self)
        self.button_print = QtWidgets.QPushButton("Export")
        self.button_print.clicked.connect(self.exportPDF)
        self.toolbar.addWidget(self.button_print)
        self.web = QtWebEngineWidgets.QWebEngineView()
        #self.web.load("http://qt-project.org/")
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.web)
        
    def setDocID(self,doc_id):
        self.doc_id = doc_id
        
    def load(self,url):
        self.show()
        self.web.load(url)
        
    def loadHtml(self,html):
        self.show()
        self.web.setHtml(html)
        
    def loadAndPrint(self,html,filepath):
        self.filepath = filepath
        self.web.setHtml(html)
        self.web.loadFinished.connect(self.printPDF)
        #self.web.printToPdf(r"D:\Programming Projects\ecn-manager\test2.pdf")
        
    # def print(self):
    #     printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
    #     dialog = QtPrintSupport.QPrintDialog(printer,self)
    #     if dialog.exec()==QtWidgets.QDialog.Accepted:
    #         print(printer.printerName())
    #         self.web.page.print(printer)
        
    def printPDF(self):
        self.web.printToPdf(self.filepath)
        if not self.msg_disable:
            self.web.pdfPrintingFinished.connect(self.printComplete) 
        
    def printComplete(self):
        self.dispMsg("pdf exporting done")
        
    def exportPDF(self):
        try:
            foldername = QtWidgets.QFileDialog().getExistingDirectory()
            if foldername:
                self.filepath = foldername+'\\'+self.doc_id+'.pdf'
                self.printPDF()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during ecn export.\n Error: {e}")
        
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    Users = WebView()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
