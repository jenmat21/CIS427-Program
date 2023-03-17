#server

import socket
import threading
import sqlite3 as sql
import pydb #database initialization are available via this file


#setup global variables
PORT = 8414 #PORT for server address
MSGLEN = 256
DBNAME = "stockDB"
MAXCLIENTS = 10
serverAddress = ("localhost", PORT) #change server address string if desired
status = True
clientSockets = []
clientThreads = []
usersOnline = ["" for x in range(0,10)]

#init db and setup cursor
newDb = pydb.initDB(DBNAME)
if newDb != None:
    print("Connected to database: " + DBNAME + "\n")
else:
    status = False
    print("Database failed to connect - Program exiting...")

#create server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#test connection with serverAddress - error if it doesn't work and exit program
try:
    serverSocket.bind(serverAddress)
    serverSocket.listen(5)
    print(f"Server started on {serverAddress[0]} and is listening on port {serverAddress[1]} for clients\n")
except Exception as e:
    status = False
    print(f"Server failed to start on {serverAddress[0]}:{serverAddress[1]} \nException is" + str(e) + "\nProgram exiting...")

#DATABASE FUNCTIONS
#returns user tuple with userID
def getUserInfo(cur, userID):
    cur.execute("SELECT * FROM Users WHERE ID = " + str(userID))
    user = cur.fetchall()
    if len(user) == 0:
        return(None)
    else:
        return(user)

#sends input string to client of max length MSGLEN
def sendMsg(msg, cSocket):
    if cSocket in clientSockets:
        totalSent = 0
        while len(msg) < MSGLEN:
            msg = msg + " "
        while totalSent < MSGLEN:
            try:
                sent = cSocket.send(msg[totalSent:].encode("utf-8"))
            except Exception as e:
                print(e)
                threadClose(cSocket)
                break
            if sent == 0 and msg != "":
                break
            elif msg == "":
                break
            totalSent += sent
        print("msg '" + msg.strip() + "' sent with total bytes: " + str(totalSent))

#recieves string from client
def recieveMsg(cSocket):
    if cSocket in clientSockets:
        chunks = []
        bytesRecieved = 0
        while bytesRecieved < MSGLEN:
            try:
                chunk = cSocket.recv(min(MSGLEN - bytesRecieved, 2048))
            except Exception as e:
                print(e)
                threadClose(cSocket)
                break
            if chunk.decode("utf-8") == "":
                threadClose(cSocket)
                break
            chunks.append(chunk)
            bytesRecieved += len(chunk)
        returnStr = ""
        for c in chunks:
            returnStr = returnStr + c.decode("utf-8")
        print("msg '" + returnStr.strip() + "' recieved with total bytes: " + str(bytesRecieved))
        return returnStr.strip()

#returns user balance of user with userID
def balance(cur, userID):
    UI = getUserInfo(cur, userID)
    if UI != None:
        return UI[0][5]
    else:
        return None

#buy stock funciton
def buy_stock(cur: sql.Cursor, ticker, quantity, stock_price, user_id):
    # Check if user has sufficient funds
    userBal = balance(cur, user_id)
    totalCost = float(quantity) * float(stock_price)
    if userBal < totalCost:
        return "failure"

    # Update stock quantity
    query = "SELECT * FROM Stocks WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (ticker, user_id))
    stock = cur.fetchone()
    if not (stock is None):
        print("in")
        query = "UPDATE Stocks SET stock_balance = stock_balance + ? WHERE stock_symbol = ? AND user_id = ?"
        cur.execute(query, (quantity, ticker, user_id))
    else:
        query = "INSERT INTO Stocks (stock_symbol, stock_name, stock_balance, user_id) VALUES (?, ?, ?, ?)"
        cur.execute(query, (ticker, ticker, quantity, user_id))

    # Update user balance
    query = "UPDATE Users SET usd_balance = usd_balance - ? WHERE ID = ?"
    cur.execute(query, (totalCost, user_id))

    cur.connection.commit()
    return "success"

#sell stock function
def sell_stock(cur: sql.Cursor, ticker, quantity, stock_price, user_id):
    query = "SELECT * FROM Stocks WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (ticker, user_id))
    stock = cur.fetchone()
    if stock is None: #check if user has any of said stock
        return "notExist"
    stock_balance = stock[3]
    if stock_balance < float(quantity): #check if user has enough of the stock
        return "lessQuantity"

    # Update stock quantity
    query = "UPDATE Stocks SET stock_balance = stock_balance - ? WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (quantity, ticker, user_id))

    #Check stock quanity, delete if 0
    threshold = 1e-5
    query = "SELECT stock_balance FROM Stocks WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (ticker, user_id))
    dbQuantity =  cur.fetchone()[0]
    if dbQuantity < threshold: #delete stock if user has sold all of it
        query = "DELETE FROM Stocks WHERE stock_symbol = ? AND user_id = ?"
        cur.execute(query, (ticker, user_id))


    # Update user balance
    query = "UPDATE Users SET usd_balance = usd_balance + ? WHERE ID = ?"
    cur.execute(query, (float(quantity) * float(stock_price), user_id))

    cur.connection.commit()
    return "success"

#returns a list of all stock tuples with user_id
def list_stocks(cur, user_id):
    query = "SELECT * FROM Stocks WHERE user_id = ?"
    cur.execute(query, (user_id,))
    
    stocks = cur.fetchall()

    return stocks

#server shutdown command
def shutdown():
    global status
    status = False
    cSockCopy = clientSockets[:]
    for i,sock in enumerate(cSockCopy):
        if threadClose(sock):
            pass
    print("Server shutting down...")
    serverSocket.close()

