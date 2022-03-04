import sqlite3
import configparser as cp
import os
from shutil import copy
from Classes.DBConnector import DBConnector

class Database(DBConnector):
    def __init__(self, dbSelection):
        '''
            Simply the constructor for the Database object.\n
            
            Parameters:
                \tdbSelection is the database selection. Predetermined choices are set in the db.conf config file.
        '''
        DBConnector.__init__(self, dbSelection)

    def __setup(self):
        '''
            This private method sets up the database with the proper tables, etc.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        setupFile = os.path.join(self._rootDir, self._folderLoc, f"{self._tableName}.sql")

        try:
            with open(setupFile, 'r') as contents:
                self._connection.executescript(contents.read())
                print("[INFO] Setup successfully ran.")
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
        backupFileName = self._dbName + timeTagSplit[1] + ".db"
        backupFolderName = os.path.join(self._rootDir, self._folderLoc, "Backups", timeTagSplit[0])

        if (not os.path.isdir(backupFolderName)):
            os.mkdir(backupFolderName)

        copy(self._dbLoc, os.path.join(self._rootDir, self._dbName, "Backups", timeTagSplit[0], backupFileName))
        print("[INFO] Backed up database!")

    def initialize(self):
        '''
            This method initializes the database by connecting to it and installing the tables, etc.\n
            Takes no parameters and returns itself.
        '''

        self._connect()
        self.__setup()

        return self

    def __del__(self):
        '''
            This private method is the destructor for the Database class.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        if (self._connection != None):
            self._disconnect()
