import socket
import threading

DEFAULT_ADDRESS = "127.0.0.1"
DEFAULT_PORT = 13001

#class BulletinBoard():
#    def __init__(self):

class clientThread(threading.Thread):
    def __init__(self, ip: str, port: int, conn):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        print("New client thread created!")

    def run(self):
        size = 4096
        while True:
            try:
                data = self.conn.recv(size)
                if data:
                    print("Data received (as bytes):", data)
                    dataStr = data.decode()
                    print("Data received (as str):", dataStr)
                    print("Reading data...")
                    s.board.read_bbp_req(dataStr) 
                    print("Data read")
                    response = s.board.handle_current_request()
                    response = bytes(response, 'utf-8')
                    self.conn.send(response)
                    print("Response sent")
                else:
                    raise error('Disconnected!')
            except:
                return False

class Server:
    def __init__(self, address : str, port: int):
        str: self.address = address
        int: self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.bboard = BulletinBoard()
        self.socket.bind((address, port))

    def listen(self):
        self.socket.listen(5)
        allThreads = []

        while True:
            client, address = self.socket.accept()
            client.settimeout(600)
            ct = clientThread(address[0], address[1], client)  
            ct.start()
            allThreads.append(ct)
        
        for th in allThreads:
            th.join()

s = Server(DEFAULT_ADDRESS, DEFAULT_PORT)
s.listen()
