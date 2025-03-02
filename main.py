import sys,os
from pathlib import Path
from PyQt6 import QtCore,uic
from PyQt6.QtWidgets import QApplication,QWidget,QDialog

from src import welcome, login, signUp, chat, home, information

from src.server import ChatServer
from private import database

from pathlib import Path
os.chdir(Path(__file__).parent)

class Signal(QWidget):
    welcome = QtCore.pyqtSignal(str)
    login = QtCore.pyqtSignal(str, QtCore.QPoint, bool)
    signUp = QtCore.pyqtSignal(str, QtCore.QPoint, bool)
    chat = QtCore.pyqtSignal(str, QtCore.QPoint, bool, str)
    home = QtCore.pyqtSignal(str, QtCore.QPoint, bool, str)
    information = QtCore.pyqtSignal(str, QtCore.QPoint, bool, str)
    database = database.Database()
    messageReceive = QtCore.pyqtSignal(str)
    
class MainMobile(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./UI/Device_select.ui",self)
        self.setWindowTitle("Select your device")
        
        self.ui.pushButton.clicked.connect(self.open_main_mobile)
        self.ui.pushButton_2.clicked.connect(self.open_main_PC)
    
        self.signal = Signal()
        self.welcome = welcome.Welcome(self.signal)
        self.login = login.Login(self.signal)
        self.signUp = signUp.SignUp(self.signal)
        self.chat = chat.Chat(self.signal)
        self.home = home.Home(self.signal)
        self.information = information.Information(self.signal)
        
    def open_main_mobile(self):
        self.signal.welcome.emit("Mobile")
        
    def open_main_PC(self):
        self.signal.welcome.emit("PC")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMobile()
    window.show()
    
    def shutdown_server():
        server.stop()
        
    server = ChatServer()
    app.aboutToQuit.connect(shutdown_server)
    app.exec()
    
    #Helo