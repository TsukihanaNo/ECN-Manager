from PySide6 import QtWidgets, QtCore, QtGui
from datetime import datetime
import sys, os


class PurchReqDetailTab(QtWidgets.QWidget):
    def __init__(self, parent = None, doc_id = None):
        super(PurchReqDetailTab,self).__init__()
        self.parent = parent
        self.cursor = self.parent.cursor
        self.db = self.parent.db
        self.settings = parent.settings
        self.user_info = self.parent.user_info
        self.windowWidth =  950
        self.windowHeight = 580
        self.setFixedSize(self.windowWidth,self.windowHeight)
        self.doc_id = doc_id
        self.tablist = []
        # self.initAtt()
        # self.initUI()