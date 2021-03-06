from Classes.Rewards import Reward
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QInputDialog, QLineEdit
from PyQt5.QtCore import QDate
from Classes.Employee import Employee
from Classes.Customer import Customer
from Classes.Item import Item
from datetime import date

currentlyLoggedIn = Employee(username = "", password= "")

#Default objects used when selected inside of their respective tables
selectedEmployee = Employee(username="", password="", employeeName="")
selectedMember = Customer(name = "", DOB = 0, phone = 0)
selectedDiscount = Reward(name = "", expireDate= 0, rewardType= "visit")
selectedItem = Item(SKU=0, name="")
selectedDiscountID = 0

#Used for accessing their respective tables
discount = Reward("", 0, "item", 0, 0, 0, "")
employee = Employee(username= "", password = "")

# Initializing Global Var
memData =["", "", ""]
employeeData = Employee.getEmployees(employee)

successfulRegistration = False

#Log-in Page  
class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi('UI/LoginWindow.ui', self)
        self.showMaximized()
        self.errMsg.setStyleSheet("color: white")

        self.submit = self.findChild(QtWidgets.QPushButton, 'submitBtn')
        self.submit.clicked.connect(self.onSubmit)

        self.register = self.findChild(QtWidgets.QPushButton, 'registerBtn')
        self.register.clicked.connect(self.onRegister)
        
        global successfulRegistration
        if (successfulRegistration == True):
            successfulRegistration = False

            self.errMsg.setText("Successfully registered!")
            self.errMsg.setStyleSheet("color: green")
    
    def onRegister(self):
        self.widget = Registration()
        self.close()

    #Login Logic
    def onSubmit(self):
        checkEmployee = Employee(username = str(self.username.text()), password = str(self.password.text()))
        try:
            global currentlyLoggedIn
            #If the supplied username and password corresponds to an employee
            if (checkEmployee.verifyLogin() == True):
                #If the employee is considered an admin or not, display the correct main page
                if (checkEmployee.accessLevel > 0):
                    currentlyLoggedIn = Employee(username=self.username.text(), password=self.password.text())
                    self.widget = adminMain()
                    self.close()
                else:
                    currentlyLoggedIn = Employee(username=self.username.text(), password=self.password.text())
                    self.widget = mainLower()
                    self.close()

            else:
                self.errMsg.setText("Incorrect Username/Password!")
                self.errMsg.setStyleSheet("color: red")

                self.username.clear()
                self.password.clear()
        except Exception as e:
            self.errMsg.setText(str(e))

class Registration(QMainWindow):
    def __init__(self):
        super(Registration, self).__init__()
        uic.loadUi('UI/registrationWindow.ui', self)
        self.showMaximized()
        
        self.submit = self.findChild(QtWidgets.QPushButton, 'submitBtn')
        self.submit.clicked.connect(self.onSubmitRegistration)
        
        self.cancel = self.findChild(QtWidgets.QPushButton, 'cancelBtn')
        self.cancel.clicked.connect(self.onCancelRegistration)
        
    #Registration Button Logic
    def onSubmitRegistration(self):
        global successfulRegistration
        successfulRegistration = False

        if (self.empPass.text() != self.empPassConfirm.text()):
            self.errMsg.setText("Passwords must be the same!")
            self.errMsg.setStyleSheet("color: red")

            self.empPass.clear()
            self.empPassConfirm.clear()
        
        elif (self.empPass.text() == ""):
            self.errMsg.setText("Passwords cannot be blank!")
            self.errMsg.setStyleSheet("color: red")

            self.empPass.clear()
            self.empPassConfirm.clear()

        elif (self.empUsername.text() == ""):
            self.errMsg.setText("Cannot have a blank name!")
            self.errMsg.setStyleSheet("color: red")
        else:
            try:
                newEmployee = Employee(username=str(self.empUsername.text()), password=str(self.empPass.text()), employeeName=str(self.empName.text()))
                #if the new employee is the first in the database, it's automatically the "owner" (highest administrator privilegdes)
                if (len(newEmployee.getEmployees()) == 0):
                    try:
                        newEmployee.createAccount()
                        successfulRegistration = True
                    except Exception as e:
                        self.errMsg.setText(str(e))
                        self.errMsg.setStyleSheet("color: red")
            
                    self.widget = Login()
                    self.close()
                #Administor/Manager verification is required for anyone to create an account
                #To prevent random people from adding themselves into the system
                else:
                    adminUser, okPressed = QInputDialog.getText(self, 'Administrator Verification', 'Enter Administrator Username:', QLineEdit.Normal, "")
                    if (okPressed and adminUser != ''):
                        adminPass, okPressed2 = QInputDialog.getText(self, 'Administrator Verification', 'Enter Administrator Password:', QLineEdit.Password, "")
                        if (okPressed2 and adminPass != ''):
                            checkAdmin = Employee(username = adminUser, password = adminPass)
                    
                            if (checkAdmin.verifyLogin() == True and checkAdmin.accessLevel > 0):
                                try:
                                    newEmployee.createAccount()
                                    successfulRegistration = True

                                    self.widget = Login()
                                    self.close()
                                except Exception as e:
                                    self.errMsg.setText(str(e))
                                    self.errMsg.setStyleSheet("color: red")

                            elif (checkAdmin.verifyLogin() == False or checkAdmin.accessLevel <= 0):
                                self.errMsg.setText("Administrator username/password was incorrect!")
                                self.errMsg.setStyleSheet("color: red")  
                         
            except Exception as e:
                self.errMsg.setText(str(e))
                self.errMsg.setStyleSheet("color: red")

            self.empUsername.clear()
            self.empPass.clear()
            self.empPassConfirm.clear()
            self.empName.clear()
    
    def onCancelRegistration(self):
        self.widget = Login()
        self.close()

