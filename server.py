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

list_of_clients = []

class Group:
    def __init__(self, groupID : int):
        self.groupID = groupID
        self.users = []
        self.posts = {}
        self.postcount = 0

    def removeUser(self, username : str):
        if DEBUG:
            print(f"Removing user {username}")
        self.users.remove(username)

    def addUser(self, username : str):
        if DEBUG:
            print(f"Adding user {username}")
        self.users += [username]

class Post:
    def __init__(self, messageHeader : str, messageBody : str, timestamp):
        self.messageHeader = messageHeader
        self.messageBody = messageBody
        self.timestamp = timestamp

class Request:
    def __init__(self, username: str, groupID: str, msgID: str, requestType: str, subject: str, body: str, timestamp):
        self.username = username
        self.groupID = groupID
        self.msgID = msgID
        self.requestType = requestType
        self.subject = subject
        self.body = body
        self.timestamp = timestamp
        if DEBUG:
            print("Request built.")


# Attempt at broadcasting message
def broadcast(message, connection):
    message = bytes(message, 'utf-8')
    for clients in list_of_clients:
        if clients!=connection:
            try:
                print("trying to send message to : " + str(clients))
                clients.send(message)
            except:
                print("failed to send message to : " + str(clients))
                clients.close()



class BulletinBoard():
    def __init__(self):
        self.groups = [Group(0), Group(1), Group(2), Group(3), Group(4), Group(5)]
        self.users = []
        self.postcount = 0

    def read_request(self, request: str):

        if DEBUG:
            print("Parsing request")

        request = request.split("\n")
        username = request[0]

        ## All users are automatically in group 0
        if username not in self.groups[0].users:
            self.groups[0].addUser(username)

        groupID = request[1]
        msgID = request[2]
        requestType = request[3]
        subject = request[4]
        body = ""
        timestamp = str(time.asctime( time.localtime(time.time())))
        
        for i in range(5, len(request)):
            body += request[i] + '\n'

        if DEBUG:
            print("Building request...")
            print("======================")
            print(f"Username: {username}")
            print(f"Group ID: {groupID}")
            print(f"Message ID: {msgID}")
            print(f"Request type: {requestType}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            print(f"Timestamp: {timestamp}")
            print("======================")

        self.currentRequest = Request(username, groupID, msgID, requestType, subject, body, timestamp)

        if DEBUG:
            print("Current request:")
            print("======================")
            print(f"Username: {self.currentRequest.username}")
            print(f"Group ID: {self.currentRequest.groupID}")
            print(f"Message ID: {self.currentRequest.msgID}")
            print(f"Request type: {self.currentRequest.requestType}")
            print(f"Subject: {self.currentRequest.subject}")
            print(f"Body: {self.currentRequest.body}")
            print(f"Timestamp: {self.currentRequest.timestamp}")
            print("======================")


    def handleRequest(self) -> str:
        if DEBUG:
            print("Handling request...")
        request = self.currentRequest
        response = ""
        requestType = int(request.requestType)
        if DEBUG:
            print(f"Request type: {requestType}")

        # Handle Error
        if (requestType == ERROR):
            if DEBUG:
                print("ERROR request.")
            response = "Error"

        # Handle Post
        elif (requestType == POST or requestType == GROUPPOST):
            if (DEBUG and requestType == POST):
                print("POST request.")
            elif (DEBUG and requestType == GROUPPOST):
                print("GROUPPOST request.")
            group = self.groups[int(request.groupID)]
            if request.username not in group.users:
                response = f"Cannot post. {request.username} is not in group {request.groupID}"
            else:
                group.posts[group.postcount] = Post(request.subject, request.body, str(request.timestamp))
                response = f"Post successful. Post ID: {group.postcount}."
                group.postcount += 1

        # Handle Users
        elif (requestType == USERS or requestType == GROUPUSERS):
            if (DEBUG and requestType == USERS):
                print("USERS request.")
            elif (DEBUG and requestType == GROUPUSERS):
                print("GROUPUSERS request.")
            response = "Current users:\n"
            group = self.groups[int(request.groupID)]
            if DEBUG:
                print(f"Group: {group.groupID}")
            for user in group.users:
                response += user + "\n"
            print(response)

        # Handle Leave
        elif (requestType == LEAVE or requestType == GROUPLEAVE):
            if (DEBUG and requestType == LEAVE):
                print("LEAVE request.")
            elif (DEBUG and requestType == GROUPLEAVE):
                print("GROUPLEAVE request.")
            username = request.username
            groupID = int(request.groupID)
            (self.groups[groupID]).removeUser(username)
            response = f"User {username} removed from group {groupID}"
            #for th in allThreads:
                #th.send(response)

        # Handle Message
        elif (requestType == MESSAGE or requestType == GROUPMESSAGE):
            if (DEBUG and requestType == MESSAGE):
                print("MESSAGE request.")
            elif (DEBUG and requestType == GROUPMESSAGE):
                print("GROUPMESSAGE request.")
            group = self.groups[int(request.groupID)]
            if request.username not in group.users:
                response = f"Cannot view post. {request.username} not in group {request.groupID}"
            elif int(request.msgID) in group.posts.keys():
                post = group.posts[int(request.msgID)]
                if DEBUG:
                    print("Post ID in dictionary")
                    print(post)
                response = f"Subject: {post.messageHeader}\nTimestamp: {post.timestamp}\n----------------\n{post.messageBody}"
            else:
                repsonse = "Error. No such post."

        # Handle Groups
        elif (requestType == GROUPS):
            if DEBUG:
                print("GROUPS request.")
            response = "Available groups:\n"
            for group in self.groups:
                response += f"Group {group.groupID}\n"

        # Handle Groupjoin
        elif (requestType == GROUPJOIN):
            if DEBUG:
                print("GROUPJOIN request.")
            group = self.groups[int(request.groupID)]
            if request.username not in group.users:
                if DEBUG:
                    print("User not in group...")
                group.addUser(request.username)
                response = f"{request.username} added to group {request.groupID}.\n"
                response += "Current users:\n"
                for user in group.users:
                    response += user + "\n"
            else:
                response = f"{request.username} already in group {request.groupID}."

        if (DEBUG):
            print(response)

        return response

class clientThread(threading.Thread):
    def __init__(self, ip: str, port: int, conn):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        if DEBUG:
            print("Client thread created.")
        broadcast("\nHELLOWORLD!\n", self.conn)

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
                    s.bboard.read_request(dataStr) 
                    print("Data read.")
                    response = s.bboard.handleRequest()
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
            list_of_clients.append(client)
            print("THREAD APPENDED!!!")
            #for th in allThreads:
                #print(str(th))
        
        for th in allThreads:
            th.join()



s = Server(DEFAULT_ADDRESS, DEFAULT_PORT)
s.listen()
