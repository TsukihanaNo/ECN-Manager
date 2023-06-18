from PySide6 import QtGui, QtCore, QtWidgets
import sys, os

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

class ProjectScheduleTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ProjectScheduleTab,self).__init__()
        self.parent = parent
        self.cursor = parent.cursor
        self.db = parent.db
        self.settings = parent.settings
        self.user_info = parent.user_info
        self.user_permissions = parent.user_permissions
        self.stageDict = parent.stageDict
        self.stageDictPCN = parent.stageDictPCN
        self.stageDictPRQ = parent.stageDictPRQ
        self.ico = parent.ico
        self.visual = parent.visual
        self.doc_id = parent.doc_id
        self.task_counter = 0
        self.task_dict = {}
        self.task_items = {}
        self.task_dependents = {}
        self.task_dependents_flipped = {}
        self.initAtt()
        self.clipboard = QtGui.QGuiApplication.clipboard()
        self.menu = QtWidgets.QMenu(self)
        self.initUI()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self): 
        mainlayout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        
        mainlayout.addWidget(self.toolbar)

        self.button_add = QtWidgets.QPushButton("Add Task")
        if self.doc_id is None:
            self.button_add.setDisabled(True)
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_add.setIcon(QtGui.QIcon(icon_loc))
        self.button_add.clicked.connect(self.addTask)
        self.button_remove = QtWidgets.QPushButton("Remove Task")
        icon_loc = icon = os.path.join(program_location,"icons","minus.png")
        self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        self.button_remove.clicked.connect(self.removeTask)
        self.button_remove.setDisabled(True)
        self.button_insert = QtWidgets.QPushButton("insert Task")
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_insert.setIcon(QtGui.QIcon(icon_loc))
        self.button_insert.setDisabled(True)
        self.button_insert.clicked.connect(self.insertTask)
        
        self.button_expand = QtWidgets.QPushButton("Expand All")
        self.button_expand.clicked.connect(self.expandAll)
        self.button_collapse = QtWidgets.QPushButton("Collapse All")
        self.button_collapse.clicked.connect(self.collapseAll)
        self.button_timeline = QtWidgets.QPushButton("Show Timeline")
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_insert)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_expand)
        self.toolbar.addWidget(self.button_collapse)
        self.toolbar.addWidget(self.button_timeline)
        
        self.tasks = QtWidgets.QTreeWidget()
        headers = ["Task", "Owner", "Start", "Finish", "Status", "Duration","Depends On","ID"]
        self.tasks.setColumnCount(len(headers))
        self.tasks.setHeaderLabels(headers)
        self.sizing()        
        self.tasks.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.tasks.selectionModel().selectionChanged.connect(self.onRowSelect)
        self.tasks.setSortingEnabled(True)
        self.tasks.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tasks.header().setStretchLastSection(False)

        mainlayout.addWidget(self.tasks)
        
        self.setLayout(mainlayout)              
        
    def sizing(self):
        self.tasks.setColumnWidth(2,90)
        self.tasks.setColumnWidth(3,90)
        self.tasks.setColumnWidth(4,90)
        self.tasks.setColumnWidth(5,60)
        self.tasks.setColumnWidth(6,80)
        self.tasks.setColumnWidth(7,40)
        
    def onRowSelect(self,selected,deselected):
        self.button_insert.setEnabled(bool(self.tasks.selectedItems()))
        self.button_remove.setEnabled(bool(self.tasks.selectedItems()))
        
    def addTask(self):
        self.task_counter+=1
        if self.tasks.selectedItems() == []:
            item = QtWidgets.QTreeWidgetItem(self.tasks)
        else:
            parent = self.tasks.currentItem()
            item = QtWidgets.QTreeWidgetItem(parent)
            self.disableWidgets(parent)
            self.tasks.expandItem(parent)
        self.task_items[str(self.task_counter)]=item

        self.generateWidgets(item,self.task_counter)
        
    def insertTask(self):
        self.task_counter+=1
        item = QtWidgets.QTreeWidgetItem()
        if self.tasks.currentItem().parent() is None:
            index = self.tasks.invisibleRootItem().indexOfChild(self.tasks.currentItem())
            self.tasks.invisibleRootItem().insertChild(index,item)
        else:
            index = self.tasks.currentItem().parent().indexOfChild(self.tasks.currentItem())
            self.tasks.currentItem().parent().insertChild(index,item)
        self.task_items[str(self.task_counter)]=item
        self.generateWidgets(item,self.task_counter)
        
        
    def generateWidgets(self,item,counter):
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText("new task...")
        self.tasks.setItemWidget(item,0,line_edit)
        users = QtWidgets.QComboBox()
        users.addItems(["","lily", "paul","deven"])
        self.tasks.setItemWidget(item,1,users)
        dateedit_start = QtWidgets.QDateEdit(calendarPopup=True)
        dateedit_start.setDate(QtCore.QDate.currentDate())
        dateedit_start.editingFinished.connect(self.propagateDates)
        self.tasks.setItemWidget(item,2,dateedit_start)
        dateedit_end = QtWidgets.QDateEdit(calendarPopup=True)
        dateedit_end.setDate(QtCore.QDate.currentDate().addDays(1))
        dateedit_end.editingFinished.connect(self.propagateDates)
        self.tasks.setItemWidget(item,3,dateedit_end)
        status = QtWidgets.QComboBox()
        status.addItems(["Pending","Started","Completed"])
        status.currentTextChanged.connect(self.updateColor)
        self.tasks.setItemWidget(item,4,status)
        line_duration = QtWidgets.QLineEdit()
        line_duration.setValidator(QtGui.QIntValidator(1,999))
        duration = dateedit_start.date().daysTo(dateedit_end.date())
        line_duration.setText(str(duration))
        line_duration.editingFinished.connect(self.updateDateFromDuration)
        self.tasks.setItemWidget(item,5,line_duration)
        line_predecessor = QtWidgets.QLineEdit()
        line_predecessor.editingFinished.connect(self.setDependents)
        self.tasks.setItemWidget(item,6,line_predecessor)
        line_id = QtWidgets.QLineEdit()
        line_id.setReadOnly(True)
        line_id.setText(str(counter))
        self.tasks.setItemWidget(item,7,line_id)

    def removeTask(self):
        item = self.tasks.currentItem()
        del self.task_items[self.tasks.itemWidget(item,7).text()]
        self.tasks.itemWidget(self.tasks.currentItem(),6).setText("")
        self.updateDependents()
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            self.tasks.takeTopLevelItem(self.tasks.indexOfTopLevelItem(item))
        # print(self.task_items)
        
            
    def propagateDates(self):
        # print(date)
        # print(self.sender().parent().text(0))
        self.updateDuration()
        self.calculateDates()
        self.calculateDates()
        self.updateColor()
        # self.showItems()
        # self.bubbleDate(self.tasks.currentItem())
        
    def showItems(self):
        for key in self.task_items.keys():
            print(self.tasks.itemWidget(self.task_items[key],6).text())
        
    def calculateDates(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            task_id = self.tasks.itemWidget(iterator.value(),7).text()
            # print(task_id)
            if task_id in self.task_dependents_flipped.keys():
                affected_tasks = self.task_dependents_flipped[task_id]
                # print("affected tasks", affected_tasks)
                for affected_task in affected_tasks:
                    # print("propagating")
                    if self.checkDepends(task_id,affected_task):
                        duration = self.tasks.itemWidget(self.task_items[affected_task],5).text()
                        start_date = self.tasks.itemWidget(self.task_items[task_id],3).date()
                        end_date = start_date.addDays(int(duration))
                        self.tasks.itemWidget(self.task_items[affected_task],2).setDate(start_date)
                        self.tasks.itemWidget(self.task_items[affected_task],3).setDate(end_date)
                        self.bubbleDate(self.task_items[affected_task])
                
            self.bubbleDate(iterator.value())
                
            iterator+=1
            
    def checkDepends(self,task_id,affected_task_id):
        check_ids = self.task_dependents[affected_task_id]
        end_date = self.tasks.itemWidget(self.task_items[task_id],3).date()
        good = True
        for check_id in check_ids:
            if check_id != task_id:
                if self.tasks.itemWidget(self.task_items[check_id],3).date()>end_date:
                    good = False
                    break
        return good
    
            
    def updateDependents(self,item):
        task_id = self.tasks.itemWidget(item,7).text()
        depends = self.tasks.itemWidget(item,6).text()
        if depends =="":
            if task_id in self.task_dependents.keys():
                del self.task_dependents[task_id]
        else:
            self.task_dependents[task_id]=depends.split(",")
        # print(self.task_dependents)
        
    def setDependents(self):
        self.updateDependents(self.tasks.currentItem())
        self.generateDependents()
        self.showDate()
        
    def updateColor(self):
        today = QtCore.QDate.currentDate()
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            item = iterator.value()
            text = self.tasks.itemWidget(item,4).currentText()
            if text =="Completed":
                item.setBackground(0,QtGui.QColor("#CAFFBF"))
            if text == "Started":
                if self.tasks.itemWidget(item,3).date()<today:
                    item.setBackground(0,QtGui.QColor("#FFADAD"))
                else:
                    item.setBackground(0,QtGui.QColor("#FDFFB6"))
            if text == "Pending":
                if self.tasks.itemWidget(item,3).date()<today:
                    item.setBackground(0,QtGui.QColor("#FFADAD"))
                else:
                    item.setBackground(0,item.background(1))
            iterator+=1
        
    def generateDependents(self):
        self.task_dependents_flipped = {}
        for key in self.task_dependents.keys():
            for task in self.task_dependents[key]:
                if task in self.task_dependents_flipped.keys():
                    self.task_dependents_flipped[task].append(key)
                else:
                    self.task_dependents_flipped[task] = [key]
        # print(self.task_dependents_flipped)
        
    def updateDuration(self):
        current_item = self.tasks.currentItem()
        duration = self.tasks.itemWidget(current_item,2).date().daysTo(self.tasks.itemWidget(current_item,3).date())
        self.tasks.itemWidget(current_item,5).setText(str(duration))
        
    def updateDateFromDuration(self):
        current_item = self.tasks.currentItem()
        date_widget =self.tasks.itemWidget(current_item,3)
        duration = int(self.tasks.itemWidget(current_item,5).text())
        end_date = date_widget.date().addDays(duration)
        date_widget.setDate(end_date)
        self.calculateDates()
        
    def expandAll(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            if iterator.value().childCount()>0:
                self.tasks.expandItem(iterator.value())
            iterator+=1
    
    def collapseAll(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            if iterator.value().childCount()>0:
                self.tasks.collapseItem(iterator.value())
            iterator+=1
                
                
    def bubbleDate(self,item):
        # print("bubbling")
        if item.parent() is not None:
            # print("bubbling")
            start_date = ""
            end_date = ""
            for x in range(item.parent().childCount()):
                if x == 0:
                    start_date = self.tasks.itemWidget(item.parent().child(x),2).date()
                    end_date = self.tasks.itemWidget(item.parent().child(x),3).date()
                else:
                    start_comp = self.tasks.itemWidget(item.parent().child(x),2).date()
                    end_comp = self.tasks.itemWidget(item.parent().child(x),3).date()
                    # print("start",start_date,start_comp)
                    # print("end",end_date,end_comp)
                    if start_comp<start_date:
                        start_date=start_comp
                    if end_comp>end_date:
                        end_date=end_comp
            self.tasks.itemWidget(item.parent(),2).setDate(start_date)
            self.tasks.itemWidget(item.parent(),3).setDate(end_date)
            duration = start_date.daysTo(end_date)
            # print(start_date,end_date,str(duration))
            self.tasks.itemWidget(item.parent(),5).setText(str(duration))
            # item.parent().setText(2,start_date.toString("MM/dd/yyyy"))
            # item.parent().setText(3,end_date.toString("MM/dd/yyyy"))
                
            self.bubbleDate(item.parent())
        
    def saveData(self):
        self.cursor.execute(f"delete from PROJECT_TASKS where PROJECT_ID='{self.doc_id}'")
        self.cursor.execute(f"delete from TASK_LINK where PROJECT_ID='{self.doc_id}'")
        self.db.commit()
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            item = iterator.value()
            task_name = self.tasks.itemWidget(item,0).text()
            owner = self.tasks.itemWidget(item,1).currentText()
            start_date = self.tasks.itemWidget(item,2).date().toString("MM/dd/yyyy")
            end_date = self.tasks.itemWidget(item,3).date().toString("MM/dd/yyyy")
            status = self.tasks.itemWidget(item,4).currentText()
            duration = self.tasks.itemWidget(item,5).text()
            predecessors = self.tasks.itemWidget(item,6).text()
            task_id = self.tasks.itemWidget(item,7).text()
            if item.childCount()>0:
                task_type = "parent"
                # print("has children:")
                for x in range(item.childCount()):
                    # print(self.tasks.itemWidget(item.child(x),7).text())
                    data = (self.doc_id,self.tasks.itemWidget(item,7).text(),self.tasks.itemWidget(item.child(x),7).text())
                    self.cursor.execute(f"INSERT INTO TASK_LINK(PROJECT_ID, PARENT_TASK_ID, CHILD_TASK_ID) VALUES(?,?,?)",(data))
            else:
                task_type = "child"
            data = (self.doc_id,task_name,owner,start_date,end_date,status,duration,predecessors,task_id,task_type)
            # print(data)
            self.cursor.execute(f"INSERT INTO PROJECT_TASKS(PROJECT_ID,TASK_NAME,ASSIGNED_TO,START_DATE,END_DATE,STATUS,DURATION,PREDECESSORS,TASK_ID,TYPE) VALUES(?,?,?,?,?,?,?,?,?,?)",(data))
            iterator+=1
        self.db.commit()
    
    def loadData(self):
        self.cursor.execute(f"select * from PROJECT_TASKS where PROJECT_ID='{self.doc_id}'")
        results = self.cursor.fetchall()
        for result in results:
            # print(result["TASK_ID"])
            parent = self.getParentTask(result["TASK_ID"])
            if parent is None:
                item = QtWidgets.QTreeWidgetItem(self.tasks)
            else:
                item = QtWidgets.QTreeWidgetItem(self.task_items[parent[0]])
            self.task_items[result["TASK_ID"]]=item
            self.generateWidgets(item,result["TASK_ID"])
            #setting data
            self.tasks.itemWidget(item,0).setText(result["TASK_NAME"])
            self.tasks.itemWidget(item,1).setCurrentText(result["ASSIGNED_TO"])
            self.tasks.itemWidget(item,2).setDate(QtCore.QDate.fromString(result["START_DATE"],"MM/dd/yyyy"))
            self.tasks.itemWidget(item,3).setDate(QtCore.QDate.fromString(result["END_DATE"],"MM/dd/yyyy"))
            self.tasks.itemWidget(item,4).setCurrentText(result["STATUS"])
            self.tasks.itemWidget(item,5).setText(result["DURATION"])
            self.tasks.itemWidget(item,6).setText(result["PREDECESSORS"])
            self.updateDependents(item)
            if result["TYPE"]=="parent":
                self.disableWidgets(item)
        self.generateDependents()
        self.loadCounter()
        self.updateColor()
        self.expandAll()
        
    def loadCounter(self):
        self.cursor.execute(f"select max(TASK_ID) from PROJECT_TASKS where PROJECT_ID='{self.doc_id}'")
        result = self.cursor.fetchone()
        self.task_counter=int(result[0])
    
    def disableWidgets(self,item):
        self.tasks.itemWidget(item,1).setEnabled(False)
        self.tasks.itemWidget(item,2).setEnabled(False)
        self.tasks.itemWidget(item,3).setEnabled(False)
        self.tasks.itemWidget(item,4).setEnabled(False)
        self.tasks.itemWidget(item,5).setEnabled(False)
        self.tasks.itemWidget(item,6).setText("")
        self.tasks.itemWidget(item,6).setEnabled(False)
        self.updateDependents(item)
    
    def getParentTask(self,task_id):
        self.cursor.execute(f"select PARENT_TASK_ID from TASK_LINK where PROJECT_ID ='{self.doc_id}' and CHILD_TASK_ID='{task_id}'")
        result = self.cursor.fetchone()
        return result
            
    def repopulateTable(self):
        pass     
    
    def resizeEvent(self, e):        
        self.sizing()
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
