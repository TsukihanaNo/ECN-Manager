from PySide6 import QtWidgets, QtCore, QtGui
from PCNTab import *
from SignatureTab import *
from NotificationTab import *
from CommentTab import *
from datetime import datetime
from string import Template
import os, sys
import sqlite3  


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class PCNWindow(QtWidgets.QWidget):
    def __init__(self,parent=None, doc_id = None):
        super(PCNWindow,self).__init__()
        self.windowWidth =  950
        self.windowHeight = 800
        self.parent = parent
        self.doc_id = doc_id
        self.settings = parent.settings
        self.db = self.parent.db
        self.cursor = self.parent.cursor
        #self.getPCNCounter()
        #self.generatePCNID()
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
        title = "PCN Window"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        
        

    def initUI(self):
        mainLayout = QtWidgets.QVBoxLayout()
        self.toolbar = QtWidgets.QToolBar()
        icon_loc = icon = os.path.join(program_location,"icons","save.png")
        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.setIcon(QtGui.QIcon(icon_loc))
        self.button_save.clicked.connect(self.save)
        
        icon_loc = icon = os.path.join(program_location,"icons","release.png")
        self.button_release = QtWidgets.QPushButton("Release")
        self.button_release.setIcon(QtGui.QIcon(icon_loc))
        
        icon_loc = icon = os.path.join(program_location,"icons","add_comment.png")
        self.button_comment = QtWidgets.QPushButton("Add Comment")
        self.button_comment.setIcon(QtGui.QIcon(icon_loc))
        
        icon_loc = icon = os.path.join(program_location,"icons","approve.png")
        self.button_approve = QtWidgets.QPushButton("Approve")
        self.button_approve.setIcon(QtGui.QIcon(icon_loc))
        
        icon_loc = icon = os.path.join(program_location,"icons","reject.png")
        self.button_reject = QtWidgets.QPushButton("Reject")
        self.button_reject.setIcon(QtGui.QIcon(icon_loc))
        
        icon_loc = icon = os.path.join(program_location,"icons","export.png")
        self.button_export = QtWidgets.QPushButton("Export")
        self.button_export.setIcon(QtGui.QIcon(icon_loc))

        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_release)
        self.toolbar.addWidget(self.button_comment)
        self.toolbar.addWidget(self.button_approve)
        self.toolbar.addWidget(self.button_reject)
        self.toolbar.addWidget(self.button_export)
        
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_pcn = PCNTab(self)
        self.tab_comment = CommentTab(self)
        self.tab_signature = SignatureTab(self,"PCN")
        self.tab_notification = NotificationTab(self)
        
        self.tab_widget.addTab(self.tab_pcn,"PCN")
        self.tab_widget.addTab(self.tab_comment, "Comments")
        self.tab_widget.addTab(self.tab_signature,"Signatures")
        self.tab_widget.addTab(self.tab_notification,"Notifications")
        mainLayout.addWidget(self.toolbar)
        mainLayout.addWidget(self.tab_widget)
        self.setLayout(mainLayout)
        
        if self.doc_id is None:
            self.tab_pcn.line_id.setPlaceholderText("Save to gen.")
            self.tab_pcn.line_title.setPlaceholderText("Please enter a title")
            self.tab_pcn.line_author.setText(self.parent.user_info["user"])
            self.tab_pcn.line_status.setText("Draft")
        else:
            self.loadData()
        
    def save(self):
        try:
            save_type = "update"
            if self.doc_id is None:
                self.generatePCNID()
                save_type = "insert"
            doc_id = self.tab_pcn.line_id.text()
            doc_type = "PCN"
            author = self.tab_pcn.line_author.text()
            #requestor = self.tab_ecn.box_requestor.currentText()
            status = self.tab_pcn.line_status.text()
            title = self.tab_pcn.line_title.text()
            overview = self.tab_pcn.text_overview.toHtml()
            reason =self.tab_pcn.text_reason.toHtml()
            change = self.tab_pcn.text_change.toHtml()
            products = self.tab_pcn.text_products.toHtml()
            replacement = self.tab_pcn.text_replacement.toHtml()
            reference = self.tab_pcn.text_reference.toHtml()
            response = self.tab_pcn.text_response.toHtml()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #dept = self.tab_ecn.combo_dept.currentText()
            
            #overview - text 1, products - text 2, replacement - text 3, reference - text 4, response - text 5
            if save_type == "insert":
                data = (doc_id,doc_type,author,status,title,overview,reason,change,products,replacement,reference,response,modifieddate)
                self.cursor.execute("INSERT INTO DOCUMENT(DOC_ID,DOC_TYPE,AUTHOR,STATUS,DOC_TITLE,DOC_TEXT_1,DOC_REASON,DOC_SUMMARY,DOC_TEXT_2,DOC_TEXT_3,DOC_TEXT_4,DOC_TEXT_5,LAST_MODIFIED) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(data))
                self.dispMsg("PCN Saved!")
            else:
                data = (title,overview,reason,change,products,replacement,reference,response,modifieddate,doc_id)
                self.cursor.execute("UPDATE DOCUMENT SET DOC_TITLE = ?, DOC_TEXT_1 = ?, DOC_REASON = ?, DOC_SUMMARY = ?, DOC_TEXT_2 = ?, DOC_TEXT_3 = ?, DOC_TEXT_4 = ?, DOC_TEXT_5 = ?, LAST_MODIFIED = ? WHERE DOC_ID = ?",(data))
                self.dispMsg("PCN Updated!")
            self.db.commit()
            self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data saving!\n Error: {e}")
            
    def loadData(self):
        self.cursor.execute(f"Select * from DOCUMENT WHERE DOC_ID='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tab_pcn.line_id.setText(result["DOC_ID"])
        self.tab_pcn.line_title.setText(result["DOC_TITLE"])
        self.tab_pcn.line_author.setText(result["AUTHOR"])
        self.tab_pcn.line_status.setText(result["STATUS"])
        self.tab_pcn.text_overview.setHtml(result["DOC_TEXT_1"])
        self.tab_pcn.text_reason.setHtml(result["DOC_REASON"])
        self.tab_pcn.text_change.setHtml(result["DOC_SUMMARY"])
        self.tab_pcn.text_products.setHtml(result["DOC_TEXT_2"])
        self.tab_pcn.text_replacement.setHtml(result["DOC_TEXT_3"])
        self.tab_pcn.text_reference.setHtml(result["DOC_TEXT_4"])
        self.tab_pcn.text_response.setHtml(result["DOC_TEXT_5"])
    
    def generatePCNID(self):
        month,counter = self.getPCNCounter()
        date_time = datetime.now().strftime('%Y%m')
        old_month = f"{month:02d}"
        #print(date_time[4:],old_month)
        if old_month == date_time[4:]:
            #print("month match")
            self.setPCNCounter(old_month, old_month, counter+1)
            self.doc_id = 'PCN'+date_time[2:]+ f"-{counter+1:02d}"
        else:
            #print("month not match")
            self.setPCNCounter(old_month, date_time[4:], 1)
            self.doc_id = 'PCN'+date_time[2:]+"-01"
        #print(self.doc_id)
        self.tab_pcn.line_id.setText(self.doc_id)
        
    def getPCNCounter(self):
        self.cursor.execute("select * from PCNCOUNTER")
        result = self.cursor.fetchone()
        if result is not None:
            return (result[0],result[1])
        else:
            #print("no results")
            return (0,0)
            
    def setPCNCounter(self,old_month,new_month,counter):
        #print(old_month,new_month,counter)
        if old_month == "00":
            data = (new_month,counter)
            self.cursor.execute(f"INSERT INTO PCNCOUNTER(MONTH,COUNTER) VALUES(?,?)",(data))
            #print("inserting data")
        else:
            data = (new_month,counter,old_month)
            self.cursor.execute(f"UPDATE PCNCOUNTER SET MONTH = ?, COUNTER=? where MONTH = ?",(data))
        self.db.commit()
        
    def release(self):
        try:
            self.save(1)
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.cursor.execute(f"SELECT FIRST_RELEASE from DOCUMENT where DOC_ID='{self.doc_id}'")
            result = self.cursor.fetchone()
            if result[0] is None:
                self.cursor.execute(f"UPDATE DOCUMENT SET FIRST_RELEASE = '{modifieddate}' where DOC_ID='{self.doc_id}'")
            data = (modifieddate, "Out For Approval",self.doc_id)
            self.cursor.execute("UPDATE DOCUMENT SET LAST_MODIFIED = ?, STATUS = ? WHERE DOC_ID = ?",(data))
            self.db.commit()
            self.addNotification(self.doc_id, "Released")
            self.tab_ecn.line_status.setText("Out For Approval")
            self.parent.repopulateTable()
            self.dispMsg("ECN has been saved and sent out for signing!")
            #self.addNotification(self.ecn_id, "Released")
            self.button_release.setDisabled(True)
            self.button_cancel.setText("Cancel")
            self.button_cancel.setDisabled(True)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (release)!\n Error: {e}")
        

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def closeEvent(self, event):
        self.parent.pcnWindow = None

# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    Users = PCNWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
