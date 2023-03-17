# client

import socket

print("Welcome to the stock trading application!\n")

# create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get server address and create address pair
connectCmd = input("Please input a server address and port: ")
address = (connectCmd[0:connectCmd.find(":")],
           int(connectCmd[connectCmd.find(":") + 1:]))
connection = False
MSGLEN = 256

# try to connect to server - error if it fails and prompt again for server address
while connection == False:
    try:
        s.connect(address)
        connection = True
        print(
            f"Connection successfully established with {address[0]}:{address[1]}\n")
    except Exception as e:
        print(
            f"Connection could not be established with server on {address[0]}:{address[1]} \nException is " + str(e))
        connectCmd = input("Please input another server address and port: ")
        address = (connectCmd[0:connectCmd.find(":")],
                   int(connectCmd[connectCmd.find(":") + 1:]))


# sends input string of max length MSGLEN to the server
def sendMsg(msg):
    totalSent = 0
    while len(msg) < MSGLEN:
        msg = msg + " "
    while totalSent < MSGLEN:
        sent = s.send(msg[totalSent:].encode("utf-8"))
        if sent == 0 and msg != "":
            quitClient()
            break
        elif msg == "":
            break
        totalSent += sent
    print("msg '" + msg.strip() + "' sent with total bytes: " + str(totalSent))

# recieves string from server


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
    print("msg '" + returnStr.strip() +
          "' recieved with total bytes: " + str(bytesRecieved))
    return returnStr.strip()

# client close function


def quitClient():
    s.close()
    print("Connection broken - Program exiting...")
    global connection
    connection = False
    return


