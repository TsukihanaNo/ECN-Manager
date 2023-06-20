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
        self.grid_size = 25
        total_days = 31*4
        task_count = 30
        self.offset = 10
        self.window_height = 600
        self.window_width = 1000
        self.scene_height = task_count * self.grid_size + self.offset*2
        self.scene_width = total_days * self.grid_size + self.offset*2
        self.initAtt()
        self.initUI()
        self.center()
        self.show()

    def initAtt(self):
        self.setGeometry(100,50,self.window_width,self.window_height)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self): 
        main_layout = QtWidgets.QHBoxLayout(self)
        self.graphic_scene = QtWidgets.QGraphicsScene(0,0,self.scene_width,self.scene_height)
        self.graphic_scene.setBackgroundBrush(QtGui.Qt.white)
        vert_lines = []
        for x in range(int((self.scene_width-self.offset*2)/self.grid_size)+1):
            vert_lines.append(QtCore.QLineF((x)*self.grid_size+self.offset,self.offset,(x)*self.grid_size+self.offset,self.scene_height-self.offset))
            
        hor_lines = []
        for y in range(int((self.scene_height-self.offset*2)/self.grid_size)+1):
            hor_lines.append(QtCore.QLineF(self.offset,(y)*self.grid_size+self.offset,self.scene_width-self.offset,(y)*self.grid_size+self.offset))
            
        for line in vert_lines:
            self.graphic_scene.addLine(line)
        for line in hor_lines:
            self.graphic_scene.addLine(line)
            
        rect = QtWidgets.QGraphicsRectItem(self.offset,self.offset,self.grid_size*10,self.grid_size)
        rect.setBrush(QtGui.QBrush(QtGui.Qt.red))
        self.graphic_scene.addItem(rect)
            
        self.graphics_view = QtWidgets.QGraphicsView(self.graphic_scene)
        self.graphics_view.show()
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