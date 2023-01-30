#client 

import socket

print("Welcome to the stock trading application!\n")

#create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#get server address and create address pair
connectCmd = input("Please input a server address and port: ")
address = (connectCmd[0:connectCmd.find(":")], int(connectCmd[connectCmd.find(":") + 1:]))
connection = False

#try to connect to server - error and exit program if it fails
try: 
    s.connect(address)
    connection = True
    print(f"Connection successfully established with {address[0]}:{address[1]}\n")
except Exception as e:
    print(f"Connection could not be established with server on {address[0]}:{address[1]} \nException is " + str(e) + "\nProgram exiting...")

def quit():
    s.close()
    print("Connection broken... Program exiting...")
    connection = False

def sendMsg(msg):
    totalSent = 0
    while totalSent < len(msg):
        sent = s.send(msg[totalSent:].encode("utf-8"))
        if sent == 0:
            quit()
        totalSent += sent
    print("msg sent with total bytes " + totalSent)

#main client command loop - "quit" to quit the program
while connection:
    cmd = input("CMD>> ")
    if cmd[0:8].lower() == "balance".lower():
        sendMsg(cmd)
    elif cmd.lower() == "quit".lower():
        quit()