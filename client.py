#client 

import socket

print("Welcome to the stock trading application!\n")

connectCmd = input("Please input a server address and port: ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = (connectCmd[0:connectCmd.find(":")], int(connectCmd[connectCmd.find(":") + 1:]))
connection = False

try: 
    s.connect(address)
    connection = True
    print(f"Connection successfully established with {address[0]}:{address[1]}\n")
except Exception as e:
    print(f"Connection could not be established with server on {address[0]}:{address[1]} \nException is " + str(e) + "\nProgram exiting...")

while connection:
    cmd = input("CMD>> ")
    if cmd == "stock":
        print("stocks apps")
    elif cmd.lower() == "quit".lower():
        break