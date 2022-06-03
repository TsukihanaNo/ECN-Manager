from PySide6 import QtWidgets, QtGui, QtCore

class CommentTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(CommentTab,self).__init__()
        self.parent = parent
        self.menu = QtWidgets.QMenu(self)
        self.getUserNameDict()
        self.initAtt()
        self.createMenu()
        self.initUI()
        
        
    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def initUI(self):
        mainlayout = QtWidgets.QVBoxLayout(self)
        
        self.messages = QtWidgets.QListView()
        self.messages.setResizeMode(QtWidgets.QListView.Adjust)
        self.messages.setItemDelegate(MessageDelegate())
        
        self.model = MessageModel()
        self.messages.setModel(self.model)
        
        mainlayout.addWidget(self.messages)
        
    def createMenu(self):
        copy_action = QtGui.QAction("Copy Message",self)
        copy_action.triggered.connect(self.copyMessage)
        self.menu.addAction(copy_action)
        
        
    def getUserNameDict(self):
        self.parent.cursor.execute(f"Select USER_ID, NAME from USER")
        results = self.parent.cursor.fetchall()
        self.user_name = {}
        for result in results:
            self.user_name[result[0]]=result[1]
            
    def copyMessage(self):
        index = self.messages.currentIndex()
        #print(index.data(QtCore.Qt.DisplayRole)[2])
        clipboard = QtGui.QGuiApplication.clipboard()
        clipboard.setText(index.data(QtCore.Qt.DisplayRole)[2])
            
    def contextMenuEvent(self,event):
        self.menu.exec_(event.globalPos())
        
    def resizeEvent(self, e):
        self.model.layoutChanged.emit()
        
    def loadComments(self):
            # self.tab_comments.enterText.clear()
            self.model.clear_message()
            command = "Select * from COMMENTS where ECN_ID = '" + self.parent.ecn_id+"'"
            self.parent.cursor.execute(command)
            results = self.parent.cursor.fetchall()
            for result in results:
                comment_type = ""
                if "Reject" in result["TYPE"]:
                    comment_type="Reject"
                if self.parent.tab_ecn.line_author.text() == result['USER']:
                    self.model.add_message(USER_ME,f"{self.user_name[result['USER']]} ({result['USER']})  -  {result['COMM_DATE']}  [{result['TYPE']}]:",result['COMMENT'],comment_type)
                else:
                    self.model.add_message(USER_THEM,f"{self.user_name[result['USER']]} ({result['USER']})  -  {result['COMM_DATE']}  [{result['TYPE']}]:",result['COMMENT'],comment_type)


USER_ME = 0
USER_THEM = 1
REJECT = "Reject"

BUBBLE_COLORS = {USER_ME: "#A0C4FF", USER_THEM: "#CAFFBF", REJECT: "#FFADAD"}
USER_TRANSLATE = {USER_ME: QtCore.QPoint(20, 0), USER_THEM: QtCore.QPoint(0, 0)}

BUBBLE_PADDING = QtCore.QMargins(15, 5, 35, 5)
TEXT_PADDING = QtCore.QMargins(25, 15, 45, 15)


class MessageDelegate(QtWidgets.QStyledItemDelegate):
    _font = None

    def paint(self, painter, option, index):
        painter.save()
        
        # if option.state & QtWidgets.QStyle.State_Selected:
        #     painter.fillRect(option.rect, option.palette.highlight())
        # Retrieve the user,message uple from our model.data method.
        user, header, text, comment_type = index.model().data(index, QtCore.Qt.DisplayRole)

        trans = USER_TRANSLATE[user]
        painter.translate(trans)
        
        bubblerect = option.rect.marginsRemoved(BUBBLE_PADDING)
        textrect = option.rect.marginsRemoved(TEXT_PADDING)

        painter.setPen(QtCore.Qt.NoPen)
        if comment_type != REJECT:
            color = QtGui.QColor(BUBBLE_COLORS[user])
        else:
            color = QtGui.QColor(BUBBLE_COLORS[REJECT])
        painter.setBrush(color)
        painter.drawRoundedRect(bubblerect, 10, 10)

        #draw the triangle bubble-pointer, starting from the top left/right.
        if user == USER_ME:
            p1 = bubblerect.topRight()
        else:
            p1 = bubblerect.topLeft()
        painter.drawPolygon([p1 + QtCore.QPoint(-10, 0), p1 + QtCore.QPoint(10, 0), p1 + QtCore.QPoint(0, 10)])

        toption = QtGui.QTextOption()
        toption.setWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        
        # draw header
        font = painter.font()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(textrect.topLeft()+QtCore.QPoint(0,5),header)
        # draw the text
        doc = QtGui.QTextDocument(text)
        doc.setTextWidth(textrect.width())
        doc.setDefaultTextOption(toption)
        doc.setDocumentMargin(0)

        painter.translate(textrect.topLeft()+QtCore.QPoint(0,10))
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        _, header, text,comment_type = index.model().data(index, QtCore.Qt.DisplayRole)
        textrect = option.rect.marginsRemoved(TEXT_PADDING)

        toption = QtGui.QTextOption()
        toption.setWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)

        doc = QtGui.QTextDocument(text)
        doc.setTextWidth(textrect.width())
        doc.setDefaultTextOption(toption)
        doc.setDocumentMargin(0)

        textrect.setHeight(doc.size().height())
        textrect = textrect.marginsAdded(QtCore.QMargins(25, 15, 0, 5))
        return textrect.size() + QtCore.QSize(0,20)


class MessageModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(MessageModel, self).__init__(*args, **kwargs)
        self.messages = []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            # Here we pass the delegate the user, message tuple.
            return self.messages[index.row()]

    def setData(self, index, role, value):
        self._size[index.row()]

    def rowCount(self, index):
        return len(self.messages)

    def clear_message(self):
        self.messages = []

    def add_message(self, who, header, text,comment_type):
        """
        Add an message to our message list, getting the text from the QLineEdit
        """
        if text:  # Don't add empty strings.
            # Access the list via the model.
            self.messages.append((who, header, text, comment_type))
            # Trigger refresh.
            self.layoutChanged.emit()
