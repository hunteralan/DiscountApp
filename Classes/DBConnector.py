from configparser import ConfigParser
import os
import mysql.connector as mc

class DBConnector:
    def __init__(self, dbSelection):
        self._rootDir = os.path.join(os.getcwd(), "Database")

        config = ConfigParser()
        config.read(os.path.join(self._rootDir, "db.conf"))

        dbChoices = (config["MAIN"]["DBname"], config["AUTH"]["DBname"])

        if (dbSelection == dbChoices[0]):
            self._dbName = 'main'
            self._tableName = config["MAIN"]["table_filename"]
            
        elif (dbSelection == dbChoices[1]):
            self._dbName = 'auth'
            self._tableName = config["AUTH"]["table_filename"]

        else:
            raise ValueError(f"{dbSelection} is not a valid database selection!\nValid selection according to config file: {dbChoices[0]}, {dbChoices[1]}")

        self._host = config["IP"]["host"]
        self._port = config["IP"]["port"]
        self._pass = config["GENERIC DB"]["password"]
        self._user = config["GENERIC DB"]["username"]

    def _resetCur(self):
        self._cursor = self._connection.cursor(buffered=True)

    def _connect(self):
        '''
            This private method creates a connection to the database.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        try:
            self._connection = mc.connect(user='dbConnector', password='root1234', host=self._host, port=self._port)
            self._resetCur()
            self._cursor.execute(f"CREATE DATABASE {self._dbName}")
            self._connection.close()
            self._cursor.close()
        except:
            None

        try:
            self._connection = mc.connect(user=self._user, database=self._dbName, password=self._pass, host=self._host, port=self._port)
            self._resetCur()
            print("[INFO] Connection successfully established.")
        except Exception as e:
            print(f"[ERROR] Connection unsuccessful: {e}")

    def _deleteDBs(self):
        self._connect()
        self._cursor.execute(f'DROP DATABASE main')
        self._cursor.execute(f'CREATE DATABASE main')
        self._cursor.execute(f'DROP DATABASE auth')
        self._cursor.execute(f'CREATE DATABASE auth')
        print("Databases successfully deleted!")

    def _disconnect(self):
        '''
            This private method properly closes a connection to the database.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        self._cursor.close()
        self._connection.close()
        print("[INFO] Connection closed.")

    def __del__(self):
        try:
            if (self._connection != None):
                self._disconnect()
        except Exception:
            None