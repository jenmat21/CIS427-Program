#server

import socket
import sqlite3 as sql

PORT = 8414
serverAddress = ("localhost", PORT)
status = False

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    serverSocket.bind(serverAddress)
    status = True
    serverSocket.listen(5)
    print(f"Server started on {serverAddress[0]} and is listening on port {serverAddress[1]}\n")
except Exception as e:
    print(f"Server failed to start on {serverAddress[0]}:{serverAddress[1]} \nException is" + str(e) + "\nProgram exiting...")

while status:
    (clientSocket, clientAddr) = serverSocket.accept()

    print(f"Connection accepted from {clientAddr[0]}:{clientAddr[1]}\n")

    serverSocket.close()
    break
    