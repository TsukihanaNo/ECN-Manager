from PySide6 import QtWidgets, QtCore, QtGui, QtCharts
import os, sys
import sqlite3  

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

#db_loc = os.path.join(program_location, "DB", "Request_DB.db")
initfile = os.path.join(program_location, "setting.ini")

class AnalyticsWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(AnalyticsWindow,self).__init__()
        self.windowWidth = 1200
        self.windowHeight = 700
        if parent is None:
            print("geting stuff")
            f = open(initfile,'r')
            self.settings = {}
            for line in f:
                key,value = line.split(" : ")
                self.settings[key]=value.strip()
            print(self.settings)
            f.close()
            self.db = sqlite3.connect(self.settings["DB_LOC"])
            self.cursor = self.db.cursor()
            self.cursor.row_factory = sqlite3.Row
        else:
            self.parent = parent
            self.settings = parent.settings
            self.db = self.parent.db
            self.cursor = self.parent.cursor
        #self.getStageDict()
        self.initAtt()
        self.initUI()
        self.show()

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


    def initAtt(self):
        self.setGeometry(100,50,self.windowWidth,self.windowHeight)
        title = "Analytics Window"
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.center()
        self.getStageDict()
        
        

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        data_layout = QtWidgets.QHBoxLayout()
        self.box = QtWidgets.QComboBox(self)
        self.box.addItems(["ECN Distribution","ECN By Author","ECN By Stage"])
        self.box.currentIndexChanged.connect(self.setChartType)
        
        titles = ['Label','Value']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  
        self.table.setFixedWidth(300)        
        
        
        self.chartview = QtCharts.QChartView()
        self.chartview.setRenderHint(QtGui.QPainter.Antialiasing)
        
        data_layout.addWidget(self.table)
        data_layout.addWidget(self.chartview)
        main_layout.addWidget(self.box)
        main_layout.addLayout(data_layout)
        
        self.showECNDistribution()
        
    def setChartType(self):
        if self.box.currentText()=="ECN Distribution":
            self.showECNDistribution()
        if self.box.currentText()=="ECN By Author":
            self.showECNAuthorDistribution()
        if self.box.currentText()=="ECN By Stage":
            self.showECNStageDistribution()
            
    def showECNStageDistribution(self):
        stages = []
        current_stages = {}
        self.cursor.execute("select DISTINCT(STAGE) from ECN where STATUS!='Completed' and STATUS!='Draft'")
        results = self.cursor.fetchall()
        for result in results:
            stages.append(result[0])
        stages = sorted(stages)
        for stage in stages:
            self.cursor.execute(f"select COUNT(ECN_ID) from ECN where STAGE='{stage}' and STATUS!='Completed'")
            result = self.cursor.fetchone()
            current_stages[stage]=result[0]
        set0 = QtCharts.QBarSet("stage")
        for value in current_stages.values():
            set0.append(value)
        
        series = QtCharts.QBarSeries()
        series.append(set0)
        series.setLabelsVisible(True)
        
        categories = []
        for key in current_stages.keys():
            categories.append(str(key))
        print(categories)
        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(categories)
        
        row = 0 
        self.table.clearContents()
        self.table.setRowCount(row)
        for key in self.stageDict.keys():
            if key!="Admin":
                self.table.insertRow(row)
                label = QtWidgets.QTableWidgetItem(key)
                label.setTextAlignment(QtCore.Qt.AlignCenter)
                val = QtWidgets.QTableWidgetItem(str(self.stageDict[key]))
                val.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row, 0, label)
                self.table.setItem(row, 1, val)
                row+=1
        
        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setTitle("ECN By Stage")
        chart.addAxis(axisX, QtCore.Qt.AlignBottom)
        series.attachAxis(axisX)
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        
        self.chartview.setChart(chart)
            
    def showECNAuthorDistribution(self):
        self.cursor.execute("Select DISTINCT(AUTHOR) from ECN")
        results = self.cursor.fetchall()
        authors = []
        for result in results:
            authors.append(result[0])
        counts = {}
        for author in authors:
            self.cursor.execute(f"select COUNT(ECN_ID) from ECN where AUTHOR='{author}' and STATUS!='Draft'")
            result = self.cursor.fetchone()
            counts[author]=result[0]
        row = 0 
        self.table.clearContents()
        self.table.setRowCount(row)
        total = sum(counts.values())
        for key in counts.keys():
            self.table.insertRow(row)
            label = QtWidgets.QTableWidgetItem(key)
            label.setTextAlignment(QtCore.Qt.AlignCenter)
            val = QtWidgets.QTableWidgetItem(str(counts[key])+"  :  "+str(round(((counts[key]/total)*100),2))+"%")
            val.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 0, label)
            self.table.setItem(row, 1, val)
            row+=1
            
        self.table.sortItems(1,QtCore.Qt.DescendingOrder)


        series = QtCharts.QPieSeries()
        for key in counts.keys():
            series.append(key, counts[key])
        series.setLabelsVisible(True)
        
        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setTitle("ECN By Author")
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        self.chartview.setChart(chart)
    
    
    def showECNDistribution(self):
        counts = self.ECNDistribution()
        row = 0
        self.table.clearContents()
        self.table.setRowCount(row)
        total = sum(counts.values())
        for key in counts.keys():
            self.table.insertRow(row)
            label = QtWidgets.QTableWidgetItem(key)
            label.setTextAlignment(QtCore.Qt.AlignCenter)
            val = QtWidgets.QTableWidgetItem(str(counts[key])+"  :  "+str(round(((counts[key]/total)*100),2))+"%")
            val.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 0, label)
            self.table.setItem(row, 1, val)
            row+=1
        
        self.table.sortItems(1,QtCore.Qt.DescendingOrder)

        series = QtCharts.QPieSeries()
        for key in counts.keys():
            series.append(key, counts[key])
        series.setLabelsVisible(True)
        
        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setTitle("ECN Distribution")
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        self.chartview.setChart(chart)
        
        
    def ECNDistribution(self):
        self.cursor.execute("select COUNT(STATUS) from ECN")
        result = self.cursor.fetchone()
        total = result[0]
        self.cursor.execute("select COUNT(ECN_ID) from ECN where STATUS='Rejected'")
        result = self.cursor.fetchone()
        count_RJ = result[0]
        self.cursor.execute("select COUNT(ECN_ID) from ECN where STATUS='Out For Approval'")
        result = self.cursor.fetchone()
        count_OFA = result[0]
        self.cursor.execute("select COUNT(ECN_ID) from ECN where STATUS='Completed'")
        result = self.cursor.fetchone()
        count_C = result[0]
        return {"Out For Approval":count_OFA,"Rejected":count_RJ,"Completed":count_C}
        

    def getStageDict(self):
        self.stageDict = {}
        stages = self.settings["Stage"].split(",")
        for stage in stages:
            key,value = stage.split("-")
            self.stageDict[key.strip()] = value.strip()

    def dispMsg(self,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg+"        ")
        msgbox.exec()

# execute the program
def main():
    app = QtWidgets.QApplication(sys.argv)
    analytics =AnalyticsWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
