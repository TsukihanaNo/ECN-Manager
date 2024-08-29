from PySide6 import QtWidgets, QtCore, QtGui
from datetime import datetime
import sys, os
from PurchReqDetailsTab import *
from SignatureTab import *
from NotificationTab import *
from CommentTab import *
from WebView import *
from string import Template


if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class PurchReqWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, doc_id = None, row = None, project_id = None):
        super(PurchReqWindow,self).__init__()
        self.window_id = "Purch_Req_window"
        self.parent = parent
        self.cursor = parent.cursor
        self.db = parent.db
        self.settings = parent.settings
        self.user_info = parent.user_info
        self.user_permissions = parent.user_permissions
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.stageDictPRQ = parent.stageDictPRQ
        self.visual = parent.visual
        self.windowWidth =  900
        self.windowHeight = 550
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.doc_id = doc_id
        self.project_id = project_id
        self.row = row
        self.tablist = []
        self.initAtt()
        self.initUI()
        if self.doc_id is not None:
            self.loadData()
        else:
            self.doc_data = {"author":self.user_info["user"],"status":"Draft"}
        self.setButtons()

            
        self.center()
        self.show()
        self.activateWindow()
        
        
    def initAtt(self):
        self.setWindowIcon(self.parent.ico)
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        self.setWindowTitle(f"Purchase Requisition - user: {self.parent.user_info['user']}")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMinimumWidth(self.windowWidth)
        #self.setWindowModality(QtCore.Qt.ApplicationModal)
        
    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        
        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.setDisabled(True)
        self.button_save.clicked.connect(self.save)
        self.button_cancel = QtWidgets.QPushButton("Delete")
        self.button_cancel.setDisabled(True)
        self.button_release = QtWidgets.QPushButton("Release")
        self.button_release.setDisabled(True)
        self.button_release.clicked.connect(self.release)
        self.button_comment = QtWidgets.QPushButton("Add Comment")
        self.button_comment.clicked.connect(self.addUserComment)
        self.button_comment.setDisabled(True)
        self.button_approve = QtWidgets.QPushButton("Approve")
        self.button_approve.clicked.connect(self.approve)
        self.button_approve.setDisabled(True)
        self.button_reject = QtWidgets.QPushButton("Reject")
        self.button_reject.clicked.connect(self.reject)
        self.button_reject.setDisabled(True)
        self.button_export = QtWidgets.QPushButton("Export")
        self.button_export.clicked.connect(self.exportPDF)
        # self.button_export.setEnabled(False)
        self.button_preview = QtWidgets.QPushButton("Preview")
        self.button_preview.clicked.connect(self.previewHTML)
        # self.button_preview.setEnabled(False)
        
        # self.button_members = QtWidgets.QPushButton("Members")
        
        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_cancel)
        self.toolbar.addWidget(self.button_release)
        self.toolbar.addWidget(self.button_comment)
        self.toolbar.addWidget(self.button_approve)
        self.toolbar.addWidget(self.button_reject)
        self.toolbar.addWidget(self.button_export)
        self.toolbar.addWidget(self.button_preview)
        # self.toolbar.addWidget(self.button_members)
        
        self.tab_purch_req = PurchReqDetailTab(self)
        self.tab_comments = CommentTab(self)
        self.tab_signature = SignatureTab(self,"PRQ")
        self.tab_notification = NotificationTab(self,"PRQ")
        
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.addTab(self.tab_purch_req,"Purch Reqs")
        self.tab_widget.addTab(self.tab_comments, "Comments")
        self.tab_widget.addTab(self.tab_signature,"Signatures")
        self.tab_widget.addTab(self.tab_notification,"Notifications")
        
        if self.parent.user_permissions["rerouting"]=="y":
            self.button_check_stage = QtWidgets.QPushButton("Check Stage")
            self.button_check_stage.clicked.connect(self.checkStage)
            self.toolbar.addWidget(self.button_check_stage)
        
        mainlayout.addWidget(self.toolbar)
        mainlayout.addWidget(self.tab_widget)
        self.setLayout(mainlayout)
        
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
        
    def setButtons(self):
        if self.user_info['user']==self.doc_data['author']:
            if self.doc_data["status"]!="Completed":
                self.button_save.setEnabled(True)
            if self.doc_data["status"]=="Draft" or self.doc_data["status"]=="Rejected":
                self.button_release.setEnabled(True)
            if self.doc_data["status"]!="Draft":
                self.button_cancel.setText("Cancel")
        else:
            if self.doc_data["status"]=="Out For Approval":
                if self.isUserSignable():
                    self.button_approve.setEnabled(True)
                    self.button_reject.setEnabled(True)
        if self.doc_data["status"]=="Out For Approval":
            self.button_comment.setEnabled(True)
            
    def generateHTML(self,doc_id):
        template_loc = os.path.join(self.parent.programLoc,'templates','prq_template.html')
        with open(template_loc) as f:
            lines = f.read()
            f.close()
            t = Template(lines)
            
            self.cursor.execute(f"SELECT * from document where doc_id='{doc_id}'")
            result = self.cursor.fetchone()
            # print("generating header 1")
            title = result["doc_title"]
            author = result["author"]
            status = result["status"]
            requisition_details = result["doc_summary"]
            
            # print("generating header 2")
            self.cursor.execute(f"SELECT * from purch_req_doc_link where doc_id='{doc_id}'")
            result = self.cursor.fetchone()
            print(result)
            req_id = result["req_id"]
            project_id = result["project_id"]
            
            # print("generating header 3")
            # print(req_id)
            req_header = self.visual.getReqHeader(req_id)
            print(req_header)
            visual_status = req_header[1]
            assigned_buyer = req_header[0]
            
            # print("generating header 4")
            requisitions = self.visual.getReqItems(req_id)
            req_lines = ""
            total_cost = 0
            if requisitions is not None:
                for req in requisitions:
                    line_no = str(req[0])
                    if req[2] is not None:
                        part_id = req[2]
                    else:
                        part_id = ""
                    if req[3] is not None:
                        vendor_part_id = req[3]
                    else:
                        vendor_part_id = ""
                    order_qty = str(req[4])
                    purchase_um = req[5]
                    if req[6] is not None:
                        po_num = req[6]
                    else:
                        po_num = ""
                    unit_price = req[7]
                    total_price = float(unit_price)*float(order_qty)
                    total_cost+=total_price

                    req_lines += "<tr><td>"+line_no+"</td>"
                    req_lines += "<td>"+part_id+"</td>"
                    req_lines += "<td>"+vendor_part_id+"</td>"
                    req_lines += "<td>"+order_qty+"</td>"
                    req_lines += "<td>"+purchase_um+"</td>"
                    req_lines += "<td>"+str(unit_price)+"</td>"
                    req_lines += "<td>"+str(total_price)+"</td>"
                    req_lines += "<td>"+po_num+"</td></tr>"
                    
            # print("generating header 5")
            signature = "<tr>"
            self.cursor.execute(f"SELECT * from signatures where doc_id='{doc_id}' and type='Signing'")
            results = self.cursor.fetchall()
            if results is not None:
                for result in results:
                    signature += "<td>"+result['job_title']+"</td>"
                    signature += "<td>"+result['name']+"</td>"
                    if result['signed_date'] is not None:
                        signature += "<td>"+str(result['signed_date'])+"</td></tr>"
                    else:
                        signature += "<td></td></tr>"
            else:
                signature="<tr><td></td><td></td><td></td></tr>"
                

            # print('substituting text')
            
            html = t.substitute(REQID=req_id,Title=title,author=author,DOCID=doc_id,PRJID=project_id,ORDERSTATUS=status,VISUALSTATUS=visual_status,BUYER=assigned_buyer,TOTALCOST=total_cost,DETAILS=requisition_details,REQLINE=req_lines,Signature=signature)

            return html

    def previewHTML(self):
        html = self.generateHTML(self.doc_id)
        self.webview = WebView()
        self.webview.setDocID(self.doc_id)
        self.webview.loadHtml(html)

    def exportHTML(self):
        try:
            foldername = QtWidgets.QFileDialog().getExistingDirectory()
            if foldername:
                export = self.generateHTML(self.doc_id)
                doc_loc = foldername+'\\'+self.doc_id+'.html'
                with open(doc_loc, 'w') as f:
                    f.write(export)
                    f.close()
                
                self.dispMsg("Export Completed!")
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during ecn export.\n Error: {e}")
            
    def exportPDF(self):
        try:
            foldername = QtWidgets.QFileDialog().getExistingDirectory()
            if foldername:
                export = self.generateHTML(self.doc_id)
                doc_loc = foldername+'\\'+self.doc_id+'.pdf'
                self.webview = WebView()
                self.webview.loadAndPrint(export,doc_loc)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during ecn export.\n Error: {e}")
        
    def save(self, msg=None):
        if self.visual.checkReqID(self.tab_purch_req.line_id.text()):
            self.tab_purch_req.loadHeader()
            self.tab_purch_req.loadItems()
            if self.doc_id is None:
                self.generateID()
            if not self.checkID():
                self.insertData()
                if not msg:
                    self.dispMsg("Project has been saved!")
            else:
                self.updateData()
                if not msg:
                    self.dispMsg("Project has been updated!")
            self.button_release.setEnabled(True)
        else:
            self.dispMsg("The purchase requisition ID does not exist in Visual. Please make sure you entered it correctly or that you have entered a purchase requisition in Visual prior to adding it here.")
        
    def AddSignatures(self):
        #inserting to signature table
        #signatures(ECN_ID TEXT, name TEXT, user_id TEXT, HAS_SIGNED TEXT, signed_date TEXT)
        try:
            #get current values in db
            # print("adding sigs")
            current_list = []
            self.cursor.execute(f"SELECT user_id FROM signatures WHERE doc_id='{self.doc_id}' and type='Signing'")
            results = self.cursor.fetchall()
            for result in results:
                current_list.append(result[0])
            # print('current list',current_list)
            #get new values
            new_list = []
            for x in range(self.tab_signature.rowCount()):
                job_title = self.tab_signature.model.get_job_title(x)
                name = self.tab_signature.model.get_name(x)
                user_id = self.tab_signature.model.get_user(x)
                new_list.append((self.doc_id,job_title,name,user_id,"Signing"))
            # print('new list',new_list)
            
            for element in new_list:
                if element[3] not in current_list:
                    #print(f'insert {element[3]} into signature db')
                    self.cursor.execute("INSERT INTO signatures(doc_id,job_title,name,user_id,type) VALUES(%s,%s,%s,%s,%s)",(element))
            for element in current_list:
                no_match = True
                for elements in new_list:
                    if element == elements[3]:
                        no_match = False
                if no_match:
                    #print(f"remove {element} from signature db")
                    self.cursor.execute(f"DELETE FROM signatures WHERE doc_id = '{self.doc_id}' and user_id='{element}'")
                    
                    
            current_list = []
            self.cursor.execute(f"SELECT user_id FROM signatures WHERE doc_id='{self.doc_id}' and type='Notify'")
            results = self.cursor.fetchall()
            for result in results:
                current_list.append(result[0])
            
            new_list = []
            for x in range(self.tab_notification.rowCount()):
                job_title = self.tab_notification.model.get_job_title(x)
                name = self.tab_notification.model.get_name(x)
                user_id = self.tab_notification.model.get_user(x)
                new_list.append((self.doc_id,job_title,name,user_id,"Notify"))
                
            for element in new_list:
                if element[3] not in current_list:
                    #print(f'insert {element[3]} into notify db')
                    self.cursor.execute("INSERT INTO signatures(doc_id,job_title,name,user_id,type) VALUES(%s,%s,%s,%s,%s)",(element))
            for element in current_list:
                no_match = True
                for elements in new_list:
                    if element == elements[3]:
                        no_match = False
                if no_match:
                    #print(f"remove {element} from notify db")
                    self.cursor.execute(f"DELETE FROM signatures WHERE doc_id = '{self.doc_id}' and user_id='{element}'")
            
            if self.doc_data["author"]==self.parent.user_info["user"]:
                self.button_release.setEnabled(self.tab_signature.rowCount()>0)
            #print('data updated')
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (signature)!\n Error: {e}")
            
    def checkSigNotiDuplicate(self):
        sigs = []
        for row in range(self.tab_signature.rowCount()):
            sigs.append(self.tab_signature.model.get_user(row))
        for row in range(self.tab_notification.rowCount()):
            sigs.append(self.tab_notification.model.get_user(row))
        #print(sigs)
        if len(sigs)==len(set(sigs)):
            return False
        else:
            return True
        
    def isUserSignable(self):
        self.cursor.execute(f"SELECT user_id from signatures where doc_id='{self.doc_id}' and user_id='{self.user_info['user']}'")
        result = self.cursor.fetchone()
        if result is not None:
            return True
        return False
    
    def getElapsedDays(self,day1,day2):
        #today  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        day1 = datetime.strptime(day1,'%Y-%m-%d %H:%M:%S')
        day2 = datetime.strptime(day2,'%Y-%m-%d %H:%M:%S')
        if day2>day1:
            elapsed = day2 - day1
        else:
            elapsed = day1 - day2
        #print(elapsed.days)
        return elapsed.days + round(elapsed.seconds/86400,2)
    
    def checkID(self):
        self.cursor.execute(f"select doc_id from document where doc_id='{self.tab_purch_req.line_doc_id.text()}'")
        result = self.cursor.fetchone()
        if result is not None:
            return True
        else:
            return False
        
    def checkFields(self):
        # print(self.tab_purch_req.text_details.toPlainText())
        if self.tab_purch_req.line_id.text()=="":
            self.dispMsg("Please enter the Visual Requsition ID.")
            return False
        if self.tab_purch_req.text_details.toPlainText()=="":
            self.dispMsg("Please enter a summary in the details section.")
            return False
        return True
        
    def generateID(self):
        date_time = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.doc_id = 'PRQ-'+date_time[2:]
        self.tab_purch_req.line_doc_id.setText(self.doc_id)

    def insertData(self):
        try:
            status = 'Draft'
            req_id = self.tab_purch_req.line_id.text()
            doc_type = "Purchase Requisition"
            title = self.tab_purch_req.line_title.text()
            modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            author = self.user_info['user']
            detail = self.tab_purch_req.text_details.toHtml()
            data = (self.doc_id,doc_type,title,detail,status,author,modifieddate)
            self.cursor.execute("INSERT INTO document(doc_id,doc_type,doc_title,doc_summary,status,author,last_modified) VALUES(%s,%s,%s,%s,%s,%s,%s)",(data))
            data = (self.doc_id,req_id,self.project_id)
            self.cursor.execute("INSERT INTO purch_req_doc_link(doc_id,req_id,project_id) VALUES(%s,%s,%s)",(data))
            # self.cursor.execute("INSERT INTO PURCH_REQS(project_id,doc_id,req_id,doc_title,DETAILS,status,author,last_modified) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(data))
            if self.checkSigNotiDuplicate():
                self.dispMsg("Duplicate signatures found")
            else:
                self.AddSignatures()
            self.db.commit()
            if self.project_id != "General":
                self.parent.model.add_req(self.doc_id,title,req_id,status)
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (insertData)!\n Error: {e}")
            
    def updateData(self):
        try:
            req_id = self.tab_purch_req.line_id.text()
            title = self.tab_purch_req.line_title.text()
            detail = self.tab_purch_req.text_details.toHtml()
            data = (req_id,title, detail,self.doc_id)
            status = self.tab_purch_req.line_status.text()
            data = (title,detail,self.doc_id)
            self.cursor.execute("UPDATE document SET doc_title = %s, doc_summary = %s WHERE doc_id = %s",(data))
            data = (req_id,self.doc_id)
            self.cursor.execute("UPDATE purch_req_doc_link SET req_id = %s WHERE doc_id = %s",(data))
            # self.cursor.execute("UPDATE PURCH_REQS SET req_id = %s, doc_title = %s, DETAILS = %s WHERE doc_id = %s",(data))
            if self.checkSigNotiDuplicate():
                self.dispMsg("Duplicate signatures found")
            else:
                self.AddSignatures()
            self.db.commit()
            if self.row is not None:
                req_header = self.visual.getReqHeader(req_id)
                visual_status = VISUAL_REQ_STATUS[req_header[1]]
                self.parent.model.update_req_data(self.row,self.doc_id,title,req_id,status,visual_status)
            else:
                self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data update (updateData)!\n Error: {e}")
    
    def loadData(self):
        self.cursor.execute(f"select * from document left join purch_req_doc_link ON document.doc_id=purch_req_doc_link.doc_id where document.doc_id='{self.doc_id}'")
        self.doc_data = self.cursor.fetchone()
        self.tab_purch_req.line_doc_id.setText(self.doc_data['doc_id'])
        self.tab_purch_req.line_title.setText(self.doc_data["doc_title"])
        self.tab_purch_req.line_status.setText(self.doc_data["status"])
        self.tab_purch_req.text_details.setHtml(self.doc_data["doc_summary"])
        self.tab_purch_req.line_author.setText(self.doc_data["author"])
        
        self.tab_purch_req.line_id.setText(self.doc_data["req_id"])
        self.tab_purch_req.loadHeader()
        self.tab_purch_req.loadItems()
        self.tab_signature.repopulateTable()
        self.tab_notification.repopulateTable()
        self.tab_comments.loadComments()
        self.setCommentCount()
        
    def release(self):
        if self.checkFields():
            try:
                print("releasing")
                self.save(1)
                modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                self.cursor.execute(f"SELECT first_release from document where doc_id='{self.doc_id}'")
                print("getting first release")
                result = self.cursor.fetchone()
                if result[0] is None:
                    self.cursor.execute(f"UPDATE document SET first_release = '{modifieddate}' where doc_id='{self.doc_id}'")
                data = (modifieddate, "Out For Approval",self.doc_id)
                self.cursor.execute("UPDATE document SET last_modified = %s, status = %s WHERE doc_id = %s",(data))
                self.db.commit()
                print("getting prq stage")
                currentStage = self.getPRQStage()
                print("got stage")
                if currentStage==0:
                    print("setting stage")
                    self.setPRQStage(self.getNextStage()[0])
                    print("adding notification")
                    self.addNotification(self.doc_id, "Stage Moved")
                self.tab_purch_req.line_status.setText("Out For Approval")
                print("changing status")
                self.parent.repopulateTable()
                self.dispMsg("Purchase Requisition has been saved and sent out for signing!")
                #self.addNotification(self.ecn_id, "Released")
                self.button_release.setDisabled(True)
                self.button_cancel.setText("Cancel")
                self.button_cancel.setDisabled(True)
            except Exception as e:
                print(e)
                self.dispMsg(f"Error occured during data update (release)!\n Error: {e}")
        else:
            self.dispMsg("There are empty Fields, cannot release.")
            
    def approve(self):
        try:
            approvedate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = (approvedate,self.doc_id,self.parent.user_info['user'])
            self.cursor.execute("UPDATE signatures SET signed_date = %s WHERE doc_id = %s and user_id = %s",(data))
            self.cursor.execute(f"UPDATE document SET last_modified = '{approvedate}' where doc_id='{self.doc_id}'")
            self.tab_signature.repopulateTable()
            self.dispMsg("PRQ has been signed!")
            self.button_approve.setDisabled(True)
            self.checkComplete()
            self.db.commit()
            print("moving prq stage check")
            self.movePRQStage()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (approve)!\n Error: {e}")
    
    def reject(self):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            self.addComment(self.doc_id, comment,"Rejecting to author")
            try:
                modifieddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = (modifieddate, "Rejected",self.doc_id)
                self.cursor.execute("UPDATE document SET last_modified = %s, status = %s WHERE doc_id = %s",(data))
                self.cursor.execute(f"UPDATE signatures SET signed_date=Null where doc_id='{self.doc_id}'")
                self.db.commit()
                self.setPRQStage(0)
                self.parent.repopulateTable()
                self.dispMsg("Rejection successful. Setting PRQ stage to 0 and all signatures have been removed.")
                self.tab_purch_req.line_status.setText("Rejected")
                self.addNotification(self.doc_id, "Rejected To Author",from_user=self.parent.user_info['user'],msg=comment)
                self.button_reject.setDisabled(True)
                self.button_approve.setDisabled(True)
            except Exception as e:
                print(e)
                self.dispMsg(f"Error occured during data update (reject)!\n Error: {e}")
        if ok and comment=="":
            self.dispMsg("Rejection failed: comment field was left blank.")
    
    def checkComplete(self):
        try:
            command = f"Select * from signatures where doc_id ='{self.doc_id}' and type='Signing'"
            self.cursor.execute(command)
            results = self.cursor.fetchall()
            completed = True
            for result in results:
                if result['signed_date'] is None or result['signed_date']== "":
                    completed = False
            if completed:
                completeddate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute(f"select first_release from document where doc_id='{self.doc_id}'")
                result = self.cursor.fetchone()
                #print(result[0])
                #first_release = datetime.strptime(str(result[0]),'%Y-%m-%d %H:%M:%S')
                elapsed = self.getElapsedDays(result[0], completeddate)
                #print(elapsed)
                #elapsed = self.getElapsedDays(first_release, completeddate)
                data = (completeddate,completeddate,elapsed, "Approved",self.doc_id)
                self.cursor.execute("UPDATE document SET last_modified = %s,comp_date = %s, comp_days = %s, status = %s WHERE doc_id = %s",(data))
                #self.db.commit()
                self.parent.repopulateTable()
                self.dispMsg("PRQ is now Approved")
                self.addNotification(self.doc_id, "Approved")
                self.tab_signature.button_add.setDisabled(True)
                self.tab_notification.button_add.setDisabled(True)
                self.tab_purch_req.line_status.setText("Approved")
            else:
                self.parent.repopulateTable()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error Occured during check Complete.\n Error: {e}")
            
    def addUserComment(self):
        comment, ok = QtWidgets.QInputDialog().getMultiLineText(self, "Comment", "Comment", "")
        if ok and comment!="":
            self.addComment(self.doc_id, comment,"User Comment")
            self.addNotification(self.doc_id, "User Comment",from_user=self.parent.user_info['user'], msg=comment)
            #self.dispMsg("Comment has been added!")

    def addComment(self,doc_id,comment,commentType):
        #comments(ECN_ID TEXT, name TEXT, user_id TEXT, comm_date DATE, comment TEXT
        data = (doc_id, self.parent.user_info['user'],datetime.now().strftime('%Y-%m-%d %H:%M:%S'),comment,commentType)
        self.cursor.execute("INSERT INTO comments(doc_id, user_id, comm_date, comment,type) VALUES(%s,%s,%s,%s,%s)",(data))
        self.db.commit()
        # self.tab_comments.enterText.clear()
        #self.tab_comments.mainText.clear()
        self.tab_comments.addComment(data[1], data[2], data[4], data[3])
        self.setCommentCount()
        #self.tab_widget.setCurrentIndex(3)
        
    def setCommentCount(self):
        self.cursor.execute(f"SELECT COUNT(comment) from comments where doc_id='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.tab_widget.setTabText(1, "Comments ("+str(result[0])+")")
    
    def existNotification(self,doc_id):
        self.cursor.execute(f"Select * from notifications where doc_id='{doc_id}' and status='Not Sent'")
        result = self.cursor.fetchone()
        if result is not None:
            return True
        else:
            return False
        
    def addNotification(self,doc_id,notificationType,from_user=None,usersList=None,msg=""):
        print('adding notification')
        if usersList is not None:
            if type(usersList)==type([]):
                users = ""
                count = 0
                for user in usersList:
                    users +=","
                    if count<len(usersList)-1:
                        users +=","
                    count+=1
            else:
                users = usersList
        else:
            users = ""
        if from_user is None:
            from_user = ""
                
        if self.existNotification(doc_id) and notificationType!="User Comment":
            data = (notificationType,from_user,users,msg, doc_id)
            self.cursor.execute("UPDATE notifications SET type = %s, from_user = %s, users = %s, msg = %s WHERE doc_id = %s",(data))
        else:
            data = (doc_id,"Not Sent",notificationType,from_user, users, msg)
            self.cursor.execute("INSERT INTO notifications(doc_id, status, type,from_user, users, msg) VALUES(%s,%s,%s,%s,%s,%s)",(data))
        self.db.commit()
        
    def checkFields(self):
        if self.tab_purch_req.line_title.text()=="":
            return False
        if self.tab_purch_req.line_id.text()=="":
            return False
        if self.tab_purch_req.text_details.toPlainText()=="":
            return False
        return True
    
    def checkStage(self):
        try:
            self.checkComplete()
            self.db.commit()
            # print("moving pcr stage check")
            # self.movePRQStage()
        except Exception as e:
            print(e)
            self.dispMsg(f"Error occured during data insertion (approve)!\n Error: {e}")
        
    def getPRQStage(self):
        try:
            self.cursor.execute(f"Select tempstage from document where doc_id='{self.doc_id}'")
            result = self.cursor.fetchone()
            #print("current stage",result[0])
            if result[0] is None:
                return 0
            else:
                return result[0]
        except Exception as e:
            self.dispMsg(f"Error trying to get PRQ stage. Error: {e}")
            
    def setPRQStage(self,stage):
        try:
            #print('setting ecn to ', stage)
            self.cursor.execute(f"UPDATE document SET stage ='{stage}', tempstage = '{stage}' where doc_id='{self.doc_id}'")
            self.db.commit()
        except Exception as e:
            self.dispMsg(f"Error trying to set PRQ stage. Error: {e}")
            
    def movePRQStage(self):
        curStage = self.getPRQStage()
        titles = self.getTitlesForStage()
        titles = titles[str(curStage)]
        #print("here are the titles",titles)
        move = True
        for title in titles:
            self.cursor.execute(f"Select signed_date from signatures where doc_id = '{self.doc_id}' and job_title='{title}' and type='Signing'")
            results = self.cursor.fetchall()
            for result in results:
                #print(result['signed_date'])
                if result['signed_date'] is None:
                    move = False
                    #print("not moving to next stage")
                    break
        if move:
            nextStages = self.getNextStage()
            if len(nextStages)>0:
                #print("moving to stage:", nextStages[0])
                self.setPRQStage(nextStages[0])
                self.addNotification(self.doc_id, "Stage Moved")
            # else:
            #     print("this is the last stage")
            
    def getNextStage(self):
        self.cursor.execute(f"Select job_title from signatures where doc_id='{self.doc_id}' and signed_date is NULL and type='Signing'")
        results = self.cursor.fetchall()
        stage = []
        for result in results:
            stage.append(self.stageDictPRQ[result[0]])
        stage = sorted(stage)
        return stage
    
    def getTitlesForStage(self):
        titles = {}
        for key, value in self.stageDictPRQ.items():
            if value not in titles:
                titles[value] = [key]
            else:
                titles[value].append(key)
        return titles
        
        
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
        
    def closeEvent(self, event):
        if self.row is None:
            self.parent.prqWindow = None