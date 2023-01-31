#server

import socket
import sqlite3 as sql

#setup port as last 4 of umid and address setup as a pair
PORT = 8414
serverAddress = ("localhost", PORT)
status = False
MSGLEN = 32

#create server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#test connection with serverAddress - error if it doesn't work and exit program
try:
    serverSocket.bind(serverAddress)
    status = True
    serverSocket.listen(5)
    print(f"Server started on {serverAddress[0]} and is listening on port {serverAddress[1]}\n")
except Exception as e:
    print(f"Server failed to start on {serverAddress[0]}:{serverAddress[1]} \nException is" + str(e) + "\nProgram exiting...")

def shutdown():
    global status
    status = False
    print("Server shutting down...")
    serverSocket.close()

#sends input string to client of max length MSGLEN
def sendMsg(msg):
    totalSent = 0
    while len(msg) < MSGLEN:
        msg = msg + " "
    while totalSent < MSGLEN:
        sent = clientSocket.send(msg[totalSent:].encode("utf-8"))
        if sent == 0 and msg != "":
            quit()
            break
        elif msg == "":
            break
        totalSent += sent
    print("msg '" + msg.strip() + "' sent with total bytes: " + str(totalSent))

#recieves string from client
def recieveMsg():
    chunks = []
    bytesRecieved = 0
    while bytesRecieved < MSGLEN:
        chunk = clientSocket.recv(min(MSGLEN - bytesRecieved, 2048))
        print(str(bytesRecieved) + ":" + str(chunk))
        if chunk == b'':
            global client
            client = False
            break
        chunks.append(chunk)
        bytesRecieved += len(chunk)
    returnStr = ""
    for c in chunks:
        returnStr = returnStr + c.decode("utf-8")
    return returnStr.strip()

#main server loop - accept connection - runs command loop until quit or shutdown is recieved
while status:
    (clientSocket, clientAddr) = serverSocket.accept()
    print(f"Connection accepted from {clientAddr[0]}:{clientAddr[1]}\n")
    client = True

    while status and client:
        msg = recieveMsg()
        print(msg)
        if msg.lower() == "shutdown".lower():
            shutdown()
        elif msg.lower() == "quit".lower():
            client = False
    