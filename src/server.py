import socket, threading, json

class ChatServer():
    def __init__(self, host="0.0.0.0", port=12345):
        """Khởi tạo server với host và port mặc định."""
        self.host = host
        self.port = port
        self.clients = {}  # Danh sách các client kết nối
        self.running = threading.Event()  # Sự kiện kiểm soát vòng lặp
        
        if self.is_server_running():
            print("⚠️ Server is already running. Cannot start another instance.")
            return
    
        self.start_server()
    
    def is_server_running(self):
        """Kiểm tra xem server đã chạy trên port này chưa."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
            # Kết nối thử đến port để kiểm tra
            result = test_socket.connect_ex((self.host, self.port))
            return result == 0  # Trả về True nếu port đã được sử dụng
            
        self.running.set()  # Đánh dấu server đang chạy

    def start_server(self):
        """Khởi động server và bắt đầu lắng nghe kết nối."""
        self.running.set()  # Đánh dấu server đang chạy
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Tái sử dụng địa chỉ
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"🖥 Server is running on {self.host}:{self.port}...\n")

            # Chạy thread chấp nhận client
            self.accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
            self.accept_thread.start()
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            self.running.clear()
    
    def accept_clients(self):
        """Chấp nhận các client mới kết nối đến server."""
        while self.running.is_set():
            try:
                client_socket, addr = self.server_socket.accept()
                # Nhận thông tin người dùng dạng JSON từ client
                user_data = json.loads(client_socket.recv(1024).decode('utf-8').strip())
                self.clients[client_socket] = {
                    "username": user_data.get("username", f"Guest_{len(self.clients) + 1}"),
                    "name": user_data.get("name", f"Guest_{len(self.clients) + 1}")
                }
                print(f"🔗 {addr} joined the chat as '{self.clients[client_socket]['name']}' ({self.clients[client_socket]['username']}).\n")
                # Tạo thread xử lý tin nhắn cho client mới
                self.broadcast_users()  # Gửi danh sách người dùng khi có người mới kết nối
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception:
                break  # Thoát vòng lặp nếu server gặp lỗi hoặc dừng

    def handle_client(self, client_socket):
        """Xử lý tin nhắn từ một client cụ thể."""
        while self.running.is_set():
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:  # Nếu không nhận được dữ liệu (client ngắt kết nối)
                    break
                sender_name = self.clients[client_socket]["name"]
                self.broadcast(f"{sender_name}: {message}", client_socket)
            except Exception:
                break

        # Xóa client khỏi danh sách khi ngắt kết nối
        self.cleanup_client(client_socket)

    def broadcast(self, message, sender_socket):
        """Gửi tin nhắn đến tất cả client trừ người gửi."""
        for client in list(self.clients.keys()):
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except Exception:
                    self.cleanup_client(client)
    
    def broadcast_users(self):
        """Gửi danh sách người dùng dạng JSON."""
        user_list = [
            {"username": data["username"], "name": data["name"]}
            for data in self.clients.values()
        ]
        message = f"USERS:{json.dumps(user_list)}"
        for client in list(self.clients.keys()):
            try:
                client.send(message.encode('utf-8'))
            except Exception:
                self.cleanup_client(client)
    def cleanup_client(self, client_socket):
        """Dọn dẹp client khi ngắt kết nối."""
        if client_socket in self.clients:
            username = self.clients[client_socket]["username"]
            name = self.clients[client_socket]["name"]
            del self.clients[client_socket]
            client_socket.close()
            print(f"🔌 '{name}' ({username}) has disconnected. Total clients: {len(self.clients)}\n")
            self.broadcast_users()  # Gửi danh sách mới khi có người rời

    def stop(self):
        """Dừng server và đóng tất cả kết nối."""
        self.running.clear()  # Dừng các vòng lặp
        for client in list(self.clients.keys()):  # Sao chép danh sách để tránh lỗi khi xóa
            self.cleanup_client(client)
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        print("🛑 Server has been shut down.")

if __name__ == "__main__":
    server = ChatServer()
    while True:
        command = input("Enter 'exit' to stop the server: ").lower()
        if command == "exit":
            server.stop()
            break