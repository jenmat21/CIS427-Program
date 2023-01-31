#database file

import sqlite3 as sql

DBNAME = "stockDB"

def initDB():
    db = sql.connect(DBNAME)
    print("Database " + DBNAME + " created")

    cur = db.cursor()

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
    

