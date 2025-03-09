import sys,os
from pathlib import Path
from PyQt6 import uic, QtCore, QtGui
from PyQt6.QtWidgets import QApplication,QMainWindow,QMessageBox

class Home(QMainWindow):
    def __init__(self,signal = None):
        super().__init__()
        os.chdir(Path(__file__).parent)
        self.signal = signal
        self.old_pos = None
        self.device = None
        
        if self.signal != None:
            self.signal.home.connect(self.open_home)
            
    def open_home(self,device, position=QtCore.QPoint(100,40), maximize=False, username=""):
        self.username = username
        self.device = device
        self.ui = uic.loadUi(f"../UI/{device}Home.ui",self)
        self.setWindowTitle("Home")
        self.setWindowIcon(QtGui.QIcon("./images/logo.png"))
        
        # Thiết lập giao diện
        self.connect_signals()
        self.configure_window(maximize, position)

    def connect_signals(self):
        """Kết nối các tín hiệu và slot"""
        self.ui.pushButton.clicked.connect(self.show_chat)
        self.ui.pushButton_2.clicked.connect(self.show_information)
                
    def configure_window(self, size, position):
        """Cấu hình cửa sổ"""
        is_mobile = self.device != "PC"
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, is_mobile)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, is_mobile)
        
        if size:
            self.showMaximized()
        else:
            self.move(position)
            self.resize(960, 540)
            self.show()
            
    def show_chat(self):
        self.close()
        self.signal.chat.emit(self.device, self.pos(), self.isMaximized(), self.username)
                
    def show_information(self):
        self.close()
        self.signal.information.emit(self.device, self.pos(), self.isMaximized(), self.username)
        
    def confirm_exit(self):
        reply = QMessageBox.question(
                self,'Exit','Are you sure you want to exit?',
                QMessageBox.StandardButton.Yes|
                QMessageBox.StandardButton.No,QMessageBox.StandardButton.No
            )
        return reply == QMessageBox.StandardButton.Yes
            
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            if self.confirm_exit():
                self.close()
            
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self,event): 
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.old_pos = None
            
    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            if self.windowState() == QtCore.Qt.WindowState.WindowNoState:
                self.resize(960,540)
                
        super().changeEvent(event)
           
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Home()
    window.show()
    app.exec()  