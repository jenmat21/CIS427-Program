#server

import socket
import sqlite3 as sql
import os
import pydb #database manipulation commands are available via this file


#setup global variables
PORT = 8414
MSGLEN = 128
DBNAME = "stockDB"
serverAddress = ("localhost", PORT)
status = True

#init db and setup cursor
db = pydb.initDB(DBNAME)
if db != None:
    print("Connected to database: " + DBNAME + "\n")
    cur = db.cursor()
else:
    status = False
    print("Database failed to connect - Program exiting...")

#create server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#test connection with serverAddress - error if it doesn't work and exit program
try:
    serverSocket.bind(serverAddress)
    serverSocket.listen(5)
    print(f"Server started on {serverAddress[0]} and is listening on port {serverAddress[1]}\n")
except Exception as e:
    status = False
    print(f"Server failed to start on {serverAddress[0]}:{serverAddress[1]} \nException is" + str(e) + "\nProgram exiting...")

#DATABASE FUNCTIONS
def addUser(fName, lName, username, password, startBalance):
    cur.execute(f"INSERT INTO Users (first_name, last_name, user_name, password, usd_balance) VALUES ('{fName}', '{lName}', '{username}', '{password}', {startBalance})")
    db.commit()

def getUserInfo(userID):
    cur.execute("SELECT * FROM Users WHERE ID = " + str(userID))
    user = cur.fetchall()
    if len(user) == 0:
        return(None)
    else:
        return(user)

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
        if chunk.decode("utf-8") == "":
            global client
            client = False
            print(f"Client with address {clientAddr[0]}:{clientAddr[1]} disconnected \nListening for new client on port {PORT}")
            break
        chunks.append(chunk)
        bytesRecieved += len(chunk)
    returnStr = ""
    for c in chunks:
        returnStr = returnStr + c.decode("utf-8")
    print("msg '" + returnStr.strip() + "' recieved with total bytes: " + str(bytesRecieved))
    return returnStr.strip()

def balance(userID):
    UI = getUserInfo(userID)
    if UI != None:
        return UI[0][5]
    else:
        return None

def buy_stock(ticker, quantity, stock_price, user_id):
    # Check if user has sufficient funds
    userBal = balance(user_id)
    totalCost = float(quantity) * float(stock_price)
    if userBal < totalCost:
        return "failure"

    # Update stock quantity
    query = "SELECT * FROM Stocks WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (ticker, user_id))
    stock = cur.fetchall()
    if stock != None:
        query = "UPDATE Stocks SET stock_balance = stock_balance + ? WHERE stock_symbol = ? AND user_id = ?"
        cur.execute(query, (quantity, ticker, user_id))
    query = "INSERT INTO Stocks (stock_symbol, stock_name, stock_balance, user_id) VALUES (?, ?, ?, ?)"
    cur.execute(query, (ticker, ticker, quantity, user_id))

    # Update user balance
    query = "UPDATE Users SET usd_balance = usd_balance - ? WHERE ID = ?"
    cur.execute(query, (totalCost, user_id))

    db.commit()
    return "success"

def sell_stock(ticker, quantity, stock_price, user_id):
    query = "SELECT * FROM Stocks WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (ticker, user_id))
    stock = cur.fetchall()
    if stock == None:
        return "notExist"
    stock_balance = stock[0][3]
    if stock_balance < float(quantity):
        return "lessQuantity"

    # Update stock quantity
    query = "UPDATE Stocks SET stock_balance = stock_balance - ? WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (quantity, ticker, user_id))

    #Check stock quanity, delete if 0
    threshold = 1e-5
    query = "SELECT stock_balance FROM Stocks WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (ticker, user_id))
    dbQuantity =  cur.fetchone()[0]
    if dbQuantity < threshold:
        query = "DELETE FROM Stocks WHERE stock_symbol = ? AND user_id = ?"
        cur.execute(query, (ticker, user_id))


    # Update user balance
    query = "UPDATE Users SET usd_balance = usd_balance + ? WHERE ID = ?"
    cur.execute(query, (float(quantity) * float(stock_price), user_id))

    db.commit()
    return "success"

def list_stocks(user_id):
    query = "SELECT * FROM Stocks WHERE user_id = ?"
    cur.execute(query, (user_id,))
    
    stocks = cur.fetchall()

    return stocks

#server shutdown command
def shutdown():
    global status
    status = False
    print("Server shutting down...")
    serverSocket.close()

#main server loop - accept connection - runs command loop until quit or shutdown is recieved
while status:
    (clientSocket, clientAddr) = serverSocket.accept()
    print(f"Connection accepted from {clientAddr[0]}:{clientAddr[1]}\n")
    client = True

    if (getUserInfo(1) == None):
        addUser("NULL", "NULL", "client", "NULL", 100)

    while status and client:
        msg = recieveMsg()
        if msg.lower() == "shutdown".lower():
            shutdown()
        elif msg.lower() == "quit".lower():
            print(f"Client with address {clientAddr[0]}:{clientAddr[1]} disconnected \nListening for new client on port {PORT}")
            client = False  
        elif msg.lower()[0:7] == "balance".lower():
            userBalance = balance(1)

            sendMsg("200 OK " + str(round(userBalance, 2)) + " " + str(1))
        elif msg.lower()[0:4] == "list".lower():
            stocks = list_stocks(1)
            sendString = ""

            for stock in stocks:
                sendString = sendString + f"[{stock[0]},{stock[1]},{stock[2]},{round(stock[3], 2)},{stock[4]}] "

            sendMsg("200 OK " + sendString)
        elif msg.lower()[0:3] == "buy".lower():
            params = msg[4:].split()
            success = buy_stock(params[0], params[1], params[2], params[3])
            newBal = balance(params[3])

            if success == "success":
                sendMsg("200 OK " + f"Successfully bought {params[1]} of {params[0]}. New balance of user {params[3]}: {round(newBal, 2)}")
            else:
                sendMsg("400 ERROR " + "Unable to buy stock. User balance insuffecient")
        elif msg.lower()[0:4] == "sell".lower():
            params = msg[5:].split()
            success = sell_stock(params[0], params[1], params[2], params[3])
            newBal = balance(params[3])

            if success == "success":
                sendMsg("200 OK " + f"Successfully sold {params[1]} of stock {params[0]}. New balance of user {params[3]}: {round(newBal, 2)}")
            elif success == "lessQuantity":
                sendMsg("400 ERROR " + f"Unable to sell stock. User holds insuffecient amount of stock {params[0]}")
            elif success == "notExist":
                sendMsg("400 ERROR " + f"Unable to sell stock. Stock entry doesn't exist")
        else:
            sendMsg("400 ERROR Invalid Command")
        