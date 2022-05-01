from datetime import datetime
from configparser import ConfigParser
from multiprocessing.sharedctypes import Value
import os
from Classes.DBConnector import DBConnector
from Classes.Item import Item

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
        DBConnector.__init__(self, "main")

        self.name = name
        self.DOB = DOB
        self.phone = phone
        self.DLN = DLN
        self.email = email
        self.cart = []

    def getAge(self):
        todaysDate = self._getDate()

        curYear = todaysDate // 10000
        birthYear = self.DOB // 10000

        curMonth = (todaysDate % 1000) // 100
        birthMonth = (self.DOB % 1000) // 100

        curDay = todaysDate % 100
        birthDay = self.DOB % 100

        return curYear - birthYear - ((curMonth, curDay) < (birthMonth, birthDay))

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

        sql = """
            SELECT *
            FROM Customer
            WHERE phone = %s;
        """
        self._connect()
        self._cursor.execute(sql, (self.phone,))
        info = self._cursor.fetchone()
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
                sql = '''
                    INSERT INTO Customer(name, DOB, phone, DLN, email, customerSince) 
                        VALUES 
                    (%s, %s, %s, %s, %s, %s)
                '''

                self._connect()
                self._cursor.execute(sql, customerInfo)
                self._connection.commit()
                self._disconnect()
                print(f"[INFO] Added {self.name} to the database!")

                
            except Exception as e:
                print(f"[ERROR] Error creating customer: {e}")
        elif (err):
            print(f"{self.name} is missing required field: {requirements[savedIdx]}")
        else:
            print("This customer already exists!")

    def displayTable(self):
        '''
            Used for debug purposes to show the entire Customer database table.
        '''

        sql = """
            SELECT *
            FROM Customer;
        """

        self._connect()
        self._cursor.execute(sql)
        table = self._cursor.fetchall()
        self._disconnect()

        for row in table:
            print(row)

        return table


    def addItemToCart(self, item):
        '''
            Used to add an item to a customers cart. Use checkout() to store into database.
        '''

        if (type(item) != Item):
            raise TypeError(f"{item} is not an Item object!")
        elif (int(item.ageRequired) > self.getAge()):
            raise ValueError(f"Member is not old enough to purchase this item!")
        elif (item._getItemInfo() == None):
            raise ValueError(f"Cannot add item to cart! Is not stored in inventory!")
        else:
            SKUList = [x.SKU for x in self.cart]

        if (item.SKU in SKUList):
            itemIdx = SKUList.index(item.SKU)
            self.cart[itemIdx].count = self.cart[itemIdx].count + item.count
        else:
            self.cart.append(item)

    def clearCart(self):
        '''
            Clear the customers shopping cart.
        '''
        self.cart = []

    def visit(self):
        '''
            Adds a visit to the customers purchase history.
        '''

        saveCart = self.cart
        self.addItemToCart(Item(0))
        self.checkout()
        self.cart = saveCart
        print(f"Added a customer visit!!")

    def displayCart(self):
        '''
            Used to display the cart of the customer.
        '''
        for item in self.cart:
            print(f"{item.SKU}:{item.name} - {item.count}")

        return self.cart

    def _checkBoughtSpecificItem(self, item):
        '''
            Used to check if a customer has ever bought a specific item.
        '''
        if (type(item) != Item):
            raise TypeError(f"{item} is not a valid Item object!")

        sql = '''
            SELECT *
            FROM purchaseHistory
            WHERE SKU = %s
        '''
        info = (item.SKU,)

        self._connect()
        self._cursor.execute(sql, info)
        exists = self._cursor.fetchone()

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
            SET quantity = quantity + %s, totalCost = totalCost + (%s * %s)
            WHERE SKU = %s AND phone = %s AND purchaseDate = %s
        '''
        query = (item.count, item.price, item.count, item.SKU, self.phone, self._getDate())
        self._connect()
        self._cursor.execute(sql, query)
        self._connection.commit()
        self._disconnect()


    def checkout(self):
        '''
            Used to store the customers shopping cart into the database.
        '''
        
        sql = '''
            INSERT INTO purchaseHistory(phone, SKU, quantity, purchaseDate, totalCost)
                VALUES
            (%s, %s, %s, %s, %s)
        '''
        for item in self.cart:
            if ((item._getItemInfo()[3] + (item.count * -1)) >= 0):
                if (item.checkExists()):
                    itemInfo = item._getItemInfo()
                else:
                    raise ValueError(f"Can't buy an item that does not exist!")

                if (self._checkBoughtSpecificItem(item)):
                    print("Updating! Youve bought this before!!!!!!")
                    self._updateItemPurchase(item)
                else:
                    try:
                        print("Adding! Youve never bought this before!!!!!!")
                        self._connect()
                        self._cursor.execute(sql, (self.phone, item.SKU, item.count, self._getDate(), (itemInfo[2] * item.count)))
                        self._connection.commit()
                        self._disconnect()
                    except Exception as e:
                        print(f"[ERROR] Unsuccessful in checking out: {e}")
                self._addAvailableRewards(item)
                
            else:
                raise ValueError("Cannot buy this item! Buying more than the inventory contains!")

        
        self.visit()
        self.clearCart() 

    def getPurchaseHistory(self):
        '''
            Used to show previous customer purchases of the self customer.
        '''

        if (self.checkExists()):
            custInfo = self.__getCustomerInfo()

            sql = """
                SELECT *
                FROM purchaseHistory
                WHERE phone = %s
            """

            self._connect()
            self._cursor.execute(sql, (custInfo[2],))
            table = self._cursor.fetchall()
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
            SELECT %s, name, r.expireDate
            FROM purchaseHistory p, Reward r
            WHERE (p.SKU = r.requirement
                AND p.SKU = %s
                AND quantity % numReq = 0
                AND r.active = 1
                AND r.expireDate >= %s
                AND type <> 'price')
                OR 
                (r.active = 1
                 AND p.SKU = r.requirement
                 AND r.expireDate >= %s
                 AND type = 'price'
                 AND r.name NOT IN (SELECT title
                                    FROM hasReward
                                    WHERE phone = %s)
                 AND r.priceReq <= (SELECT SUM(totalCost)
                                    FROM purchaseHistory
                                    WHERE purchaseDate >= r.CreatedOn
                                        AND purchaseDate <= r.expireDate
                                        AND phone = %s))
        '''

        query = (self.phone, item.SKU, self._getDate(), self._getDate(), self.phone, self.phone)

        self._connect()
        self._cursor.execute(sql, query)
        self._connection.commit()
        self._disconnect()

    def checkAvailableRewards(self):
        '''
            Check what rewards the specific customer has.
        '''

        sql = '''
            SELECT *
            FROM hasReward
            WHERE phone = %s
        '''
        query = (self.phone,)

        self._connect()
        self._cursor.execute(sql, query)
        results = self._cursor.fetchall()
        self._disconnect()

        for row in results:
            print(row)

        return results

    def redeemReward(self, rewardVerificationID):
        success = True

        try:
            sql = '''
                DELETE
                FROM hasReward
                WHERE rewardVerifyID = %s
                    AND phone = %s
            '''

            query = (rewardVerificationID, self.phone)

            self._connect()
            self._cursor.execute(sql, query)
            self._connection.commit()
            self._disconnect()
        except:
            success = False

        return success