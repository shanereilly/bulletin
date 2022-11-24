import socket
import threading
import time

# Setting Constants
DEBUG = False
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
FIRSTMESSAGE = 11
DEFAULT_ADDRESS = "127.0.0.1"
DEFAULT_PORT = 13001

# Set up a global list of clients for the server to keep track of all the clients
list_of_clients = []

# Set up global lists for each group to store the client connection.
# These client connection lists are then used to contact the clients of a particular
# group when needed (i.e. a user sends a message which needs to notify all members
# of group 1)
group_0 = []
group_1 = []
group_2 = []
group_3 = []
group_4 = []
group_5 = []


# Sets up a Group class to store the users in each group, the posts in that group, the groupID,
# and the total postcount. The Group class allows for further modularization of the code
# by allowing us to simply initialize a new instance of the Group class for each group.
class Group:
    def __init__(self, groupID : int):
        self.groupID = groupID
        self.users = []
        self.posts = {}
        self.postcount = 0

    # The remove user method removes the username from a group's user list
    def removeUser(self, username : str):
        if DEBUG:
            print(f"Removing user {username}")
        self.users.remove(username)

    # The add user method adds a username to the group's user list
    def addUser(self, username : str):
        if DEBUG:
            print(f"Adding user {username}")
        self.users += [username]

# A post is implmeneted as a class in this code. Essentially, this class allows
# us to instantiate a post object with the necessary attributes of a post:
# such as a Header (subject), Body, and the timestamp of when the post was made.
class Post:
    def __init__(self, messageHeader : str, messageBody : str, timestamp):
        self.messageHeader = messageHeader
        self.messageBody = messageBody
        self.timestamp = timestamp

# Similar to our implementation of a post, a request is modled using this Request class.
# This class allows the generation of a request to be built with all its necessary features.
# These features include: the username that is making the request (username), the group ID of
# the request (groupID), the message ID of the request (msgID), the type of request being made
# (requestType), the subject of the request if there is one (subject), the body of the request
# if there is one (body), and lastly the time at which the request is being built (timestamp).
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


# This broadcast function is a global function which broadcasts a message (message in input)
# to all clients in the list of clients we defined earlier excluding the user that is making
# the request (connection as input). This functon is called whenever a message needs to be
# sent to every client in the client list. This ocurrs for group 0 (public messaging board)
# posts because everyone belongs to the public messaging board when they connect to the server.
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


# This second broadcast function is designed to broadcast a message but only to a specific group.
# This function takes an extra input (group) as compared to the broadcast function above which
# tells this function which clients to broadcast the message to.
def broadcast_specific(message, connection, group):
    message = bytes(message, 'utf-8')
    for clients in group:
        if (clients!=connection):
            try:
                print("trying to send message to : " + str(clients))
                clients.send(message)
            except:
                print("failed to send message to : " + str(clients))
                clients.close()

# Add connection function takes a groupID and a connection as input to add the connection to the
# global group list of the given groupID. 
def addConn(groupID, connection):
    if int(groupID) == 0:
        group_0.append(connection)
    elif int(groupID) == 1:
        group_1.append(connection)
    elif int(groupID) == 2:
        group_2.append(connection)
    elif int(groupID) == 3:
        group_3.append(connection)
    elif int(groupID) == 4:
        group_4.append(connection)
    elif int(groupID) == 5:
        group_5.append(connection)


