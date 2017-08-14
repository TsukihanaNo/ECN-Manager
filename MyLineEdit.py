from PySide import QtGui, QtCore

class MyLineEdit(QtGui.QLineEdit):
    def __init__(self,parent = None):
        super(MyLineEdit,self).__init__(parent)
        self.setStyleSheet("border: 2px solid gray; border-radius: 10px; padding: 0 8px")
        self.parent = parent    
