from Classes.Employee import Employee
from Classes.Database import Database

if __name__ == "__main__":
    authDB = Database(dbSelection="auth").initialize()
    mainDB = Database(dbSelection="main").initialize()

    superUser = Employee(username="admin", password="admin1", employeeName="SuperUser", accessLevel=1)
    superUser.createAccount()

    tmp = Employee(username="hunter", password="admin1", employeeName="SuperUser", accessLevel=0)
    tmp.createAccount()