from typing import Optional, Union
from PySide6 import QtGui, QtCore, QtWidgets
import sys, os

import PySide6.QtCore
import PySide6.QtWidgets

from ProjectTimeline import *

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
        self.item_clip = ()
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
        self.button_insert = QtWidgets.QPushButton("Insert Before")
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_insert.setIcon(QtGui.QIcon(icon_loc))
        self.button_insert.setDisabled(True)
        self.button_insert.clicked.connect(self.insertTask)
        self.button_insert_after = QtWidgets.QPushButton("Insert After")
        icon_loc = icon = os.path.join(program_location,"icons","add.png")
        self.button_insert_after.setIcon(QtGui.QIcon(icon_loc))
        self.button_insert_after.setDisabled(True)
        self.button_insert_after.clicked.connect(self.insertTaskAfter)
        # self.button_cut = QtWidgets.QPushButton("Cut")
        # self.button_cut.clicked.connect(self.cut)
        # self.button_copy = QtWidgets.QPushButton("Copy")
        # self.button_copy.clicked.connect(self.copy)
        # self.button_paste = QtWidgets.QPushButton("Paste")
        # self.button_paste.clicked.connect(self.paste)
        # self.button_paste_child = QtWidgets.QPushButton("Paste As Child")
        # self.button_paste_child.clicked.connect(self.pasteAsChild)
        
        self.button_expand = QtWidgets.QPushButton("Expand All")
        self.button_expand.clicked.connect(self.expandAll)
        self.button_collapse = QtWidgets.QPushButton("Collapse All")
        self.button_collapse.clicked.connect(self.collapseAll)
        self.button_timeline = QtWidgets.QPushButton("Show Timeline")
        self.button_export_csv = QtWidgets.QPushButton("Export CSV")
        self.button_export_csv.clicked.connect(self.export)
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_insert)
        self.toolbar.addWidget(self.button_insert_after)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_expand)
        self.toolbar.addWidget(self.button_collapse)
        self.toolbar.addWidget(self.button_timeline)
        self.toolbar.addWidget(self.button_export_csv)
        # self.toolbar.addWidget(self.button_copy)
        # self.toolbar.addWidget(self.button_cut)
        # self.toolbar.addWidget(self.button_paste)
        # self.toolbar.addWidget(self.button_paste_child)
        
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
        self.tasks.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.tasks.setItemDelegate(TreeDelegate(self))
        self.tasks.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        # self.tasks.setStyleSheet("QTreeView::item {border-bottom: 1px solid gray;} QLineEdit {border:0; background-color: transparent} QComboBox {border: 0; margin: 0; background-color: transparent} QDateTimeEdit {border:0; background-color: transparent}")

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
        self.button_insert_after.setEnabled(bool(self.tasks.selectedItems()))
        self.button_remove.setEnabled(bool(self.tasks.selectedItems()))

    def showTimeline(self):
        self.timeline = ProjectTimeline(self)
        
    def addTask(self):
        self.task_counter+=1
        if self.tasks.selectedItems() == []:
            item = QtWidgets.QTreeWidgetItem(self.tasks)
            item.setFlags(item.flags()|QtCore.Qt.ItemIsEditable)
            self.tasks.editItem(item,0)
        else:
            parent = self.tasks.currentItem()
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setFlags(item.flags()|QtCore.Qt.ItemIsEditable)
            # self.disableWidgets(parent)
            self.tasks.expandItem(parent)
        self.task_items[str(self.task_counter)]=item

        # self.generateWidgets(item,self.task_counter)
    
    def cut(self):
        if self.tasks.currentItem().parent() is None:
                index = self.tasks.invisibleRootItem().indexOfChild(self.tasks.currentItem())
        else:
            index = self.tasks.currentItem().parent().indexOfChild(self.tasks.currentItem())
        self.item_clip = (self.tasks.currentItem().parent().takeChild(index),1)
        print(self.item_clip)
        
    def copy(self):
        item = self.tasks.currentItem()
        self.item_clip = (item,0)
        
    def paste(self):
        item = self.item_clip[0]
        print(item)
        if self.item_clip[1]==1:
            if self.tasks.currentItem().parent() is None:
                index = self.tasks.invisibleRootItem().indexOfChild(self.tasks.currentItem())
                self.tasks.invisibleRootItem().insertChild(index,item)
                print("pasting, parent none")
            else:
                index = self.tasks.currentItem().parent().indexOfChild(self.tasks.currentItem())
                self.tasks.currentItem().parent().insertChild(index,item)
                print("pasting")
    
    def pasteAsChild(self):
        pass
        
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
        
    def insertTaskAfter(self):
        self.task_counter+=1
        item = QtWidgets.QTreeWidgetItem()
        if self.tasks.currentItem().parent() is None:
            index = self.tasks.invisibleRootItem().indexOfChild(self.tasks.currentItem())
            self.tasks.invisibleRootItem().insertChild(index+1,item)
        else:
            index = self.tasks.currentItem().parent().indexOfChild(self.tasks.currentItem())
            self.tasks.currentItem().parent().insertChild(index+1,item)
        self.task_items[str(self.task_counter)]=item
        self.generateWidgets(item,self.task_counter)
        self.tasks.itemWidget(item,0).setFocus()
        
    def generateWidgets(self,item,counter):
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText("new task...")
        line_edit.returnPressed.connect(self.insertTaskAfter)
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
        status.currentTextChanged.connect(self.updateStatus)
        self.tasks.setItemWidget(item,4,status)
        line_duration = QtWidgets.QLineEdit()
        line_duration.setValidator(QtGui.QIntValidator(1,999))
        line_duration.setAlignment(QtCore.Qt.AlignCenter)
        duration = dateedit_start.date().daysTo(dateedit_end.date())
        line_duration.setText(str(duration))
        line_duration.editingFinished.connect(self.updateDateFromDuration)
        self.tasks.setItemWidget(item,5,line_duration)
        line_predecessor = QtWidgets.QLineEdit()
        line_predecessor.setAlignment(QtCore.Qt.AlignCenter)
        line_predecessor.editingFinished.connect(self.setDependents)
        self.tasks.setItemWidget(item,6,line_predecessor)
        line_id = QtWidgets.QLineEdit()
        line_id.setReadOnly(True)
        line_id.setText(str(counter))
        line_id.setAlignment(QtCore.Qt.AlignCenter)
        self.tasks.setItemWidget(item,7,line_id)

    def removeTask(self):
        item = self.tasks.currentItem()
        del self.task_items[self.tasks.itemWidget(item,7).text()]
        self.tasks.itemWidget(item,6).setText("")
        self.updateDependents(item)
        parent = item.parent()
        if parent:
            parent.removeChild(item)
            if parent.childCount()==0:
                self.enableWidgets(parent)
        else:
            self.tasks.takeTopLevelItem(self.tasks.indexOfTopLevelItem(item))
        # print(self.task_items)
        
            
    def propagateDates(self):
        # print(date)
        # print(self.sender())
        self.showData()
        # print(self.sender().parent().text(0))
        # self.updateDuration()
        # self.calculateDates()
        # self.calculateDates()
        # self.updateColor()
        # self.showItems()
        # self.bubbleDate(self.tasks.currentItem())
        
    def showData(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            print(iterator.value().text(0))
            iterator+=1
        
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
            if task_id in self.task_dependents[task_id]:
                self.task_dependents[task_id].remove(task_id)
                self.tasks.itemWidget(item,6).setText(",".join(self.task_dependents[task_id]))
        # print(self.task_dependents)
        
    def setDependents(self):
        self.updateDependents(self.tasks.currentItem())
        self.generateDependents()
        self.propagateDates()
        
    def updateColor(self):
        today = QtCore.QDate.currentDate()
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            item = iterator.value()
            text = self.tasks.itemWidget(item,4).currentText()
            if text =="Completed":
                self.tasks.itemWidget(item,0).setStyleSheet("background-color:#CAFFBF")
            if text == "Started":
                if self.tasks.itemWidget(item,3).date()<today:
                    self.tasks.itemWidget(item,0).setStyleSheet("background-color:#FFADAD")
                else:
                    self.tasks.itemWidget(item,0).setStyleSheet("background-color:#FDFFB6")
            if text == "Pending":
                if self.tasks.itemWidget(item,3).date()<today:
                    self.tasks.itemWidget(item,0).setStyleSheet("background-color:#FFADAD")
                else:
                    self.tasks.itemWidget(item,0).setStyleSheet("")
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
        if duration<0:
            self.tasks.itemWidget(current_item,3).setStyleSheet("background-color:#FFADAD")
        else:
            self.tasks.itemWidget(current_item,3).setStyleSheet("")
        
    def updateDateFromDuration(self):
        current_item = self.tasks.currentItem()
        date_widget =self.tasks.itemWidget(current_item,3)
        duration = int(self.tasks.itemWidget(current_item,5).text())
        start_date = self.tasks.itemWidget(current_item,2).date()
        end_date = start_date.addDays(duration)
        date_widget.setDate(end_date)
        self.propagateDates()
        
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
            
    def updateStatus(self):
        item = self.tasks.currentItem()
        if item is not None:
            self.bubbleStatus(item)
            self.updateColor()
                
    def bubbleStatus(self,item):
        parent = item.parent()
        if parent is not None:
            completed = True
            for x in range(parent.childCount()):
                if self.tasks.itemWidget(parent.child(x),4).currentText() != "Completed":
                    completed = False
                    break;
            if completed:
                self.tasks.itemWidget(parent,4).setCurrentText("Completed")
            else:
                self.tasks.itemWidget(parent,4).setCurrentText("Pending")
            self.bubbleStatus(parent)
                
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
                item = QtWidgets.QTreeWidgetItem(self.task_items[str(parent[0])])
            self.task_items[str(result["TASK_ID"])]=item
            self.generateWidgets(item,str(result["TASK_ID"]))
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
        if result[0] is not None:
            self.task_counter=int(result[0])
            print(self.task_counter)
    
    def disableWidgets(self,item):
        self.tasks.itemWidget(item,1).setEnabled(False)
        self.tasks.itemWidget(item,1).setCurrentText("")
        self.tasks.itemWidget(item,2).setEnabled(False)
        self.tasks.itemWidget(item,3).setEnabled(False)
        self.tasks.itemWidget(item,4).setEnabled(False)
        self.tasks.itemWidget(item,5).setEnabled(False)
        self.tasks.itemWidget(item,6).setText("")
        self.tasks.itemWidget(item,6).setEnabled(False)
        self.updateDependents(item)
        
    def enableWidgets(self,item):
        self.tasks.itemWidget(item,1).setEnabled(True)
        self.tasks.itemWidget(item,2).setEnabled(True)
        self.tasks.itemWidget(item,3).setEnabled(True)
        self.tasks.itemWidget(item,4).setEnabled(True)
        self.tasks.itemWidget(item,5).setEnabled(True)
        self.tasks.itemWidget(item,6).setEnabled(True)
        self.updateDependents(item)
    
    def getParentTask(self,task_id):
        self.cursor.execute(f"select PARENT_TASK_ID from TASK_LINK where PROJECT_ID ='{self.doc_id}' and CHILD_TASK_ID='{task_id}'")
        result = self.cursor.fetchone()
        return result
    
    
    def export(self):
        starting_date, ending_date = self.getStartEndDates()
        total_days = starting_date.daysTo(ending_date)
        # print(total_days)
        main_list = []
        #list template: task name, owner, start date, end date, duration, depends on, task id, gants
        gants_year = ["","","","","","","",""]
        gants_months = ["","","","","","","",""]
        gants_days = []
        for day in range(total_days):
            new_date = starting_date.addDays(day)
            gants_year.append(str(new_date.year()))
            gants_months.append(str(new_date.month()))
            gants_days.append(str(new_date.day()))
        main_headers = ["task name","owner","start date","end date","duration","status","depends on","task id"]
        main_headers.extend(gants_days)
        main_list.append(gants_year)
        main_list.append(gants_months)
        main_list.append(main_headers)
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            item = iterator.value()
            self.indent_level = 0
            task_name = self.tasks.itemWidget(item,0).text()
            self.getIndentLevel(item)
            task_name = self.indent_level*":" + " " + task_name
            owner = self.tasks.itemWidget(item,1).currentText()
            start_date = self.tasks.itemWidget(item,2).date().toString("MM/dd/yyyy")
            end_date = self.tasks.itemWidget(item,3).date().toString("MM/dd/yyyy")
            status = self.tasks.itemWidget(item,4).currentText()
            duration = self.tasks.itemWidget(item,5).text()
            predecessors = self.tasks.itemWidget(item,6).text()
            task_id = self.tasks.itemWidget(item,7).text()
            line = [task_name,owner,start_date,end_date,duration,status,predecessors,task_id]
            start = self.tasks.itemWidget(item,2).date()
            end = self.tasks.itemWidget(item,3).date()
            for x in range(total_days):
                date = starting_date.addDays(x)
                if date<start:
                    line.append("")
                elif date>=start and date<=end:
                    if status == "Pending":
                        line.append("x")
                    elif status == "Started":
                        line.append("y")
                    else:
                        line.append("z")
                else:
                    line.append("")
            main_list.append(line)
            iterator+=1
        f = open(f"{self.doc_id} schedule.csv", "w")
        for line in main_list:
            text = ",".join(line)
            text+="\n"
            f.write(text)
        f.close()
        self.dispMsg("export completed!")
        
    def getIndentLevel(self,item):
        if item.parent() is not None:
            self.indent_level+=1
            self.getIndentLevel(item.parent())
        
    def getStartEndDates(self):
        starting_date = ""
        ending_date = ""
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            item = iterator.value()
            if starting_date=="":
                starting_date = self.tasks.itemWidget(item,2).date()
                ending_date = self.tasks.itemWidget(item,3).date()
            else:
                start_date = self.tasks.itemWidget(item,2).date()
                end_date = self.tasks.itemWidget(item,3).date()
                print(start_date,end_date)
                if start_date<starting_date:
                    starting_date=start_date
                if end_date>ending_date:
                    ending_date=end_date
            iterator+=1
        print(starting_date,ending_date)
        return starting_date,ending_date
        
    def repopulateTable(self):
        pass 
    
    def resizeEvent(self, e):        
        self.sizing()
            
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()


class TreeDelegate(QtWidgets.QStyledItemDelegate):
    
    def __init__(self,parent=None):
        super(TreeDelegate,self).__init__(parent)
        self.parent = parent
    
    def paint(self, painter, option, index):
        # painter.save()
        color = QtGui.QColor("#BDB2FF")
        r = option.rect
        # print(index.data())
        painter.setBrush(color)
        painter.drawRoundedRect(r, 5, 5)
        painter.drawText(r.topLeft()+QtCore.QPoint(10,15),index.data())
            
        # painter.restore()
        
    def createEditor(self,parent,option,index):
        print(index.column())
        if index.column()==0:
            editor = QtWidgets.QLineEdit(parent)
        elif index.column()==1:
            editor = QtWidgets.QComboBox(parent)
            editor.addItems(["lily","paul","deven"])
        elif index.column()==2 or index.column()==3:
            editor = QtWidgets.QDateEdit(parent,calendarPopup=True)
            editor.setDate(QtCore.QDate.currentDate())
            editor.editingFinished.connect(self.parent.propagateDates)    
        editor.setAutoFillBackground(True)
        return editor
        
    def setEditorData(self,editor,index):
        if index.column()==0:
            editor.setText(index.data())
        elif index.column()==1:
            editor.setCurrentText(index.data())
        elif index.column()==2 or index.column()==3:
            editor.setDate(QtCore.QDate.fromString(index.data(),"MM/dd/yyyy"))
        
        
    def setModelData(self, editor,model,index):
        if index.column()==0:
            model.setData(index,editor.text())
        elif index.column()==1:
            model.setData(index,editor.currentText())
        elif index.column()==2 or index.column()==3:
            model.setData(index,editor.date().toString("MM/dd/yyyy"))
            
    def updateEditorGeometry(self, editor, option, index):
            editor.setGeometry(option.rect)
    
    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,25)