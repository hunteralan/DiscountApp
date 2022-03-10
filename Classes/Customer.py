from datetime import datetime
from configparser import ConfigParser
import os
from Classes.DBConnector import DBConnector
from Classes.Item import Item
from Classes.Rewards import Reward

class Customer(DBConnector):
    def __init__(self, name, DOB, phone, DLN=None, email=None):
        '''
            Constructor for the Customer Class.\n
            {name}: This is the name of the customer.\n
            {DOB}: Date of birth of the customer.\n
            {phone}: Phone number of the customer.\n
            {DLN}: Drivers license number of the customer.\n
            {email}: Email of the customer
        '''
        config = ConfigParser()
        config.read(os.path.join(os.path.join(os.getcwd(), "Database"), "db.conf"))

        self.__config = config["MAIN"]
        DBConnector.__init__(self, self.__config["DBname"])

        self.name = name
        self.DOB = DOB
        self.phone = phone
        self.DLN = DLN
        self.email = email
        self.cart = []

    def _getDate(self):
        '''
            Private method which returns the current date for database uses.
        '''
        now = datetime.now()
        timeTag = str(now).replace('-', '').replace(' ', '_').replace(':', '').split('.')[0]
        return int(timeTag.split('_')[0])

    def __getCustomerInfo(self):
        '''
            Used to get the customer information for verification.
        '''

        self._connect()

        sql = """
            SELECT *
            FROM Customer
            WHERE phone = (?);
        """
        info = self._cursor.execute(sql, (self.phone,)).fetchone()

        self._disconnect()

        return info


    def checkExists(self):
        '''
            Used to check if employee with the supplied username exists.
        '''

        exists = self.__getCustomerInfo()

        if (exists != None):
            exists = True
        else:
            exists = False

        return exists

    def createAccount(self):
        '''
            Used to create the account of the customer and store it into the database.
        '''

        requirements = ("name", "DOB", "phone", "DLN", "email", "customerSince")
        customerInfo = (self.name, self.DOB, self.phone, self.DLN, self.email, self._getDate())
        err = False

        for idx in range(len(requirements)):
            if (customerInfo[idx] == None and self.__config.getboolean(requirements[idx]) == True):
                err = True
                savedIdx = idx


        if (not self.checkExists() and not err):

            try:
                self._connect()

                sql = '''
                    INSERT INTO Customer(name, DOB, phone, DLN, email, customerSince) 
                        VALUES 
                    ((?), (?), (?), (?), (?), (?))
                '''

                self._cursor.execute(sql, customerInfo)
                self._connection.commit()
                print(f"[INFO] Added {self.name} to the database!")

                self._disconnect()
            except Exception as e:
                print(f"[ERROR] Error changing password: {e}")
        elif (err):
            print(f"{self.name} is missing required field: {requirements[savedIdx]}")
        else:
            print("This customer already exists!")

    def displayTable(self):
        '''
            Used for debug purposes to show the entire Customer database table.
        '''

        self._connect()

        sql = """
            SELECT *
            FROM Customer;
        """
        table = self._cursor.execute(sql).fetchall()

        self._disconnect()

        for row in table:
            print(row)


    def addItemToCart(self, item):
        '''
            Used to add an item to a customers cart. Use checkout() to store into database.
        '''
        SKUList = [x.SKU for x in self.cart]

        if (type(item) != Item):
            raise TypeError(f"{item} is not an Item object!")
        if (item.SKU in SKUList):
            itemIdx = SKUList.index(item.SKU)
            self.cart[itemIdx] = self.cart[itemIdx].count + item.count
        else:
            self.cart.append(item)

    def clearCart(self):
        '''
            Clear the customers shopping cart.
        '''
        self.cart = {}

    def visit(self):
        '''
            Adds a visit to the customers purchase history.
        '''

        self.addItemToCart(Item(0))
        self.checkout()
        print(f"Added a customer visit!!")

    def displayCart(self):
        '''
            Used to display the cart of the customer.
        '''
        for item in self.cart:
            print(f"{item.SKU}:{item.name} - {item.count}")

    def _checkBoughtSpecificItem(self, item):
        '''
            Used to check if a customer has ever bought a specific item.
        '''
        if (type(item) != Item):
            raise TypeError(f"{item} is not a valid Item object!")

        sql = '''
            SELECT *
            FROM purchaseHistory
            WHERE SKU = (?)
        '''
        info = (item.SKU,)

        exists = self._cursor.execute(sql, info).fetchone()

        if (exists == None):
            exists = False
        else:
            exists = True

        return exists

    def _updateItemPurchase(self, item):
        '''
            Increases the quantity of the customers purchase if multiple of the same purchases are made on the same day.
        '''
        if (type(item) != Item):
            raise TypeError(f"{item} is not a valid Item object!")

        sql = '''
            UPDATE purchaseHistory
            SET quantity = quantity + (?), totalCost = totalCost + ((?) * (?))
            WHERE SKU = (?) AND phone = (?) AND purchaseDate = (?)
        '''
        query = (item.count, item.price, item.count, item.SKU, self.phone, self._getDate())
        self._cursor.execute(sql, query)
        self._connection.commit()


    def checkout(self):
        '''
            Used to store the customers shopping cart into the database.
        '''

        self._connect()
        sql = '''
            INSERT INTO purchaseHistory(phone, SKU, quantity, purchaseDate, totalCost)
                VALUES
            ((?), (?), (?), (?), (?))
        '''
        for item in self.cart:
            if (self._checkBoughtSpecificItem(item)):
                print("Updating! Youve bought this before!!!!!!")
                self._updateItemPurchase(item)
            else:
                try:
                    print("Adding! Youve never bought this before!!!!!!")
                    self._cursor.execute(sql, (self.phone, item.SKU, item.count, self._getDate(), (item.price * item.count)))
                    self._connection.commit()
                except Exception as e:
                    print(f"[ERROR] Unsuccessful in checking out: {e}")
            self._addAvailableRewards(item)

        self._disconnect()
        self.cart = []

    def displayAllPurchaseTable(self):
        '''
            Used for debug purposes to show the entire purchaseHistory database table.
        '''

        self._connect()

        sql = """
            SELECT *
            FROM purchaseHistory;
        """
        table = self._cursor.execute(sql).fetchall()

        self._disconnect()

        for row in table:
            print(row)

    def getPurchaseHistory(self):
        '''
            Used to show previous customer purchases of the self customer.
        '''

        if (self.checkExists()):
            custInfo = self.__getCustomerInfo()

            self._connect()

            sql = """
                SELECT *
                FROM purchaseHistory
                WHERE phone = (?)
            """
            table = self._cursor.execute(sql, (custInfo[2],)).fetchall()

            self._disconnect()

            for row in table:
                print(row)

            return table

        else:
            print(f"{self.phone} is not associated with a valid customer!")

    def _addAvailableRewards(self, item):
        '''
            Add rewards to the customers hasRewards table where applicable.
        '''
        sql = '''
            INSERT INTO hasReward(phone, title, useBy)
            SELECT (?), name, r.expireDate
            FROM purchaseHistory p, Reward r
            WHERE (p.SKU = r.requirement
                AND p.SKU = (?)
                AND quantity % numReq = 0
                AND r.active = 1
                AND r.expireDate >= (?)
                AND type <> 'price')
                OR 
                (r.active = 1
                 AND p.SKU = r.requirement
                 AND r.expireDate >= (?)
                 AND type = 'price'
                 AND r.name NOT IN (SELECT title
                                    FROM hasReward
                                    WHERE phone = (?))
                 AND r.priceReq <= (SELECT SUM(totalCost)
                                    FROM purchaseHistory
                                    WHERE purchaseDate >= r.CreatedOn
                                        AND purchaseDate <= r.expireDate
                                        AND phone = (?)))
        '''

        query = (self.phone, item.SKU, self._getDate(), self._getDate(), self.phone, self.phone)

        self._cursor.execute(sql, query).fetchall()
        self._connection.commit()

    def checkAvailableRewards(self):
        '''
            Check what rewards the specific customer has.
        '''
        self._connect()

        sql = '''
            SELECT *
            FROM hasReward
            WHERE phone = (?)
        '''
        query = (self.phone,)

        results = self._cursor.execute(sql, query).fetchall()

        for row in results:
            print(row)