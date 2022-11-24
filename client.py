import socket
import sys
import select
import threading
from typing import Tuple

# Setting Constants
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
FIRSTMESSAGE = 11


# Clients are modled using a client class called Client. When a new client connection is created
# (a new client object is instantiated) a client is assigned its socket connection value and username.
# The client class has a method which creates bulletin board requests called createBulletinRequest.
# This method takes a list of variables to create a request from the client to eventually send to the
# server (bulletin board). This class also contains a make request method to prepare the variables that
# are to be sent to the createBulletinRequest method. The process of making a request follows this path:
# The client code reads the input from a user, parses it, then sends it to the makeRequest method. There,
# the request variables are put together from the parsed user input. Lastly the makeRequest method passes
# the variables into the createBulletinRequest function which generates and returns the request. From there
# the makeRequest function actually sends the request to the server using the client connection.
class Client:
    # Constructor
    def __init__(self, connection, username: str):
        self.connection = connection
        self.username = username

    def createBulletinRequest(self, groupID: int, msgID: int, reqAct: int, subject: str, body: str):
        reqList = [self.username, str(groupID), str(msgID), str(reqAct), subject, body]
        req = "\n".join(reqList)
        return req

    # makeRequest: given a valid main menu selection, creates and sends appropriate request to server
    def makeRequest(self, selection: Tuple[int, str, str]):
        # Initial request variables
        # Zero is the default group ID. Any other group must be specified
        groupID = 0
        msgID = 0
        reqAct = 0
        subject = ""
        body = ""

        first = selection[0]

        # Handle error
        if (first == ERROR):
            print("Error")
        elif (first == FIRSTMESSAGE):
            reqAct = FIRSTMESSAGE
        # Post
        elif (first == POST):
            reqAct = POST
            # Zero is the default group ID. Any other group must be specified with the %grouppost command
            groupID = 0
            subject = selection[1]

            print("Please enter your message body. Enter 'q' alone when finished:")
            body = ""
            bodyLine = ""
            while (1):
                if (bodyLine == "q"):
                    break
                else:
                    body += (bodyLine + "\n")
                    bodyLine = input()

        # Users
        elif (first == USERS):
            reqAct = USERS
        # Leave
        elif (first == LEAVE):
            reqAct = LEAVE
        # Message
        elif (first == MESSAGE):
            reqAct = MESSAGE
            msgID = int(selection[1])
        # Groups
        elif (first == GROUPS):
            reqAct = GROUPS
        # Groupjoin
        elif (first == GROUPJOIN):
            reqAct = GROUPJOIN
            groupID = int(selection[1])
        # Grouppost
        elif (first == GROUPPOST):
            reqAct = GROUPPOST
            groupID = int(selection[1])
            subject = str(selection[2]).strip("[]")
            subject = subject.strip("\'")
            print("Please enter your message body. Enter 'q' alone when finished:")
            body = ""
            bodyLine = ""
            while (1):
                if (bodyLine == "q"):
                    break
                else:
                    body += (bodyLine + "\n")
                    bodyLine = input()
        # Groupusers
        elif (first == GROUPUSERS):
            reqAct = GROUPUSERS
            groupID = int(selection[1])
        # Groupleave
        elif (first == GROUPLEAVE):
            reqAct = GROUPLEAVE
            groupID = int(selection[1])
        # Groupmessage
        elif (first == GROUPMESSAGE):
            reqAct = GROUPMESSAGE
            groupID = int(selection[1])
            msgID = int(selection[2])

        if DEBUG:
            print("Building request...")

        # Pass variables into createBulletinRequest to generate request message
        request = self.createBulletinRequest(groupID, msgID, reqAct, subject, body)
        request = bytes(request, 'utf-8')

        if DEBUG:
            print("Request built:")
            print(request)

        # Send request message to the server
        self.connection.send(request)

        if DEBUG:
            print("Request sent.")

    # method that handles the server response to the client
    # simply writes the response from the server
    def handle_response(self, resp):
        response = resp.decode()
        sys.stdout.write(response)
        sys.stdout.flush()