#Administrator Page
class adminMain(QMainWindow):
    def __init__(self):
        super(adminMain, self).__init__()
        uic.loadUi('UI/adminControlPanel.ui', self)
        self.showMaximized()
        try:
            #Finding and setting up all buttons
            self.addMember = self.findChild(QtWidgets.QPushButton, 'addMember')
            self.addMember.clicked.connect(self.onAddMember)
            
            self.viewMember = self.findChild(QtWidgets.QPushButton, 'viewMember')
            self.viewMember.clicked.connect(self.onViewMember)

            self.modifyEmployee = self.findChild(QtWidgets.QPushButton, 'changeEmpBtn')
            self.modifyEmployee.clicked.connect(self.onModifyEmployee)            
            
            self.addItem = self.findChild(QtWidgets.QPushButton, 'addItem')
            self.addItem.clicked.connect(self.onAddItem)
            
            self.viewItem = self.findChild(QtWidgets.QPushButton, 'viewItems')
            self.viewItem.clicked.connect(self.onViewItem)
            
            self.addDiscount = self.findChild(QtWidgets.QPushButton, 'addDiscount')
            self.addDiscount.clicked.connect(self.onAddDiscount)
            
            self.viewDiscount = self.findChild(QtWidgets.QPushButton, 'viewDiscount')
            self.viewDiscount.clicked.connect(self.onViewDiscount)

            self.logOut = self.findChild(QtWidgets.QPushButton, 'logOut')
            self.logOut.clicked.connect(self.onLogOut)
            
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
            
    def onLogOut (self):
        self.widget = Login()
        self.close()
        
    def onAddMember (self):
        self.widget = addMember()
        self.close()
        
    def onAddItem (self):
        self.widget = addItem()
        self.close()
    
    def onAddDiscount (self):
        self.widget = addDiscount()
        self.close()

    # Go to the correct employee modification screen based on if
    # the currently logged in employee is an owner or manager
    def onModifyEmployee (self):
        if (currentlyLoggedIn.accessLevel == 10):
            self.widget = modifyEmployee()
        else:
            self.widget = modifyEmployeeManager()
        self.close()

    def onViewMember (self):
        self.widget = viewMember()
        self.close()

    def onViewItem (self):
        self.widget = viewItems()
        self.close()

    def onViewDiscount (self):
        self.widget = viewDiscounts()
        self.close()

#Non-administrator main page; less features than admins
class mainLower(QMainWindow):
    def __init__(self):
        super(mainLower, self).__init__()
        uic.loadUi('UI/MainWindowLow.ui', self)
        self.showMaximized()

        self.addMember = self.findChild(QtWidgets.QPushButton, 'addMember')
        self.addMember.clicked.connect(self.onAddMember)
        
        self.viewMember = self.findChild(QtWidgets.QPushButton, 'viewMember')
        self.viewMember.clicked.connect(self.onViewMember)
        
        self.changeEmpPass = self.findChild(QtWidgets.QPushButton, 'changeEmpPass')
        self.changeEmpPass.clicked.connect(self.onChangeEmpPass)

        self.viewItem = self.findChild(QtWidgets.QPushButton, 'viewItems')
        self.viewItem.clicked.connect(self.onViewItem)

        self.viewDiscount = self.findChild(QtWidgets.QPushButton, 'viewDiscount')
        self.viewDiscount.clicked.connect(self.onViewDiscount)
            
        self.logOut = self.findChild(QtWidgets.QPushButton, 'logOut')
        self.logOut.clicked.connect(self.onLogOut)
            

    def onLogOut (self):
        self.widget = Login()
        self.close()
        
    def onAddMember (self):
        self.widget = addMember()
        self.close()

    def onViewMember (self):
        self.widget = viewMember()
        self.close()

    def onViewItem (self):
        self.widget = viewItems()
        self.close()

    def onViewDiscount (self):
        self.widget = viewDiscounts()
        self.close()
    
    def onChangeEmpPass (self):
        self.widget = modifyEmpPass()
        self.close()

#Member Creation Page
class addMember(QMainWindow):
    def __init__(self):
        super(addMember, self).__init__()
        uic.loadUi('UI/addMember.ui', self)
        self.showMaximized()
        global memData
        #Setting the date in the page to be the current date
        currentDate = str(date.today())
        splitDate = currentDate.split("-")

        todayDate = QDate(int(splitDate[0]), int(splitDate[1]), int(splitDate[2]))
        self.dateEdit.setDate(todayDate)
        
        self.submit = self.findChild(QtWidgets.QPushButton, 'submitButton')
        self.submit.clicked.connect(lambda: self.onSubmitAddMember(currentDate, todayDate))
        
        self.scan = self.findChild(QtWidgets.QPushButton, 'autoAdd')
        self.scan.clicked.connect(self.onAutoAdd)
        
        self.cancel = self.findChild(QtWidgets.QPushButton, 'cancelButton')
        self.cancel.clicked.connect(self.onCancelAddMember)

        self.name = self.findChild(QtWidgets.QLineEdit, 'name')
        self.DLN = self.findChild(QtWidgets.QLineEdit, 'DLN')
        self.phone = self.findChild(QtWidgets.QLineEdit, 'PhoneNo')
        self.email = self.findChild(QtWidgets.QLineEdit, 'email')
        
        if (memData[0] != ""):
            self.updateFields()
            memData = ["", "", ""]

    def onSubmitAddMember (self, currentDate, todayDate):
        try:
            name = str(self.name.text())

            DOB = str(self.dateEdit.date().toPyDate())
            DOB = str(DOB.replace('-', ''))
            DOB = int(DOB)

            dateDifference = DOB - (int(currentDate.replace('-','')))

            if (self.phone.text().isnumeric() == False):
                phone = 0
            else:
                phone = int(self.phone.text())

            if (self.DLN.text().isnumeric() == False):
                DLN = 0
            else:
                DLN = self.DLN.text()

            email = str(self.email.text())

            if (dateDifference >= 0):
                self.errMsg.setText("Cannot add a member who's DOB is after or on today's date!")
                self.errMsg.setStyleSheet("color: red")

            elif (int(phone) <= 0 or int(DLN) <= 0):
                    self.errMsg.setText("Phone Number and/or DLN cannot be negative/be a 0!")
                    self.errMsg.setStyleSheet("color: red")

            elif (name == ""):
                self.errMsg.setText("Name cannot be blank!")
                self.errMsg.setStyleSheet("color: red")

            else:
                try:
                    newCustomer = Customer(name, DOB, phone, DLN, email)
                    Customer.createAccount(newCustomer)
                    self.errMsg.setText("Success!")
                    self.errMsg.setStyleSheet("color: green")

                except Exception as e:
                    self.errMsg.setText(str(e))
                    self.errMsg.setStyleSheet("color: red")

            self.name.clear()
            self.DLN.clear()
            self.phone.clear()
            self.email.clear()
            self.dateEdit.setDate(todayDate)
            
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
            
    def onAutoAdd (self):
        global memData
        if (memData[0] == ""):
            self.widget = scan()
            self.close()

    # Updates the member registration page with the data gathered from the scan
    def updateFields (self):
        try:
            global memData
            data = memData

            self.name.setText(str(data[0]) + " " + str(data[1]))
            self.DLN.setText(str(data[2]))

            year = data[4][4:]
        
            day = data[4][2:4]

            month = data[4][0:2]

            birthday = QDate(int(year), int(month), int(day))
            self.dateEdit.setDate(birthday)
        except Exception as e:
            self.errMsg.setText("Error scanning license, try again!")
            self.errMsg.setStyleSheet("color: red")

    def onCancelAddMember (self):
        if (currentlyLoggedIn.accessLevel > 0):
            self.widget = adminMain()
        else:
            self.widget = mainLower()
        self.close()

