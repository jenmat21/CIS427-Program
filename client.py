#client 

import socket

print("Welcome to the stock trading application!\n")

#create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#get server address and create address pair
connectCmd = input("Please input a server address and port: ")
address = (connectCmd[0:connectCmd.find(":")], int(connectCmd[connectCmd.find(":") + 1:]))
connection = False
MSGLEN = 128

#try to connect to server - error and exit program if it fails
try: 
    s.connect(address)
    connection = True
    print(f"Connection successfully established with {address[0]}:{address[1]}\n")
except Exception as e:
    print(f"Connection could not be established with server on {address[0]}:{address[1]} \nException is " + str(e) + "\nProgram exiting...")

#sends input string of max length MSGLEN to the server
def sendMsg(msg):
    totalSent = 0
    while len(msg) < MSGLEN:
        msg = msg + " "
    while totalSent < MSGLEN:
        sent = s.send(msg[totalSent:].encode("utf-8"))
        if sent == 0 and msg != "":
            quit()
            break
        elif msg == "":
            break
        totalSent += sent
    print("msg '" + msg.strip() + "' sent with total bytes: " + str(totalSent))

#recieves string from server
def recieveMsg():
    chunks = []
    bytesRecieved = 0
    while bytesRecieved < MSGLEN:
        chunk = s.recv(min(MSGLEN - bytesRecieved, 2048))
        if chunk.decode("utf-8") == "":
            quitClient()
            break
        chunks.append(chunk)
        bytesRecieved += len(chunk)
    returnStr = ""
    for c in chunks:
        returnStr = returnStr + c.decode("utf-8")
    print("msg '" + returnStr.strip() + "' recieved with total bytes: " + str(bytesRecieved))
    return returnStr.strip()

def quitClient():
    s.close()
    print("Connection broken - Program exiting...")
    global connection 
    connection = False
    return

