#database file

import sqlite3 as sql

#db init
def initDB(DBNAME):
    try:
        db = sql.connect(DBNAME)
        print("Database " + DBNAME + " created")
        cur = db.cursor()
    except Exception as e:
        print("Database failed to initialize with error " + str(e))
        return None


    cur.execute('''CREATE TABLE IF NOT EXISTS Users 
           ( 
            ID integer NOT NULL PRIMARY KEY AUTOINCREMENT,  
            first_name text, 
            last_name text, 
            user_name text NOT NULL, 
            password text,          
            usd_balance real NOT NULL             
            ); ''')
    print("Users table created in database")

    cur.execute('''CREATE TABLE IF NOT EXISTS Stocks  
           ( 
            ID integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
            stock_symbol text NOT NULL, 
            stock_name text NOT NULL, 
            stock_balance real, 
            user_id integer,
            FOREIGN KEY (user_id) REFERENCES Users (ID)             
            ); ''')
    print("Stocks table created in database")
    return db
    
#db buy
def buyStock(userID, stockSymbol, amount, price):
        pass

#db sell
def sellStock(userID, stockSymbol, amount, price):
        pass
#db get stock list
def getStockList():
        pass

#db get stock
def getStock(stockSymbol):
        pass

#db get user info
def getUserInfo(userID):
        pass

#db addUser
def addUser(fName, lName, username, password, startBalance):
        pass