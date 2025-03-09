import sys,os
from pathlib import Path
from PyQt6 import uic, QtCore, QtGui
from PyQt6.QtWidgets import QApplication,QWidget,QLineEdit,QMainWindow,QMessageBox

class Login(QMainWindow):
    def __init__(self,signal = None):
        super().__init__()
        os.chdir(Path(__file__).parent)
        self.signal = signal
        self.old_pos = None
        self.device = None
        
        # Kết nối signal nếu có
        if self.signal != None:
            self.signal.login.connect(self.open_login)

    def open_login(self,device, position=QtCore.QPoint(100,40), maximize=False):
        self.device = device
        self.ui = uic.loadUi(f"../UI/{device}Login.ui",self)
        self.setWindowTitle("Log In")
        self.setWindowIcon(QtGui.QIcon("./images/logo.png"))
        
        # Thiết lập giao diện
        self.connect_signals()
        self.configure_window(maximize, position)
    
    def connect_signals(self):
        """Kết nối các tín hiệu và slot"""
        self.ui.pushButton.clicked.connect(self.check_login)
        self.ui.pushButton_2.clicked.connect(self.changeIcon)
        self.ui.pushButton_2.setCheckable(True)
        self.ui.pushButton_3.clicked.connect(self.changeIcon_2)
        self.ui.pushButton_3.setCheckable(True)
        self.ui.pushButton_4.clicked.connect(self.show_signUp)            
        self.init_lineedit_event()
        
    def init_lineedit_event(self):
        self.ui.lineEdit.installEventFilter(self)
        self.ui.lineEdit_2.installEventFilter(self)   
        
    def configure_window(self, size, position):
        """Cấu hình cửa sổ""" 
        is_mobile = self.device != "PC"
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, is_mobile)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, is_mobile)
        
        if size:
            self.showMaximized()
        else:
            self.move(position)
            self.resize(960,540)
            self.showNormal()   
    
    def check_login(self):
        username = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        if not username or not password:
            return self.show_message_box("Error nofitication","Username and password can't be empty",QMessageBox.Icon.Warning)
        if not self.signal.database.username_exists(username):
            return self.show_message_box("Error nofitication","Account is not exist",QMessageBox.Icon.Warning) 
        if not self.signal.database.check_password(username, password):
            return self.show_message_box("Error nofitication","Account is not exist",QMessageBox.Icon.Warning) 
        self.show_message_box("Nofitication","Account logged in successfully")     
        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()
        self.show_home(username)
        
    def changeIcon(self, checked):
        if checked:
            self.ui.pushButton_2.setIcon(QtGui.QIcon("../images/blind_795831.png"))
            self.ui.lineEdit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.ui.pushButton_2.setIcon(QtGui.QIcon("../images/eye_15632446.png"))
            self.ui.lineEdit.setEchoMode(QLineEdit.EchoMode.Password)
        
    def changeIcon_2(self,checked):
        if checked:
            self.ui.pushButton_3.setIcon(QtGui.QIcon("../images/blind_795831.png"))
            self.ui.lineEdit_2.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.ui.pushButton_3.setIcon(QtGui.QIcon("../images/eye_15632446.png"))
            self.ui.lineEdit_2.setEchoMode(QLineEdit.EchoMode.Password)
        
    def show_signUp(self):
        self.close()
        self.signal.signUp.emit(self.device, self.pos(), self.isMaximized())
    
    def show_home(self, username):
        self.close()
        self.signal.home.emit(self.device, self.pos(), self.isMaximized(), username)

    def eventFilter(self, obj, event):
        if isinstance(obj,QLineEdit):
            if event.type() == QtCore.QEvent.Type.FocusIn:
                parent_widget = obj.parent()
                if isinstance(parent_widget,QWidget):
                    parent_widget.setStyleSheet("""
                                                QWidget{
                                                    border-radius: 20px;
                                                    border: 1px solid blue;   
                                                }
                                                """)
            if event.type() == QtCore.QEvent.Type.FocusOut:
                parent_widget = obj.parent()
                if isinstance(parent_widget,QWidget):
                    parent_widget.setStyleSheet("""
                                                QWidget{
                                                    	border-radius: 20px;
	                                                    border: 1px solid black;
                                                }
                                                """)
                    
        return super().eventFilter(obj,event)
    
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
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.check_login()
            
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
    
    def show_message_box(self, title="Message Box", content="This is a message box", icon=QMessageBox.Icon.Information): 
        msg = QMessageBox() 
        msg.setIcon(icon) 
        msg.setText(content) 
        msg.setWindowTitle(title) 
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    app.exec()
    