class scan(QMainWindow):
    def __init__(self):
        super(scan, self).__init__()
        uic.loadUi('UI/testScan.ui', self) 
        self.showMaximized()  

        self.submitBtn = self.findChild(QtWidgets.QPushButton, 'submitBtn')
        self.submitBtn.clicked.connect(self.scanFunc)

        self.returnBtn = self.findChild(QtWidgets.QPushButton, 'returnBtn')
        self.returnBtn.clicked.connect(self.onReturn)

    def scanFunc(self):
        try:
            scanString = self.plainTextEdit.toPlainText()

            info = []
            #Parsing through the data, looking for specific prefixes before each required piece of data
            for lns in scanString.splitlines():
                #Prefixes may not be the same for each state
                index = lns.find("DAQ")
                if (index != -1):
                    DLN = lns[index:]
                if lns.startswith("DAC"):
                    firstName = lns
                elif lns.startswith("DCS"):
                    lastName = lns
                elif lns.startswith("DAJ"):
                    state = lns
                elif lns.startswith("DBB"):
                    DOB = lns
            info = [firstName, lastName, DLN, state, DOB]

            global memData
            self.slimDown(info)
            memData = info
            self.widget = addMember()
            self.close()
        except Exception as e:
            self.widget = addMember()
            self.close()

    #Removes the prefixes and newline character from each piece of data
    def slimDown(self, data):
        index = 0
        for each in data:
            noPrefix = each[3:] #Only keep the data after the third character
            noNewLine = noPrefix.rstrip() #Remove the newline character
            data[index] = noNewLine
            index += 1
        #Orders the data to match the output
        return data
    
    def onReturn (self):
        self.widget = addMember()
        self.close()

#Item Creation Page
class addItem(QMainWindow):
    def __init__(self):
        super(addItem, self).__init__()
        uic.loadUi('UI/addItem.ui', self)
        self.showMaximized()
        
        self.submit = self.findChild(QtWidgets.QPushButton, 'submit')
        self.submit.clicked.connect(self.onSubmit)
        
        self.cancel = self.findChild(QtWidgets.QPushButton, 'cancel')
        self.cancel.clicked.connect(self.onCancel)
        
    def onSubmit(self):
        try:
            itemName = str(self.addItemName.text())
            itemSKU = int(self.itemSKU.text())
            itemPrice = self.itemPrice.value()
            ageReq = self.ageReq.isChecked()
            itemAmount = int(self.itemAmount.text())
            
            if (itemName == ""):
                self.errMsg.setText("Item cannot have a blank name!")
                self.errMsg.setStyleSheet("color: red")
            elif (itemSKU == ""):
                self.errMsg.setText("Item SKU cannot be blank!")
                self.errMsg.setStyleSheet("color: red")
            elif (itemPrice == "" or itemPrice <= 0.0):
                self.errMsg.setText("Item Price cannot be 0 or negative!")
                self.errMsg.setStyleSheet("color: red")
            elif (itemAmount == "" or itemAmount <= 0):
                self.errMsg.setText("Item Amount cannot be 0 or negative!")
                self.errMsg.setStyleSheet("color: red")
            else:
                if (ageReq == True):
                    newItem = Item(name=itemName, SKU=itemSKU, price=itemPrice, count=itemAmount, ageRequired=21)
                    Item.storeItem(newItem)
                else:
                    newItem = Item(name=itemName, SKU=itemSKU, price=itemPrice, count=itemAmount)
                    Item.storeItem(newItem)

            if (Item.checkExists(newItem)):
                self.errMsg.setText("Successfully Added Item")
                self.errMsg.setStyleSheet("color: green")
            else:
                self.errMsg.setText("Error Adding Item")
                self.errMsg.setStyleSheet("color: red")
            
            #Resetting the values in the fields
            self.addItemName.clear()
            self.itemSKU.clear()
            self.itemPrice.setValue(1.00)
            self.ageReq.setChecked(False)
            self.itemAmount.clear()
            
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
    
    def onCancel(self):
        self.widget = adminMain()
        self.close()

#Discount Creation Page
class addDiscount(QMainWindow):
    def __init__(self):
        super(addDiscount, self).__init__()
        uic.loadUi('UI/addDiscount.ui', self)
        self.showMaximized()
        
        self.submit = self.findChild(QtWidgets.QPushButton, 'submitBtn')
        self.submit.clicked.connect(self.onSubmit)
            
        self.cancel = self.findChild(QtWidgets.QPushButton, 'cancelBtn')
        self.cancel.clicked.connect(self.onCancel)
        
        todaydate = str(date.today())
        
        splitDate = todaydate.split("-")
    
        todayDate = QDate(int(splitDate[0]), int(splitDate[1]), int(splitDate[2]))
        self.dateEdit.setDate(todayDate)

        self.quantityLabel.hide()
        self.quantityBox.hide()
        self.sku.hide()

        #Dynamically shows inputs based on what the discount/reward type is
        self.discountType.currentIndexChanged[str].connect(self.changeType)
        
    def onSubmit(self):
        error = False
        try:
            discountName = str(self.name.text())
            price = 0
            quantity = 0
            itemSKU = 0

            expiryDate= str(self.dateEdit.date().toPyDate())
            tempExpiryDate = expiryDate.replace('-','')

            if (self.discountType.currentText() == "Priced"):
                rewardType = "price"
                price = float(self.priceBox.value())
                
                if (price <= 0 == False):
                    self.errMsg.setText("Price Has to Be a Postive Non-Zero Number!")
                    error = True
                    
            elif (self.discountType.currentText() == "Visit"):
                rewardType = "visit"
                quantity = self.quantityBox.value()
                
                if (quantity <= int("0")):
                    self.errMsg.setText("Quantity Has to Be a Postive Non-Zero Number!")
                    error = True
                    
            elif (self.discountType.currentText() == "Item"):
                rewardType = "item"
                quantity = self.quantityBox.value()
                itemSKU = self.sku.text()
                
                if (itemSKU.isnumeric() == False and itemSKU == ""):
                    itemSKU = int("-1")
                
                if (quantity <= int("0")):
                    self.errMsg.setText("Quantity Has to Be a Postive Non-Zero Number!")
                    error = True
                
                if (int(itemSKU) < 0):
                    self.errMsg.setText("SKU Has to Be a Postive Number or Zero!")
                    error = True
                
            description = self.description.toPlainText()
            
            if (discountName == ""):
                self.errMsg.setText("Reward Name Cannot Be Blank")
                error = True
            
            if (error == False):
                reward = Reward(name= discountName, expireDate= int(tempExpiryDate), rewardType= rewardType, 
                    numRequired= quantity, priceReq= price, description= description, requirement= itemSKU)
                reward.createReward(currentlyLoggedIn)
                self.errMsg.setText("Successfully added discount!")
                self.errMsg.setStyleSheet("color: green")
                
            else:
                self.errMsg.setStyleSheet("color: red")

            self.name.clear()
            self.priceBox.setValue(0.00)
            self.quantityBox.setValue(0)
            self.sku.clear()
            self.description.clear()

            todaydate = str(date.today())
            splitDate = todaydate.split("-")
            todayDate = QDate(int(splitDate[0]), int(splitDate[1]), int(splitDate[2]))
            self.dateEdit.setDate(todayDate)

        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
    
    def onCancel(self):
        self.widget = adminMain()
        self.close()

    #Different reward types need different inputs
    #Showing/Hiding fields as needed
    def changeType (self, s):
        if (s == "Visit"):
            self.priceLabel.hide()
            self.priceBox.hide()
            self.quantityLabel.show()
            self.quantityBox.show()
            self.sku.hide()
        
        if (s == "Priced"):
            self.priceLabel.show()
            self.priceBox.show()
            self.quantityLabel.hide()
            self.quantityBox.hide()
            self.sku.hide()
        
        if (s == "Item"):
            self.sku.show()
            self.quantityLabel.show()
            self.quantityBox.show()
            self.priceLabel.hide()
            self.priceBox.hide()

