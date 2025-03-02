import sys,os
import socket,threading
from pathlib import Path
from PyQt6 import uic, QtCore, QtGui
from PyQt6.QtWidgets import QApplication,QLabel,QVBoxLayout,QMainWindow,QMessageBox

class Chat(QMainWindow):
    def __init__(self,signal = None):
        super().__init__()
        os.chdir(Path(__file__).parent)
        self.signal = signal
        if self.signal != None:
            self.signal.chat.connect(self.open_chat)
        else:
            self.open_chat("Mobile")

    def open_chat(self,device, position=QtCore.QPoint(100,40), size=False, username=""):
        self.userdata = self.signal.database.get_data(username)
        self.device = device
        self.ui = uic.loadUi(f"../UI/{device}Chat.ui",self)
        self.scroll_layout = QVBoxLayout(self.ui.scrollcontent)
        self.scroll_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.connect_client()
        self.signal.messageReceive.connect(self.sendUI)
        self.ui.pushButton.clicked.connect(self.sendMessage)
        if self.userdata["name"]:
            self.ui.label.setText(self.userdata["name"])
        else:
            self.ui.label.setText(self.userdata["username"])
        
        self.ui.pushButton_7.clicked.connect(self.show_home)
        if self.device == "PC":
            self.ui.pushButton_5.clicked.connect(self.toggle_right_panel)
            self.ui.pushButton_3.clicked.connect(self.show_information)
            if self.userdata["name"]:
                self.ui.label_2.setText(self.userdata["name"])
            else:
                self.ui.label_2.setText(self.userdata["username"])
            self.ui.label_3.setText(f"@{self.userdata["username"]}")
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint,device!="PC")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground,device!="PC")
        if size:
            self.showMaximized()
        else:
            self.move(position)
            self.resize(960,540)
            self.show()
    
    def show_home(self):
        self.close()
        self.signal.home.emit(self.device, self.pos(), self.isMaximized(), self.userdata["username"])
        
    def show_information(self):
        self.close()
        self.signal.information.emit(self.device, self.pos(), self.isMaximized(), self.userdata["username"])
        
    def connect_client(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            serverIP = ip
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((serverIP, 12345))
            print(f"✅ Connect to {serverIP} successfully!\n")

            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            print("Error! Can't connect to server")
            
    def receive_messages(self):
        """ Nhận tin nhắn từ server """
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                self.signal.messageReceive.emit(message)
            except:
                print("❌ Disconnect to server!\n")
                break
            
    def sendUI(self,message):
        message_label = QLabel(message,self)
        message_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignJustify)
        message_label.setStyleSheet("""
            padding: 5px;
            border-radius: 10px;
            border-bottom-left-radius: 2px;
            font-size: 14px;
            border: 1px solid lightgray;
            margin-right: 60px;
            color: black;
            background-color:white;
        """)
        if self.device == "PC":
            message_label.setStyleSheet("""
                padding: 5px;
                border-radius: 10px;
                border-bottom-left-radius: 2px;
                font-size: 14px;
                border: 1px solid lightgray;
                margin-right: 400px;
                color: black;
                background-color:white;
            """)
        message_label.setWordWrap(True)
        message_label.adjustSize()
        self.scroll_layout.addWidget(message_label)
        
    def sendMessage(self):
        message = self.ui.textEdit.toPlainText().strip()
        if not message:
            return
        if self.client_socket:
            try:
                self.client_socket.send(message.encode())
                message_label = QLabel(message,self)
                message_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignJustify)
                message_label.setStyleSheet("""
                    padding: 5px;
                    border-radius: 10px;
                    border-bottom-right-radius: 2px;
                    font-size: 14px;
                    border: 1px solid lightgray;
                    margin-left: 60px;
                    color: rgb(255, 255, 255);
                    background-color:#55aaff;
                """)
                if self.device == "PC":
                    message_label.setStyleSheet("""
                        padding: 5px;
                        border-radius: 10px;
                        border-bottom-right-radius: 2px;
                        font-size: 14px;
                        border: 1px solid lightgray;
                        margin-left: 400px;
                        color: rgb(255, 255, 255);
                        background-color:#55aaff;
                    """)
                message_label.setWordWrap(True)
                message_label.adjustSize()
                self.scroll_layout.addWidget(message_label)
            except:
                print("⚠️ Can't send message.")
        else:
            print("Error! You didn't connect to server!")
            
        self.ui.textEdit.clear()
    
    def toggle_right_panel(self):
        self.ui.widget_4.setVisible(not self.ui.widget_4.isVisible())
        
    def close_Application(self):
        reply = QMessageBox.question(
                self,'Exit','Are you sure you want to exit?',
                QMessageBox.StandardButton.Yes|
                QMessageBox.StandardButton.No,QMessageBox.StandardButton.No
            )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            self.client_socket.close()
            
    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            if self.windowState() == QtCore.Qt.WindowState.WindowNoState:
                self.resize(960,540)
                
        super().changeEvent(event)
    
    def closeEvent(self, event):
        self.client_socket.close()

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
    window = Chat()
    window.show()
    app.exec()  