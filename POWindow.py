from PySide6 import QtWidgets, QtCore
from datetime import datetime
from PurchReqTab import *
from ProjectScheduleTab import *
from string import Template
import sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))
    
VISUAL_PO_STATUS = {'R':"Released",'C':"Closed",'X': "Cancelled",'F': "Firmed"}

    
class POWindow(QtWidgets.QWidget):
    def __init__(self, parent = None, part_id = None):
        super(POWindow,self).__init__()
        self.parent = parent
        self.cursor = parent.cursor
        self.db = parent.db
        self.visual = parent.visual
        self.windowWidth =  950
        self.windowHeight = 580
        self.part_id = part_id
        self.initAtt()
        self.initUI()
        if self.part_id is not None:
            self.loadPOs()
        self.center()
        self.show()
        self.activateWindow()
        
    def initAtt(self):
        # self.setWindowIcon(self.parent.ico)
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        # self.setWindowTitle(f"Project- user: {self.parent.user_info['user']}")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMinimumWidth(self.windowWidth)
        self.setMinimumHeight(self.windowHeight)
        #self.setWindowModality(QtCore.Qt.ApplicationModal)
        

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
        
    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        # self.toolbar = QtWidgets.QToolBar()
        
        # self.button_save = QtWidgets.QPushButton("Save")
        # self.button_save.clicked.connect(self.save)
        
        # self.toolbar.addWidget(self.button_save)
        
        hlayout = QtWidgets.QHBoxLayout()
        self.po_list = QtWidgets.QListWidget()
        self.po_list.setFixedWidth(100)
        self.po_list.itemSelectionChanged.connect(self.showPoInfo)
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        hlayout.addWidget(self.po_list)
        hlayout.addWidget(self.text_edit)

        # mainlayout.addWidget(self.toolbar)
        mainlayout.addLayout(hlayout)
        self.setLayout(mainlayout)
        
    def loadPOs(self):
        po_list = []
        results = self.visual.getPurchLineInfo(self.part_id)
        for result in results:
            if result[0] not in po_list:
                po_item = QtWidgets.QListWidgetItem(result[0])
                self.po_list.addItem(po_item)
                po_list.append(result[0])
            
    def showPoInfo(self):
        po_id = self.po_list.currentItem().text()
        self.text_edit.clear()
        html = self.generateHTML(po_id)
        self.text_edit.setHtml(html)

        
    def generateHTML(self,po):
        template_loc = os.path.join(program_location,'templates','po_template.html')
        with open(template_loc) as f:
            lines = f.read() 
            f.close()

            t = Template(lines)
            
            #get po header info: ID, VENDOR_ID, STATUS,DESIRED_RECV_DATE, PROMISE_DATE
            result = self.visual.getPurchOrderInfo(po)
            vendor_id = result[1]
            vendor_name = self.visual.getVendorName(vendor_id)
            vendor_info = f"{vendor_id} - {vendor_name}"
            status = VISUAL_PO_STATUS[result[2]]
            order_date = datetime.strftime(result[3],'%Y-%m-%d')
            if result[4] is not None:
                desired_receive_date = datetime.strftime(result[4],'%Y-%m-%d')
            else:
                desired_receive_date = ""
            if result[5] is not None:
                promised_ship_date = datetime.strftime(result[5],'%Y-%m-%d')
            else:
                promised_ship_date = ""
            if result[6] is not None:
                promised_delivery_date = datetime.strftime(result[6],'%Y-%m-%d')
            else:
                promised_delivery_date = ""
            buyer = result[7]
            
            #get purch lines
            purch_lines =""
            results = self.visual.getPurchLines(po)
            if results is not None:
                for result in results:
                    line_no = str(result[1])
                    if result[2] is not None:
                        part_id = result[2]
                    else:
                        part_id = ""
                    if result[3] is not None:
                        vendor_part_id = result[3]
                    else:
                        vendor_part_id = ""
                    order_qty = str(result[4])
                    purchase_um = result[5]
                    unit_price = str(result[6])
                    if result[7] is not None:
                        last_recv_date = datetime.strftime(result[7],'%Y-%m-%d')
                    else:
                        last_recv_date = ""
                    if result[8] is not None:
                        gl_account = str(result[8])
                    else:
                        gl_account = ""
                    purch_lines += "<tr><td>"+line_no+"</td>"
                    purch_lines += "<td>"+part_id+"</td>"
                    purch_lines += "<td>"+vendor_part_id+"</td>"
                    purch_lines += "<td>"+order_qty+"</td>"
                    purch_lines += "<td>"+purchase_um+"</td>"
                    purch_lines += "<td>"+unit_price+"</td>"
                    purch_lines += "<td>"+last_recv_date+"</td>"
                    purch_lines += "<td>"+gl_account+"</td></tr>"
                    
            #get deliveries
            deliveries =""
            results = self.visual.getPurchOrderDelivery(po)
            if results is not None:
                for result in results:
                    po_line_no = str(result[1])
                    del_line_no = str(result[2])
                    if result[3] is not None:
                        desired_receive_date = datetime.strftime(result[3],'%Y-%m-%d')
                    else:
                        desired_receive_date = ""
                    if result[4] is not None:
                        actual_receive_date = datetime.strftime(result[4],'%Y-%m-%d')
                    else:
                        actual_receive_date = ""
                    order_qty = str(result[5])
                    received_qty = str(result[6])
                    
                    deliveries += "<tr><td>"+po_line_no+"</td>"
                    deliveries += "<td>"+del_line_no+"</td>"
                    deliveries += "<td>"+desired_receive_date+"</td>"
                    deliveries += "<td>"+actual_receive_date+"</td>"
                    deliveries += "<td>"+order_qty+"</td>"
                    deliveries += "<td>"+received_qty+"</td></tr>"
                    
            #get notation
            notation = self.visual.getPONotation(po)
            if notation is None:
                notation = ""
            
            html = t.substitute(POID=po,ORDERDATE=order_date,VENDORID=vendor_info,DESIREDRECVDATE=desired_receive_date,PROMISEDDELIVERYDATE=promised_delivery_date,PROMISEDSHIPDATE=promised_ship_date,ORDERSTATUS=status, BUYER=buyer,PURCHLINE=purch_lines,DELIVERYSCHEDULE=deliveries,NOTATION=notation)

            return html

        