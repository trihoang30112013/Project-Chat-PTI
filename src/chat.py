import sys,os,json
import socket,threading
from pathlib import Path
from PyQt6 import uic, QtCore, QtGui
from PyQt6.QtWidgets import QApplication,QLabel,QWidget,QVBoxLayout,QHBoxLayout,QMainWindow,QMessageBox

class Chat(QMainWindow):
    def __init__(self,signal = None):
        super().__init__()
        os.chdir(Path(__file__).parent)
        self.signal = signal
        self.client_socket = None
        self.old_pos = None
        self.device = None
        self.userdata = {}
        
        # Kết nối signal nếu có
        if self.signal:
            self.signal.chat.connect(self.open_chat)

    def open_chat(self,device, position=QtCore.QPoint(100,40), maximize=False, username=""):
        self.userdata = self.signal.database.get_data(username)
        self.device = device
        self.ui = uic.loadUi(f"../UI/{device}Chat.ui",self)
        self.setWindowTitle("Chat")
        self.setWindowIcon(QtGui.QIcon("./images/logo.png"))
                
        # Thiết lập giao diện
        self.setup_ui()
        self.connect_signals()
        self.configure_window(maximize, position)
        self.connect_to_server()
    
    def setup_ui(self):
        """Thiết lập các thành phần UI"""
        display_name = self.userdata.get("name") or self.userdata.get("username", "Unknown")
        self.ui.label.setText(display_name)
        
        # Cấu hình scroll area
        self.scroll_layout = QVBoxLayout(self.ui.scrollcontent)
        self.scroll_layout.setSpacing(5)
        self.scroll_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        
        if self.device == "PC":
            self.user_list_layout = QVBoxLayout(self.ui.scrollaccount)
            self.user_list_layout.setSpacing(5)
            self.user_list_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
            
            self.ui.label_2.setText(display_name)
            self.ui.label_3.setText(f"@{self.userdata.get('username', '')}")
            
    def connect_signals(self):
        """Kết nối các tín hiệu và slot"""
        self.ui.pushButton.clicked.connect(self.send_message)
        self.ui.pushButton_7.clicked.connect(self.show_home)
        self.signal.messageReceive.connect(self.display_message)
        self.signal.userListReceived.connect(self.update_user_list)
        
        if self.device == "PC":
            self.ui.pushButton_5.clicked.connect(self.toggle_right_panel)
            self.ui.pushButton_3.clicked.connect(self.show_information)
        
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
    
    def connect_to_server(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                server_ip = s.getsockname()[0]
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, 12345))
            # Gửi thông tin người dùng dạng JSON
            user_data = {
                "username": self.userdata.get("username", "Unknown"),
                "name": self.userdata.get("name", "Unknown")
            }
            self.client_socket.send(json.dumps(user_data).encode('utf-8'))
            print(f"✅ Sent user data: {user_data}")
            print(f"✅ Connected to {server_ip}:12345 successfully!\n")
            
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            print(f"❌ Error connecting to server: {e}")
            
    def receive_messages(self):
        """ Nhận tin nhắn từ server """
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                if message.startswith("USERS:"):
                    users_json = message.replace("USERS:", "")
                    users = json.loads(users_json)
                    self.signal.userListReceived.emit(users)
                else:
                    self.signal.messageReceive.emit(message)
            except Exception:
                print("❌ Disconnected from server!\n")
                break
    
    def update_user_list(self, users):
        """Cập nhật danh sách người dùng trong panel bên phải."""
        if self.device != "PC":
            return  # Chỉ hiển thị trên PC
        
        # Xóa danh sách cũ
        for i in reversed(range(self.user_list_layout.count())):
            self.user_list_layout.itemAt(i).widget().setParent(None)
        
        # Lấy username của bản thân
        my_name = self.userdata.get("name") or self.userdata.get("username", "Unknown")
    
        # Thêm danh sách người dùng mới
        for user in users:
            user_name = user.get("name", "Unknown")  # Lấy "name" từ dictionary
            if user_name and user_name != my_name:  # Không hiển thị bản thân
                container_widget = QWidget()
                h_layout = QHBoxLayout(container_widget)
                h_layout.setContentsMargins(0, 0, 0, 0)
                h_layout.setSpacing(5)
                
                avatar_label = QLabel()
                placeholder_pixmap = QtGui.QPixmap("../images/assistant-512.png")
                avatar_label.setPixmap(placeholder_pixmap.scaled(48, 48, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
                avatar_label.setFixedSize(48, 48)
                avatar_label.setScaledContents(False)
                
                name_label = QLabel(user_name)
                name_label.setStyleSheet("""
                    padding: 5px;
                    font-size: 14px;
                    color: black;
                    background-color: #f0f0f0;
                    border-radius: 5px;
                """)
                
                h_layout.addWidget(avatar_label)
                h_layout.addWidget(name_label)
                h_layout.addStretch()
                
                self.user_list_layout.addWidget(container_widget)
                        
    def create_message(self, message, is_sent=False):
        """Tạo label với chiều rộng bằng độ dài văn bản."""

        container_widget = QWidget()

        label = QLabel(message, container_widget)
        label.setWordWrap(True)  # Cho phép xuống dòng nếu văn bản quá dài

        # Tính kích thước văn bản dựa trên font
        font_metrics = QtGui.QFontMetrics(label.font())
        text_width = font_metrics.horizontalAdvance(message) + 20  # Thêm padding 10px mỗi bên
        max_width = 400 if self.device == "PC" else 200  # Giới hạn chiều rộng tối đa
        
        # Đảm bảo chiều rộng không vượt quá max_width
        label.setMaximumWidth(min(text_width, max_width))
        label.setMinimumWidth(min(text_width, max_width))
        
        # Style cơ bản
        base_style = """
            padding: 5px;
            border-radius: 10px;
            font-size: 14px;
            border: 1px solid lightgray;
        """
        
        # Style tùy theo tin nhắn gửi hay nhận
        if is_sent:
            style = base_style + f"""
                border-bottom-right-radius: 2px;
                color: rgb(255, 255, 255);
                background-color: #55aaff;
            """
        else:
            style = base_style + f"""
                border-bottom-left-radius: 2px;
                color: black;
                background-color: white;
            """
        label.setStyleSheet(style)
        
        widget_layout = QVBoxLayout(container_widget)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(label)
        
        label.adjustSize()
        container_widget.setMinimumSize(label.sizeHint())
        
        if is_sent:
            self.scroll_layout.addWidget(container_widget, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        else:
            self.scroll_layout.addWidget(container_widget, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
            
        return container_widget
    
    def display_message(self, message):
        self.create_message(message, is_sent=False)
    
    def send_message(self):
        message = self.ui.textEdit.toPlainText().strip()
        if not message:
            return
        
        if not self.client_socket:
            print("Error! Not connected to server!")
            return
        
        try:
            self.client_socket.send(message.encode('utf-8'))
            self.create_message(message, is_sent=True)
        except Exception:
            print("⚠️ Can't send message!")
        
        self.ui.textEdit.clear()
    
    def show_home(self):
        self.close()
        self.signal.home.emit(self.device, self.pos(), self.isMaximized(), self.userdata["username"])
        
    def show_information(self):
        self.close()
        self.signal.information.emit(self.device, self.pos(), self.isMaximized(), self.userdata["username"])
    
    def toggle_right_panel(self):
        self.ui.widget_4.setVisible(not self.ui.widget_4.isVisible())
           
    def confirm_exit(self):
        reply = QMessageBox.question(
                self,'Exit','Are you sure you want to exit?',
                QMessageBox.StandardButton.Yes|
                QMessageBox.StandardButton.No,QMessageBox.StandardButton.No
            )
        return reply == QMessageBox.StandardButton.Yes
    
    def closeEvent(self, event):
        if self.client_socket:
            self.client_socket.close()
        event.accept()
    
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
    window = Chat()
    window.show()
    app.exec()  