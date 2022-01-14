from PySide6 import QtGui, QtCore
from multiprocessing.connection import Listener

class Hook(QtCore.QObject):
    launch = QtCore.Signal(str)
    def __init__(self):
        super(Hook, self).__init__()
        self.address = ('localhost',6000)
        self.running = True
        self.listener = Listener(self.address,authkey=b'secret password')
        
    def run(self):
        while self.running:
            print("starting hook")
            conn = self.listener.accept()
            print('connection accepted from', self.listener.last_accepted)
            msg = conn.recv()
            # do something with msg
            #print(msg)
            if msg !='close':
                self.launch.emit(msg)
            if msg == 'close':
                conn.close()
