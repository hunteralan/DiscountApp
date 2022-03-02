import hashlib as hl
import uuid
from configparser import ConfigParser
import os
import sqlite3

class Employee:
    def __init__(self, username, password=None, employeeName=None, accessLevel=0):
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

        self.__rootDir = os.path.join(os.getcwd(), "Database")

        config = ConfigParser()
        config.read(os.path.join(self.__rootDir, "db.conf"))

        self.__config = config["AUTH"]
        self.__connection = None
        self.__cursor = None

        self.username = username

        if (self.checkExists()):
            self.employeeName = self.__getEmployeeInfo()[0]
            self.accessLevel = self.__getEmployeeInfo()[0]
        else:
            self.employeeName = employeeName
            self.accessLevel = accessLevel

        self.password = password

    def __connect(self):
        '''
            This private method creates a connection to the database.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        try:
            dbName = self.__config["name"]
            self.__connection = sqlite3.connect(os.path.join(self.__rootDir, "auth", f"{dbName}.db"))
            self.__cursor = self.__connection.cursor()
            print("[INFO] EM: Connection successfully established.")
        except Exception as e:
            print(f"[ERROR] Connection unsuccessful: {e}")

    def __disconnect(self):
        '''
            This private method properly closes a connection to the database.\n
            THIS SHOULD NOT BE TOUCHED OUTSIDE OF THE CLASS!!
        '''

        self.__connection.close()
        print("[INFO] EM: Connection closed.")

    def displayTable(self):
        '''
            Used for debug purposes to show the entire Employee database table.
        '''

        self.__connect()

        sql = """
            SELECT *
            FROM Employee;
        """
        table = self.__cursor.execute(sql).fetchall()

        self.__disconnect()

        for row in table:
            print(row)

    def __getEmployeeInfo(self):
        '''
            Used to get the employee information for verification.
        '''

        self.__connect()

        sql = """
            SELECT *
            FROM Employee
            WHERE username = (?);
        """
        info = self.__cursor.execute(sql, (self.username,)).fetchone()

        self.__disconnect()

        return info

    def verifyLogin(self):
        '''
            Verify the employee object is supplied the correct info.\n
            Used to authorize the employee.
        '''

        verified = False

        employeeInfo = self.__getEmployeeInfo()
        if (employeeInfo[1] == self.username and employeeInfo[2] == self.password):
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

        if (self.password != None and self.employeeName != None):
            self.__connect()

            sql = """
                INSERT INTO Employee (accessLevel, username, password, salt, name)
                VALUES 
                (?, ?, ?, ?, ?)
            """

            try:
                self.__cursor.execute(sql, (self.accessLevel, self.username, self.password, uuid.uuid4().hex, self.employeeName))
                self.__connection.commit()
                print(f"[INFO] Added {self.username} to the database!")
            except Exception:
                print(f"This employee already exists!")

            self.__disconnect()
        
        elif (self.employeeName == None):
            print("Cannot add employee to database with blank name!")

        else:
            print("Cannot add employee to database with blank password!")

    def deleteAccount(self, employee):
        '''
            Removes the employee from the database, requires user of admin priveleges.\n
            Users cannot remove themselves from the database. Users of same level cannot remove other users of same access level.\n
            User to be removed must also exist in the database.\n\n

            Params:\n\t
                {employee}: this is the Employee object with the supplied username you wish to remove. Does not require user to be removed's password.
        '''

        self.__connect()

        if (type(employee) != Employee):
            print(f"{employee} is not a proper Employee!")
        elif (not employee.checkExists()):
            print("This employee does not exist in the database!")
        elif (int(self.__config["accessLevel_admin_priv"]) > self.accessLevel):
            print(f"No sufficient privilage to remove from database: not admin")
        elif (employee.accessLevel >= self.accessLevel):
            print(f"No sufficient privilage to remove from database: user is same or higher management level")
        else:
            sql = """
                DELETE 
                FROM Employee
                WHERE username = (?)
            """

            self.__cursor.execute(sql, (employee.username,))
            self.__connection.commit()
            print(f"[INFO] Removed {employee.username} from the database!")

            self.__disconnect()

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
            self.__connect()

            sql = """
                UPDATE Employee
                SET password = (?)
                WHERE username = (?)
            """

            try:
                self.__cursor.execute(sql, (newPassword, self.username,))
                self.__connection.commit()
                print(f"[INFO] Changed {self.username}'s password in the database!")
                self.password = newPassword
            except Exception as e:
                print(f"[ERROR] Error changing password: {e}")

            self.__disconnect()
        elif (type(employee) == Employee and employee.checkExists() and employee.accessLevel < self.accessLevel and self.accessLevel >= int(self.__config["accessLevel_admin_priv"])): # Logic if another employee wants to change anothers password
            self.__connect()

            sql = """
                UPDATE Employee
                SET password = (?)
                WHERE username = (?)
            """

            try:
                self.__cursor.execute(sql, (newPassword, employee.username,))
                self.__connection.commit()
                print(f"[INFO] Changed {employee.username}'s password in the database!")
                self.password = newPassword
            except Exception as e:
                print(f"[ERROR] Error changing password: {e}")

            self.__disconnect()
        elif (type(employee) == Employee and employee.accessLevel >= self.accessLevel):
            print("Cannot change the password of a user! (Higher management)")
        elif (type(employee) == Employee and self.accessLevel < int(self.__config["accessLevel_admin_priv"])):
            print("You do not have admin privilege!")
        else:
            print("User either does not exist or incorrect info is supplied for user!")


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
                    print(f"Cannot promote an employee to higher rank than yourself!")

                elif (type(employee) == Employee and self.accessLevel > employee.accessLevel and employee.checkExists() and self.accessLevel >= int(self.__config["accessLevel_admin_priv"])):
                    self.__connect()
                    
                    info = employee.__getEmployeeInfo()

                    sql = '''
                        UPDATE Employee
                        SET accessLevel = (?)
                        WHERE username = (?)
                    '''
                    self.__cursor.execute(sql, (newLevel, employee.username,))
                    self.__connection.commit()
                    print(f"[INFO] Changed {employee.username}'s access level in the database!")
                    self.accessLevel = newLevel

                    self.__disconnect()

                elif (self.accessLevel <= employee.accessLevel):
                    print("Cannot promote a user in a higher or equivelent position")

                elif (type(employee) != Employee or not employee.checkExists()):
                    print(f"{employee.username} is not a valid employee")

                else:
                    print(f"No sufficient privilage to promote users: not admin")
            else:
                print(f"Incorrect creditials supplied for {self.username}")
        else:
            print(f"{employee} is not an employee object!")
