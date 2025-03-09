import sys,os
from pathlib import Path
from PyQt6 import uic, QtCore, QtGui
from PyQt6.QtWidgets import QApplication,QMainWindow,QMessageBox

class Welcome(QMainWindow):
    def __init__(self,signal=None):
        super().__init__()
        os.chdir(Path(__file__).parent) #Xử lý vấn đề đường dẫn
        self.signal = signal
        self.old_pos = None
        self.device = None
        
        if self.signal != None:
            self.signal.welcome.connect(self.open_welcome)
            
    def open_welcome(self, device):
        self.device = device
        self.ui = uic.loadUi(f"../UI/{self.device}Welcome.ui",self)
        self.setWindowTitle(f"Welcome")
        self.setWindowIcon(QtGui.QIcon("./images/logo.png"))
        
        self.setup_ui()
        self.connect_signals()
        self.configure_window()
    
    def setup_ui(self):
        """Thiết lập các thành phần UI"""
        self.ui.label.setStyleSheet("""
                                    image: url(../images/logo.png);
                                    """)
        
    def connect_signals(self):
        """Kết nối các tín hiệu và slot"""
        self.ui.pushButton.clicked.connect(self.show_login)
        self.ui.pushButton_2.clicked.connect(self.show_signUp)
           
    def configure_window(self):
        """Cấu hình cửa sổ"""
        is_mobile = self.device != "PC"
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, is_mobile)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, is_mobile)
        
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
                
    def show_login(self):
        self.close()
        self.signal.login.emit(self.device, self.pos(), self.isMaximized())
        
    def show_signUp(self):
        self.close()
        self.signal.signUp.emit(self.device, self.pos(), self.isMaximized())
    
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
        if event.key() == QtCore.Qt.Key.Key_Enter or event.key() == QtCore.Qt.Key.Key_Return:
            self.show_login()
            
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
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Welcome()
    window.show()
    app.exec()
    