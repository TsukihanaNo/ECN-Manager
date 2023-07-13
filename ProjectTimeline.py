from PySide6 import QtGui, QtCore, QtWidgets
import sys, os

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

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
        # self.window_height = 600
        # self.window_width = 1000
        self.initAtt()
        self.initUI()
        self.center()
        self.show()

    def initAtt(self):
        # self.setGeometry(100,50,self.window_width,self.window_height)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowState(QtGui.Qt.WindowMaximized)

    def initUI(self): 
        self.grid_size = 25
        starting_date = QtCore.QDate.fromString("01/01/2023","MM/dd/yyyy")
        ending_date = QtCore.QDate.fromString("12/31/2023","MM/dd/yyyy")
        total_days = starting_date.daysTo(ending_date)
        task_count = 30
        spacing = 5
        self.offset = 10
        self.scene_height = task_count * self.grid_size + task_count* spacing+ self.offset*2
        self.scene_width = total_days * self.grid_size + self.offset*2
        main_layout = QtWidgets.QHBoxLayout(self)
        self.graphic_scene = QtWidgets.QGraphicsScene(0,0,self.scene_width,self.scene_height)
        self.graphic_scene.setBackgroundBrush(QtGui.Qt.white)
        vert_lines = []
        line_pen = QtGui.QPen()
        line_pen.setBrush(QtGui.Qt.gray)
        
        MONTH = {1:"JANUARY", 2:"FEBUARY", 3: "MARCH", 4: "APRIL", 5:"MAY", 6:"JUNE", 7:"JULY", 8:"AUGUST", 9:"SEPTEMBER", 10:"OCTOBER", 11:"NOVEMBER", 12: "DECEMBER"}
        
        for x in range(int((self.scene_width-self.offset*2)/self.grid_size)):
            line = QtCore.QLineF((x)*self.grid_size+self.offset*2,self.offset*4,(x)*self.grid_size+self.offset*2,self.scene_height-self.offset)
            line_item = QtWidgets.QGraphicsLineItem(line)
            line_item.setPen(line_pen)
            vert_lines.append(line_item)
            
        #draw days
        for day in range(total_days):
            current = starting_date.addDays(day)
            # print(current.day())
            text_item = QtWidgets.QGraphicsSimpleTextItem(str(current.day()))
            offset = text_item.boundingRect().width()/2
            text_item.setPos(day*self.grid_size+self.offset*2-offset,self.offset*2)
            self.graphic_scene.addItem(text_item)
            if current.day()==1:
                month_item = QtWidgets.QGraphicsSimpleTextItem(MONTH[current.month()])
                # offset = month_item.boundingRect().width()/2
                month_item.setPos(day*self.grid_size+self.offset*2,self.offset-5)
                self.graphic_scene.addItem(month_item)
            
        # hor_lines = []
        # for y in range(int((self.scene_height-self.offset*2)/self.grid_size)+1):
        #     hor_lines.append(QtCore.QLineF(self.offset,(y)*self.grid_size+self.offset,self.scene_width-self.offset,(y)*self.grid_size+self.offset))
            
        for line in vert_lines:
            self.graphic_scene.addItem(line)
        # for line in hor_lines:
        #     self.graphic_scene.addLine(line)
        
        for x in range(task_count):
            rect = QtWidgets.QGraphicsRectItem(self.offset*2+self.grid_size*20*x,self.offset*4+spacing*(x)+self.grid_size*x,self.grid_size*20,self.grid_size)
            rect.setBrush(QtGui.QBrush(QtGui.Qt.gray))
            rect.setPen(QtGui.Qt.NoPen)
            self.graphic_scene.addItem(rect)
            
        # rect = QtWidgets.QGraphicsRectItem(self.offset*2+self.grid_size*10,self.offset*4+spacing+self.grid_size,self.grid_size*20,self.grid_size)
        # rect.setBrush(QtGui.QBrush(QtGui.Qt.gray))
        # rect.setPen(QtGui.Qt.NoPen)
        # self.graphic_scene.addItem(rect)
            
        self.graphics_view = QtWidgets.QGraphicsView(self.graphic_scene)
        self.graphics_view.show()
        self.graphics_view.horizontalScrollBar().setValue(0)
        self.graphics_view.verticalScrollBar().setValue(0)
        # self.tree = QtWidgets.QTreeWidget()
        # self.tree.setFixedWidth(300)
        # main_layout.addWidget(self.tree)
        main_layout.addWidget(self.graphics_view)
    
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
    
# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    timeline = ProjectTimeline()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()