#Accessed only by the owner(s)
class modifyEmployee(QMainWindow):
    def __init__(self):
        super(modifyEmployee, self).__init__()
        uic.loadUi('UI/modifyEmployee.ui', self)
        self.showMaximized()

        self.changePass = self.findChild(QtWidgets.QPushButton, 'changePassBtn')
        self.changePass.clicked.connect(self.onChangePass)

        self.changeAccess = self.findChild(QtWidgets.QPushButton, 'changeAccessBtn')
        self.changeAccess.clicked.connect(self.onChangeAccess)

        self.deleteEmp = self.findChild(QtWidgets.QPushButton, 'deleteEmpBtn')
        self.deleteEmp.clicked.connect(self.onDeleteEmp)

        self.cancel = self.findChild(QtWidgets.QPushButton, 'cancelBtn')
        self.cancel.clicked.connect(self.onCancel)

    def onChangePass (self):
        self.widget = modifyEmpPass()
        self.close()
    
    def onChangeAccess (self):
        self.widget = modifyEmpAccess()
        self.close()

    def onDeleteEmp (self):
        self.widget = viewEmployees()
        self.close()

    #Returns to the correct control panel based the current employee's privileges
    #This will be seen many times throughout the rest of the code
    def onCancel (self):
        if (currentlyLoggedIn.accessLevel > 0):
            self.widget = adminMain()
        else:
            self.widget = mainLower()
        self.close()

#Accessed only by the manager(s); less functionality than the owner(s)
class modifyEmployeeManager(QMainWindow):
    def __init__(self):
        super(modifyEmployeeManager, self).__init__()
        uic.loadUi('UI/modifyEmployeeManager.ui', self)
        self.showMaximized()

        self.changePass = self.findChild(QtWidgets.QPushButton, 'changePassBtn')
        self.changePass.clicked.connect(self.onChangePass)

        self.viewEmp = self.findChild(QtWidgets.QPushButton, 'deleteEmpBtn')
        self.viewEmp.clicked.connect(self.onViewEmp)

        self.cancel = self.findChild(QtWidgets.QPushButton, 'cancelBtn')
        self.cancel.clicked.connect(self.onCancel)

    def onChangePass (self):
        self.widget = modifyEmpPass()
        self.close()

    def onViewEmp (self):
        self.widget = viewEmployees()
        self.close()

    def onCancel (self):
        if (currentlyLoggedIn.accessLevel > 0):
            self.widget = adminMain()
        else:
            self.widget = mainLower()
        self.close()

class modifyEmpPass(QMainWindow):
    def __init__(self):
        super(modifyEmpPass, self).__init__()

        if (currentlyLoggedIn.accessLevel > 0):
            uic.loadUi('UI/modifyEmpPass.ui', self)
            self.showMaximized()
        else:
            uic.loadUi('UI/modifyEmpPassLow.ui', self)
            self.showMaximized()

        self.submit = self.findChild(QtWidgets.QPushButton, 'submitBtn')
        self.submit.clicked.connect(self.onSubmit)

        self.cancel = self.findChild(QtWidgets.QPushButton, 'cancelBtn')
        self.cancel.clicked.connect(self.onCancel)

    
    def onSubmit (self):
        enteredUsername = ""

        if (currentlyLoggedIn.accessLevel > 0):
            enteredUsername = str(self.username.text())

        newPass = str(self.newPass.text())
        confirmPass = str(self.confirmPass.text())

        try:
            if (newPass == ""):
                self.errMsg.setText("Password cannot be blank!")
                self.errMsg.setStyleSheet("color: red")

            elif (newPass != confirmPass):
                self.errMsg.setText("Passwords do not match!")
                self.errMsg.setStyleSheet("color: red")

                self.newPass.clear()
                self.confirmPass.clear()

            else:
                if (enteredUsername == "" or enteredUsername == currentlyLoggedIn.username):
                    currentlyLoggedIn.changePassword(newPassword = newPass)

                    self.widget = Login()
                    self.close()

                else:
                    currentlyLoggedIn.changePassword(newPassword = newPass, employee=Employee(username = enteredUsername))
                    
                    self.username.clear()
                    self.newPass.clear()
                    self.confirmPass.clear()

                    self.errMsg.setText("Success!")
                    self.errMsg.setStyleSheet("color: green")

                
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
            
    def onCancel (self):
        if (currentlyLoggedIn.accessLevel > 0):
            self.widget = modifyEmployee()
        else:
            self.widget = mainLower()
        self.close()

