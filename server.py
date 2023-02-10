# server

import socket
import sqlite3 as sql
import os
import pydb


# setup port as last 4 of umid and address setup as a pair
PORT = 8414
serverAddress = ("localhost", PORT)
status = False
MSGLEN = 32
DBNAME = "stockDB"

# create server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# test connection with serverAddress - error if it doesn't work and exit program
try:
    serverSocket.bind(serverAddress)
    status = True
    serverSocket.listen(5)
    print(
        f"Server started on {serverAddress[0]} and is listening on port {serverAddress[1]}\n")
except Exception as e:
    print(f"Server failed to start on {serverAddress[0]}:{serverAddress[1]} \nException is" + str(
        e) + "\nProgram exiting...")

# connect to DB
if not os.path.isfile(DBNAME):
    pydb.initDB()
db = sql.connect(DBNAME)
print("Connected to  database: " + DBNAME)
cur = db.cursor()


def shutdown():
    global status
    status = False
    print("Server shutting down...")
    serverSocket.close()

# sends input string to client of max length MSGLEN


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

# recieves string from client


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

def buy_stock(ticker, quantity, stock_price, user_id):
    # Check if user has sufficient funds
    query = "SELECT usd_balance FROM Users WHERE ID = ?"
    cur.execute(query, (user_id,))
    balance = cur.fetchone()[0]
    if balance < quantity * stock_price:
        raise Exception("Insufficient funds")

    # Update stock quantity
    query = "SELECT user_id FROM Stocks WHERE stock_symbol = ?"
    cur.execute(query, (ticker))
    stock = cur.fetchone()
    if stock is not None:
        query = "UPDATE Stocks SET stock_balance = stock_balance + ? WHERE stock_symbol = ?"
        cur.execute(query, (quantity, ticker))
    query = "INSERT INTO Stocks (stock_symbol, stock_balance) VALUES (?, ?)"
    cur.execute(query, (ticker, quantity))

    # Update user balance
    query = "UPDATE Users SET usd_balance = usd_balance - ? WHERE ID = ?"
    cur.execute(query, (quantity * stock_price, user_id))

    db.commit()

#Here we will need the stock price as well to update the balance when the user sells the stock: check line 122-124
def sell_stock(ticker, quantity, stock_price, user_id):
    query = "SELECT stock_balance FROM Stocks WHERE user_id = ? AND stock_symbol = ?"
    cur.execute(query, (user_id, ticker))
    result = cur.fetchone()
    if result is None:
        print("User does not hold the stock with ticker '{}'".format(ticker))
        return
    query = "SELECT quantity FROM Stocks WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (ticker, user_id))
    stock_balance = cur.fetchone()[0]
    if stock_balance < quantity:
        raise Exception("Insufficient stock quantity")
    # Update stock quantity
    query = "UPDATE Stocks SET stock_balance = stock_balance - ? WHERE stock_symbol = ? AND user_id = ?"
    cur.execute(query, (quantity, ticker, user_id))

    # Update user balance
    query = "UPDATE Users SET usd_balance = usd_balance + ? WHERE ID = ?"
    cur.execute(query, (quantity * stock_price, user_id))

    db.commit()


def balance(user_id):
    UI = pydb.getUserInfo(5)
    query = "SELECT usd_balance FROM Users WHERE ID = ?"
    cur.execute(query, (user_id,))
    balance = cur.fetchall()
    return balance
    db.commit()


def list_stocks(user_id):
    query = "SELECT stock_name FROM Stocks WHERE user_id = ?"
    cur.execute(query, (user_id))
    stocks = cur.fetchall()
    return stocks
    db.commit()


# main server loop - accept connection - runs command loop until quit or shutdown is recieved
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
        elif msg[0:3].lower() == "buy".lower():
            arguments = msg.split(' ')
            function_arguments = arguments[1:]
            buy_stock(*function_arguments)
        elif msg[0:3].lower() == "sell".lower():
            arguments = msg.split(' ')
            function_arguments = arguments[1:]
            sell_stock(*function_arguments)
        elif msg.lower() == "balance".lower():
            balance(1)
        elif msg.lower() == "list".lower():
            list_stocks(1)
