from PySide6 import QtWidgets, QtCore, QtGui, QtCharts
import os, sys
import sqlite3
from datetime import datetime, date, timedelta
from SearchResults import *

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
        self.windowWidth = 1000
        self.windowHeight = 600
        self.titleStageDict = parent.titleStageDict
        self.stageDict = parent.stageDict
        #print(self.titleStageDict)
        if parent is None:
            #print("geting stuff")
            f = open(initfile,'r')
            self.settings = {}
            for line in f:
                key,value = line.split(" : ")
                self.settings[key]=value.strip()
            #print(self.settings)
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
        self.box.addItems(["ECN By Status","ECN By Author","ECN By Stage","ECN By Days","ECN By Months","ECN Waiting On User"])
        self.box.currentIndexChanged.connect(self.setChartType)
        
        titles = ['Label','Value']
        self.table = QtWidgets.QTableWidget(0,len(titles),self)
        self.table.setHorizontalHeaderLabels(titles)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.launchSearch)

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
        if self.box.currentText()=="ECN Waiting On User":
            self.showECNWaitUserDistribution()
            
    def launchSearch(self):
        if self.box.currentText()=="ECN Waiting On User":
            row = self.table.currentRow()
            user = self.table.item(row, 0).text()
            matches = []
            self.cursor.execute(f"select JOB_TITLE from USER where USER_ID='{user}'")
            result = self.cursor.fetchone()
            title = result[0]
            command = f"Select SIGNATURE.ECN_ID from SIGNATURE INNER JOIN ECN ON SIGNATURE.ECN_ID=ECN.ECN_ID WHERE ECN.STATUS='Out For Approval' and SIGNATURE.USER_ID='{user}' and SIGNATURE.SIGNED_DATE is NULL and SIGNATURE.TYPE='Signing' and ECN.STAGE='{self.stageDict[title]}'"
            #self.cursor.execute(f"select ECN_ID from SIGNATURE where USER_ID='{user}' and TYPE='Signing' and SIGNED_DATE is Null")
            self.cursor.execute(command)
            results = self.cursor.fetchall()
            for result in results:
                matches.append(result[0])
            self.parent.searchResult = SearchResults(self.parent,matches)
        
    def showECNWaitUserDistribution(self):
        users = {}
        self.cursor.execute("Select DISTINCT(SIGNATURE.USER_ID) from SIGNATURE INNER JOIN ECN ON SIGNATURE.ECN_ID=ECN.ECN_ID where SIGNATURE.TYPE='Signing' and SIGNATURE.SIGNED_DATE is Null and ECN.STATUS='Out For Approval'")
        results = self.cursor.fetchall()
        for result in results:
            users[result[0]]=0
        remove_key = []
        for key in users.keys():
            self.cursor.execute(f"select JOB_TITLE from USER where USER_ID='{key}'")
            result = self.cursor.fetchone()
            title = result[0]
            command = f"Select COUNT(SIGNATURE.ECN_ID) from SIGNATURE INNER JOIN ECN ON SIGNATURE.ECN_ID=ECN.ECN_ID WHERE ECN.STATUS='Out For Approval' and SIGNATURE.USER_ID='{key}' and SIGNATURE.SIGNED_DATE is NULL and SIGNATURE.TYPE='Signing' and ECN.STAGE='{self.stageDict[title]}'"
            self.cursor.execute(command)
            #self.cursor.execute(f"Select COUNT(ECN_ID) from SIGNATURE where TYPE='Signing' and SIGNED_DATE is Null and USER_ID='{key}'")
            result = self.cursor.fetchone()
            if result[0]==0:
                remove_key.append(key)
            else:
                users[key]=result[0]
        
        for item in remove_key:
            del users[item]

        
        set0 = QtCharts.QBarSet("ECN Count")
        for value in users.values():
            set0.append(value)
        
        series = QtCharts.QBarSeries()
        series.append(set0)
        series.setLabelsVisible(True)
        
        # titles={}
        # for key,value in self.stageDict.items():
        #     titles[value]=key
        
        categories = []
        for key in users.keys():
            categories.append(key)
        #print(categories)
        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(categories)
        
        row = 0 
        self.table.clearContents()
        self.table.setRowCount(row)
        self.table.setHorizontalHeaderLabels(['User','Count'])
        for key in users.keys():
            self.table.insertRow(row)
            label = QtWidgets.QTableWidgetItem(key)
            label.setTextAlignment(QtCore.Qt.AlignCenter)
            val = QtWidgets.QTableWidgetItem(str(users[key]))
            val.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 0, label)
            self.table.setItem(row, 1, val)
            row+=1
        
        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setTitle("ECNs Waiting On User")
        chart.addAxis(axisX, QtCore.Qt.AlignBottom)
        series.attachAxis(axisX)
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        
        self.chartview.setChart(chart)
            
    def showECNMonthDistribution(self):
        months ={'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
        today = date.today()
        year = today.year
        years = []
        data_release = {}
        data_complete = {}
        duration = 5
        for x in range(duration):
            years.append(year-x)
        for year in years:
            for month in months.keys():
                check_date = f"{year}-{month}"
                self.cursor.execute(f"select COUNT(ECN_ID) from ECN where STATUS!='Draft' and STATUS!='Completed' and FIRST_RELEASE like '{check_date}%'")
                result = self.cursor.fetchone()
                #print(date,result[0])
                if year in data_release.keys():
                    data_release[year].append((month,result[0]))
                else:
                    data_release[year]=[(month,result[0])]
                self.cursor.execute(f"select COUNT(ECN_ID) from ECN where STATUS='Completed' and COMP_DATE like '{check_date}%'")
                result = self.cursor.fetchone()
                #print(date,result[0])
                if year in data_complete.keys():
                    data_complete[year].append((month,result[0]))
                else:
                    data_complete[year]=[(month,result[0])]
        #rint(data_release,data_complete)
        
        categories = []
        for key in months.keys():
            categories.append(months[key])
        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(categories)
        
        chart = QtCharts.QChart()
        chart.setTitle("ECN By Month")
        chart.addAxis(axisX, QtCore.Qt.AlignBottom)
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        
        row = 0
        
        self.table.clearContents()
        self.table.setRowCount(row)
        self.table.setHorizontalHeaderLabels(['Year/Month','Count'])
        for year in sorted(years):
            month_count = 0
            for item in data_release[year]:
                self.table.insertRow(row)
                label = QtWidgets.QTableWidgetItem(str(year)+"/"+str(item[0]))
                label.setTextAlignment(QtCore.Qt.AlignCenter)
                val = QtWidgets.QTableWidgetItem("R - " + str(data_release[year][month_count][1]) + " :  C - " + str(data_complete[year][month_count][1]))
                val.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row, 0, label)
                self.table.setItem(row, 1, val)
                row+=1
                month_count+=1
            
        
        for year in years:
            #print("release")
            set0 =QtCharts.QBarSet('Release')
            for item in data_release[year]:
                #print(item)
                set0.append(item[1])
            #print("completed")
            set1 =QtCharts.QBarSet(str(year))
            for item in data_complete[year]:
                #print(item)
                set1.append(item[1])
            series = QtCharts.QBarSeries()
            series.append(set0)
            series.append(set1)
            chart.addSeries(series)
            
        series.attachAxis(axisX)

        self.chartview.setChart(chart)
        
            
    def showECNDayDistribution(self):#strftime strptime
        days = []
        today = date.today()
        duration = 7
        release_counts = {}
        complete_counts = {}
        for x in range(duration):
            days.append(datetime.strftime(today-timedelta(days=x),'%Y-%m-%d'))
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
        #print(stages)
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
