#server

import socket
import sqlite3 as sql

#setup port as last of umid and address setup as a pair
PORT = 8414
serverAddress = ("localhost", PORT)
status = False

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

#main server loop - accept connection - closes afterwards temporarily
while status:
    (clientSocket, clientAddr) = serverSocket.accept()

    print(f"Connection accepted from {clientAddr[0]}:{clientAddr[1]}\n")

    serverSocket.close()
    break
    