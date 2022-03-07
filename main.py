from Classes.Database import Database
from GUI import *
import sys

if __name__ == "__main__":
    authDB = Database(dbSelection="auth").initialize()
    mainDB = Database(dbSelection="main").initialize()

    #Create PyQt5 app
    app = QtWidgets.QApplication(sys.argv)
    #Create instance of window
    window = Login()
    #Start the app
    sys.exit(app.exec_())
    
    #superUser = Employee(username="admin", password="admin1", employeeName="SuperUser", accessLevel=1)
    #superUser.createAccount()

    #tmp = Employee(username="hunter", password="admin1", employeeName="SuperUser", accessLevel=0)
    #tmp.createAccount()