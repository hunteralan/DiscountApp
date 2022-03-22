from configparser import ConfigParser
import os
from Classes.DBConnector import DBConnector


class Item(DBConnector):
    def __init__(self, SKU, name="", price=0.00, count=1):
        config = ConfigParser()
        config.read(os.path.join(os.path.join(os.getcwd(), "Database"), "db.conf"))

        DBConnector.__init__(self, "main")

        self.name = name
        self.SKU = SKU
        self.price = price

        if (count == 0):
            raise ValueError("Cannot add zero number of items!")
        else:
            self.count = count

    def displayTable(self):
        '''
            Used for debug purposes to show the entire Employee database table.
        '''

        sql = """
            SELECT *
            FROM Inventory
        """
        self._connect()
        self._cursor.execute(sql)
        table = self._cursor.fetchall()
        self._disconnect()

        for row in table:
            print(row)

    def _getItemInfo(self):
        '''
            Used to get the customer information for verification.
        '''

        sql = """
            SELECT *
            FROM Inventory
            WHERE SKU = %s;
        """
        self._connect()
        self._cursor.execute(sql, (self.SKU,))
        info = self._cursor.fetchone()
        self._disconnect()
        print(info)

        return info


    def checkExists(self):
        '''
            Used to check if employee with the supplied username exists.
        '''

        exists = self._getItemInfo()

        if (exists != None):
            exists = True
        else:
            exists = False

        return exists

    def storeItem(self):
        '''
            Used to store the item into the database.
        '''

        if (not self.checkExists()):
            sql = '''
                INSERT INTO Inventory(name, SKU, price, count) 
                    VALUES 
                (%s, %s, %s, %s)
            '''

            itemInfo = (self.name, self.SKU, self.price, self.count)
        else:
            sql = '''
                UPDATE Inventory
                SET count = %s + %s
                WHERE SKU = %s
            '''

            itemInfo = (self._getItemInfo()[3], self.count, self.SKU)

        self._connect()
        try:
            self._cursor.execute(sql, itemInfo)
            self._connection.commit()
            print(f"[INFO] Added {self.name} to the database!")

        except Exception as e:
            print(f"[ERROR] Error adding item to Inventory: {e}")
        self._disconnect()

        