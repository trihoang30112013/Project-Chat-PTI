from pathlib import Path
import os, bcrypt, json

# class Database():
#     def __init__(self):
#         self.file_path = Path(__file__).parent / "user_pass.txt"
    
#     def username_exists(self, username):
#         return username in self.load_user()
    
#     def load_user(self):
#         if not os.path.exists(self.file_path):
#             return {}
#         with open(self.file_path, "r") as file:
#             user = {}
#             for line in file:
#                 if ":" in line:
#                     username,password = line.strip().split(":", 1)
#                     user[username] = password
#         return user
    
#     def save_user(self, username, password):
#         if not self.username_exists(username):
#             hash_pw = self.hash_password(password)
#             with open(self.file_path, "a+") as file:
#                 file.write(f"{username}:{hash_pw.decode('utf-8')}\n")

#     def hash_password(self, password):
#         salt = bcrypt.gensalt()
#         return bcrypt.hashpw(password.encode('utf-8'),salt)
            
#     def check_password(self, username, plain_password):
#         return bcrypt.checkpw(plain_password.encode("utf-8"), self.load_user()[username].encode("utf-8"))

@staticmethod
def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

@staticmethod
def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

class Account:
    def __init__(self, id, username, password, name=None, image=None):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.image = image
        
    def __str__(self):
        return f"Username: {self.username}, Password: {self.password}"
    
class Database():
    def __init__(self):
        self.file_path = Path(__file__).parent / "info.json"
        self.account_data = list()
        
        while True:
            try:
                self.account_data = load_json(self.file_path)
                break
            except:
                save_json(self.file_path, self.account_data)
                
    def get_data(self, username) -> Account:
        for account in self.account_data:
            if account.get("username") == username:
                return account
        return None
    
    def add_account(self, username, password, name=None, image=None):
        item = Account(
            len(self.account_data)+1, 
            username, 
            self.hash_password(password).decode("utf-8"), 
            name, 
            image
        )
        self.account_data.append(item.__dict__)
        # self.account_data.append(
        #     {
        #         "id": len(self.account_data)+1, 
        #         "username": username, 
        #         "password": self.hash_password(password).decode("utf-8"),
        #         "name": name,
        #         "image": image
        #     }
        # )
        save_json(self.file_path, self.account_data)
    
    def update_account(self, username, data_update=[]):
        for account in self.account_data:
            if account.get("username") == username:
                account[f"{data_update[0]}"] = data_update[1]
                save_json(self.file_path, self.account_data)
                return
    
    def username_exists(self, username):
        return self.get_data(username)
        
    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'),salt)
    
    def check_password(self, username, plain_password):
        return bcrypt.checkpw(plain_password.encode("utf-8"), self.get_data(username).get("password").encode("utf-8"))