# We implemented the bulletin board as its own class which has the following attributes: A list of groups
# to store each group (Group class object) in, a list of users to store the users on the bulletin board,
# and a postcount to store the current post number in the bulletin board. We chose to implement the bulletin
# board as class so that we could simply initialize a single bulletin board which holds all of the information
# mentioned above and store that in a single BulletinBoard object variable. The Server class initializes this
# single BulletinBoard object variable.
class BulletinBoard():
    def __init__(self):
        self.groups = [Group(0), Group(1), Group(2), Group(3), Group(4), Group(5)]
        self.users = []
        self.postcount = 0

    # Read request method of the BulletinBoard class takes a request string as input
    # and parses it and builds it using the Request class commented on earlier. Also
    # note that this method automatically adds every user to group 0 (public message board).
    def read_request(self, request: str):

        if DEBUG:
            print("Parsing request")

        # Setting request and username variables (string operations)
        request = request.split("\n")
        username = request[0]

        ## All users are automatically added to group 0
        if username not in self.groups[0].users:
            self.groups[0].addUser(username)

        # Setting request varibales to pass into Request class below
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

        # Creating an object of the class Request and setting a new variable self.currentRequest equal to
        # the new object. This creates/builds the request object and stores it in a variable.
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

    # This method (handleRequest) is the main method which handles every request. Requests such as:
    # posting (user wants to post a message) which is done using either %post or %grouppost, 
    # displaying the current users in a group (%users command), leaving the public message board or
    # group (using %leave or %groupleave command), joining the public message board (group 0) or
    # another group (using %groupjoin command), and viewing messages using the %message or %groupmessage command.
    # This method takes a client connection as input and returns a response as a string. That response
    # string is eventually sent to the client. An example of a response that is sent is when a user
    # attempts to access a message from a group which they do not belong to. A response message is sent
    # in this case saying "Cannot view post. User X not in group #"
    def handleRequest(self, conn) -> str:
        if DEBUG:
            print("Handling request...")
        request = self.currentRequest
        response = ""
        requestType = int(request.requestType)
        if DEBUG:
            print(f"Request type: {requestType}")

        # Handle first message (when a new user joins the server) to notify all clients that are in the public message board
        if (requestType == FIRSTMESSAGE):
            if DEBUG:
                print("First message. Identifying user...")
            broadcast(f"{request.username} has joined the message board.\n", conn)
            response = ""

        # Handle Error in request type
        if (requestType == ERROR):
            if DEBUG:
                print("ERROR request.")
            response = "Error"

        # Handles the posting of messages using the %post command and %grouppost command. This portion of 
        # code also utilizes the broadcast functions that were defined earlier to notify clients of a new post 
        # if they are suppossed to be notified. At the very end of this function, if a post is made, the
        # postcount is incremented.
        elif (requestType == POST or requestType == GROUPPOST):
            if (DEBUG and requestType == POST):
                print("POST request.")
            elif (DEBUG and requestType == GROUPPOST):
                print("GROUPPOST request.")
            group = self.groups[int(request.groupID)]
            groupID = int(request.groupID)
            if request.username not in group.users:
                response = f"Cannot post. {request.username} is not in group {request.groupID}\n"
            else:
                group.posts[group.postcount] = Post(request.subject, request.body, str(request.timestamp))
                response = f"Post successful. Post ID: {group.postcount}.\n"
                if (groupID == 0):
                    broadcast_specific(f"MSG ID: {group.postcount}, SENDER: {request.username}. POST DATE: {group.posts[group.postcount].timestamp}, SUBJECT: {group.posts[group.postcount].messageHeader}\n", conn, group_0)
                elif (groupID == 1):
                    broadcast_specific(f"MSG ID: {group.postcount}, SENDER: {request.username}. POST DATE: {group.posts[group.postcount].timestamp}, SUBJECT: {request.subject}, GROUP: {groupID}\n", conn, group_1)
                elif (groupID == 2):
                    broadcast_specific(f"MSG ID: {group.postcount}, SENDER: {request.username}. POST DATE: {group.posts[group.postcount].timestamp}, SUBJECT: {request.subject}, GROUP: {groupID}\n", conn, group_2)
                elif (groupID == 3):
                    broadcast_specific(f"MSG ID: {group.postcount}, SENDER: {request.username}. POST DATE: {group.posts[group.postcount].timestamp}, SUBJECT: {request.subject}, GROUP: {groupID}\n", conn, group_3)
                elif (groupID == 4):
                    broadcast_specific(f"MSG ID: {group.postcount}, SENDER: {request.username}. POST DATE: {group.posts[group.postcount].timestamp}, SUBJECT: {request.subject}, GROUP: {groupID}\n", conn, group_4)
                elif (groupID == 5):
                    broadcast_specific(f"MSG ID: {group.postcount}, SENDER: {request.username}. POST DATE: {group.posts[group.postcount].timestamp}, SUBJECT: {request.subject}, GROUP: {groupID}\n", conn, group_5)
                group.postcount += 1
                

        # Handles %users command to list all current users in the public message board (group 0) or a specific group.
        # The method of feedback to the client is the same as the other portions of code in this larger handleRequests
        # method. A reponse string is generated and returned at the end of the function so that the client will be
        # notified of the results.
        elif (requestType == USERS or requestType == GROUPUSERS):
            if (DEBUG and requestType == USERS):
                print("USERS request.")
            elif (DEBUG and requestType == GROUPUSERS):
                print("GROUPUSERS request.")
            response = "Current users:\n"
            group = self.groups[int(request.groupID)]
            if DEBUG:
                print(f"Group: {group.groupID}")
            if request.username not in group.users:
                response = f"Cannot return users. User {request.username} not in group {group.groupID}.\n"
            else:
                for user in group.users:
                    response += user + "\n"

        # Handles a user leaving either the public message board or a specific group (%leave or %groupleave command).
        # This portion of code generates a response code letting the client know that they have left the group "User X
        # remove drom group #" and also notifies all clients who are suppossed to be notified about this client's
        # departure using both broadcast and broadcast_specific functions. When a client has left a group, they are
        # removed from the list of clients that belong to that group, and as such, will no longer receive notifications
        # about messages to that group AND will no longer have access to that group's messages.
        elif (requestType == LEAVE or requestType == GROUPLEAVE):
            if (DEBUG and requestType == LEAVE):
                print("LEAVE request.")
            elif (DEBUG and requestType == GROUPLEAVE):
                print("GROUPLEAVE request.")
            username = request.username
            groupID = int(request.groupID)
            (self.groups[groupID]).removeUser(username)
            response = f"User {username} removed from group {groupID}\n"
            if (groupID == 0):
                broadcast(f"User {username} left group {groupID}\n", conn)
                group_0.remove(conn)
            elif (groupID == 1):
                broadcast_specific(f"User {username} left group {groupID}\n", conn, group_1)
                group_1.remove(conn)
            elif (groupID == 2):
                broadcast_specific(f"User {username} left group {groupID}\n", conn, group_2)
                group_2.remove(conn)
            elif (groupID == 3):
                broadcast_specific(f"User {username} left group {groupID}\n", conn, group_3)
                group_3.remove(conn)
            elif (groupID == 4):
                broadcast_specific(f"User {username} left group {groupID}\n", conn, group_4)
                group_4.remove(conn)
            elif (groupID == 5):
                broadcast_specific(f"User {username} left group {groupID}\n", conn, group_5)
                group_5.remove(conn)


        # Handles the viewing of messages using either the %message or %groupmessage command.
        # This portion of code simultaneously allows a client to view a message that they have
        # permission to see (they belong to the proper group) and prevents clients who do not
        # have the proper permission from seeing messages that they should not see. Also handles
        # the case of a user attempting to view a message that does not exist.
        elif (requestType == MESSAGE or requestType == GROUPMESSAGE):
            if (DEBUG and requestType == MESSAGE):
                print("MESSAGE request.")
            elif (DEBUG and requestType == GROUPMESSAGE):
                print("GROUPMESSAGE request.")
            group = self.groups[int(request.groupID)]
            if request.username not in group.users:
                response = f"Cannot view post. {request.username} not in group {request.groupID}\n"
            elif int(request.msgID) in group.posts.keys():
                post = group.posts[int(request.msgID)]
                if DEBUG:
                    print("Post ID in dictionary")
                    print(post)
                response = f"Subject: {post.messageHeader}\nTimestamp: {post.timestamp}\n----------------\n{post.messageBody}"
            else:
                repsonse = "Error. No such post."

        # Handles the displaying of available groups (%groups command) by setting the response string.
        elif (requestType == GROUPS):
            if DEBUG:
                print("GROUPS request.")
            response = "Available groups:\n"
            for group in self.groups:
                response += f"Group {group.groupID}\n"

        # Handles users joining groups via the %groupjoin command. This portion of code utilizes the same broadcast
        # and broadcast specific to notify the proper clients when a user joins a group. This portion of code also
        # returns a response string which notifies the client that they have successfully joing a group "User X added to group #"
        # If a user attempts to join a group that they are already in, a response message is sent to the client notifying
        # them that they are already in the requested group.
        elif (requestType == GROUPJOIN):
            if DEBUG:
                print("GROUPJOIN request.")
            group = self.groups[int(request.groupID)]
            groupID = int(request.groupID)
            if request.username not in group.users:
                if DEBUG:
                    print("User not in group...")
                group.addUser(request.username)
                response = f"{request.username} added to group {request.groupID}.\n"
                response += "Current users:\n"
                addConn(request.groupID, conn)
                for user in group.users:
                    response += user + "\n"
                if (groupID == 0):
                    broadcast(f"User {username} joined group {request.groupID}\n", conn)
                elif (groupID == 1):
                    broadcast_specific(f"User {request.username} joined group {groupID}\n", conn, group_1)
                elif (groupID == 2):
                    broadcast_specific(f"User {request.username} joined group {groupID}\n", conn, group_2)
                elif (groupID == 3):
                    broadcast_specific(f"User {request.username} joined group {groupID}\n", conn, group_3)
                elif (groupID == 4):
                    broadcast_specific(f"User {request.username} joined group {groupID}\n", conn, group_4)
                elif (groupID == 5):
                    broadcast_specific(f"User {request.username} joined group {groupID}\n", conn, group_5)
            else:
                response = f"{request.username} already in group {request.groupID}."

        if (DEBUG):
            print(response)

        # Returns the response message as the output of the handleRequests method. This response code is set
        # by one of the portions of code above to ensure that the client is given the proper response based
        # upon their requested action.
        return response



