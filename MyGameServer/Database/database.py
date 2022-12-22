import mysql.connector
from mysql.connector import errorcode
import json

def NewChar(name, charData):
    global mydb
    global mycursor
    sql = "INSERT INTO gamesave (name, chardata) VALUES (%s, %s)"
    val = (name, charData)
    mycursor.execute(sql, val)
    mydb.commit()

def ClearSave():
    global mydb
    global mycursor
    mycursor.execute("DELETE FROM gamesave")
    mydb.commit()


def Init():
    global mydb
    global mycursor

    try:
        mydb = mysql.connector.connect(
            host = "localhost",
            port ='3306',
            user ='admin',
            passwd = 'adminpass'
            )
    except mysql.connector.Error as err:
        if err.errno== errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


    mycursor = mydb.cursor()
    mycursor.execute('SHOW DATABASES')

    for result in mycursor:
        if "adventuredatabase" in result:
            break
    else:
        mycursor.execute('CREATE DATABASE adventuredatabase')
        mycursor.execute('USE adventuredatabase')
        mycursor.execute('CREATE Table gamesave (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), chardata JSON)')
        NewChar('me', json.dumps({"x":320, "y":240}))
        sql = "INSERT INTO gamesave (name, chardata) VALUES (%s, %s)"
        val = ("me", '{"x":320,"y":240}')
        mycursor.execute(sql, val)
        mydb.commit() #any changes in data, use commit after


    mydb = mysql.connector.connect(
            host = "localhost",
            port ='3306',
            user ='admin',
            passwd = 'adminpass',
            database = "adventuredatabase"
            )

    mycursor = mydb.cursor()

def InsertCharPos(id, x, y):
    global mycursor
    global mydb

    if id == 0:
        name = "me"
    elif type(id) == int:
        name = "you"
    else:
        name = str(id)


    if not isinstance(x, int) or not isinstance(y, int):
        return False

    j = {"x":x, "y":y}
    sql = "INSERT INTO gamesave (name, chardata) VALUES (%s, %s)"
    val = (name, json.dumps(j))
    mycursor.reset()
    mycursor.execute(sql, val) 
    
    mydb.commit()

    return True


def GetCharData(id):
    global mycursor
    
    if id == 0:
        name = "me"
    elif type(id) == int:
        name = "you"
    else:
        name = str(id)
    mycursor.reset()
    mycursor.execute(f"SELECT chardata FROM gamesave WHERE name='{name}'")
    result = mycursor.fetchone()
    return result[0]

def GetCharPos(id):
    result = GetCharData(id)
    dict = json.loads(result)
    return dict['x'], dict['y']

def SetCharPos(id, x, y):
    global mycursor
    global mydb

    if id == 0:
        name = "me"
    elif type(id) == int:
        name = "you"
    else:
        name = str(id)


    if not isinstance(x, int) or not isinstance(y, int):
        return False

    j = {"x":x, "y":y}
    sql = "UPDATE gamesave SET charData=%s WHERE name=%s"
    val = (json.dumps(j), name)
    mycursor.reset()
    mycursor.execute(sql, val) 
    
    mydb.commit()

    return True
