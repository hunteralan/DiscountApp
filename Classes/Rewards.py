from Classes.DBConnector import DBConnector
from Classes.Employee import Employee
import os
from configparser import ConfigParser

class Reward(DBConnector):
    def __init__(self, name: str, requirement: int, numRequired:int, expireDate:int, rewardType:str, priceReq:float=0.00, description = ""):
        config = ConfigParser()
        config.read(os.path.join(os.path.join(os.getcwd(), "Database"), "db.conf"))

        self.__config = config["MAIN"]
        DBConnector.__init__(self, self.__config["DBname"])

        self.name = name
        self.requirement = requirement
        self.description = description
        self.numRequired = numRequired
        self.expiresOn = expireDate
        self.priceReq = priceReq

        if (rewardType not in ["price", "item", "visit"]):
            raise ValueError(f"{rewardType} is not a valid reward type!")
        else:
            self.rewardType = rewardType

    def displayAllRewards(self):
        '''
            Used for debug to display all rewards that exist in the rewards table.
        '''
        numRewards = 0
        self._connect()

        sql = '''
            SELECT *
            FROM Reward
        '''

        table = self._cursor.execute(sql).fetchall()

        self._disconnect()

        for row in table:
            print(row)
            numRewards += 1

        return numRewards

    def displayActiveRewards(self):
        '''
            Used to display all rewards with active = 1
        '''

        numRewards = 0
        self._connect()

        sql = '''
            SELECT *
            FROM Reward
            WHERE active = (?)
        '''

        table = self._cursor.execute(sql (1,)).fetchall()

        self._disconnect()

        for row in table:
            print(row)
            numRewards += 1

        return numRewards

    def __getRewardInfo(self):
        '''
            Used to get the customer information for verification.
        '''

        self._connect()

        sql = """
            SELECT *
            FROM Reward
            WHERE name = (?);
        """
        info = self._cursor.execute(sql, (self.name,)).fetchone()

        self._disconnect()

        return info


    def checkExists(self):
        '''
            Used to check if employee with the supplied username exists.
        '''

        exists = self.__getRewardInfo()

        if (exists != None):
            exists = True
        else:
            exists = False

        return exists

    def getDate(self):
        '''
            Gets the current date for database use.
        '''
        from datetime import datetime
        now = datetime.now()
        timeTag = str(now).replace('-', '').replace(' ', '_').replace(':', '').split('.')[0]
        return int(timeTag.split('_')[0])

    def createReward(self, employee):
        '''
            Creates a reward and saves it to the database.
        '''
        if (type(employee) == Employee and employee.checkExists() and employee.verifyLogin()):
            if (not self.checkExists()):
                rewardInfo = (self.name, self.requirement, self.description, employee.username, 1, self.numRequired, self.getDate(), self.expiresOn, self.priceReq, self.rewardType)

                try:
                    self._connect()

                    sql = '''
                        INSERT INTO Reward(name, requirement, description, createdBy, active, numReq, createdOn, expireDate, priceReq, type) 
                            VALUES 
                        ((?), (?), (?), (?), (?), (?), (?), (?), (?), (?))
                    '''

                    self._cursor.execute(sql, rewardInfo)
                    self._connection.commit()
                    print(f"[INFO] Added {self.name} to the database!")

                    self._disconnect()
                except Exception as e:
                    print(f"[ERROR] Error adding reward: {e}")
        
            else:
                print("This reward already exists!")
        elif (not employee.checkExists()):
            print("The employee with the supplied username does not exist!")
        elif (not employee.verifyLogin()):
            print("The supplied password for the employee is incorrect!")
        else:
            raise TypeError(f"{employee} is not a valid employee object!")

    def disableReward(self):
        '''
            Disables a reward by setting active = 0.
        '''

        if (self.checkExists()):
            rewardInfo = (0, self.name)

            try:
                self._connect()

                sql = '''
                    UPDATE Reward
                    SET active = (?)
                    WHERE name = (?)
                '''

                self._cursor.execute(sql, rewardInfo)
                self._connection.commit()
                print(f"[INFO] Disabled reward {self.name} in the database!")

                self._disconnect()
            except Exception as e:
                print(f"[ERROR] Error disabling reward: {e}")
    
        else:
            print("Cannot disable nonexisting reward!")

    def enableReward(self):
        '''
            Enables a reward by setting active = 1
        '''

        if (self.checkExists()):
            rewardInfo = (1, self.name)

            try:
                self._connect()

                sql = '''
                    UPDATE Reward
                    SET active = (?)
                    WHERE name = (?)
                '''

                self._cursor.execute(sql, rewardInfo)
                self._connection.commit()
                print(f"[INFO] Disabled reward {self.name} in the database!")

                self._disconnect()
            except Exception as e:
                print(f"[ERROR] Error enabling reward: {e}")
    
        else:
            print("Cannot enable nonexisting reward!")