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
        self.window_height = 600
        self.window_width = 1000
        self.initAtt()
        self.initUI()
        self.show()

    def initAtt(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self): 
        main_layout = QtWidgets.QHBoxLayout(self)
        self.graphic_scene = QtWidgets.QGraphicsScene(0,0,self.window_width,self.window_height)
        self.graphic_scene.setBackgroundBrush(QtGui.Qt.white)
        vert_lines = []
        grid_size = 20
        for x in range(int(self.window_width/grid_size)):
            vert_lines.append(QtCore.QLineF((x+1)*grid_size,0,(x+1)*grid_size,self.window_height))
            
        hor_lines = []
        for y in range(int(self.window_height/grid_size)):
            hor_lines.append(QtCore.QLineF(0,(y+1)*grid_size,self.window_width,(y+1)*grid_size))
            
        for line in vert_lines:
            self.graphic_scene.addLine(line)
        for line in hor_lines:
            self.graphic_scene.addLine(line)
            
        self.graphics_view = QtWidgets.QGraphicsView(self.graphic_scene)
        self.graphics_view.show()
        main_layout.addWidget(self.graphics_view)
    
    
# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    timeline = ProjectTimeline()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()