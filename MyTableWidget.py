from PySide import QtGui, QtCore

class MyTableWdiget(QtGui.QTableWidget):
    def __init__(self,row=1, column=1, parent = None):
        super(MyTableWdiget,self).__init__(parent)
        self.parent = parent  
        self.setRowCount(row)
        self.setColumnCount(column)
        self.combos = {}
        self.checkcols = []

    # def resizeEvent(self,event):
    #     width = int(self.width()/self.columnCount())-3
    #     for x in range(self.columnCount()):
    #         self.setColumnWidth(x,width)
    #     print(self.parent.width())


    def keyPressEvent(self,event):
        #print(event.key())
        if event.key() == 16777220: #neter
            if self.currentRow() == self.rowCount()-1:
                self.insertRow(self.rowCount())
                self.setCurrentCell(self.currentRow()+1,self.currentColumn())
                if len(self.combos)!=0:
                    self.generateRow()
            if self.currentRow() != self.rowCount()-1:
                self.setCurrentCell(self.currentRow()+1,self.currentColumn())
        elif event.key() == 16777235: #up
            if self.currentRow()!=0:
                self.setCurrentCell(self.currentRow()-1,self.currentColumn())
        elif event.key() == 16777237: #down
            if self.currentRow() != self.rowCount()-1:
                self.setCurrentCell(self.currentRow()+1,self.currentColumn())
        elif event.key() == 16777234: #left
            if self.currentColumn()>0:
                self.setCurrentCell(self.currentRow(),self.currentColumn()-1)
        elif event.key() == 16777236: #right
            if self.currentColumn() != self.columnCount()-1:
                self.setCurrentCell(self.currentRow(),self.currentColumn()+1)
        elif event.key() == 16777216: #escape key
            if self.currentRow()==self.rowCount()-1 and self.rowCount()>1:
                if not self.item(self.currentRow(),self.currentColumn()):
                    if self.checkRow():
                        self.setCurrentCell(self.currentRow()-1,0)
                        self.removeRow(self.rowCount()-1)
        else:
            self.edit(self.currentIndex())

    def checkRow(self):
        for col in self.checkcols:
            if self.item(self.currentRow(),):
                return False
        return True

    def setCombos(self,col,item):
        if col < self.columnCount():
            self.combos[col] = item

    def setCheckCol(self,checkcols):
        self.checkcols=checkcols

    def generateRow(self,new=False):
        if len(self.combos)!=0:
            if new:
                for index in self.combos.keys():
                    box = QtGui.QComboBox()
                    box.addItems(self.combos[index])
                    self.setCellWidget(0,index,box)
            else:
                for index in self.combos.keys():
                    box = QtGui.QComboBox()
                    box.addItems(self.combos[index])
                    self.setCellWidget(self.currentRow(),index,box)
