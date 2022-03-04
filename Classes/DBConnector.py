from configparser import ConfigParser
import os
import sqlite3

class DBConnector:
    def __init__(self, dbSelection):
        self._rootDir = os.path.join(os.getcwd(), "Database")

        config = ConfigParser()
        config.read(os.path.join(self._rootDir, "db.conf"))

        dbChoices = (config["MAIN"]["DBname"], config["AUTH"]["DBname"])

        if (dbSelection == dbChoices[0]):
            self._dbLoc = os.path.join(self._rootDir, "main", f"{dbChoices[0]}.db")
            self._dbName = dbChoices[0]
            self._folderLoc = "main"
            self._tableName = config["MAIN"]["table_filename"]
            
        elif (dbSelection == dbChoices[1]):
            self._dbLoc = os.path.join(self._rootDir, "auth", f"{dbChoices[1]}.db")
            self._dbName = dbChoices[1]
            self._folderLoc = "auth"
            self._tableName = config["AUTH"]["table_filename"]

        else:
            raise ValueError(f"{dbSelection} is not a valid database selection!\nValid selection according to config file: {dbChoices[0]}, {dbChoices[1]}")

        self._connection = None
        self._cursor = None


    def _connect(self):
        '''
            This private method creates a connection to the database.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        try:
            self._connection = sqlite3.connect(self._dbLoc)
            self._connection.execute("PRAGMA foreign_keys = 1")
            self._cursor = self._connection.cursor()
            print("[INFO] Connection successfully established.")
        except Exception as e:
            print(f"[ERROR] Connection unsuccessful: {e}")


    def _disconnect(self):
        '''
            This private method properly closes a connection to the database.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        self._connection.close()
        print("[INFO] Connection closed.")
