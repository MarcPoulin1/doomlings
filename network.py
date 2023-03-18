import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '172.16.5.150'
        self.port = 5050
        self.player_id = self.connect()

    def connect(self):
        try:
            self.client.connect((self.server, self.port))
            return self.client.recv(4096*8).decode()
        except socket.error as e:
            print(e)

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(4096*32))
        except socket.error as e:
            print(e)
