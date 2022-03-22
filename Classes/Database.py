import os
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

        setupFile = os.path.join(self._rootDir, self._dbName, f"{self._tableName}.sql")

        if (self._dbName == "main"):
            multi = True
        elif (self._dbName == "auth"):
            multi = False

        try:
            with open(setupFile, 'r') as contents:
                self._connect()
                self._cursor.execute(contents.read(), multi=multi)
                self._disconnect()
                print("[INFO] Setup successfully ran.")
        except Exception as e:
            print(f"[ERROR] Setup unsuccessful: {e}")

        if (self._dbName == "main"):
            self._connect()
            self._cursor.execute("INSERT IGNORE INTO Inventory (name, SKU, price, count) VALUES ('Visit', 0, 0.00, 1)")
            self._connection.commit()
            self._disconnect()

    #def backup(self):


    def initialize(self):
        '''
            This method initializes the database by connecting to it and installing the tables, etc.\n
            Takes no parameters and returns itself.
        '''

        self.__setup()

        return self
