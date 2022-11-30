import sqlite3


def getTemp(tag_num):
    try:
        sqliteConnection = sqlite3.connect('/home/shabah/IoTProject/IoT/Phase4/real_iot.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = f"""SELECT * from user_preferences  WHERE rfid_tag_num = '{tag_num}'"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        for row in records:
            temp1 = row[2]
            print("Temp: ", row[2])
            print("\n")

        cursor.close()
        return temp1

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
            
def getLight(tag_num):
    try:
        sqliteConnection = sqlite3.connect('/home/shabah/IoTProject/IoT/Phase4/real_iot.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = f"""SELECT * from user_preferences  WHERE rfid_tag_num = '{tag_num}'"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        for row in records:
            light1 = row[3]
            print("Light: ", row[3])
            print("\n")

        cursor.close()
        return light1

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
            
def getHumidity(tag_num):
    try:
        sqliteConnection = sqlite3.connect('/home/shabah/IoTProject/IoT/Phase4/real_iot.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = f"""SELECT * from user_preferences  WHERE rfid_tag_num = '{tag_num}'"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        for row in records:
            humidity1 = row[4]
            print("Humidity", row[4])
            print("\n")

        cursor.close()
        return humidity1

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")        
            
def getAll():
    try:
        sqliteConnection = sqlite3.connect('/home/shabah/IoTProject/IoT/Phase4/real_iot.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = """SELECT * from user_preferences"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Total rows are:  ", len(records))
        print("Printing each row")
        for row in records:
            print("Id: ", row[0])
            print("Tag: ", row[1])
            print("Temp: ", row[2])
            print("Light: ", row[3])
            print("\n")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
            
#getLight("CCC79463")  
