from Classes.Database import Database
from Classes.Customer import Customer
from Classes.Item import Item
from Classes.Employee import Employee
from Classes.Rewards import Reward
from GUI import *
import sys

if __name__ == "__main__":
    # This is all sample code!!

    authDB = Database(dbSelection="auth").initialize()
    mainDB = Database(dbSelection="main").initialize()


    item = Item(name="Bread", SKU=809876768789, price=1.32, count=2)
    item.storeItem()

    emp = Employee(username="admin", password="admin")
    emp.createAccount()

    newReward = Reward(name="Free Meal", requirement=0, numRequired=5, rewardType="visit", description="This is a free meal after 5 meals.", expireDate=20220325) # Finish Testing
    newReward.createReward(emp)

    newReward1 = Reward(name="Free Bread", requirement=809876768789, rewardType="price", priceReq=20, numRequired=2, description="This is a free bread after bread purchases.",expireDate=20220325) # Finish Testing
    newReward1.createReward(emp)

    cust = Customer(name="SampleCustomer", DOB=20220309, phone=5054769254)
    cust.createAccount()

    cust.addItemToCart(item)
    cust.checkout()
    cust.getPurchaseHistory()
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
