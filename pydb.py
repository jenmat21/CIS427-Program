#database file

import sqlite3 as sql
db = None
cur = None

#db init
def initDB(DBNAME):
    global db
    global cur
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
    
#db get user info
def getUserInfo(userID):
        cur.execute("SELECT * FROM Users WHERE ID = " + str(userID))
        user = cur.fetchall()
        if len(user) == 0:
                return(None)
        else:
                 return(user)

#db addUser
def addUser(fName, lName, username, password, startBalance):
        print("in")
        cur.execute(f"INSERT INTO Users (first_name, last_name, user_name, password, usd_balance) VALUES ('{fName}', '{lName}', '{username}', '{password}', {startBalance})")