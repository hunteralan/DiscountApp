from Classes.DBConnector import DBConnector
from Classes.Database import Database
from Classes.Customer import Customer
from Classes.Item import Item
from Classes.Employee import Employee
from Classes.Rewards import Reward

authDB = Database(dbSelection="auth").initialize()
mainDB = Database(dbSelection="main").initialize()

from GUI import *
import sys

if __name__ == "__main__":

    #Create PyQt5 app
    app = QtWidgets.QApplication(sys.argv)
    #Create instance of window
    window = Login()
    #Start the app
    sys.exit(app.exec_())