# Main menu function takes a client as an argument and sets up the main loop waiting for user (client) input.
# Sends user input to be parsed after user successfully inputs.
def mainMenu(client):
    recvThread = threading.Thread(target=recieveData, args = [client], daemon = True)
    recvThread.start()
    client.makeRequest((FIRSTMESSAGE, "", ""))
    while True:
        selection = input("Enter one of the following commands:\n\t%exit\n\t%post [message subject]\n\t%users\n\t%leave\n\t%message [message ID]\n\t%groups\n\t%groupjoin [groupID]\n\t%grouppost [groupID] [message subject]\n\t%groupusers [groupID]\n\t%groupleave [groupID]\n\t%groupmessage [groupID] [messageID]\n")
        selection = parseSelection(selection)

        if DEBUG:
            print(selection)

        if selection[0] != 0:
            client.makeRequest(selection)

# Function to parse the user input so that a request can be made to the server properly.
# Made up of a block of if/else statements to understand/interpret commands given as input.
def parseSelection(selection: str) -> Tuple[int, str, str]:
    main_menu_commands = ["%exit", "%post", "%users", "%leave", "%message", "%groups", "%groupjoin", "%grouppost", "%groupusers", "%groupleave", "%groupmessage"]
    error = (ERROR,"","")
    command = selection.split()
    first = command[0]
    if first not in main_menu_commands:
        print("Invalid command")
        return error
    elif first == "%exit":
        sys.exit()
    elif first == "%post":
        if len(command) < 2:
            print("%post command requires a message subject")
            return error
        else:
            return (POST, " ".join(command[1:]), "")
    elif first == "%users":
        return (USERS, "", "")
    elif first == "%leave":
        return (LEAVE, "", "")
    elif first == "%message":
        if len(command) < 2:
            print("%message command requires a message ID")
            return error
        else:
            return (MESSAGE, command[1], "")
    elif first == "%groups":
        return (GROUPS, "", "")
    elif first == "%groupjoin":
        if len(command) < 2:
            print("%groupjoin command requires a group ID")
            return error
        else:
            return (GROUPJOIN, command[1], "")
    elif first == "%grouppost":
        if len(command) < 3:
            print("%grouppost command requires a group ID and a message subject")
            return error
        else:
            return (GROUPPOST, command[1], command[2:])
    elif first == "%groupusers":
        if len(command) < 2:
            print("%groupusers command requires a group ID")
            return error
        else:
            return (GROUPUSERS, command[1], "")
    elif first == "%groupleave":
        if len(command) < 2:
            print("%groupleave command requires a group ID")
            return error
        else:
            return (GROUPLEAVE, command[1], "")
    elif first == "%groupmessage":
        if len(command) < 3:
            print("%groupmessage command requires a group ID and a message ID")
            return error
        else:
            return (GROUPMESSAGE, command[1], command[2])

# Function to handle the initial menu given before a connection the server is made.
def initialMenu() -> Tuple[str,int]:
    response = input("Enter one of the following commands:\n\t%connect [address] [port]\n\t%exit\n")
    command = response.split()
    if command[0] == "%exit":
        sys.exit()
    elif (len(command) == 3) and (command[0] == "%connect") and verifyAddress(command[1]) and verifyPort(command[2]):
        return (command[1], int(command[2]))
    else:
        print("Invalid command")
        return initialMenu()

# Function to verify the IP address
def verifyAddress(address: str) -> bool:
    nums = address.split('.')
    if len(nums) != 4:
        print("IP address is incorrect")
        return False
    for num in nums:
        if int(num) > 0xFF:
            print("IP address is incorrect")
            return False
    return True

# Function to verify the port given
def verifyPort(port: str) -> bool:
    num = int(port)
    if num > 0xFFFF:
        print("IP address is incorrect")
        return False
    return True

# Fucntion to receive data from the server.
# sends response to the handle response function
def recieveData(client):
    while True:
        response = client.connection.recv(4096)
        client.handle_response(response)

# Main function / Driver code
# Calls the initial menu and attempts to establish a client connection to the server.
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address, port = initialMenu()
    username = input("Enter a nonexistent username: ")
    try:
        sock.connect((address, port))
    except socket.error:
        print("Unable to connect. Ensure the server is running and the IP address/port are correct.")
        sys.exit()
    client = Client(sock, username)
    mainMenu(client)

main()