#Accessed only by owner(s)
#Allows for the owner to promote or demote other employees
class modifyEmpAccess(QMainWindow):
    def __init__(self):
        super(modifyEmpAccess, self).__init__()
        uic.loadUi('UI/changeAccessLevel.ui', self)
        self.showMaximized()

        global employeeData
        index = 1
        for employee in employeeData:
            self.employeeList.insertItem(index, str(employee[1]))
            index += 1

        self.submit = self.findChild(QtWidgets.QPushButton, 'submitBtn')
        self.submit.clicked.connect(self.onSubmit)
            
        self.cancel = self.findChild(QtWidgets.QPushButton, 'cancelBtn')
        self.cancel.clicked.connect(self.onCancel)

    def onSubmit (self):
        username = self.employeeList.currentText()

        if (self.accessLevel.currentIndex() == 0):
            self.errMsg.setText("Select an Access Level!")
            self.errMsg.setStyleSheet("color: red")
        
        elif (self.employeeList.currentIndex() == 0):
            self.errMsg.setText("Select an Employee!")
            self.errMsg.setStyleSheet("color: red")

            self.employeeList.setCurrentIndex(0)
        else:
            try:
                emp = Employee(username = username)
                
                currentlyLoggedIn.changeAccessLevel(employee=emp, newLevel=(self.accessLevel.currentIndex()) -1)
                
                self.errMsg.setText("Success!")
                self.errMsg.setStyleSheet("color: green")

            except Exception as e:
                self.errMsg.setText(str(e))
                self.errMsg.setStyleSheet("color: red")
        
            self.employeeList.setCurrentIndex(0)
            self.accessLevel.setCurrentIndex(0)
    
    def onCancel (self):
        self.widget = modifyEmployee()
        self.close()

#loads all members and their various options
class viewMember(QMainWindow):
    def __init__(self):
        super(viewMember, self).__init__()
        uic.loadUi('UI/viewMembers.ui', self)
        self.showMaximized()

        infoCust = Customer("", "", None, "")
        data = Customer.displayTable(infoCust)

        self.loadData(data)

        self.searchBtn = self.findChild(QtWidgets.QPushButton, 'searchBtn')
        self.searchBtn.clicked.connect(lambda: self.search(data))        

        self.returnBtn = self.findChild(QtWidgets.QPushButton, 'returnBtn')
        self.returnBtn.clicked.connect(self.onReturn)

        self.cartBtn = self.findChild(QtWidgets.QPushButton, 'viewCartBtn')
        self.cartBtn.clicked.connect(self.onCart)

        self.viewPurchases = self.findChild(QtWidgets.QPushButton, 'viewPurchases')
        self.viewPurchases.clicked.connect(self.onPurchases)

        self.viewAvailableRewards = self.findChild(QtWidgets.QPushButton, 'viewRewardsBtn')
        self.viewAvailableRewards.clicked.connect(self.onViewRewards)

        self.tableWidget.cellClicked.connect(self.wasClicked)

    def loadData(self, data):
        try:
            self.tableWidget.setRowCount(len(data))
            tableIndex = 0

            for row in data:
                self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(row[0]))
                self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1])))
                self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem(str(row[2])))
                self.tableWidget.setItem(tableIndex, 3, QtWidgets.QTableWidgetItem(str(row[3])))
                self.tableWidget.setItem(tableIndex, 4, QtWidgets.QTableWidgetItem(row[4]))

                tableIndex += 1

        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    #Searching for data in the table is NOT case sensitive.
    #This algorithm is used in each table that allows for searching
    #This could be an external function, but unfortunately, each search has different requirements
    def search(self, data):
        self.errMsg.setText("")
        self.errMsg.setStyleSheet("color: white")

        try:
            filterBy = self.filterBox.currentIndex()
            searchFor = self.searchBox.text()

            if (filterBy == 0 or searchFor == ""):
                self.tableWidget.clearContents()
                self.loadData(data)

            else:
                self.tableWidget.clearContents()
                tableIndex = 0

                for row in data:
                    results = (str(row[filterBy - 1]).lower()).find(searchFor.lower())
                    if (results != -1):
                        self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(row[0]))
                        self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1])))
                        self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem(str(row[2])))
                        self.tableWidget.setItem(tableIndex, 3, QtWidgets.QTableWidgetItem(str(row[3])))
                        self.tableWidget.setItem(tableIndex, 4, QtWidgets.QTableWidgetItem(row[4]))

                        tableIndex += 1
                
                self.tableWidget.setRowCount(tableIndex)

                if(tableIndex == 0):
                    self.errMsg.setText("No entries found!")
                    self.errMsg.setStyleSheet("color: red")

        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
    
    def onCart (self):
        global selectedMember

        if selectedMember.name == "":
            self.errMsg.setText("You must select a member first!")
            self.errMsg.setStyleSheet("color: red")
        else:
            self.widget = viewCart()
            self.close()

    def onPurchases (self):
        global selectedMember

        if (selectedMember.name == ""):
            self.errMsg.setText("You must select a member first!")
            self.errMsg.setStyleSheet("color: red")
        else:
            self.widget = viewHistory()
            self.close()
    
    def onViewRewards (self):
        global selectedMember

        if (selectedMember.name == ""):
            self.errMsg.setText("You must select a member first!")
            self.errMsg.setStyleSheet("color: red")
        else:
            self.widget = viewAvailableRewards()
            self.close()
    
    def onReturn (self):
        if (currentlyLoggedIn.accessLevel > 0):
            self.widget = adminMain()
        else:
            self.widget = mainLower()
        self.close()

    #No matter where the user clicks in the table,
    #The required data will be selected properly each time.
    #A version of this algorithm is used in every page where
    #selecting from a table is required
    def wasClicked(self, row):
        customer = self.tableWidget.item(row, 0)
        customerDOB = self.tableWidget.item(row, 1)
        customerPhone = self.tableWidget.item(row, 2)

        name = customer.text()
        phone = str(customerPhone.text())
        DOB = customerDOB.text()

        global selectedMember
        selectedMember = Customer(name=name, DOB = int(DOB), phone=phone)

        print("Selected Name: " + name)

