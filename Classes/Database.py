import sqlite3
import configparser as cp
import os
from shutil import copy

class Database:
    def __init__(self, dbSelection):
        '''
            Simply the constructor for the Database object.\n
            
            Parameters:
                \tdbSelection is the database selection. Predetermined choices are set in the db.conf config file.
        '''


        self.__rootDir = os.path.join(os.getcwd(), "Database")

        config = cp.ConfigParser()
        config.read(os.path.join(self.__rootDir, "db.conf"))
        dbChoices = (config["MAIN"]["name"], config["AUTH"]["name"])
        self.__connection = None
        self.__cursor = None
        

        if (dbSelection == dbChoices[0]):
            self.__db = os.path.join(self.__rootDir, "main", f"{dbChoices[0]}.db")
            self.__dbName = dbChoices[0]
            self.__folderLoc = "main"
            self.__tableName = config["MAIN"]["table_filename"]
            
        elif (dbSelection == dbChoices[1]):
            self.__db = os.path.join(self.__rootDir, "auth", f"{dbChoices[1]}.db")
            self.__dbName = dbChoices[1]
            self.__folderLoc = "auth"
            self.__tableName = config["AUTH"]["table_filename"]

        else:
            raise ValueError(f"{dbSelection} is not a valid database selection!\nValid selection according to config file: {dbChoices[0]}, {dbChoices[1]}")

    def __connect(self):
        '''
            This private method creates a connection to the database and sets the proper internal attributes.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        try:
            self.__connection = sqlite3.connect(self.__db)
            self.__cursor = self.__connection.cursor()
            print("[INFO] DB: Connection successfully established.")
        except Exception as e:
            print(f"[ERROR] Connection unsuccessful: {e}")

    def __disconnect(self):
        '''
            This private method properly closes a connection to the database.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        self.__connection.close()
        print("[INFO] DB: Connection closed.")

    def __setup(self):
        '''
            This private method sets up the database with the proper tables, etc.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        setupFile = os.path.join(self.__rootDir, self.__folderLoc, f"{self.__tableName}.sql")

        try:
            with open(setupFile, 'r') as contents:
                self.__connection.executescript(contents.read())
                print("[INFO] Setup successfully ran.")
                success = True
        except Exception as e:
            print(f"[ERROR] Setup unsuccessful: {e}")

    def backup(self):
        '''
            This method backs the database up.
        '''


        from datetime import datetime

        now = datetime.now()
        timeTag = str(now).replace('-', '').replace(' ', '_').replace(':', '').split('.')[0]
        timeTagSplit = timeTag.split('_')
        backupFileName = self.__dbName + timeTagSplit[1] + ".db"
        backupFolderName = os.path.join(self.__rootDir, self.__folderLoc, "Backups", timeTagSplit[0])

        if (not os.path.isdir(backupFolderName)):
            os.mkdir(backupFolderName)

        copy(self.__db, os.path.join(self.__rootDir, self.__dbName, "Backups", timeTagSplit[0], backupFileName))
        print("[INFO] Backed up database!")

    def initialize(self):
        '''
            This method initializes the database by connecting to it and installing the tables, etc.\n
            Takes no parameters and returns itself.
        '''

        self.__connect()
        self.__setup()

        return self

    def __del__(self):
        '''
            This private method is the destructor for the Database class.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        if (self.__connection != None):
            self.__disconnect()
