#database file

import sqlite3 as sql
dbName = ""

#db init function called by server - in a seperate file to reduce clutter in the server file
def initDB(DBNAME):
    try:
        db = sql.connect(DBNAME)
        global dbName 
        dbName = DBNAME
        print("Database " + DBNAME + " created")
        cur = db.cursor()
    except Exception as e:
        print("Database failed to initialize with error " + str(e))
        return None

    #create users table
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

    #Initialize tuples in users table
    cur.execute('''INSERT INTO Users (user_name, password, usd_balance) 
                    VALUES ("root", "root01", 100),
                    ("Mary", "Mary01", 100),
                    ("John", "John01", 100),
                    ("Moe", "Moe01", 100); ''')
    print("Users table filled with default users")

    #create stocks table
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
    db.commit()
    cur.close()
    return db

def getDB():
    retDB = sql.connect(dbName)
    return retDB