class viewCart(QMainWindow):
    def __init__(self):
        print("[GUI]  Entering viewCart()")
        super(viewCart, self).__init__()
        uic.loadUi('UI/viewCart.ui', self)
        self.showMaximized()

        self.returnBtn = self.findChild(QtWidgets.QPushButton, 'returnBtn')
        self.returnBtn.clicked.connect(self.onReturn)

        self.clearCartBtn = self.findChild(QtWidgets.QPushButton, 'clearCartBtn')
        self.clearCartBtn.clicked.connect(self.onClearCart)

        self.checkOutBtn = self.findChild(QtWidgets.QPushButton, 'checkOutBtn')
        self.checkOutBtn.clicked.connect(self.onCheckOut)

        self.onAddItemBtn = self.findChild(QtWidgets.QPushButton, 'addItemsToCartBtn')
        self.onAddItemBtn.clicked.connect(self.onAddItem)
        
        self.loadData()
        
    
    def loadData(self):
        try:
            global selectedMember
            
            cartData = selectedMember.cart

            tableIndex = 0
            self.tableWidget.setRowCount(len(cartData))
            if (len(cartData) == 0):
                self.errMsg.setText("Cart is empty!")
                self.errMsg.setStyleSheet("color: red")
            else:
                for idx in range(len(cartData)):
                    itemName = cartData[idx].name
                    itemSKU = cartData[idx].SKU
                    itemQuantity = cartData[idx].count

                    self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(str(itemName)))
                    self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(itemSKU)))
                    self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem(str(itemQuantity)))
            
                    tableIndex += 1
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def onClearCart(self):
        selectedMember.clearCart()
        self.loadData()

    def onCheckOut(self):
        try:
            print("CUSTOMER PHONE NUMBER: ", selectedMember.phone)
            cartData = selectedMember.cart
            
            if (len(cartData) == 0):
                self.errMsg.setText("Cannot check out with an empty cart!")
                self.errMsg.setStyleSheet("color: red")
            else:
                selectedMember.checkout()
                self.errMsg.setText("Checkout successful!")
                self.errMsg.setStyleSheet("color: green")

            self.loadData()
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
    
    def onAddItem(self):
        self.widget = viewItemsToPurchase()
        self.close()
    
    def onReturn(self):
        self.widget = viewMember()
        self.close()

#Viewing purchase history of the selected member
class viewHistory(QMainWindow):
    def __init__(self):
        super(viewHistory, self).__init__()
        uic.loadUi('UI/viewPurchaseHistory.ui', self)
        self.showMaximized()

        global selectedMember
        global purchaseHistory

        self.returnBtn = self.findChild(QtWidgets.QPushButton, 'returnBtn')
        self.returnBtn.clicked.connect(self.onReturn)

        purchaseHistory = selectedMember.getPurchaseHistory()

        self.loadData(purchaseHistory)
    
    def loadData(self, purchaseHistory):
        try:
            tableIndex = 0
            self.tableWidget.setRowCount(len(purchaseHistory))
            
            for item in purchaseHistory:
                print(item)
                self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(str(item[1])))
                self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(item[2])))
                self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem("$" + str(item[4]) + " ($" + str(item[4] / item[2]) + ")"))

                tableIndex += 1
            
            if (tableIndex == 0):
                self.errMsg.setText("Member " + selectedMember.name + " has nothing in their cart!")
                self.errMsg.setStyleSheet("color: red")
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
    
    def onReturn(self):
        self.widget = viewMember()
        self.close()

class viewItems(QMainWindow):
    def __init__(self):
        super(viewItems, self).__init__()
        uic.loadUi('UI/viewItems.ui', self)
        self.showMaximized()

        item = Item("", 0, 1)
        data = Item.displayTable(item)

        self.loadData(data)

        self.searchBtn = self.findChild(QtWidgets.QPushButton, 'searchBtn')
        self.searchBtn.clicked.connect(lambda: self.search(data))        

        self.returnBtn = self.findChild(QtWidgets.QPushButton, 'returnBtn')
        self.returnBtn.clicked.connect(self.onReturn)

    def loadData(self, data):
        
        try:
            self.tableWidget.setRowCount(len(data))
            tableIndex = 0

            for row in data:
                self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(row[0]))
                self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1])))
                self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem("$" + str(round(row[2],2))))
                self.tableWidget.setItem(tableIndex, 3, QtWidgets.QTableWidgetItem(str(row[3])))

                tableIndex += 1
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def search(self, data):

        self.errMsg.setText("")
        self.errMsg.setStyleSheet("color: white")

        try:
            filterBy = self.filterBox.currentIndex()
            searchFor = self.searchBox.text()

            if (filterBy == 0 or searchFor == ""):
                self.tableWidget.clearContents()
                self.loadData(data)

            else:
                self.tableWidget.clearContents()
                tableIndex = 0

                for row in data:
                    results = (str(row[filterBy - 1]).lower()).find(searchFor.lower())
                    if (results != -1):
                        self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(row[0]))
                        self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1])))
                        self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem(str(row[2])))

                        tableIndex += 1
                
                self.tableWidget.setRowCount(tableIndex)

                if(tableIndex == 0):
                    self.errMsg.setText("No entries found!")
                    self.errMsg.setStyleSheet("color: red")

        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def onReturn (self):
        if (currentlyLoggedIn.accessLevel > 0):
            self.widget = adminMain()
        else:
            self.widget = mainLower()
        self.close()

class viewItemsToPurchase(QMainWindow):
    def __init__(self):
        super(viewItemsToPurchase, self).__init__()
        uic.loadUi('UI/viewItemsToAddToCart.ui', self)
        self.showMaximized()

        item = Item("", 0, 1)
        data = Item.displayTable(item)

        self.loadData(data)

        self.searchBtn = self.findChild(QtWidgets.QPushButton, 'searchBtn')
        self.searchBtn.clicked.connect(lambda: self.search(data))        

        self.addToCartBtn = self.findChild(QtWidgets.QPushButton, 'addToCartBtn')
        self.addToCartBtn.clicked.connect(self.addToCart)

        self.returnBtn = self.findChild(QtWidgets.QPushButton, 'returnBtn')
        self.returnBtn.clicked.connect(self.onReturn)

        self.tableWidget.cellClicked.connect(self.wasClicked)

    def loadData(self, data):
        
        try:
            self.tableWidget.setRowCount(len(data))
            tableIndex = 0

            for row in data:
                self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(row[0])) #name
                self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1]))) #SKU
                self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem(str(row[2]))) #Price
                self.tableWidget.setItem(tableIndex, 3, QtWidgets.QTableWidgetItem(str(row[3]))) #Quantity
                if (row[4] == 21):
                    self.tableWidget.setItem(tableIndex, 4, QtWidgets.QTableWidgetItem("Yes")) #Age Req
                elif (row[4] == 0):
                    self.tableWidget.setItem(tableIndex, 4, QtWidgets.QTableWidgetItem("No")) #Age Req
            
                tableIndex += 1
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def search(self, data):

        self.errMsg.setText("")
        self.errMsg.setStyleSheet("color: white")

        try:
            filterBy = self.filterBox.currentIndex()
            searchFor = self.searchBox.text()

            if (filterBy == 0 or searchFor == ""):
                self.tableWidget.clearContents()
                self.loadData(data)

            else:
                self.tableWidget.clearContents()
                tableIndex = 0

                for row in data:
                    results = (str(row[filterBy - 1]).lower()).find(searchFor.lower())
                    if (results != -1):
                        self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(row[0]))
                        self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1])))
                        self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem(str(row[2])))
                        self.tableWidget.setItem(tableIndex, 3, QtWidgets.QTableWidgetItem(str(row[3])))
                        self.tableWidget.setItem(tableIndex, 4, QtWidgets.QTableWidgetItem(str(row[4])))

                        tableIndex += 1
                
                self.tableWidget.setRowCount(tableIndex)

                if(tableIndex == 0):
                    self.errMsg.setText("No entries found!")
                    self.errMsg.setStyleSheet("color: red")

        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
    
    def wasClicked(self, row):
        global selectedItem
        itemName = self.tableWidget.item(row, 0).text()
        itemSKU = self.tableWidget.item(row, 1).text()
        itemPrice = self.tableWidget.item(row, 2).text()
        itemQuantity = self.tableWidget.item(row, 3).text()
        itemAgeReq = self.tableWidget.item(row, 4).text()
        
        if (itemAgeReq == "Yes"):
            itemAgeReq = 21
        else:
            itemAgeReq = 0

        selectedItem = Item(SKU=itemSKU, name=itemName, price=itemPrice, count=itemQuantity, ageRequired=itemAgeReq)

        self.errMsg.setText("Item: " + itemName + " was selected!")
        self.errMsg.setStyleSheet("color: green")
    
    def addToCart(self):
        try:
            global selectedItem
            global selectedMember

            currentDate = str(date.today())
            splitDate = currentDate.split("-")
            dateCombined = splitDate[0] + splitDate[1] + splitDate[2]

            num,ok = QInputDialog.getInt(self,"Add to " + selectedMember.name + "'s cart","Quantity of " + selectedItem.name + ": ")
            
            if ok:
                try:
                    selectedItem.count = num
                    selectedMember.addItemToCart(selectedItem)

                    self.errMsg.setText(str(selectedItem.count) + " " + selectedItem.name + "'s was successfully added to " + selectedMember.name + "'s cart!")
                    self.errMsg.setStyleSheet("color: green")
                except Exception as e:
                    self.errMsg.setText(str(e))
                    self.errMsg.setStyleSheet("color: red")

            else:
                selectedItem = Item(SKU=0)
                self.errMsg.setText("Cancelled adding item to cart!")
                self.errMsg.setStyleSheet("color: red")
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
         
    def onReturn (self):
        self.widget = viewCart()
        self.close()

