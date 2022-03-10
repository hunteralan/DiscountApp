import hashlib
import hmac
from typing import ValuesView
import uuid
from configparser import ConfigParser
import os
from Classes.DBConnector import DBConnector

class Employee(DBConnector):
    def __init__(self, username:str, password:str=None, employeeName:str=None, accessLevel:int=0):
        '''
            Constructor for the employee class.\n
            
            Params:\n\t
                {Username}: Self explanatory and required\n\t

                {Password}: Can be entered for authentication or left blank to be referrenced by higher management.\n
                    \tFor example, a manager only needs the username to delete an employee from the database but to be authenticated\n
                    \t the Employee class must be supplied the password as it is stored in the database. Can call verifyLogin to verify info.\n\t

                {accessLevel}: In order to perform operations on other employees, accessLevel must be both greater than \n
                    \tthe employee to be operated on as well as above the admin threshold set in db.conf
        '''
        config = ConfigParser()
        config.read(os.path.join(os.path.join(os.getcwd(), "Database"), "db.conf"))

        self.__config = config["AUTH"]
        DBConnector.__init__(self, self.__config["DBname"])

        self.username = username

        if (self.checkExists()):
            self.employeeName = self.__getEmployeeInfo()[0]
            self.accessLevel = self.__getEmployeeInfo()[0]
            self.salt = self.__getEmployeeInfo()[3]
        else:
            self.employeeName = employeeName
            self.accessLevel = accessLevel
            self.salt = uuid.uuid4().hex.encode()

        if (password != None):
            passwordHash = hashlib.pbkdf2_hmac("sha256", password.encode(), self.salt, 100000)
            self.password = passwordHash

    def displayTable(self):
        '''
            Used for debug purposes to show the entire Employee database table.
        '''

        self._connect()

        sql = """
            SELECT *
            FROM Employee;
        """
        table = self._cursor.execute(sql).fetchall()

        self._disconnect()

        for row in table:
            print(row)

    def __getEmployeeInfo(self):
        '''
            Used to get the employee information for verification.
        '''

        self._connect()

        sql = """
            SELECT *
            FROM Employee
            WHERE username = (?);
        """
        info = self._cursor.execute(sql, (self.username,)).fetchone()

        self._disconnect()

        return info

    def verifyLogin(self):
        '''
            Verify the employee object is supplied the correct info.\n
            Used to authorize the employee.
        '''

        verified = False

        employeeInfo = self.__getEmployeeInfo()
        
        if (employeeInfo != None and employeeInfo[1] == self.username and hmac.compare_digest(self.password, employeeInfo[2])):
            verified = True

        return verified

    def checkExists(self):
        '''
            Used to check if employee with the supplied username exists.
        '''

        exists = self.__getEmployeeInfo()

        if (exists != None):
            exists = True
        else:
            exists = False

        return exists

    def createAccount(self):
        '''
            Used to add this employee to the database with the supplied credentials.\n
            Will not work if you attempt to add an existing employee or supply the employee with no password.
        '''

        if (self.password not in [None, ''] and self.employeeName not in [None, ''] and self.username not in [None, '']):

            self._connect()

            sql = """
                INSERT INTO Employee (accessLevel, username, password, salt, name)
                VALUES 
                (?, ?, ?, ?, ?)
            """

            try:
                self._cursor.execute(sql, (self.accessLevel, self.username, self.password, self.salt, self.employeeName))

                self._connection.commit()
                print(f"[INFO] Added {self.username} to the database!")
            except Exception:
                raise ValueError(f"User already exists!")

            self._disconnect()
        
        elif (self.employeeName in [None, '']):
            raise ValueError("Cannot add employee to database with blank name!")

        elif (self.username in [None, '']):
            raise ValueError("Cannot add employee to database with blank username!")


        else:
            raise ValueError("Cannot add employee to database with blank password!")

    def deleteAccount(self, employee):
        '''
            Removes the employee from the database, requires user of admin priveleges.\n
            Users cannot remove themselves from the database. Users of same level cannot remove other users of same access level.\n
            User to be removed must also exist in the database.\n\n

            Params:\n\t
                {employee}: this is the Employee object with the supplied username you wish to remove. Does not require user to be removed's password.
        '''

        self._connect()

        if (type(employee) != Employee):
            raise TypeError(f"{employee} is not a proper Employee!")
        elif (not employee.checkExists()):
            raise KeyError("This employee does not exist in the database!")
        elif (int(self._config["accessLevel_admin_priv"]) > self.accessLevel):
            raise ValueError(f"No sufficient privilage to remove from database: not admin")
        elif (employee.accessLevel >= self.accessLevel):
            raise ValueError(f"No sufficient privilage to remove from database: user is same or higher management level")
        else:
            sql = """
                DELETE 
                FROM Employee
                WHERE username = (?)
            """

            self._cursor.execute(sql, (employee.username,))
            self._connection.commit()
            print(f"[INFO] Removed {employee.username} from the database!")

            self._disconnect()

    def changePassword(self, newPassword, employee=None):
        '''
            This method changes the password of a user. \n
            Employee whos getting their password changed must already exist in the database.
            
            Params:\n\t
                {newPassword}: The password you wish to change to. 
                {employee}: This is an optional parameter. If an external source wants to change a users password, \n\t
                    the employee supplied must be of a lesser accessLevel than the one calling it
        '''

        if (employee==None and self.verifyLogin() and self.checkExists()): # Logic if user wants to change own password
            self._connect()

            sql = """
                UPDATE Employee
                SET password = (?)
                WHERE username = (?)
            """

            self._cursor.execute(sql, (newPassword, self.username,))
            self._connection.commit()
            print(f"[INFO] Changed {self.username}'s password in the database!")
            self.password = newPassword

            self._disconnect()
        elif (type(employee) == Employee and employee.checkExists() and employee.accessLevel < self.accessLevel and self.accessLevel >= int(self._config["accessLevel_admin_priv"])): # Logic if another employee wants to change anothers password
            self._connect()

            sql = """
                UPDATE Employee
                SET password = (?)
                WHERE username = (?)
            """

            self._cursor.execute(sql, (newPassword, employee.username,))
            self._connection.commit()
            print(f"[INFO] Changed {employee.username}'s password in the database!")
            self.password = newPassword

            self._disconnect()
        elif (type(employee) == Employee and employee.accessLevel >= self.accessLevel):
            raise ValueError("Cannot change the password of a user! (Higher management)")
        elif (type(employee) == Employee and self.accessLevel < int(self._config["accessLevel_admin_priv"])):
            raise ValueError("You do not have admin privilege!")
        else:
            raise ValueError("User either does not exist or incorrect info is supplied for user!")


    def changeAccessLevel(self, employee, newLevel):
        '''
            This can be used by an external employee to promote a lower accessLevel employee.\n
            Will save the promotion to the database. \n
            Params:\n\t
                {employee}: This is the employee you wish to promote/demote. Cannot be higher rank than the employee calling it.
        '''
        if (type(employee) == Employee):
            if (self.checkExists() and self.verifyLogin()):
                if (newLevel > self.accessLevel):
                    raise ValueError(f"Cannot promote an employee to higher rank than yourself!")

                elif (type(employee) == Employee and self.accessLevel > employee.accessLevel and employee.checkExists() and self.accessLevel >= int(self._config["accessLevel_admin_priv"])):
                    self._connect()
                    
                    info = employee.__getEmployeeInfo()

                    sql = '''
                        UPDATE Employee
                        SET accessLevel = (?)
                        WHERE username = (?)
                    '''
                    self._cursor.execute(sql, (newLevel, employee.username,))
                    self._connection.commit()
                    print(f"[INFO] Changed {employee.username}'s access level in the database!")
                    self.accessLevel = newLevel

                    self._disconnect()

                elif (self.accessLevel <= employee.accessLevel):
                    raise ValueError("Cannot promote a user in a higher or equivelent position")

                elif (type(employee) != Employee or not employee.checkExists()):
                    raise ValueError(f"{employee.username} is not a valid employee")

                else:
                    raise ValueError(f"No sufficient privilage to promote users: not admin")
            else:
                raise ValueError(f"Incorrect creditials supplied for {self.username}")
        else:
            raise TypeError(f"{employee} is not an employee object!")

