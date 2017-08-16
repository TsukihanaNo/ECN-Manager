from PySide import QtGui, QtCore

class SlidingStackedWidget(QtGui.QStackedWidget):
    def __init__(self, parent = None):
        super(SlidingStackedWidget,self).__init__()
        self.parent = parent
        self.animationstyle = QtCore.QEasingCurve.OutBack
        self.vertical = False
        self.wrap = True
        self.speed = 500
        self.active = False
        self.now = 0
        self.next = 0
        self.pnow = QtCore.QPoint(0,0)

    def setWraP(self,wrap):
    	self.wrap = wrap

    def setAnimationstyle(self,animationstyle):
        self.animationstyle = animationstyle

    def setSpeed(self,speed):
        self.speed = speed

    def slideInIndex(self,index):
        #print(index,self.count())
        # if index>self.count()-1:
        #     if self.vertical:
        #         direction = "top2bottom"
        #     else:
        #         direction = "right2left"
        #     index = index%self.count()
        # elif index >= 0:
        #     if self.vertical:
        #         direction = "bottom2top"
        #     else:
        #         direction = "left2right"
        #     index = (index+self.count())%self.count()
        #print(direction)
        direction = "left2right"
        self.slideInWidget(index,direction)

    def slideInWidget(self,index,direction):
        if self.active:
            return
        else:
            self.active = True

        index_now = self.currentIndex()
        index_next = index
        if index_now==index_next:
            self.active = False
            return;

        offsetx = self.frameRect().width()
        offsety = self.frameRect().height()

        self.widget(index_next).setGeometry(0,0,offsetx,offsety)

        if direction == "bottom2top":
            offsetx=0
            offsety=-offsety
        elif direction == "top2bottom":
            offsetx=0
            #offsety remains the same
        elif direction == "right2left":
            offsetx=-offsetx
            offsety=0
        elif direction == "left2right":
            #offsetx remains the same
            offsety=0

        pnext = QtCore.QPoint(self.widget(index_next).pos())
        pnow = QtCore.QPoint(self.widget(index_now).pos())
        self.pnow = pnow

        self.widget(index_next).move(pnext.x()-offsetx, pnext.y()-offsety)
        self.widget(index_next).show()
        self.widget(index_next).raise_()

        self.animate_now = QtCore.QPropertyAnimation(self.widget(index_now),"pos")
        self.animate_now.setDuration(self.speed)
        self.animate_now.setEasingCurve(self.animationstyle)
        self.animate_now.setStartValue(QtCore.QPoint(pnow.x(),pnow.y()))
        self.animate_now.setEndValue(QtCore.QPoint(pnow.x()+offsetx,pnow.y()+offsety))

        self.animate_next = QtCore.QPropertyAnimation(self.widget(index_next),"pos")
        self.animate_next.setDuration(self.speed)
        self.animate_next.setEasingCurve(self.animationstyle)
        self.animate_next.setStartValue(QtCore.QPoint(pnext.x()-offsetx,pnext.y()+offsety))
        self.animate_next.setEndValue(QtCore.QPoint(pnext.x(),pnext.y()))

        self.parallelanimation = QtCore.QParallelAnimationGroup(self)
        self.parallelanimation.addAnimation(self.animate_now)
        self.parallelanimation.addAnimation(self.animate_next)

        self.next = index_next
        self.now = index_now
        self.active = True

        self.parallelanimation.finished.connect(self.animationDone)

        self.parallelanimation.start()

    def animationDone(self):
    	self.setCurrentIndex(self.next)
    	self.widget(self.now).hide()
    	self.widget(self.now).move(self.pnow)
    	self.active = False

    def slideInNext(self):
    	now = self.currentIndex()
    	if (self.wrap) and (now<self.count()-1):
    		self.slideInIndex(now+1)

    def slideInPrev(self):
    	now = self.currentIndex()
    	if (self.wrap) and (now>0):
    		self.slideInIndex(now-1)


    # def animate(self):
    #     self.offsetx = self.frameRect().width()
    #     self.offsety = self.frameRect().height()
    #     self.pnow = self.widget(self.currentIndex()).pos()
    #     self.widgetnow = self.widget(self.currentIndex())

    #     if self.currentIndex()==self.count()-1:
    #         self.pnext = self.widget(0).pos()
    #         self.widgetnext = self.widget(0)
    #     else:
    #         self.pnext = self.widget(self.currentIndex()+1).pos()
    #         self.widgetnext = self.widget(self.currentIndex()+1)

    #     self.widgetnext.setGeometry(0,0,self.offsetx,self.offsety)
    #     self.widgetnext.move(self.pnext.x()-self.offsetx,self.pnext.y()-self.offsety)

    #     self.widgetnext.show()


    #     self.animate_now = QtCore.QPropertyAnimation(self.widgetnow,"pos")
    #     self.animate_now.setDuration(self.speed)
    #     self.animate_now.setEasingCurve(self.animationstyle)
    #     self.animate_now.setStartValue(QtCore.QPoint(self.pnow.x(),self.pnow.y()))
    #     self.animate_now.setEndValue(QtCore.QPoint(self.pnow.x()+self.offsetx,self.pnow.y()))

    #     self.animate_next = QtCore.QPropertyAnimation(self.widgetnext,"pos")
    #     self.animate_next.setDuration(self.speed)
    #     self.animate_next.setEasingCurve(self.animationstyle)
    #     self.animate_next.setStartValue(QtCore.QPoint(self.pnext.x()-self.offsetx,self.pnext.y()))
    #     self.animate_next.setEndValue(QtCore.QPoint(0,0))

    #     self.parallelanimation = QtCore.QParallelAnimationGroup(self)
    #     self.parallelanimation.addAnimation(self.animate_now)
    #     self.parallelanimation.addAnimation(self.animate_next)

    #     self.parallelanimation.start()

    #     self.parallelanimation.finished.connect(self.changePage)

    # def changePage(self):
    #     print('changing index')
    #     page = self.parent.pagecombobox.currentIndex()
    #     print(page)
    #     self.widgetnow.hide()
    #     self.widgetnow.move(self.pnow.x(),self.pnow.y())
    #     self.widgetnow.update()
    #     self.setCurrentIndex(page)
    #     print(self.currentIndex())