from PySide6 import QtWidgets, QtCore, QtGui, QtCharts
import os, sys
import sqlite3
import datetime

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
        main_layout = QtWidgets.QHBoxLayout(self)
        table_layout = QtWidgets.QVBoxLayout()
        self.box = QtWidgets.QComboBox(self)
        self.box.addItems(["ECN By Status","ECN By Author","ECN By Stage","ECN By Days","ECN By Months"])
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
       
        table_layout.addWidget(self.box)
        table_layout.addWidget(self.table)
        main_layout.addLayout(table_layout)
        main_layout.addWidget(self.chartview)
        
        self.showECNStatusDistribution()
        
    def setChartType(self):
        if self.box.currentText()=="ECN By Status":
            self.showECNStatusDistribution()
        if self.box.currentText()=="ECN By Author":
            self.showECNAuthorDistribution()
        if self.box.currentText()=="ECN By Stage":
            self.showECNStageDistribution()
        if self.box.currentText()=="ECN By Days":
            self.showECNDayDistribution()
        if self.box.currentText()=="ECN By Months":
            self.showECNMonthDistribution()
            
    def showECNMonthDistribution(self):
        months ={'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
        today = datetime.date.today()
        year = today.year
        years = []
        data_release = {}
        data_complete = {}
        duration = 5
        for x in range(duration):
            years.append(year-x)
        for year in years:
            for month in months.keys():
                date = f"{year}-{month}"
                # self.cursor.execute(f"select COUNT(ECN_ID) from ECN where STATUS!='Draft' and STATUS!='Completed' and FIRST_RELEASE like '{date}%'")
                # result = self.cursor.fetchone()
                # #print(date,result[0])
                # if year in data_release.keys():
                #     data_release[year].append((month,result[0]))
                # else:
                #     data_release[year]=[(month,result[0])]
                self.cursor.execute(f"select COUNT(ECN_ID) from ECN where STATUS='Completed' and COMP_DATE like '{date}%'")
                result = self.cursor.fetchone()
                #print(date,result[0])
                if year in data_complete.keys():
                    data_complete[year].append((month,result[0]))
                else:
                    data_complete[year]=[(month,result[0])]
        print(data_release,data_complete)
        
        categories = []
        for key in months.keys():
            categories.append(months[key])
        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(categories)
        
        chart = QtCharts.QChart()
        chart.setTitle("ECN By Month")
        chart.addAxis(axisX, QtCore.Qt.AlignBottom)
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        
        for year in years:
            print("release")
            # set0 =QtCharts.QBarSet('Release')
            # for item in data_release[year]:
            #     print(item)
            #     set0.append(item[1])
            print("completed")
            set0 =QtCharts.QBarSet(str(year))
            for item in data_complete[year]:
                print(item)
                set0.append(item[1])
            series = QtCharts.QBarSeries()
            series.append(set0)
            #series.append(set1)
            chart.addSeries(series)
            
        series.attachAxis(axisX)

        self.chartview.setChart(chart)
        
            
    def showECNDayDistribution(self):#strftime strptime
        days = []
        today = datetime.date.today()
        duration = 7
        release_counts = {}
        complete_counts = {}
        for x in range(duration):
            days.append(datetime.datetime.strftime(today-datetime.timedelta(days=x),'%Y-%m-%d'))
        days = sorted(days)
        for day in days:
            self.cursor.execute(f"select COUNT(ECN_ID) from ECN where date(FIRST_RELEASE) = '{day}'")
            result = self.cursor.fetchone()
            release_counts[day]=result[0]
            self.cursor.execute(f"select COUNT(ECN_ID) from ECN where date(COMP_DATE)='{day}'")
            result = self.cursor.fetchone()
            complete_counts[day]=result[0]
            
        row = 0 
        self.table.clearContents()
        self.table.setRowCount(row)
        self.table.setHorizontalHeaderLabels(['Date','Count'])
        for key in release_counts.keys():
            self.table.insertRow(row)
            label = QtWidgets.QTableWidgetItem(key)
            label.setTextAlignment(QtCore.Qt.AlignCenter)
            val = QtWidgets.QTableWidgetItem("R - " + str(release_counts[key]) + " : C- "+str(complete_counts[key]))
            val.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 0, label)
            self.table.setItem(row, 1, val)
            row+=1
            
        set0 = QtCharts.QBarSet("Released")
        for value in release_counts.values():
            set0.append(value)
        set1 = QtCharts.QBarSet("Completed")
        for value in complete_counts.values():
            set1.append(value)
        
        series = QtCharts.QBarSeries()
        series.append(set0)
        series.append(set1)
        series.setLabelsVisible(True)
        
        categories = []
        for key in release_counts.keys():
            categories.append(str(key))
        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(categories)
        
        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setTitle("ECN By Day")
        chart.addAxis(axisX, QtCore.Qt.AlignBottom)
        series.attachAxis(axisX)
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        
        self.chartview.setChart(chart)
            
            
    def showECNStageDistribution(self):
        stages = []
        current_stages = {}
        # self.cursor.execute("select DISTINCT(STAGE) from ECN where STATUS!='Completed' and STATUS!='Draft'")
        # results = self.cursor.fetchall()
        # for result in results:
        #     stages.append(result[0])
        for value in self.stageDict.values():
            stages.append(value)
        stages = sorted(set(stages))
        print(stages)
        for stage in stages:
            self.cursor.execute(f"select COUNT(ECN_ID) from ECN where STAGE='{stage}' and STATUS!='Completed' and STATUS!='Draft' and STATUS!='Canceled'")
            result = self.cursor.fetchone()
            current_stages[stage]=result[0]
        set0 = QtCharts.QBarSet("stage")
        for value in current_stages.values():
            set0.append(value)
        
        series = QtCharts.QBarSeries()
        series.append(set0)
        series.setLabelsVisible(True)
        
        # titles={}
        # for key,value in self.stageDict.items():
        #     titles[value]=key
        
        categories = []
        for key in current_stages.keys():
            categories.append(str(key))
        #print(categories)
        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(categories)
        
        row = 0 
        self.table.clearContents()
        self.table.setRowCount(row)
        self.table.setHorizontalHeaderLabels(['Job Title','Stage'])
        for key in self.stageDict.keys():
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
        self.table.setHorizontalHeaderLabels(['Author','Count'])
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
            series.append(key+"  :  "+str(round(((counts[key]/total)*100),2))+"%", counts[key])
        series.setLabelsVisible(True)
        
        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setTitle("ECN By Author")
        chart.legend().hide()
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        self.chartview.setChart(chart)
    
    
    def showECNStatusDistribution(self):
        counts = self.ECNDistribution()
        row = 0
        self.table.clearContents()
        self.table.setRowCount(row)
        self.table.setHorizontalHeaderLabels(['Status','Count'])
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
            if counts[key]>0:
                series.append(key+"  :  "+str(round(((counts[key]/total)*100),2))+"%", counts[key])
        series.setLabelsVisible(True)
        
        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setTitle("ECN Distribution")
        chart.legend().hide()
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
        self.cursor.execute("select COUNT(ECN_ID) from ecn where STATUS='Canceled'")
        result = self.cursor.fetchone()
        count_cl = result[0]
        return {"Out For Approval":count_OFA,"Rejected":count_RJ,"Completed":count_C,"Canceled":count_cl}
        

    def getStageDict(self):
        self.stageDict = {}
        stages = self.settings["Stage"].split(",")
        for stage in stages:
            key,value = stage.split("-")
            if key.strip()!="Admin":
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