#main client command loop - "quit" to quit the program and "shutdown" to shutdown the server
while connection:
    cmd = input("CMD>> ")
    if cmd[0:1].lower() == "1".lower():
        sendMsg(cmd[2:])
    elif cmd.lower() == "shutdown".lower():
        sendMsg(cmd)
        print("Shutting down server...")
        quitClient()
    elif cmd.lower() == "quit".lower():
        sendMsg("quit")
        quitClient()
    elif cmd.lower()[0:7] == "balance".lower():
        sendMsg(cmd)
        response = recieveMsg()
        if response[0:3] == "200":
            print(f"Balance for user {1}: " + response[7:])
        elif response[0:3] == "400":
            print(response)
    elif cmd.lower()[0:5] == "list".lower():
        sendMsg(cmd)
        response = recieveMsg()
        if response[0:3] == "200":
            print(f"The list of stock records for user {1}:")

            stocks = response[7:].split()
            stocksList = []
            for stock in stocks:
                stockTuple = stock[1:-1].split(",")
                stocksList.append(stockTuple)

            for stock in stocksList:
                print(stock[0], stock[1], stock[3], stock[4])
        elif response[0:3] == "400":
            print(response)
    elif cmd.lower()[0:3] == "buy".lower():
        parameters = cmd.split(" ")
        price_flag = False
        stock_flag = False
        uid_flag = False
        symbol = ""
        if len(parameters) == 0 or len(parameters) == 1:
            symbol = str(input("Please enter stock symbol\n"))
            while stock_flag == False:
                try:
                    stock = float(input("Please enter stock ammount as a float or integer\n"))
                    stock_flag = True
                except:
                    stock_flag = False
            while price_flag == False:
                try:
                    price = float(input("Please enter stock price per share as a float or integer\n"))
                    price_flag = True
                except:
                    price_flag = False
            while uid_flag == False:
                try:
                    uid = int(input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "BUY " + symbol +" "+ stock +" "+ price +" "+ uid+"\n"
        elif len(parameters) == 2:
            symbol = str(parameters[1])
            while stock_flag == False:
                try:
                    stock = float(input("Please enter stock ammount as a float or integer\n"))
                    stock_flag = True
                except:
                    stock_flag = False
            while price_flag == False:
                try:
                    price = float(input("Please enter stock price per share as a float or integer\n"))
                    price_flag = True
                except:
                    price_flag = False
            while uid_flag == False:
                try:
                    uid = int(input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "BUY " + symbol +" "+ price +" "+ stock +" "+ uid+"\n"
        elif len(parameters) == 3:
            symbol = str(parameters[1])
            try:
                stock = float(parameters[2])
            except:
                while stock_flag == False:
                    try:
                        stock = float(input("Please enter stock ammount as a float or integer\n"))
                        stock_flag = True
                    except:
                        stock_flag = False
            while price_flag == False:
                try:
                    price = float(input("Please enter stock price per share as a float or integer\n"))
                    price_flag = True
                except:
                    price_flag = False
            
            while uid_flag == False:
                try:
                    uid = int(input("Please enter user id numberas an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "BUY " + symbol +" "+ price +" "+ stock +" "+ uid+"\n"
        elif len(parameters) == 4:
            symbol = str(parameters[1])
            try:
                stock = float(parameters[2])
            except:
                while stock_flag == False:
                    try:
                        stock = float(input("Please enter stock ammount as a float or integer\n"))
                        stock_flag = True
                    except:
                        stock_flag = False
            try:
                price = float(parameters[3])
            except:
                while price_flag == False:
                    try:
                        price = float(input("Please enter stock price per share as a float or integer\n"))
                        price_flag = True
                    except:
                        price_flag = False
            while uid_flag == False:
                try:
                    uid = int(input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "BUY " + symbol +" "+ price +" "+ stock +" "+ uid+"\n"
        elif len(parameters) >= 5:
            symbol = str(parameters[1])
            try:
                stock = float(parameters[2])
            except:
                while stock_flag == False:
                    try:
                        stock = float(input("Please enter stock ammount as a float or integer\n"))
                        stock_flag = True
                    except:
                        stock_flag = False
            try:
                price = float(parameters[3])
            except:
                while price_flag == False:
                    try:
                        price = float(input("Please enter stock price per share as a float or integer\n"))
                        price_flag = True
                    except:
                        price_flag = False
            try:
                uid = int(parameters[4])
            except:
                while uid_flag == False:
                    try:
                        uid = float(input("Please enter user id number as an integer\n"))
                        uid_flag = True
                    except:
                        uid_flag = False
            cmd = "BUY " + symbol +" "+ price +" "+ stock +" "+ uid+"\n"
        sendMsg(cmd)
        response = recieveMsg()
        if response[0:3] == "200":
            print(response[7:])
        elif response[0:3] == "400":
            print(response)
    elif cmd.lower()[0:4] == "sell".lower():
        parameters = cmd.split(" ")
        price_flag = False
        stock_flag = False
        uid_flag = False
        symbol = ""
        if len(parameters) == 0 or len(parameters) == 1:
            symbol = str(input("Please enter stock symbol\n"))
            while price_flag == False:
                try:
                    price = float(input("Please enter stock price per share as a float or integer\n"))
                    price_flag = True
                except:
                    price_flag = False
            while stock_flag == False:
                try:
                    stock = float(input("Please enter stock ammount as a float or integer\n"))
                    stock_flag = True
                except:
                    stock_flag = False
            while uid_flag == False:
                try:
                    uid = int(input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "SELL " + symbol +" "+ price +" "+ stock +" "+ uid+"\n"
        elif len(parameters) == 2:
            symbol = str(parameters[1])
            while price_flag == False:
                try:
                    price = float(input("Please enter stock price per share as a float or integer\n"))
                    price_flag = True
                except:
                    price_flag = False
            while stock_flag == False:
                try:
                    stock = float(input("Please enter stock ammount as a float or integer\n"))
                    stock_flag = True
                except:
                    stock_flag = False
            while uid_flag == False:
                try:
                    uid = int(input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "SELL " + symbol +" "+ price +" "+ stock +" "+ uid+"\n"
        elif len(parameters) == 3:
            symbol = str(parameters[1])
            try:
                price = float(parameters[2])
            except:
                while price_flag == False:
                    try:
                        price = float(input("Please enter stock price per share as a float or integer\n"))
                        price_flag = True
                    except:
                        price_flag = False
            while stock_flag == False:
                try:
                    stock = float(input("Please enter stock ammount as a float or integer\n"))
                    stock_flag = True
                except:
                    stock_flag = False
            while uid_flag == False:
                try:
                    uid = int(input("Please enter user id numberas an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "SELL " + symbol +" "+ price +" "+ stock +" "+ uid+"\n"
        elif len(parameters) == 4:
            symbol = str(parameters[1])
            try:
                price = float(parameters[2])
            except:
                while price_flag == False:
                    try:
                        price = float(input("Please enter stock price per share as a float or integer\n"))
                        price_flag = True
                    except:
                        price_flag = False
            try:
                stock = float(parameters[3])
            except:
                while stock_flag == False:
                    try:
                        stock = float(input("Please enter stock ammount as a float or integer\n"))
                        stock_flag = True
                    except:
                        stock_flag = False
            while uid_flag == False:
                try:
                    uid = int(input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "SELL " + symbol +" "+ price +" "+ stock +" "+ uid+"\n"
        elif len(parameters) >= 5:
            symbol = str(parameters[1])
            try:
                price = float(parameters[2])
            except:
                while price_flag == False:
                    try:
                        price = float(input("Please enter stock price per share as a float or integer\n"))
                        price_flag = True
                    except:
                        price_flag = False
            try:
                stock = float(parameters[3])
            except:
                while stock_flag == False:
                    try:
                        stock = float(input("Please enter stock ammount as a float or integer\n"))
                        stock_flag = True
                    except:
                        stock_flag = False
            try:
                uid = int(parameters[4])
            except:
                while uid_flag == False:
                    try:
                        uid = float(input("Please enter user id number as an integer\n"))
                        uid_flag = True
                    except:
                        uid_flag = False
            cmd = "SELL " + symbol +" "+ price +" "+ stock +" "+ uid+"\n"
        sendMsg(cmd)
        response = recieveMsg()
        if response[0:3] == "200":
            print(response[7:])
        elif response[0:3] == "400":
            print(response)