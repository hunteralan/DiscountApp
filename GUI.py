import sys
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from Classes.Employee import Employee
from Classes.Database import Database 

class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('UI/registration.ui', self)
        
        self.submit = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.submit.clicked.connect(self.onSubmitRegistration)
        
        self.cancel = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.cancel.clicked.connect(self.onCancelRegistration)
        
        self.username = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.password = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        self.passwordCheck = self.findChild(QtWidgets.QLineEdit, 'lineEdit_3')
        self.name = self.findChild(QtWidgets.QLineEdit, 'lineEdit_4')
        
        self.show()
    
    def onSubmitRegistration(self):
        if (self.password.text() != self.passwordCheck.text()):
            failMsg = QMessageBox()
            failMsg.setIcon(QMessageBox.Critical)
            failMsg.setWindowTitle('Error!')
            failMsg.setText("Your Passwords Must Be The Same!")

            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            
            x = failMsg.exec_()
        else:
            try:
                print(self.username.text() + '\n')
                print(self.password.text() + '\n')
                print(self.passwordCheck.text() + '\n')
                print(self.name.text() + '\n')
            
                newEmployee = Employee(username=self.username.text(), password=self.password.text(), employeeName=self.name.text())
                newEmployee.createAccount()
                Employee("test").displayTable()
            
                self.lineEdit.clear()
                self.lineEdit_2.clear()
                self.lineEdit_3.clear()
                self.lineEdit_4.clear()
            except Exception:
                print("Exception here")
    def onCancelRegistration(self):
        self.close()


if __name__ == '__main__':
    
    #authDB = Database(dbSelection="auth").initialize()
    #mainDB = Database(dbSelection="main").initialize()
    
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    
    sys.exit(app.exec_())
    