def login(cur, userID, password):
    #check if userID exists
    query = "SELECT * FROM Users WHERE user_name = ?"
    cur.execute(query, (userID,))
    user = cur.fetchone()
    if user == None:
        return "notExist"

    #check password
    if user[4] == password:
        return "success " + str(user[0]) + " " + str(user[3])
    else:
        return "passWrong " + str(user[3])
    
def threadClose(clientSocket, clientThread = None):
    sockID = None
    threadID = None
    userIndex = None
    for i,sock in enumerate(clientSockets):
        if sock.getpeername()[0] == clientSocket.getpeername()[0] and sock.getpeername()[1] == clientSocket.getpeername()[1]:
            sockID = i
            threadID = i
            userIndex = i
    if sockID != None and threadID != None:
        if clientThread == None:
            clientThread = threading.current_thread()
        global status
        if status == False:
            sendMsg("shutdown", clientSocket)
        clientSockets.pop(sockID)
        clientThreads.pop(threadID)
        try:
            user = usersOnline[userIndex]
            usersOnline.pop(userIndex)
        except Exception as e:
            pass
        addr = clientSocket.getpeername()
        print(f"Client with address {addr[0]}:{addr[1]} disconnected")
        return True
    return False

def isSocketClose(sock: socket.socket):
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        sock.setblocking(False)
        data = sock.recv(2048, socket.MSG_PEEK)
        if data.decode("utf-8") == "":
            return True
    except BlockingIOError:
        sock.setblocking(True)
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        sock.setblocking(True)
        return False
    sock.setblocking(True)
    return False

#thread function
def threadLoop(clientSocket, clientIndex):
    clientUID = None
    clientUserName = ""
    db = pydb.getDB()
    cur = db.cursor()

    #main loop
    while status and not isSocketClose(clientSocket):
        msg = recieveMsg(clientSocket)
        if msg == None:
            break
        if msg.lower() == "shutdown".lower(): #shutdown command
            if usersOnline[clientIndex] == "root":   
                sendMsg("200 OK Shutdown Initiated", clientSocket) 
                shutdown()
            else:
                print("ERROR 400 User is not root, cannot issue shutdown command")
                sendMsg("ERROR 400 User Not Root", clientSocket)
        elif msg.lower() == "quit".lower(): #quit command - listen for next client afterwards
            if threadClose(clientSocket) == True:
                pass
        elif msg.lower()[0:5] == "login".lower():
            params = msg[6:].split()
            loginTry = login(cur, params[0], params[1])

            if loginTry[0:7] == "success":
                clientUID = loginTry[8:9]
                clientUserName = loginTry[10:]
                usersOnline.insert(clientIndex, clientUserName)
                sendMsg(f"200 OK {clientUID} Successfully logged in user {clientUserName} with userID {clientUID}", clientSocket)
            elif loginTry == "notExist":
                sendMsg("403 ERROR User does not exist", clientSocket)
            elif loginTry[0:9] == "passWrong":
                sendMsg(f"403 Error Password incorrect for user {loginTry[10:]}", clientSocket)
        elif msg.lower() == "logout".lower():
            clientUID = None
            clientUserName = ""
            usersOnline.pop(clientIndex)
            sendMsg("200 OK", clientSocket)
        elif msg.lower()[0:7] == "balance".lower(): #user balance command, user id is 1 by default
            userBalance = balance(cur, clientUID)
            sendMsg("200 OK " + str(round(userBalance, 2)), clientSocket)
        elif msg.lower()[0:4] == "list".lower(): #list user's stocks, user id is 1 by default
            stocks = list_stocks(cur, clientUID)
            sendString = ""

            for stock in stocks:
                sendString = sendString + f"[{stock[0]},{stock[1]},{stock[2]},{round(stock[3], 2)},{stock[4]}] "

            sendMsg("200 OK " + sendString,clientSocket)
        elif msg.lower()[0:3] == "buy".lower(): #buy function
            params = msg[4:].split()
            success = buy_stock(cur, params[0].upper(), params[1], params[2], params[3])
            newBal = balance(cur, params[3])

            if success == "success":
                sendMsg("200 OK " + f"Successfully bought {params[1]} of {params[0].upper()}. New balance of user {params[3]}: {round(newBal, 2)}", clientSocket)
            else:
                sendMsg("400 ERROR " + "Unable to buy stock. User balance insuffecient", clientSocket)
        elif msg.lower()[0:4] == "sell".lower(): #sell function
            params = msg[5:].split()
            success = sell_stock(cur, params[0].upper(), params[1], params[2], params[3])
            newBal = balance(cur, params[3])

            if success == "success":
                sendMsg("200 OK " + f"Successfully sold {params[1]} of stock {params[0].upper()}. New balance of user {params[3]}: {round(newBal, 2)}", clientSocket)
            elif success == "lessQuantity":
                sendMsg("400 ERROR " + f"Unable to sell stock. User holds insuffecient amount of stock {params[0].upper()}", clientSocket)
            elif success == "notExist":
                sendMsg("401 ERROR " + f"Unable to sell stock. Stock entry doesn't exist", clientSocket)
        elif not isSocketClose(clientSocket):
            sendMsg("400 ERROR Invalid Command", clientSocket)

#main server loop - accept connections from clients
while status:
    if len(clientSockets) < MAXCLIENTS:
        try:
            (clientSocket, clientAddr) = serverSocket.accept()
        except Exception as e:
            break
        clientSockets.append(clientSocket)

        clientIndex = len(clientThreads)
        cThread = threading.Thread(target=threadLoop, args=(clientSocket, clientIndex))
        clientThreads.append(cThread)
        cThread.start()

        print(f"\nConnection accepted from {clientAddr[0]}:{clientAddr[1]}\nStarting new thread for client\n")