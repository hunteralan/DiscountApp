from Classes.Employee import Employee
from Classes.Database import Database
from GUI import *

if __name__ == "__main__":
    authDB = Database(dbSelection="auth").initialize()
    mainDB = Database(dbSelection="main").initialize()


    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    
    sys.exit(app.exec_())
    
    #superUser = Employee(username="admin", password="admin1", employeeName="SuperUser", accessLevel=1)
    #superUser.createAccount()

    #tmp = Employee(username="hunter", password="admin1", employeeName="SuperUser", accessLevel=0)
    #tmp.createAccount()