from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QInputDialog, QLineEdit
from Classes.Employee import Employee

class Registration(QMainWindow):
    def __init__(self):
        super(Registration, self).__init__()
        uic.loadUi('UI/registrationWindow.ui', self)
        self.showMaximized()
        self.submit = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.submit.clicked.connect(self.onSubmitRegistration)
        
        self.cancel = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.cancel.clicked.connect(self.onCancelRegistration)
        
        self.username = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.password = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        self.passwordCheck = self.findChild(QtWidgets.QLineEdit, 'lineEdit_3')
        self.name = self.findChild(QtWidgets.QLineEdit, 'lineEdit_4')
        
        self.show()
    
    def onSubmitRegistration(self):
        if (self.password.text() != self.passwordCheck.text()):
            
            Registration.errorMessage(self, "Passwords must be the same!")
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
        else:
            try:
                adminUser, okPressed = QInputDialog.getText(self, 'Administrator Verification', 'Enter Administrator Username:', QLineEdit.Normal, "")
                if (okPressed and adminUser != ''):
                    adminPass, okPressed2 = QInputDialog.getText(self, 'Administrator Verification', 'Enter Administrator Password:', QLineEdit.Normal, "")
                    if (okPressed2 and adminPass != ''):
                        checkAdmin = Employee(username = str(adminUser), password = str(adminPass))
                
                        if (checkAdmin.verifyLogin() == True and checkAdmin.accessLevel > 0):
                            newEmployee = Employee(username=self.username.text(), password=self.password.text(), employeeName=self.name.text())
                            newEmployee.createAccount()
                    
                            successMsg = QMessageBox()
                            successMsg.setWindowTitle('Success!')
                            successMsg.setText('Success Creating Account!')
                            
                            successMsg.exec()
                    
                            self.widget = Login()
                            self.close()
                        elif (checkAdmin.verifyLogin() == False or checkAdmin.accessLevel <= 0):
                            Registration.errorMessage("Cannot Add Employee!")
                else:
                    #adminUser.
                    print("test")            
            except Exception as e:
                Registration.errorMessage(self, str(e))
            
            self.lineEdit.clear()
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            self.lineEdit_4.clear()
            
                  
    def onCancelRegistration(self):
        self.widget = Login()
        self.close()

    def errorMessage(self, message):
        failMsg = QMessageBox()
        failMsg.setIcon(QMessageBox.Critical)
        failMsg.setWindowTitle('Error!')
        failMsg.setText(message)
        
        failMsg.exec_()
        
class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi('UI/loginWindow2.ui', self)
        self.showMaximized()
        Employee("test").displayTable()
        self.submit = self.findChild(QtWidgets.QPushButton, 'pushButton_3')
        self.submit.clicked.connect(self.onRegister)
        
        self.cancel = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.cancel.clicked.connect(self.onSubmit)
        
        self.username = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.password = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        
        self.show()
    
    def onRegister(self):
        self.widget = Registration()
        self.close()
            
    def onSubmit(self):
        #self.close()
        checkEmployee = Employee(username = self.username.text(), password = self.password.text())
        try:
            if (checkEmployee.verifyLogin() == True):
                self.widget = Main(self.username.text())
                self.close()
            else:
                Login.errorMessage(self, "Invalid username and/or password!")
        except Exception as e:
            Login.errorMessage(self, str(e))
            
    def errorMessage(self, message):
        failMsg = QMessageBox()
        failMsg.setIcon(QMessageBox.Critical)
        failMsg.setWindowTitle('Error!')
        failMsg.setText(message)
        
        failMsg.exec_()
    
        
class Main(QMainWindow):
    def __init__(self, username):
        super(Main, self).__init__()
        uic.loadUi('UI/MainWindow.ui', self)
        self.showMaximized()
        self.label_3.setText(username)
        
        self.show()