class viewDiscounts(QMainWindow):
    def __init__(self):
        super(viewDiscounts, self).__init__()
        uic.loadUi('UI/viewDiscounts.ui', self)
        self.showMaximized()

        global data

        self.loadData()

        self.searchBtn = self.findChild(QtWidgets.QPushButton, 'searchBtn')
        self.searchBtn.clicked.connect(self.search)        

        self.returnBtn = self.findChild(QtWidgets.QPushButton, 'returnBtn')
        self.returnBtn.clicked.connect(self.onReturn)

        self.activeBtn = self.findChild(QtWidgets.QPushButton, 'setActiveBtn')
        self.activeBtn.clicked.connect(self.onActive)

        self.tableWidget.cellClicked.connect(self.wasClicked)

    def loadData(self):
        try:
            
            global data
            global discount
            global selectedDiscount

            selectedDiscount = Reward(name = "", expireDate= 0, rewardType= "visit")

            data = Reward.displayAllRewards(discount)

            self.tableWidget.setRowCount(len(data))
            tableIndex = 0

            for row in data:
                self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(str(row[0])))
                self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1])))
                self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem(str(row[2])))
                self.tableWidget.setItem(tableIndex, 3, QtWidgets.QTableWidgetItem(str(row[3])))
                self.tableWidget.setItem(tableIndex, 4, QtWidgets.QTableWidgetItem(str(row[4])))
                if (row[5] == 0): #Active Status
                    self.tableWidget.setItem(tableIndex, 5, QtWidgets.QTableWidgetItem("No"))
                else:
                    self.tableWidget.setItem(tableIndex, 5, QtWidgets.QTableWidgetItem("Yes"))
                self.tableWidget.setItem(tableIndex, 6, QtWidgets.QTableWidgetItem(str(row[6])))
                self.tableWidget.setItem(tableIndex, 7, QtWidgets.QTableWidgetItem(str(row[7])))
                self.tableWidget.setItem(tableIndex, 8, QtWidgets.QTableWidgetItem(str(row[8])))
                self.tableWidget.setItem(tableIndex, 9, QtWidgets.QTableWidgetItem(str(row[9])))

                tableIndex += 1
            self.errMsg.setText("Successfully loaded data!")
            self.errMsg.setStyleSheet("color: green")
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def search(self):

        self.errMsg.setText("")
        self.errMsg.setStyleSheet("color: white")

        try:
            filterBy = self.filterBox.currentIndex()

            searchFor = self.searchBox.text()

            if (searchFor.lower() == "no"):
                searchFor = "0"
            elif (searchFor.lower() == "yes"):
                searchFor = "1"

            if (filterBy == 0 or searchFor == ""):
                self.tableWidget.clearContents()
                self.loadData()

            else:
                self.tableWidget.clearContents()
                tableIndex = 0

                for row in data:
                    results = (str(row[filterBy - 1]).lower()).find(searchFor.lower())
                    if (results != -1):
                        
                        self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(str(row[0])))
                        self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1])))
                        self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem(str(row[2])))
                        self.tableWidget.setItem(tableIndex, 3, QtWidgets.QTableWidgetItem(str(row[3])))
                        self.tableWidget.setItem(tableIndex, 4, QtWidgets.QTableWidgetItem(str(row[4])))
                        if (row[5] == 0):
                            self.tableWidget.setItem(tableIndex, 5, QtWidgets.QTableWidgetItem("No"))
                        else:
                            self.tableWidget.setItem(tableIndex, 5, QtWidgets.QTableWidgetItem("Yes"))
                        self.tableWidget.setItem(tableIndex, 6, QtWidgets.QTableWidgetItem(str(row[6])))
                        self.tableWidget.setItem(tableIndex, 7, QtWidgets.QTableWidgetItem(str(row[7])))
                        self.tableWidget.setItem(tableIndex, 8, QtWidgets.QTableWidgetItem(str(row[8])))
                        self.tableWidget.setItem(tableIndex, 9, QtWidgets.QTableWidgetItem(str(row[9])))

                        tableIndex += 1
                
                self.tableWidget.setRowCount(tableIndex)

                if(tableIndex == 0):
                    self.errMsg.setText("No entries found!")
                    self.errMsg.setStyleSheet("color: red")

        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def onActive (self):
        try:
            global selectedDiscount

            if (selectedDiscount.isActive() == True):
                selectedDiscount.disableReward()
            else:
                selectedDiscount.enableReward()
            self.loadData()
        except Exception as e:
            self.errMsg.setText("You must select a reward before changing active status!")
            self.errMsg.setStyleSheet("color: red")

    def wasClicked(self, row):
        reward = self.tableWidget.item(row, 0)
        name = reward.text()
        global selectedDiscount
        selectedDiscount = Reward(name = name, expireDate= 0, rewardType= "visit")

    def onReturn (self):
        if (currentlyLoggedIn.accessLevel > 0):
            self.widget = adminMain()
        else:
            self.widget = mainLower()
        self.close()

