from PySide6 import QtWidgets, QtGui, QtCore

class CommentTab(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(CommentTab,self).__init__()
        self.parent = parent
        self.initAtt()
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
        
    def resizeEvent(self, e):
        self.model.layoutChanged.emit()
        
    def loadComments(self):
            # self.tab_comments.enterText.clear()
            command = "Select * from COMMENTS where ECN_ID = '" + self.parent.ecn_id+"'"
            self.parent.cursor.execute(command)
            results = self.parent.cursor.fetchall()
            for result in results:
                comment_type = ""
                if "Reject" in result["TYPE"]:
                    comment_type="Reject"
                if self.parent.tab_ecn.line_author.text() == result['USER']:
                    self.model.add_message(USER_ME,f"{result['USER']}  -  {result['COMM_DATE']}  [{result['TYPE']}]:",result['COMMENT'],comment_type)
                else:
                    self.model.add_message(USER_THEM,f"{result['USER']}  -  {result['COMM_DATE']}  [{result['TYPE']}]:",result['COMMENT'],comment_type)


USER_ME = 0
USER_THEM = 1
REJECT = "Reject"

BUBBLE_COLORS = {USER_ME: "#90caf9", USER_THEM: "#a5d6a7", REJECT: "#ffadad"}
USER_TRANSLATE = {USER_ME: QtCore.QPoint(20, 0), USER_THEM: QtCore.QPoint(0, 0)}

BUBBLE_PADDING = QtCore.QMargins(15, 5, 35, 5)
TEXT_PADDING = QtCore.QMargins(25, 15, 45, 15)


class MessageDelegate(QtWidgets.QStyledItemDelegate):
    _font = None

    def paint(self, painter, option, index):
        painter.save()
        # Retrieve the user,message uple from our model.data method.
        user, header, text, comment_type = index.model().data(index, QtCore.Qt.DisplayRole)

        trans = USER_TRANSLATE[user]
        painter.translate(trans)

        # option.rect contains our item dimensions. We need to pad it a bit
        # to give us space from the edge to draw our shape.
        bubblerect = option.rect.marginsRemoved(BUBBLE_PADDING)
        textrect = option.rect.marginsRemoved(TEXT_PADDING)

        # draw the bubble, changing color + arrow position depending on who
        # sent the message. the bubble is a rounded rect, with a triangle in
        # the edge.
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

    def add_message(self, who, header, text,comment_type):
        """
        Add an message to our message list, getting the text from the QLineEdit
        """
        if text:  # Don't add empty strings.
            # Access the list via the model.
            self.messages.append((who, header, text, comment_type))
            # Trigger refresh.
            self.layoutChanged.emit()
