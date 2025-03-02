import sys,os
from pathlib import Path
from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QApplication,QMainWindow,QMessageBox

class Welcome(QMainWindow):
    def __init__(self,signal=None):
        super().__init__()
        os.chdir(Path(__file__).parent) #Xử lý vấn đề đường dẫn
        self.signal = signal
        self.old_pos = None
        
        if self.signal != None:
            self.signal.welcome.connect(self.open_welcome)
        else:
            self.open_welcome("Mobile")
            
    def open_welcome(self, device):
        self.device = device
        self.ui = uic.loadUi(f"../UI/{self.device}Welcome.ui",self)
        self.setWindowTitle(f"{self.device} mode")
        
        self.ui.pushButton.clicked.connect(self.show_login)
        self.ui.pushButton_2.clicked.connect(self.show_signUp)
        
        if self.device == "PC":
            width_min,height_min = 960,540
            width_max,height_max = 16777215,16777215
            self.showNormal()
            self.move(100,40)
        else:
            width_min,height_min = 300,600
            width_max,height_max = 300,600
            self.showNormal()
            self.move(100,40)
            
        self.setMinimumSize(width_min,height_min)
        self.setMaximumSize(width_max,height_max)
        
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint,self.device!="PC")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground,self.device!="PC")
            
        self.ui.label.setStyleSheet("""
                                    image: url(../images/logo.png);
                                    """)
        self.show()
    
    def show_login(self):
        self.close()
        self.signal.login.emit(self.device, self.pos(), self.isMaximized())
        
    def show_signUp(self):
        self.close()
        self.signal.signUp.emit(self.device, self.pos(), self.isMaximized())
    
    def close_Application(self):
        reply = QMessageBox.question(
                self,'Exit','Are you sure you want to exit?',
                QMessageBox.StandardButton.Yes|
                QMessageBox.StandardButton.No,QMessageBox.StandardButton.No
            )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close_Application()
            
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self,event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint()-self.old_pos
            self.move(self.pos()+delta)
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
       if event.button() == QtCore.Qt.MouseButton.LeftButton:
           self.old_pos = None
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Welcome()
    window.show()
    app.exec()
    