class viewAvailableRewards(QMainWindow):
    def __init__(self):
        super(viewAvailableRewards, self).__init__()
        uic.loadUi('UI/viewMemberRewards.ui', self)
        self.showMaximized()

        self.loadData()      

        self.useRewardBtn = self.findChild(QtWidgets.QPushButton, 'useRewardBtn')
        self.useRewardBtn.clicked.connect(self.redeemReward)

        self.returnBtn = self.findChild(QtWidgets.QPushButton, 'returnBtn')
        self.returnBtn.clicked.connect(self.onReturn)

        self.tableWidget.cellClicked.connect(self.wasClicked)

    def loadData(self):
        try:
            
            global availableRewards
            global selectedMember

            availableRewards = selectedMember.checkAvailableRewards()

            self.tableWidget.setRowCount(len(availableRewards))
            tableIndex = 0

            for row in availableRewards:
                self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(str(row[1])))
                self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[2])))
                self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem(str(row[3])))

                tableIndex += 1
            if (not availableRewards):
                self.errMsg.setText("Member has no available rewards!")
                self.errMsg.setStyleSheet("color: red")
            else:
                self.errMsg.setText("Successfully loaded data!")
                self.errMsg.setStyleSheet("color: green")
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")
    
    def onReturn(self):
        self.widget = viewMember()
        self.close()
    
    def redeemReward(self):
        global selectedDiscountID
        global selectedMember
        try:
            selectedMember.redeemReward(selectedDiscountID)
            selectedDiscountID = 0

            self.errMsg.setText("Successfully redeemed reward!")
            self.errMsg.setStyleSheet("color: green")

            self.loadData()
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def wasClicked(self, row):
        reward = self.tableWidget.item(row, 2)
        ID = reward.text()
        global selectedDiscountID
        selectedDiscountID = int(ID)

class viewEmployees(QMainWindow):
    def __init__(self):
        super(viewEmployees, self).__init__()
        uic.loadUi('UI/deleteEmployees.ui', self)
        self.showMaximized()

        self.loadData()

        self.searchBtn = self.findChild(QtWidgets.QPushButton, 'searchBtn')
        self.searchBtn.clicked.connect(self.search)        

        self.returnBtn = self.findChild(QtWidgets.QPushButton, 'returnBtn')
        self.returnBtn.clicked.connect(self.onReturn)

        if (currentlyLoggedIn.accessLevel == 10):
            self.deleteBtn = self.findChild(QtWidgets.QPushButton, 'deleteBtn')
            self.deleteBtn.clicked.connect(self.onDelete)
        else:
            self.deleteBtn.hide()

        self.tableWidget.cellClicked.connect(self.wasClicked)

    def loadData(self):
        try:
            global employee
            global employeeData
            
            employeeData = Employee.getEmployees(employee)

            self.tableWidget.setRowCount(len(employeeData))
            tableIndex = 0

            for row in employeeData:
                self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(str(row[4]))) #name
                self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1]))) #username
                if (row[0]== 0):
                    self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem("Employee")) #role
                elif (row[0] == 1):
                    self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem("Manager")) #role
                else:
                    self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem("Owner")) #role

                tableIndex += 1
        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def search(self):

        self.errMsg.setText("")
        self.errMsg.setStyleSheet("color: white")

        try:
            filterBy = self.filterBox.currentIndex()

            searchFor = self.searchBox.text()
            
            if (searchFor.lower() == "employee"):
                searchFor = "0"
            elif (searchFor.lower() == "manager"):
                searchFor = "1"
            elif (searchFor.lower() == "owner"):
                searchFor = "10"

            if (filterBy == 0 or searchFor == ""):
                self.tableWidget.clearContents()
                self.loadData()

            else:
                self.tableWidget.clearContents()
                tableIndex = 0

                if (filterBy == 1):
                    filterBy = 4
                elif (filterBy == 2):
                    filterBy = 1
                elif (filterBy == 3):
                    filterBy = 0
                
                for row in employeeData:
                    results = (str(row[filterBy]).lower()).find(searchFor.lower())
                    if (results != -1):
                        self.tableWidget.setItem(tableIndex, 0, QtWidgets.QTableWidgetItem(str(row[4]))) #name
                        self.tableWidget.setItem(tableIndex, 1, QtWidgets.QTableWidgetItem(str(row[1]))) #username
                        if (row[0]== 0):
                            self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem("Employee")) #role
                        elif (row[0] == 1):
                            self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem("Manager")) #role
                        else:
                            self.tableWidget.setItem(tableIndex, 2, QtWidgets.QTableWidgetItem("Owner")) #role

                        tableIndex += 1
                
                self.tableWidget.setRowCount(tableIndex)

                if(tableIndex == 0):
                    self.errMsg.setText("No entries found!")
                    self.errMsg.setStyleSheet("color: red")

        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def onDelete (self):
        global selectedEmployee
        try:
            if (selectedEmployee.username == ""):
                self.errMsg.setText("You must select an employee to delete!")
                self.errMsg.setStyleSheet("color: red")
            else:
                verification = QMessageBox(QMessageBox.Question, 'Delete Verification', "Are you sure you want to delete employee " + selectedEmployee.username + "?")
                verification.addButton(QMessageBox.Yes)
                verification.addButton(QMessageBox.No)
                verification.setStyleSheet("color:black;background:white")

                ret = verification.exec()

                if ret == verification.Yes:
                    try:
                        currentlyLoggedIn.deleteAccount(selectedEmployee)
                    except Exception as e:
                        self.errMsg.setText(str(e))
                        self.errMsg.setStyleSheet("color: red")
                    self.loadData()
                else:
                    self.errMsg.setText("Deletion Cancelled")
                    self.errMsg.setStyleSheet("color: red")

        except Exception as e:
            self.errMsg.setText(str(e))
            self.errMsg.setStyleSheet("color: red")

    def wasClicked(self, row):
        employee = self.tableWidget.item(row, 1)
        name = employee.text()
        global selectedEmployee
        selectedEmployee = Employee(username = name, password = "")

    def onReturn (self):
        if (currentlyLoggedIn.accessLevel == 10):
            self.widget = modifyEmployee()
        else:
            self.widget = modifyEmployeeManager()
        self.close()