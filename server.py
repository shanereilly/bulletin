import socket
import threading
import time

# Constants
DEBUG = True
ERROR = 0
POST = 1
USERS = 2
LEAVE = 3
MESSAGE = 4
GROUPS = 5
GROUPJOIN = 6
GROUPPOST = 7
GROUPUSERS = 8
GROUPLEAVE = 9
GROUPMESSAGE = 10
DEFAULT_ADDRESS = "127.0.0.1"
DEFAULT_PORT = 13001

class Group:
    def __init__(self, groupID : int):
        self.id = groupID
        self.users = []
        self.posts = {}

    def removeUser(self, username):
        self.users.remove(username)
    def addUser(self, username):
        self.users += [username]

class Post:
    def __init__(self, messageHeader :str, messageBody : str):
        str: self.messageHeader = messageHeader
        str: self.messageBody = messageBody

class Request:
    def __init__(self, username: str, groupID: str, msgID: str, act: str, subject: str, body: str, timestamp):
        self.username = username
        self.groupID = groupID
        self.msgID = msgID
        self.requestType = requestType
        self.subject = subject
        self.body = body
        self.timestamp = timestamp

class BulletinBoard():
    def __init__(self):
        self.groups = [Group(0), Group(1), Group(2), Group(3), Group(4), Group(5)]
        self.users = []
        self.postcount = 0

    def read_request(self, request: str):
        print("Parsing request")
        request = request.split("\n")
        username = request[0]
        groupID = request[1]
        msgID = request[2]
        reqAct = request[3]
        subject = request[4]
        body = ""
        timestamp = str(time.time)
        print("Current request:\n", request)
        print("Timestamp: ", timestamp)
        
        for i in range(5, len(request)):
            body += request[i] + '\n'
        self.currentRequest = Request(username, groupID, msgID, reqAct, subject, body, timestamp)

    def handle_request(self) -> str:
        print("Handling request...")
        request = self.currentRequest
        response = ""
        requestType = int(self.requestType)

        # Handle Error
        if (requestType == ERROR):
            response = "Error"

        # Handle Post
        elif (requestType == POST):
            self.postcount += 1
            group = self.groups[request.groupID]
            group.posts[self.postcount] = Post(request.subject, request.body)
            response = f"Post successful. Post ID: {self.postcount}."

        #Handle Users
        elif (requestType == USERS or requestType == GROUPUSERS):
           response = "Current users:\n"
           group = self.groups[request.groupID]
           for user in group.users:
               response += user + "\n"

        # Handle Leave
        elif (requestType == LEAVE or requestType == GROUPLEAVE):
            username = request.username
            groupID = int(request.groupID)
            self.groups[groupID].removeUser
            response = f"User {username} removed from group {groupID}"

        # Handle Message
        elif (requestType == MESSAGE or requestType == GROUPMESSAGE):
            group = self.groups[request.groupID]
            if request.msgID in group.posts:
                post = group.posts[request.msgID]
                response = f"{post.postHeader}\n{post.postBody}"
            else:
                repsonse = "Error. No such post."

        # Handle Groups
        elif (requestType == GROUPS):
            response = "Available groups:\n"
            for group in self.groups:
                response += "Group {group.groupID}\n"

        # Handle Groupjoin
        elif (requestType == GROUPJOIN):
            group = self.groups[request.groupID]
            if request.username not in group.users:
                group.users += [request.username]
                response = f"{request.username} added to group {request.groupID}."
            else:
                response = f"{request.username} already in group {request.groupID}."

        # Handle Grouppost
        elif (requestType == GROUPPOST):
            self.postcount += 1
            group = self.groups[request.groupID]
            group.posts[self.postcount] = Post(request.subject, request.body)
            response = f"Post successfully added in group {request.groupID}. Post ID: {self.postcount}."
        if (DEBUG):
            print(response)
        return response

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
                    s.bboard.read_req(dataStr) 
                    print("Data read.")
                    response = s.bboard.handle_request()
                    response = bytes(response, 'utf-8')
                    self.conn.send(response)
                    print("Response sent.")
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
        self.bboard = BulletinBoard()
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
