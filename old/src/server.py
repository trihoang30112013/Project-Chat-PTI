import socket, threading
class ChatServer():
    def __init__(self):
        """ Khởi động server """
        self.server_socket = None
        self.clients = []
        self.running = threading.Event()  # Sự kiện kiểm soát vòng lặp
        self.running.set()  # Đánh dấu server đang chạy

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("0.0.0.0", 12345))
            self.server_socket.listen(5)
            print("🖥 Server is running on port 12345...\n")

            self.accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
            self.accept_thread.start()
        except Exception as e:
            print(f"❌ Server error: {e}")

    def accept_clients(self):
        """ Chấp nhận client mới kết nối """
        while self.running.is_set():  # Kiểm tra nếu server đang chạy
            try:
                client_socket, addr = self.server_socket.accept()
                self.clients.append(client_socket)
                print(f"🔗 {addr} joined this chat.\n")
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except:
                break  # Thoát nếu server dừng

    def handle_client(self, client_socket):
        """ Xử lý tin nhắn từ client """
        while self.running.is_set():
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                self.broadcast(message, client_socket)
            except:
                break

        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()

    def broadcast(self, message, sender_socket):
        """ Gửi tin nhắn đến tất cả client khác """
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message.encode())
                except:
                    self.clients.remove(client)

    def stop(self):
        """ Dừng server """
        self.running.clear()  # Dừng vòng lặp
        for client in self.clients:
            client.close()  # Đóng tất cả client
        self.server_socket.close()
        print("🛑 Server has been shut down.")
                 
if __name__ == "__main__":
    ChatServer()
    while True:
        if input().lower() == "exit":
            break