# Clients are implemented using threads, these client threads are implemented as objects of a 
# class clientThread. This class initializes a client thread object with an ip address, a port
# number, and a connection value. Every client that connects to this server is instantiated using
# this clientThread class. The clientThread class also contains a method run() which runs for every
# client in order to constantly look for data to recieve as input from a client thread or send to the
# client as an ouput/response.
class clientThread(threading.Thread):
    def __init__(self, ip: str, port: int, conn):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        if DEBUG:
            print("Client thread created.")
    
    # run() method described above, essentially continually monitors for input/output from/to the client
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
                    response = s.bboard.handleRequest(self.conn)
                    response = bytes(response, 'utf-8')
                    self.conn.send(response)
                    print("Response sent.")
                else:
                    raise error('Disconnected!')
            except:
                return False

# The server is implemented as a class itself. When a new server object is created, the server object
# is instantiated with an address, a port number, a socket value, a bulletin board (creates bulletin board
# object) and binds the address/port to the socket. The server class also contains a listen method which
# continually prepares to accpet a client connection and create a client thread (create an object of
# class clientThread). The listen method also adds any new client connections to the list of clients
# in order to know where to send notifications. Latly the listen method joins all new threads and stores them
# in a list called allThreads.
class Server:
    def __init__(self, address : str, port: int):
        str: self.address = address
        int: self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bboard = BulletinBoard()
        self.socket.bind((address, port))

    # listen method descirbed above, essentially keeps connection open "listening" for any new clients
    # and prepares to accept them and create a client thread out of them.
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
        
        for th in allThreads:
            th.join()


# ** Driver code **
# Creates a new server object with the defualt address and default port listed in the constants section
# at the top of the code. Once a new server object is created and stored in a variable, s, the listen
# method of the server object s is called to continually listen for new clients.
s = Server(DEFAULT_ADDRESS, DEFAULT_PORT)
s.listen()