# main client command loop - "quit" to quit the program and "shutdown" to shutdown the server
loggedIn = False
uid = None
userName = None
while connection:
    cmd = input("CMD>> ")

    # check login
    if loggedIn == False and (cmd.lower() != "quit" and cmd[0:5].lower() != "login"):
        print("Command cannot be executed. You are not logged in. \nPlease try the login command or quit the program.")
        continue

    if cmd.lower() == "shutdown".lower():
        sendMsg(cmd)
        print("Shutting down server...")
        quitClient()
    elif cmd.lower() == "quit".lower():
        sendMsg("quit")
        quitClient()
    elif cmd[0:5].lower() == "login".lower():
        sendMsg(cmd)
        response = recieveMsg()
        if response[0:3] == "200":
            loggedIn = True
            uid = response[7:8]
            userName = cmd.split()[1]
            print(response[9:])
        elif response[0:3] == "403":
            print(response)
    elif cmd.lower() == "logout".lower():
        sendMsg(cmd)
        response = recieveMsg()
        uid = None
        userName = ""
        loggedIn = False
    elif cmd.lower()[0:7] == "balance".lower():
        sendMsg(cmd)
        response = recieveMsg()
        if response[0:3] == "200":
            print(f"Balance for user {userName}: " + response[7:])
        elif response[0:3] == "400":
            print(response)
    elif cmd.lower()[0:4] == "list".lower():
        sendMsg(cmd)
        response = recieveMsg()
        if response[0:3] == "200":
            print(f"The list of stock records for user {userName}:")

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
        price_flag = False  # boolean for the price per share
        stock_flag = False  # boolean for stock amount
        uid_flag = False  # boolean for user id
        symbol = ""
        # "BUY" or "BUY " case we need a stock symbol, price per share, stock ammount and a user id
        if len(parameters) == 0 or len(parameters) == 1:
            symbol = str(input("Please enter stock symbol\n"))
            while stock_flag == False:
                try:
                    # Ensure that stock is a positive number
                    stock = float(
                        input("Please enter stock ammount as a float or integer\n"))
                    if stock > 0:
                        stock_flag = True
                except:
                    stock_flag = False
            while price_flag == False:
                try:
                    # Ensure that price is a positive number
                    price = float(
                        input("Please enter stock price per share as a float or integer\n"))
                    if price > 0:
                        price_flag = True
                except:
                    price_flag = False
            while uid_flag == False:
                try:
                    # Ensure that uid is an integer
                    uid = int(
                        input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "BUY " + symbol + " " + \
                str(stock) + " " + str(price) + " " + \
                str(uid)+"\n"  # The message to be sent
        elif len(parameters) == 2:  # "BUY symbol" case
            symbol = str(parameters[1])
            while stock_flag == False:
                try:
                    stock = float(
                        input("Please enter stock ammount as a float or integer\n"))
                    if stock > 0:
                        stock_flag = True
                except:
                    stock_flag = False
            while price_flag == False:
                try:
                    price = float(
                        input("Please enter stock price per share as a float or integer\n"))
                    if price > 0:
                        price_flag = True
                except:
                    price_flag = False
            while uid_flag == False:
                try:
                    uid = int(
                        input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "BUY " + symbol + " " + \
                str(stock) + " " + str(price) + " " + str(uid)+"\n"
        elif len(parameters) == 3:  # "BUY symbol pricepershare" case
            symbol = str(parameters[1])
            try:
                stock = float(parameters[2])
            except:
                while stock_flag == False:
                    try:
                        stock = float(
                            input("Please enter stock ammount as a float or integer\n"))
                        if stock > 0:
                            stock_flag = True
                    except:
                        stock_flag = False
            while price_flag == False:
                try:
                    price = float(
                        input("Please enter stock price per share as a float or integer\n"))
                    if price > 0:
                        price_flag = True
                except:
                    price_flag = False

            while uid_flag == False:
                try:
                    uid = int(
                        input("Please enter user id numberas an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "BUY " + symbol + " " + \
                str(stock) + " " + str(price) + " " + \
                str(uid)+"\n"  # The message to be sent
        elif len(parameters) == 4:  # "BUY symbol pricepershare stockamount" case
            symbol = str(parameters[1])
            try:
                stock = float(parameters[2])
            except:
                while stock_flag == False:
                    try:
                        stock = float(
                            input("Please enter stock ammount as a float or integer\n"))
                        if stock > 0:
                            stock_flag = True
                    except:
                        stock_flag = False
            try:
                price = float(parameters[3])
            except:
                while price_flag == False:
                    try:
                        price = float(
                            input("Please enter stock price per share as a float or integer\n"))
                        if price > 0:
                            price_flag = True
                    except:
                        price_flag = False
            while uid_flag == False:
                try:
                    uid = int(
                        input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "BUY " + symbol + " " + \
                str(stock) + " " + str(price) + " " + \
                str(uid)+"\n"  # Message to be sent
        elif len(parameters) >= 5:  # "BUY symbol price per share stock amount uid" and corners case
            symbol = str(parameters[1])
            try:
                stock = float(parameters[2])
            except:
                while stock_flag == False:
                    try:
                        stock = float(
                            input("Please enter stock ammount as a float or integer\n"))
                        if stock > 0:
                            stock_flag = True
                    except:
                        stock_flag = False
            try:
                price = float(parameters[3])
            except:
                while price_flag == False:
                    try:
                        price = float(
                            input("Please enter stock price per share as a float or integer\n"))
                        if price > 0:
                            price_flag = True
                    except:
                        price_flag = False
            try:
                uid = int(parameters[4])
            except:
                while uid_flag == False:
                    try:
                        uid = float(
                            input("Please enter user id number as an integer\n"))
                        uid_flag = True
                    except:
                        uid_flag = False
            cmd = "BUY " + symbol + " " + \
                str(stock) + " " + str(price) + " " + str(uid)+"\n"
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
        if len(parameters) == 0 or len(parameters) == 1:  # "SELL" and "SELL " case
            symbol = str(input("Please enter stock symbol\n"))
            # Ensure real positive numbers for price and stock amount, ensure integer for uid
            while price_flag == False:
                try:
                    price = float(
                        input("Please enter stock price per share as a float or integer\n"))
                    if price > 0:
                        price_flag = True
                except:
                    price_flag = False
            while stock_flag == False:
                try:
                    stock = float(
                        input("Please enter stock ammount as a float or integer\n"))
                    if stock > 0:
                        stock_flag = True
                except:
                    stock_flag = False
            while uid_flag == False:
                try:
                    uid = int(
                        input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "SELL " + symbol + " " + \
                str(stock) + " " + str(price) + " " + str(uid)+"\n"
        elif len(parameters) == 2:  # "Sell symbol" case
            symbol = str(parameters[1])
            # Ensure real positive numbers for price and stock amount, ensure integer for uid
            while price_flag == False:
                try:
                    price = float(
                        input("Please enter stock price per share as a float or integer\n"))
                    if price > 0:
                        price_flag = True
                except:
                    price_flag = False
            while stock_flag == False:
                try:
                    stock = float(
                        input("Please enter stock ammount as a float or integer\n"))
                    if stock > 0:
                        stock_flag = True
                except:
                    stock_flag = False
            while uid_flag == False:
                try:
                    uid = int(
                        input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "SELL " + symbol + " " + \
                str(stock) + " " + str(price) + " " + str(uid)+"\n"
        elif len(parameters) == 3:  # "SELL symbol stock" case
            symbol = str(parameters[1])
            # Ensure real positive numbers for price and stock amount, ensure integer for uid
            try:
                stock = float(parameters[2])
            except:
                while stock_flag == False:
                    try:
                        stock = float(
                            input("Please enter stock ammount as a float or integer\n"))
                        if stock > 0:
                            stock_flag = True
                    except:
                        stock_flag = False
            while price_flag == False:
                try:
                    price = float(
                        input("Please enter stock price per share as a float or integer\n"))
                    if price > 0:
                        price_flag = True
                except:
                    price_flag = False
            while uid_flag == False:
                try:
                    uid = int(
                        input("Please enter user id numberas an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "SELL " + symbol + " " + \
                str(stock) + " " + str(price) + " " + str(uid)+"\n"
        elif len(parameters) == 4:  # "SELL symbol stock price" case
            symbol = str(parameters[1])
            # Ensure real positive numbers for price and stock amount, ensure integer for uid
            try:
                price = float(parameters[3])
            except:
                while price_flag == False:
                    try:
                        price = float(
                            input("Please enter stock price per share as a float or integer\n"))
                        if price > 0:
                            price_flag = True
                    except:
                        price_flag = False
            try:
                stock = float(parameters[2])
            except:
                while stock_flag == False:
                    try:
                        stock = float(
                            input("Please enter stock ammount as a float or integer\n"))
                        if stock > 0:
                            stock_flag = True
                    except:
                        stock_flag = False
            while uid_flag == False:
                try:
                    uid = int(
                        input("Please enter user id number as an integer\n"))
                    uid_flag = True
                except:
                    uid_flag = False
            cmd = "SELL " + symbol + " " + \
                str(stock) + " " + str(price) + " " + str(uid)+"\n"
        elif len(parameters) >= 5:  # "SELL symbol stock price uid" and corner case
            symbol = str(parameters[1])
            # Ensure real positive numbers for price and stock amount, ensure integer for uid
            try:
                price = float(parameters[3])
            except:
                while price_flag == False:
                    try:
                        price = float(
                            input("Please enter stock price per share as a float or integer\n"))
                        if price > 0:
                            price_flag = True
                    except:
                        price_flag = False
            try:
                stock = float(parameters[2])
            except:
                while stock_flag == False:
                    try:
                        stock = float(
                            input("Please enter stock ammount as a float or integer\n"))
                        if stock > 0:
                            stock_flag = True
                    except:
                        stock_flag = False
            try:
                uid = int(parameters[4])
            except:
                while uid_flag == False:
                    try:
                        uid = int(
                            input("Please enter user id number as an integer\n"))
                        uid_flag = True
                    except:
                        uid_flag = False
            cmd = "SELL " + symbol + " " + \
                str(stock) + " " + str(price) + " " + str(uid)+"\n"
        sendMsg(cmd)
        response = recieveMsg()
        if response[0:3] == "200":
            print(response[7:])
        elif response[0:3] == "400" or response[0:3] == "401":
            print(response)
    else:
        print(f"command '{cmd}' not recognized... please try again")
