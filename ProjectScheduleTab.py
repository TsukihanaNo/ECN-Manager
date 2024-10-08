import os
import sys
from typing import Optional, Union

import PySide6.QtCore
import PySide6.QtWidgets
from PySide6 import QtCore, QtGui, QtWidgets

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
        self.access = parent.access
        self.task_counter = 0
        self.task_dict = {}
        self.task_items = {}
        self.task_dependents = {}
        self.task_dependents_flipped = {}
        self.changed_start_dates = []
        self.changed_end_dates = []
        self.item_clip = ()
        self.initAtt()
        self.clipboard = QtGui.QGuiApplication.clipboard()
        self.menu = QtWidgets.QMenu(self)
        if self.access == "write":
            self.createMenu()
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
        # icon_loc = icon = os.path.join(program_location,"icons","minus.png")
        # self.button_remove.setIcon(QtGui.QIcon(icon_loc))
        self.button_remove.clicked.connect(self.removeTask)
        self.button_remove.setDisabled(True)
        self.button_insert = QtWidgets.QPushButton("Insert Before")
        # icon_loc = icon = os.path.join(program_location,"icons","add.png")
        # self.button_insert.setIcon(QtGui.QIcon(icon_loc))
        self.button_insert.setDisabled(True)
        self.button_insert.clicked.connect(self.insertTask)
        self.button_insert_after = QtWidgets.QPushButton("Insert After")
        # icon_loc = icon = os.path.join(program_location,"icons","add.png")
        # self.button_insert_after.setIcon(QtGui.QIcon(icon_loc))
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
        self.button_move_up = QtWidgets.QPushButton("Move Up")
        self.button_move_up.setEnabled(False)
        self.button_move_up.clicked.connect(self.moveUp)
        self.button_move_down = QtWidgets.QPushButton("Move Down")
        self.button_move_down.clicked.connect(self.moveDown)
        self.button_move_down.setEnabled(False)
        
        # self.button_expand = QtWidgets.QPushButton("Expand All")
        # self.button_expand.clicked.connect(self.expandAll)
        # self.button_collapse = QtWidgets.QPushButton("Collapse All")
        # self.button_collapse.clicked.connect(self.collapseAll)
        self.button_timeline = QtWidgets.QPushButton("Show Timeline")
        self.button_timeline.clicked.connect(self.showTimeline)
        self.button_export_csv = QtWidgets.QPushButton("Export CSV")
        self.button_export_csv.clicked.connect(self.export)
        self.button_save_template = QtWidgets.QPushButton("Save as Template")
        self.button_save_template.clicked.connect(self.generateTemplate)
        self.button_load_template = QtWidgets.QPushButton("Load Template")
        self.button_load_template.clicked.connect(self.loadTemplate)
        
        self.toolbar.addWidget(self.button_add)
        self.toolbar.addWidget(self.button_insert)
        self.toolbar.addWidget(self.button_insert_after)
        self.toolbar.addWidget(self.button_remove)
        self.toolbar.addWidget(self.button_move_up)
        self.toolbar.addWidget(self.button_move_down)
        # self.toolbar.addWidget(self.button_expand)
        # self.toolbar.addWidget(self.button_collapse)
        self.toolbar.addWidget(self.button_timeline)
        self.toolbar.addWidget(self.button_export_csv)
        self.toolbar.addWidget(self.button_save_template)
        self.toolbar.addWidget(self.button_load_template)
        # self.toolbar.addWidget(self.button_copy)
        # self.toolbar.addWidget(self.button_cut)
        # self.toolbar.addWidget(self.button_paste)
        # self.toolbar.addWidget(self.button_paste_child)
        
        if self.access == "read":
            self.button_add.setDisabled(True)
            self.button_save_template.setDisabled(True)
            self.button_load_template.setDisabled(True)
        
        self.tasks = QtWidgets.QTreeWidget()
        headers = ["Task", "Owner", "Start", "Finish", "Status", "Duration","Depends On","ID","◆"]
        self.tasks.setColumnCount(len(headers))
        self.tasks.setHeaderLabels(headers)
        self.sizing()        
        self.tasks.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.tasks.selectionModel().selectionChanged.connect(self.onRowSelect)
        # self.tasks.setSortingEnabled(True)
        self.tasks.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tasks.header().setStretchLastSection(False)
        self.tasks.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.tasks.setItemDelegate(TreeDelegate(self))
        self.tasks.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.SelectedClicked)
        # self.tasks.setDragEnabled(True)
        # self.tasks.viewport().setAcceptDrops(True)
        # self.tasks.setDropIndicatorShown(True)
        # self.tasks.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.tasks.itemSelectionChanged.connect(self.currentItemCheck)
        # print(self.tasks.dragDropMode(),self.tasks.dropIndicatorPosition())
        self.tasks.setStyleSheet("QTreeView::item:selected {background-color:#f4ebf7;}")

        mainlayout.addWidget(self.tasks)
        
        self.setLayout(mainlayout)   
        
    def createMenu(self):
        copy_task_action = QtGui.QAction("Copy",self)
        # copy_task_action.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Copy))
        cut_task_action = QtGui.QAction("Cut",self)
        cut_task_action.setShortcut(QtGui.QKeySequence("Ctrl+X"))
        paste_action = QtGui.QAction("Paste",self)
        paste_action.setShortcut(QtGui.QKeySequence("Ctrl+V"))
        paste_as_child_action = QtGui.QAction("Paste As Child",self)
        add_action = QtGui.QAction("Add Task",self)
        insert_action = QtGui.QAction("Insert Before",self)
        insert_after_action = QtGui.QAction("Insert After",self)
        insert_after_action.setShortcut(QtGui.QKeySequence("Ctrl+I"))
        remove_action = QtGui.QAction("Remove Task",self)
        remove_action.setShortcut(QtGui.QKeySequence("Ctrl+D"))
        expand_action = QtGui.QAction("Expand All",self)
        collapse_action = QtGui.QAction("Collapse All",self)
        move_up_action = QtGui.QAction("Move Up",self)
        move_up_action.setShortcut(QtGui.QKeySequence("Ctrl+Up"))
        move_down_action = QtGui.QAction("Move Down",self)
        move_down_action.setShortcut(QtGui.QKeySequence("Ctrl+Down"))
        milestone_action = QtGui.QAction("Toggle Milestone",self)
        copy_task_action.triggered.connect(self.copy)
        cut_task_action.triggered.connect(self.cut)
        paste_action.triggered.connect(self.paste)
        paste_as_child_action.triggered.connect(self.pasteAsChild)
        add_action.triggered.connect(self.addTask)
        insert_action.triggered.connect(self.insertTask)
        insert_after_action.triggered.connect(self.insertTaskAfter)
        remove_action.triggered.connect(self.removeTask)
        expand_action.triggered.connect(self.expandAll)
        collapse_action.triggered.connect(self.collapseAll)
        move_up_action.triggered.connect(self.moveUp)
        move_down_action.triggered.connect(self.moveDown)
        milestone_action.triggered.connect(self.toggleMilestone)
        self.addAction(copy_task_action)
        self.addAction(cut_task_action)
        self.addAction(paste_action)
        self.addAction(remove_action)
        self.addAction(move_up_action)
        self.addAction(move_down_action)
        self.addAction(insert_after_action)
        self.menu.addAction(copy_task_action)
        self.menu.addAction(cut_task_action)
        self.menu.addAction(paste_action)
        self.menu.addAction(paste_as_child_action)
        self.menu.addSeparator()
        self.menu.addAction(milestone_action)
        self.menu.addSeparator()
        self.menu.addAction(add_action)
        self.menu.addAction(insert_action)
        self.menu.addAction(insert_after_action)
        self.menu.addAction(remove_action)
        self.menu.addSeparator()
        self.menu.addAction(expand_action)
        self.menu.addAction(collapse_action)
        
    def sizing(self):
        self.tasks.setColumnWidth(2,90)
        self.tasks.setColumnWidth(3,90)
        self.tasks.setColumnWidth(4,90)
        self.tasks.setColumnWidth(5,60)
        self.tasks.setColumnWidth(6,80)
        self.tasks.setColumnWidth(7,40)
        self.tasks.setColumnWidth(8,15)
        
    def onRowSelect(self,selected,deselected):
        if self.access == "write":
            toggle = bool(self.tasks.selectedItems())
            self.button_insert.setEnabled(toggle)
            self.button_insert_after.setEnabled(toggle)
            self.button_remove.setEnabled(toggle)
            self.button_move_up.setEnabled(toggle)
            self.button_move_down.setEnabled(toggle)

    def showTimeline(self):
        self.timeline = ProjectTimeline(self)
        
    def enableEditButtons(self,value):
        self.button_add.setEnabled(value)
        self.button_insert.setEnabled(value)
        self.button_insert_after.setEnabled(value)
        self.button_move_down.setEnabled(value)
        self.button_move_up.setEnabled(value)
        self.button_remove.setEnabled(value)
        
    def addTask(self):
        self.task_counter+=1
        if self.tasks.selectedItems() == []:
            item = QtWidgets.QTreeWidgetItem(self.tasks)
        else:
            parent = self.tasks.currentItem()
            self.disableWidgets(parent)
            item = QtWidgets.QTreeWidgetItem(parent)
            self.tasks.expandItem(parent)
        self.initItemValues(item)
        item.setFlags(item.flags()|QtCore.Qt.ItemIsEditable)
        self.tasks.setCurrentItem(item)
        # self.tasks.editItem(item,0)
        self.task_items[str(self.task_counter)]=item
    
    def cut(self):
        if self.tasks.currentItem().parent() is None:
            index = self.tasks.invisibleRootItem().indexOfChild(self.tasks.currentItem())
            self.item_clip = (self.tasks.invisibleRootItem().takeChild(index),1)
        else:
            index = self.tasks.currentItem().parent().indexOfChild(self.tasks.currentItem())
            self.item_clip = (self.tasks.currentItem().parent().takeChild(index),1)
        # print(self.item_clip)
        
    def copy(self):
        item = self.tasks.currentItem()
        self.item_clip = (item,0)
        
    def paste(self):
        if self.tasks.currentItem() is not None:
            item = self.item_clip[0]
            # print(item)
            if self.item_clip[1]==1: #paste from cut
                if self.tasks.currentItem().parent() is None:
                    index = self.tasks.invisibleRootItem().indexOfChild(self.tasks.currentItem())
                    self.tasks.invisibleRootItem().insertChild(index+1,item)
                    # print("pasting, parent none")
                else:
                    index = self.tasks.currentItem().parent().indexOfChild(self.tasks.currentItem())
                    self.tasks.currentItem().parent().insertChild(index+1,item)
                    # print("pasting")
            else: #paste from copy
                new_item = QtWidgets.QTreeWidgetItem()
                new_item.setText(0,item.text(0))
                self.task_counter+=1
                self.initItemValues(new_item)
                self.task_items[str(self.task_counter)]=new_item
                self.generateCopy(item,new_item)
                if self.tasks.currentItem().parent() is None:
                    index = self.tasks.invisibleRootItem().indexOfChild(self.tasks.currentItem())
                    self.tasks.invisibleRootItem().insertChild(index+1,new_item)
                else:
                    index = self.tasks.currentItem().parent().indexOfChild(self.tasks.currentItem())
                    self.tasks.currentItem().parent().insertChild(index+1,new_item)
                self.expandAll()
                
    def generateCopy(self,item,parent):
        if item.childCount()>0:
            for x in range(item.childCount()):
                child = QtWidgets.QTreeWidgetItem(parent)
                child.setText(0,item.child(x).text(0))
                self.task_counter+=1
                self.initItemValues(child)
                self.task_items[str(self.task_counter)]=child
                if item.child(x).childCount()>0:
                    self.generateCopy(item.child(x),child)
                else:
                    child.setFlags(child.flags()|QtCore.Qt.ItemIsEditable)
            
    
    def pasteAsChild(self):
        if self.tasks.currentItem() is not None:
            item = self.item_clip[0]
            # print(item)
            if self.item_clip[1]==1:
                self.tasks.currentItem().insertChild(0,item)
                self.tasks.currentItem().setExpanded(True)
            else:
                self.dispMsg("not implemented yet")
    
    def moveUp(self):
        item = self.tasks.currentItem()
        if item is not None:
            parent = item.parent()
            current_index = parent.indexOfChild(item)
            if current_index>0:
                # print("moving up")
                parent.takeChild(current_index)
                parent.insertChild(current_index-1,item)
                self.tasks.setCurrentItem(item)
    
    def moveDown(self):
        item = self.tasks.currentItem()
        # print(item.text(0))
        if item is not None:
            parent = item.parent()
            current_index = parent.indexOfChild(item)
            if current_index<parent.childCount()-1:
                # print("moving down")
                parent.takeChild(current_index)
                parent.insertChild(current_index+1,item)
                self.tasks.setCurrentItem(item)
            
    def moveLeft(self):
        pass
    
    def moveRight(self):
        pass
        
    def insertTask(self):
        if self.tasks.currentItem() is not None:
            self.task_counter+=1
            item = QtWidgets.QTreeWidgetItem()
            if self.tasks.currentItem().parent() is None:
                index = self.tasks.invisibleRootItem().indexOfChild(self.tasks.currentItem())
                self.tasks.invisibleRootItem().insertChild(index,item)
            else:
                index = self.tasks.currentItem().parent().indexOfChild(self.tasks.currentItem())
                self.tasks.currentItem().parent().insertChild(index,item)
            self.initItemValues(item)
            item.setFlags(item.flags()|QtCore.Qt.ItemIsEditable)
            self.tasks.setCurrentItem(item)
            # self.tasks.editItem(item,0)
            self.task_items[str(self.task_counter)]=item
            # self.generateWidgets(item,self.task_counter)
        
    def insertTaskAfter(self):
        if self.tasks.currentItem() is not None:
            self.task_counter+=1
            item = QtWidgets.QTreeWidgetItem()
            if self.tasks.currentItem().parent() is None:
                index = self.tasks.invisibleRootItem().indexOfChild(self.tasks.currentItem())
                self.tasks.invisibleRootItem().insertChild(index+1,item)
            else:
                index = self.tasks.currentItem().parent().indexOfChild(self.tasks.currentItem())
                self.tasks.currentItem().parent().insertChild(index+1,item)
            self.initItemValues(item)
            item.setFlags(item.flags()|QtCore.Qt.ItemIsEditable)
            # print(item.flags())
            self.tasks.setCurrentItem(item)
            # self.tasks.editItem(item,0)
            self.task_items[str(self.task_counter)]=item
        
    def currentItemCheck(self):
        if self.tasks.selectedItems()==[]:
            self.tasks.setCurrentItem(None)

    def removeTask(self):
        item = self.tasks.currentItem()
        if item is not None:
            tally = []
            del self.task_items[item.text(7)]
            tally.append(item.text(7))
            item.setText(6,"")
            # del self.task_items[self.tasks.itemWidget(item,7).text()]
            # self.tasks.itemWidget(item,6).setText("")
            # self.updateDependents(item)
            self.findChildIds(item,tally)
            # print(tally)
            parent = item.parent()
            if parent:
                parent.removeChild(item)
                if parent.childCount()==0:
                    self.enableWidgets(parent)
            else:
                self.tasks.takeTopLevelItem(self.tasks.indexOfTopLevelItem(item))
            # print(tally)
            if self.tasks.currentItem() is not None:
                self.tasks.currentItem().setSelected(True)
            self.removeChildIds(tally)
            self.cleanUpDepedents(tally)
            self.generateDependents()
            # print(self.task_dependents)
            # print(self.task_dependents_flipped)
            self.propagateDates("removal")
            # print(self.task_items)
            # print(self.task_dependents)
        
    def findChildIds(self, item, tally):
        if item.childCount()>0:
            for x in range(item.childCount()):
                tally.append(item.child(x).text(7))
                if item.child(x).childCount()>0:
                    self.findChildIds(item.child(x),tally)

    def removeChildIds(self,tally):
        for child_id in tally:
            if child_id in self.task_items.keys():
                del self.task_items[child_id]
            # if child_id in self.task_dependents.keys():
            #     del self.task_dependents[child_id]
                
    def cleanUpDepedents(self,tally):
        self.task_dependents = {}
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            item = iterator.value()
            if item.text(6)!="":
                tasks = item.text(6).split(",")
                # print(tasks)
                to_remove = []
                for task in tasks:
                    if task in tally:
                        to_remove.append(task)
                for task in to_remove:
                    tasks.remove(task)
                # print("tasks",tasks)
                item.setText(6,",".join(tasks))
                self.updateDependents(item)
            iterator+=1
        
    def initItemValues(self,item):
        date = QtCore.QDate.currentDate()
        date = date.toString("MM/dd/yyyy")
        item.setText(2,date)
        item.setText(3,date)
        item.setText(4,"Pending")
        item.setText(5,"0")
        item.setText(7,str(self.task_counter))
        item.setText(8,"")
        
            
    def propagateDates(self,propagateFrom):
        # print(date)
        # print(self.sender())
        # self.showData()
        # print(self.sender().parent().text(0))
        # print(propagateFrom)
        self.changed_start_dates = []
        self.changed_end_dates = []
        if propagateFrom=="start":
            self.updateDateFromDuration()
        else:
            self.updateDuration()
        self.calculateDates()
        self.calculateDates()
        self.calculateDates()
        # print(self.changed_start_dates,self.changed_end_dates)
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
            item = iterator.value()
            task_id = item.text(7)
            # print(task_id)
            if task_id in self.task_dependents_flipped.keys():
                affected_tasks = self.task_dependents_flipped[task_id]
                # print("affected tasks", affected_tasks)
                for affected_task in affected_tasks:
                    # print("propagating")
                    if self.checkDepends(task_id,affected_task):
                        duration = self.task_items[affected_task].text(5)
                        start_date = QtCore.QDate.fromString(self.task_items[task_id].text(3),"MM/dd/yyyy")
                        end_date = start_date.addDays(int(duration))
                        old_start_date = QtCore.QDate.fromString(self.task_items[affected_task].text(2),"MM/dd/yyyy")
                        old_end_date = QtCore.QDate.fromString(self.task_items[affected_task].text(3),"MM/dd/yyyy")
                        if old_start_date != start_date:
                            if affected_task not in self.changed_start_dates:
                                self.changed_start_dates.append(affected_task)
                        if old_end_date!=end_date:
                            if affected_task not in self.changed_end_dates:
                                self.changed_end_dates.append(affected_task)
                        self.task_items[affected_task].setText(2,start_date.toString("MM/dd/yyyy"))
                        self.task_items[affected_task].setText(3,end_date.toString("MM/dd/yyyy"))
                        self.bubbleDate(self.task_items[affected_task])
                
            self.bubbleDate(item)
                
            iterator+=1
            
    def checkDepends(self,task_id,affected_task_id):
        check_ids = self.task_dependents[affected_task_id]
        end_date = QtCore.QDate.fromString(self.task_items[task_id].text(3),"MM/dd/yyy")
        good = True
        for check_id in check_ids:
            if check_id != task_id:
                if QtCore.QDate.fromString(self.task_items[check_id].text(3),"MM/dd/yyyy")>end_date:
                    good = False
                    break
        return good
    
            
    def updateDependents(self,item):
        task_id = item.text(7)
        depends = item.text(6)
        if depends =="":
            if task_id in self.task_dependents.keys():
                del self.task_dependents[task_id]
        else:
            self.task_dependents[task_id]=depends.split(",")
            if task_id in self.task_dependents[task_id]:
                self.task_dependents[task_id].remove(task_id)
                item.setText(6,",".join(self.task_dependents[task_id]))
            if item.parent() is not None:
                parent_id = item.parent().text(7)
                if parent_id in self.task_dependents[task_id]:
                    self.task_dependents[task_id].remove(parent_id)
                    item.setText(6,",".join(self.task_dependents[task_id]))
        # print(self.task_dependents)
        
    def setDependents(self):
        self.updateDependents(self.tasks.currentItem())
        self.generateDependents()
        self.propagateDates("dependents")
        
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
        if self.tasks.currentItem() is not None:
            current_item = self.tasks.currentItem()
            start_date = QtCore.QDate.fromString(current_item.text(2),"MM/dd/yyyy")
            end_date = QtCore.QDate.fromString(current_item.text(3),"MM/dd/yyyy")
            duration = start_date.daysTo(end_date)
            current_item.setText(5,str(duration))
        # if duration<0:
        #     self.tasks.itemWidget(current_item,3).setStyleSheet("background-color:#FFADAD")
        # else:
        #     self.tasks.itemWidget(current_item,3).setStyleSheet("")
        
    def updateDateFromDuration(self):
        current_item = self.tasks.currentItem()
        duration = int(current_item.text(5))
        start_date = QtCore.QDate.fromString(current_item.text(2),"MM/dd/yyyy")
        end_date = start_date.addDays(duration)
        end_date=end_date.toString("MM/dd/yyyy")
        current_item.setText(3,end_date)
        # date_widget =self.tasks.itemWidget(current_item,3)
        # duration = int(self.tasks.itemWidget(current_item,5).text())
        # start_date = self.tasks.itemWidget(current_item,2).date()
        # end_date = start_date.addDays(duration)
        # date_widget.setDate(end_date)
        self.propagateDates("duration")
        
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
            
    def getRowCount(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        counter = 0
        while iterator.value():
            iterator+=1
            counter+=1
        return counter
            
    def toggleMilestone(self):
        item = self.tasks.currentItem()
        if item.text(8)=="":
            item.setText(8,"◆")
        else:
            item.setText(8,"")
            
    def updateStatus(self):
        item = self.tasks.currentItem()
        if item is not None:
            self.bubbleStatus(item)
            # self.updateColor()
                
    def bubbleStatus(self,item):
        parent = item.parent()
        if parent is not None:
            completed = True
            for x in range(parent.childCount()):
                if parent.child(x).text(4)!="Completed":
                    completed = False
                    break
            if completed:
                parent.setText(4,"Completed")
            else:
                parent.setText(4,"Pending")
            self.bubbleStatus(parent)
                
    def bubbleDate(self,item):
        # print("bubbling")
        if item.parent() is not None:
            # print("bubbling")
            parent = item.parent()
            start_date = ""
            end_date = ""
            for x in range(item.parent().childCount()):
                if x == 0:
                    start_date = QtCore.QDate.fromString(parent.child(x).text(2),"MM/dd/yyyy")
                    end_date = QtCore.QDate.fromString(parent.child(x).text(3),"MM/dd/yyyy")
                else:
                    start_comp = QtCore.QDate.fromString(parent.child(x).text(2),"MM/dd/yyyy")
                    end_comp = QtCore.QDate.fromString(parent.child(x).text(3),"MM/dd/yyyy")
                    if start_comp<start_date:
                        start_date=start_comp
                    if end_comp>end_date:
                        end_date=end_comp
            old_start_date = QtCore.QDate.fromString(parent.text(2),"MM/dd/yyyy")
            old_end_date = QtCore.QDate.fromString(parent.text(3),"MM/dd/yyyy")
            parent_id = parent.text(7)
            if old_start_date != start_date:
                if parent_id not in self.changed_start_dates:
                    self.changed_start_dates.append(parent_id)
            if old_end_date != end_date:
                if parent_id not in self.changed_end_dates:
                    self.changed_end_dates.append(parent_id)
            parent.setText(2,start_date.toString("MM/dd/yyyy"))
            parent.setText(3,end_date.toString("MM/dd/yyyy"))
            duration = start_date.daysTo(end_date)
            parent.setText(5,str(duration))
            self.bubbleDate(parent)
        
    def saveData(self):
        self.cursor.execute(f"delete from project_tasks where project_id='{self.doc_id}'")
        self.cursor.execute(f"delete from task_link where project_id='{self.doc_id}'")
        self.db.commit()
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
        while iterator.value():
            item = iterator.value()
            task_name = item.text(0)
            owner = item.text(1)
            start_date = item.text(2)
            end_date = item.text(3)
            status = item.text(4)
            duration = item.text(5)
            predecessors = item.text(6)
            task_id = item.text(7)
            milestone = item.text(8)
            if item.childCount()>0:
                task_type = "parent"
                # print("has children:")
                for x in range(item.childCount()):
                    # print(self.tasks.itemWidget(item.child(x),7).text())
                    data = (self.doc_id,task_id,item.child(x).text(7))
                    self.cursor.execute(f"INSERT INTO task_link(project_id, parent_task_id, child_task_id) VALUES(%s,%s,%s)",(data))
            else:
                task_type = "child"
            data = (self.doc_id,task_name,owner,start_date,end_date,status,duration,predecessors,task_id,task_type,milestone)
            # print(data)
            self.cursor.execute(f"INSERT INTO project_tasks(project_id,task_name,assigned_to,start_date,end_date,status,duration,predecessors,task_id,type,milestone) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(data))
            iterator+=1
        self.db.commit()
    
    def loadData(self):
        self.cursor.execute(f"select * from project_tasks where project_id='{self.doc_id}'")
        results = self.cursor.fetchall()
        for result in results:
            # print(result["task_id"])
            parent = self.getParentTask(result["task_id"])
            if parent is None:
                item = QtWidgets.QTreeWidgetItem(self.tasks)
            else:
                item = QtWidgets.QTreeWidgetItem(self.task_items[str(parent[0])])
            self.task_items[str(result["task_id"])]=item
            # self.generateWidgets(item,str(result["task_id"]))
            #setting data
            if result["type"]!="parent" and self.access=="write":
                item.setFlags(item.flags()|QtCore.Qt.ItemIsEditable)
            item.setText(0,result["task_name"])
            item.setText(1,result["assigned_to"])
            item.setText(2,result["start_date"])
            item.setText(3,result["end_date"])
            item.setText(4,result["status"])
            item.setText(5,result["duration"])
            item.setText(6,result["predecessors"])
            item.setText(7,str(result["task_id"]))
            item.setText(8,result["milestone"])
            self.updateDependents(item)
        self.generateDependents()
        self.loadCounter()
        # self.updateColor()
        self.expandAll()
        
    def generateTemplate(self):
        filename, ok = QtWidgets.QFileDialog.getSaveFileName(self,("Save File"),"template.csv",".csv")
        if filename !="" and ok:
            iterator = QtWidgets.QTreeWidgetItemIterator(self.tasks)
            template = []
            #task id, task name, milestone, parent id, item_type
            while iterator.value():
                item = iterator.value()
                if item.childCount()>0:
                    item_type = "parent"
                else:
                    item_type = "child"
                if item.parent() is None:
                    template.append((item.text(7),item.text(0),item.text(8),"None",item_type))
                else:
                    template.append((item.text(7),item.text(0),item.text(8),item.parent().text(7),item_type))
                iterator+=1
            # print(template)
            f = open(filename, "w")
            for line in template:
                text = ",".join(line)
                text+="\n"
                f.write(text)
            f.close()
            self.dispMsg("Template Saved!")
        
    def loadTemplate(self):
        filename,ok = QtWidgets.QFileDialog.getOpenFileName(self,self.tr("Open Template"),program_location,self.tr("Template Files (*.csv)"))
        if filename!="" and ok:
            f = open(filename, "r")
            counter = 0
            for line in f:
                # print(line.strip("\n").split(","))
                data = line.strip("\n").split(",")
                task_id = data[0]
                task_name = data[1]
                milestone = data[2]
                parent = data[3]
                item_type = data[4]
                if int(task_id)>counter:
                    counter=int(task_id)
                if parent=="None":
                    item = QtWidgets.QTreeWidgetItem(self.tasks)
                else:
                    item = QtWidgets.QTreeWidgetItem(self.task_items[parent])
                self.task_items[task_id]=item
                # self.generateWidgets(item,str(result["task_id"]))
                #setting data
                if item_type!="parent":
                    item.setFlags(item.flags()|QtCore.Qt.ItemIsEditable)
                current_date = QtCore.QDate.currentDate().toString("MM/dd/yyyy")
                item.setText(0,task_name)
                item.setText(1,"")
                item.setText(2,current_date)
                item.setText(3,current_date)
                item.setText(4,"Pending")
                item.setText(5,"0")
                item.setText(6,"")
                item.setText(7,task_id)
                item.setText(8,milestone)
                self.updateDependents(item)
            self.task_counter=counter
            self.generateDependents()
            self.expandAll()
        
    def loadCounter(self):
        self.cursor.execute(f"select max(task_id) from project_tasks where project_id='{self.doc_id}'")
        result = self.cursor.fetchone()
        if result[0] is not None:
            self.task_counter=int(result[0])
            # print(self.task_counter)
    
    def disableWidgets(self,item):
        item.setText(1,"")
        item.setText(6,"")
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.updateDependents(item)
        
    def enableWidgets(self,item):
        item.setFlags(item.flags()|QtCore.Qt.ItemIsEditable)
        self.updateDependents(item)
    
    def getParentTask(self,task_id):
        self.cursor.execute(f"select parent_task_id from task_link where project_id ='{self.doc_id}' and child_task_id='{task_id}'")
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
            task_name = item.text(0)
            self.getIndentLevel(item)
            task_name = self.indent_level*":" + " " + task_name
            owner = item.text(1)
            start_date = item.text(2)
            end_date = item.text(3)
            status = item.text(4)
            duration = item.text(5)
            predecessors = item.text(6)
            task_id = item.text(7)
            line = [task_name,owner,start_date,end_date,duration,status,predecessors,task_id]
            start = QtCore.QDate.fromString(start_date,"MM/dd/yyyy")
            end = QtCore.QDate.fromString(end_date,"MM/dd/yyyy")
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
                starting_date = QtCore.QDate.fromString(item.text(2),"MM/dd/yyyy")
                ending_date = QtCore.QDate.fromString(item.text(3),"MM/dd/yyyy")
                # starting_date = self.tasks.itemWidget(item,2).date()
                # ending_date = self.tasks.itemWidget(item,3).date()
            else:
                start_date = QtCore.QDate.fromString(item.text(2),"MM/dd/yyyy")
                end_date = QtCore.QDate.fromString(item.text(3),"MM/dd/yyyy")
                # start_date = self.tasks.itemWidget(item,2).date()
                # end_date = self.tasks.itemWidget(item,3).date()
                # print(start_date,end_date)
                if start_date<starting_date:
                    starting_date=start_date
                if end_date>ending_date:
                    ending_date=end_date
            iterator+=1
        # print(starting_date,ending_date)
        return starting_date,ending_date
        
    def repopulateTable(self):
        pass 
    
    def contextMenuEvent(self,event):
        self.menu.exec_(event.globalPos())
    
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
        default_color = PySide6.QtGui.QColor.fromRgbF(0.000000, 0.000000, 0.000000, 0.000000)
        color = QtGui.QColor("#BDB2FF") #purple
        color2 = QtGui.QColor("#CAFFBF") #green
        color3 = QtGui.QColor("#FDFFB6") #yellow
        color4 = QtGui.QColor("#FFADAD") #red
        r = option.rect
        # print(index.data())
        pen = painter.pen()
        font = painter.font()
        painter.setBrush(color)
        painter.setPen(QtGui.Qt.NoPen)
        # if option.state & QtWidgets.QStyle.State_Selected:
        #     if index.column()==0:
        #         painter.drawRect(r.topLeft().x(),r.topLeft().y(),5,r.height())
        if index.column()==0:
            status = index.siblingAtColumn(4).data()
            if status=="Completed":
                painter.setBrush(color2)
                painter.drawRect(r)
            else:
                today = QtCore.QDate.currentDate()
                end_date = QtCore.QDate.fromString(index.siblingAtColumn(3).data(),"MM/dd/yyyy")
                if end_date<today:
                    painter.setBrush(color4)
                else:
                    if status == "Started":
                        painter.setBrush(color3)
                    else:
                        painter.setBrush(default_color)
                painter.drawRect(r)
        if index.column()==2:
            if index.siblingAtColumn(7).data() in self.parent.changed_start_dates:
                painter.setBrush(color3)
                painter.drawRect(r)
        if index.column()==3:
            if index.siblingAtColumn(7).data() in self.parent.changed_end_dates:
                painter.setBrush(color3)
                painter.drawRect(r)
        
        painter.setBrush(default_color)
                
        painter.setPen(pen)
        painter.drawLine(r.bottomLeft(),r.bottomRight())
        
        if QtCore.Qt.ItemIsEditable not in index.flags():
            font.setBold(True)
            painter.setFont(font)
        else:
            font.setBold(False)
            painter.setFont(font)
        if index.column()==0:
            painter.drawText(r,QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter,index.data())
        else:
            painter.drawText(r,QtCore.Qt.AlignCenter,index.data())
            
        # painter.restore()
        
    def createEditor(self,parent,option,index):
        if index.column() == 0:
            editor = QtWidgets.QLineEdit(parent)
        elif index.column() ==1:
            editor = QtWidgets.QComboBox(parent)
            editor.addItems(self.parent.parent.members)
        elif index.column() ==4:
            editor = QtWidgets.QComboBox(parent)
            editor.addItems(["Pending","Started","Completed"])
        elif index.column() ==5:
            editor = QtWidgets.QLineEdit(parent)
            editor.editingFinished.connect(self.parent.updateDateFromDuration)
        elif index.column()==6:
            editor = QtWidgets.QLineEdit(parent)
            editor.editingFinished.connect(self.parent.setDependents)
        elif index.column()==7 or index.column()==8:
            return None
        else:
            editor = QtWidgets.QDateEdit(parent,calendarPopup=True)
            editor.setDate(QtCore.QDate.currentDate())
            # editor.editingFinished.connect(self.parent.propagateDates)
        editor.setAutoFillBackground(True)
        return editor
        
    def setEditorData(self,editor,index):
        if index.column() in [0,5,6,7]:
            editor.setText(index.data())
        elif index.column() in [1,4]:
            editor.setCurrentText(index.data())
        else:
            editor.setDate(QtCore.QDate.fromString(index.data(),"MM/dd/yyyy"))
        
        
    def setModelData(self, editor,model,index):
        if index.column() in [0,5,6,7]:
            model.setData(index,editor.text())
        elif index.column() in [1,4]:
            model.setData(index,editor.currentText())
        else:
            model.setData(index,editor.date().toString("MM/dd/yyyy"))
            if index.column()==2:
                self.parent.propagateDates("start")
            else:
                self.parent.propagateDates("end")
        if index.column()==4:
            self.parent.updateStatus()
            
    def updateEditorGeometry(self, editor, option, index):
            editor.setGeometry(option.rect)
    
    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width()-50,25)