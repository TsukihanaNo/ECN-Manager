from PySide6 import QtGui, QtCore, QtWidgets
import sys, os

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))
    
MONTH = {1:"JANUARY", 2:"FEBUARY", 3: "MARCH", 4: "APRIL", 5:"MAY", 6:"JUNE", 7:"JULY", 8:"AUGUST", 9:"SEPTEMBER", 10:"OCTOBER", 11:"NOVEMBER", 12: "DECEMBER"}

class ProjectTimeline(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ProjectTimeline,self).__init__()
        if parent is not None:
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
        self.window_height = 800
        self.window_width = 1000
        self.zoom_factor = 1
        self.initAtt()
        # self.show()
        self.initUI()
        self.center()
        self.show()

    def initAtt(self):
        self.setGeometry(100,50,self.window_width,self.window_height)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # self.setWindowState(QtGui.Qt.WindowMaximized)

    def initUI(self):     
        main_layout = QtWidgets.QVBoxLayout(self)
        self.toolbar = QtWidgets.QToolBar()
        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.clicked.connect(self.save)
        self.button_zoom_in = QtWidgets.QPushButton("Zoom In")
        self.button_zoom_in.clicked.connect(self.ZoomIn)
        self.button_zoom_out = QtWidgets.QPushButton("Zoom Out")
        self.button_zoom_out.clicked.connect(self.ZoomOut)
        self.label_zoom = QtWidgets.QLabel(f"Zoom: {self.zoom_factor*100}% ")
        self.radio_days = QtWidgets.QRadioButton("Days")
        self.radio_days.setChecked(True)
        self.radio_weeks = QtWidgets.QRadioButton("Weeks")
        self.radio_months = QtWidgets.QRadioButton("Months")
        self.toolbar.addWidget(self.button_save)
        self.toolbar.addWidget(self.button_zoom_in)
        self.toolbar.addWidget(self.button_zoom_out)
        self.toolbar.addWidget(self.label_zoom)
        self.toolbar.addWidget(self.radio_days)
        self.toolbar.addWidget(self.radio_weeks)
        self.toolbar.addWidget(self.radio_months)
        main_layout.addWidget(self.toolbar)
        
        self.grid_size = 25
        # starting_date = QtCore.QDate.fromString("01/01/2023","MM/dd/yyyy")
        # ending_date = QtCore.QDate.fromString("12/31/2023","MM/dd/yyyy")
        starting_date,ending_date = self.parent.getStartEndDates()
        total_days = starting_date.daysTo(ending_date)
        current_date_pos = starting_date.daysTo(QtCore.QDate.currentDate())
        task_count = self.parent.getRowCount()
        # task_count=100
        spacing = 5
        self.offset = 10
        self.drawDayMode(task_count,spacing,starting_date,total_days,current_date_pos)
        # self.drawWeekMode(task_count,spacing,starting_date,ending_date)
            
        self.graphics_view = QtWidgets.QGraphicsView(self.graphic_scene)
        self.graphics_view.show()
        self.graphics_view.horizontalScrollBar().setValue(0)
        self.graphics_view.verticalScrollBar().setValue(0)
        self.graphics_view.verticalScrollBar().valueChanged.connect(self.moveGroup)
        self.graphics_view.centerOn(current_date_pos*self.grid_size+self.offset*2,0)
        # self.tree = QtWidgets.QTreeWidget()
        # self.tree.setFixedWidth(300)
        # main_layout.addWidget(self.tree)
        
        main_layout.addWidget(self.graphics_view)
        
    def drawDayMode(self,task_count,spacing,starting_date,total_days,current_date_pos):
        scene_height = task_count * self.grid_size + task_count* spacing+ self.offset*2
        if scene_height<self.height():
            scene_height=self.height()
        scene_width = total_days * self.grid_size + self.offset*2
        if scene_width<self.width():
            scene_width=self.width()
            steps = (scene_width-self.offset*2)/self.grid_size
            total_days = int(steps)
        self.graphic_scene = QtWidgets.QGraphicsScene(0,0,scene_width,scene_height)
        self.graphic_scene.setBackgroundBrush(QtGui.Qt.white)
        vert_lines = []
        line_pen = QtGui.QPen()
        # line_pen.setStyle(QtGui.Qt.DotLine)
        line_pen.setBrush(QtGui.QColor("#ece1f7"))
        current_line_pen = QtGui.QPen()
        current_line_pen.setBrush(QtGui.Qt.red)
        text_pen = QtGui.QPen()
        text_pen.setBrush(QtGui.Qt.red)
        
        for x in range(int((scene_width-self.offset*2)/self.grid_size)):
            line = QtCore.QLineF((x)*self.grid_size+self.offset*2,self.offset*4,(x)*self.grid_size+self.offset*2,scene_height-self.offset)
            line_item = QtWidgets.QGraphicsLineItem(line)
            if x == current_date_pos:
                line_item.setPen(current_line_pen)
            else:
                line_item.setPen(line_pen)
            vert_lines.append(line_item)
            
        for line in vert_lines:
            self.graphic_scene.addItem(line)
            
        #drawing the tasks
        iterator = QtWidgets.QTreeWidgetItemIterator(self.parent.tasks)
        counter = 0
        while iterator.value():
            tree_item = iterator.value()
            starting = QtCore.QDate.fromString(tree_item.text(2),"MM/dd/yyyy")
            # ending = QtCore.QDate.fromString(tree_item.text(3),"MM/dd/yyyy")
            starting_point = starting_date.daysTo(starting)
            duration = int(tree_item.text(5))
            rect = QtWidgets.QGraphicsRectItem(self.offset*2+self.grid_size*starting_point,self.offset*4+spacing*counter+self.grid_size*counter,self.grid_size*duration,self.grid_size)
            rect.setBrush(QtGui.QBrush(QtGui.QColor("#e8d7f7")))
            rect.setPen(QtGui.Qt.NoPen)
            self.graphic_scene.addItem(rect)
            text = QtWidgets.QGraphicsSimpleTextItem(tree_item.text(0))
            # text.setPen(text_pen)
            text.setPos(self.offset*2+self.grid_size*starting_point,self.offset*4+spacing*counter+self.grid_size*counter)
            self.graphic_scene.addItem(text)
            iterator+=1
            counter+=1
            
        #draw days
        self.group_days = QtWidgets.QGraphicsItemGroup()
        rect_bg = QtWidgets.QGraphicsRectItem(0,0,scene_width,self.offset*4)
        rect_bg.setBrush(QtGui.Qt.white)
        rect_bg.setPen(QtGui.Qt.NoPen)
        self.group_days.addToGroup(rect_bg)
        for day in range(total_days):
            current = starting_date.addDays(day)
            # print(current.day())
            text_item = QtWidgets.QGraphicsSimpleTextItem(str(current.day()))
            offset = text_item.boundingRect().width()/2
            text_item.setPos(day*self.grid_size+self.offset*2-offset,self.offset*2)
            if current == QtCore.QDate.currentDate():
                text_item.setPen(text_pen)
            # self.graphic_scene.addItem(text_item)
            self.group_days.addToGroup(text_item)
            if current.day()==1:
                month_item = QtWidgets.QGraphicsSimpleTextItem(MONTH[current.month()]+ f" {current.year()}")
                # offset = month_item.boundingRect().width()/2
                month_item.setPos(day*self.grid_size+self.offset*2,self.offset-5)
                # self.graphic_scene.addItem(month_item)
                self.group_days.addToGroup(month_item)
        self.graphic_scene.addItem(self.group_days)
        
        
        
    def ZoomIn(self):
        # old_pos = self.graphics_view.mapToScene()
        self.zoom_factor = self.zoom_factor * 1.25
        self.label_zoom.setText(f"Zoom: {int(self.zoom_factor*100)}% ")
        self.graphics_view.scale(1.25,1.25)
    
    def ZoomOut(self):
        self.zoom_factor = self.zoom_factor * (1/1.25)
        self.label_zoom.setText(f"Zoom: {int(self.zoom_factor*100)}% ")
        self.graphics_view.scale(1/1.25,1/1.25)
        
    def moveGroup(self):
        y_offset = self.graphics_view.mapToScene(0,0,self.graphics_view.width(),self.graphics_view.height()).first().y()
        # print(y_offset)
        # print(self.group_days.pos().x(),self.group_days.pos().y())
        self.group_days.setPos(0,y_offset)
        
    def save(self):
        image = QtGui.QImage(int(self.graphic_scene.width()),int(self.graphic_scene.height()),QtGui.QImage.Format_RGB32)
        painter = QtGui.QPainter(image)
        painter.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.TextAntialiasing)
        self.graphic_scene.render(painter)
        image.save("timeline.png")
        painter.end()
        self.dispMsg("image saved!")
    
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
        
    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()
    
# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    timeline = ProjectTimeline()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()