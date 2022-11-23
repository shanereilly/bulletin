import socket
import sys
import select
from typing import Tuple

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
        if (first == ERROR):
            print("Error")
            # Handle error
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

        request = self.createBulletinRequest(groupID, msgID, reqAct, subject, body)
        request = bytes(request, 'utf-8')

        if DEBUG:
            print("Request built:")
            print(request)

        self.connection.send(request)

        if DEBUG:
            print("Request sent.")

    def handle_response(self, resp):
        respStr = resp.decode()
        print(respStr)

def mainMenu(client):
    while True:
        read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
        selection = input("Enter one of the following commands:\n\t%exit\n\t%post [message subject]\n\t%users\n\t%leave\n\t%message [message ID]\n\t%groups\n\t%groupjoin [groupID]\n\t%grouppost [groupID] [message subject]\n\t%groupusers [groupID]\n\t%groupleave [groupID]\n\t%groupmessage [groupID] [messageID]\n")
        selection = parseSelection(selection)

        if DEBUG:
            print(selection)

        if selection[0] != 0:
            client.makeRequest(selection)
            response = client.connection.recv(4096)
            client.handle_response(response)

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

def verifyPort(port: str) -> bool:
    num = int(port)
    if num > 0xFFFF:
        print("IP address is incorrect")
        return False
    return True

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address, port = initialMenu()
    username = input("Enter your username: ")
    try:
        sock.connect((address, port))
    except socket.error:
        print("Unable to connect. Ensure the server is running and the IP address/port are correct.")
        sys.exit()
    client = Client(sock, username)
    mainMenu(client)

main()
