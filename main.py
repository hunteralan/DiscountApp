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
    # This is all sample code!!
    
    

    
    #item = Item(name="Bread", SKU=809876, price=1.32, count=10)
    #item.storeItem()
    #item.displayTable()

    #emp = Employee(username="admin", password="admin", employeeName="SuperUser", accessLevel=10)
    #emp.createAccount()
    #emp.displayTable()
    #emp.verifyLogin()
    #emp.changePassword("tttt")
    #emp.displayTable()
    #emp.displayTable()
    #emp = Employee(username="admin", password="admin")
    #
    #newReward = Reward(name="Free Meal", requirement=0, numRequired=5, rewardType="visit", description="This is a free meal after 5 meals.", expireDate=20220325) # Finish Testing
    #newReward.createReward(emp)
    #
    #newReward1 = Reward(name="Free Bread", requirement=809876, rewardType="price", priceReq=20, numRequired=2, description="This is a free bread after bread purchases.",expireDate=20220325) # Finish Testing
    #newReward1.createReward(emp)
    #
    #cust = Customer(name="SampleCustomer", DOB=20220309, phone=5054769254)
    #cust.createAccount()
    #
    #item = Item(SKU=809876, count=3)
    #
    #cust.addItemToCart(item)
    #cust.checkout()
    #cust.getPurchaseHistory()
    #
    #item.displayTable()

    #Create PyQt5 app
    app = QtWidgets.QApplication(sys.argv)
    #Create instance of window
    window = Login()
    #Start the app
    sys.exit(app.exec_())