from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QPushButton, QMainWindow, QApplication, QDateEdit, QComboBox, QTextEdit, QDialog, QTableView, QLabel
from PyQt5.QtCore import QAbstractTableModel, Qt
import sys
import numpy as np
from db_handler import *

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('accounts.ui', self)
        self.con = sql_connection()
        create_tables(self.con)
        self.accounts_list = fetch_accounts(self.con)

        self.create_button = self.findChild(QPushButton, 'create_button')
        self.create_button.clicked.connect(self.createAccount)

        self.add_button = self.findChild(QPushButton, 'add_button')
        self.add_button.clicked.connect(self.addRecord)

        self.query_button = self.findChild(QPushButton, 'query_button')
        self.query_button.clicked.connect(self.queryAccount)

        self.delete_button = self.findChild(QPushButton, 'delete_button')
        self.delete_button.clicked.connect(self.deleteAccount)

        self.delete_rec_button = self.findChild(QPushButton, 'delete_rec_button')
        self.delete_rec_button.clicked.connect(self.deleteRecord)

        self.date = self.findChild(QDateEdit, 'date')
        self.account = self.findChild(QComboBox, 'accounts_drop')
        self.account.clear()
        self.account.addItems(self.accounts_list)
        self.amount = self.findChild(QTextEdit, 'amount_num')
        self.c_d = self.findChild(QComboBox, 'c_d_drop')
        self.account_2 = self.findChild(QComboBox, 'accounts_drop_2')
        self.account_2.clear()
        self.account_2.addItems(self.accounts_list)

        self.show()

    def dialogW(self, msg):
        QMessageBox.warning(self, 'Error', msg, QMessageBox.Ok, QMessageBox.Ok)

    def dialogQ(self, msg):
        qm = QMessageBox()
        ret = qm.question(self, "Confirm", msg, qm.Yes, qm.No)
        return ret == qm.Yes

    def dialogS(self, msg):
        QMessageBox.information(self, 'Success', msg, QMessageBox.Ok, QMessageBox.Ok)

    def createAccount(self):
        print ("created account")
        dlg = CustomDialog(self.con)
        dlg.exec_()
        self.accounts_list = fetch_accounts(self.con)
        self.account.clear()
        self.account.addItems(self.accounts_list)
        self.account_2.clear()
        self.account_2.addItems(self.accounts_list)


    def addRecord(self):
        date = self.date.date().toPyDate()
        account = self.account.currentText()
        amount = self.amount.toPlainText()
        c_d = 0 if self.c_d.currentText() == "Credit" else 1

        if account == "":
            self.dialogW("Please select a valid account name.")
            return
        if not amount.isdigit():
            self.dialogW("Please insert a valid amount in numbers.")
            return

        amount = int(amount)
        date = date.strftime("%d-%m-%Y")
        if insert_new_record(self.con, date, account, amount, c_d):
            self.dialogS("Record successfully added!")
        else:
            self.dialogW("There was some error. Please try again.")

    def queryAccount(self):
        account_2 = self.account_2.currentText()
        if account_2 == "":
            self.dialogW("Please select a valid account name.")
            return
        
        table = TableDialog(self.con, account_2)
        table.exec_()

    def deleteAccount(self):
        account_2 = self.account_2.currentText()
        if account_2 == "":
            self.dialogW("Please select a valid account name.")
            return
        
        delete = self.dialogQ("Are you sure to delete the selected account?")
        
        if delete:
            delete_account_and_records(self.con, account_2)
            self.accounts_list = fetch_accounts(self.con)
            self.account.clear()
            self.account.addItems(self.accounts_list)
            self.account_2.clear()
            self.account_2.addItems(self.accounts_list)
            self.dialogS("Selected account has been successfully deleted!")


    def deleteRecord(self):
        print ("last record deleted")
        # DIALOG DISPLAYING RECORD ASKING FOR CONFIRMATION
        # get hold of records.db
        # delete last record
        # SUCCESS DIALOG BOX

class TableDialog(QDialog):
    def __init__(self, con, account):
        super(TableDialog, self).__init__()
        uic.loadUi('table.ui', self)

        self.con = con
        self.account = account
        self.data, self.credit, self.debit, self.overall = fetch_records_account(con, self.account)
        self.table = self.findChild(QTableView, 'table')
        self.findChild(QLabel, 'title').setText(self.account)
        self.findChild(QLabel, 'credit').setText(str(self.credit))
        self.findChild(QLabel, 'debit').setText(str(self.debit))
        self.findChild(QLabel, 'overall').setText(str(self.overall))

        self.model = TableModel(self.data, ['Date', 'Account Name', 'Amount', 'Credit/Debit'])
        self.table.setModel(self.model)

class TableModel(QAbstractTableModel):
    def __init__(self, data, labels):
        super(TableModel, self).__init__()
        self.data = np.array(data)
        self.headerdata = labels
        self.cols = 4
        for row in range(self.data.shape[0]):
            self.data[row,3] = "Credit" if not int(self.data[row,3]) else "Debit"

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self.data[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self.data.shape[0]

    def columnCount(self, index):
        return self.cols

    def headerData(self, col, orientation, role):
        if orientation==Qt.Horizontal and role==Qt.DisplayRole:
            return self.headerdata[col]
        if orientation==Qt.Vertical and role==Qt.DisplayRole:
            return col+1
        return None

class CustomDialog(QDialog):
    def __init__(self, con):
        super(CustomDialog, self).__init__()
        uic.loadUi('account_dialog.ui', self)

        self.con = con

        self.account_name = self.findChild(QTextEdit, 'account_field')    
        self.ok_button = self.findChild(QPushButton, 'ok_button')
        self.cancel_button = self.findChild(QPushButton, 'cancel_button')
        self.ok_button.clicked.connect(self.createAccount)
        self.cancel_button.clicked.connect(self.close)
        
    def dialogW(self, msg):
        QMessageBox.warning(self, 'Error', msg, QMessageBox.Ok, QMessageBox.Ok)

    def dialogS(self, msg):
        QMessageBox.information(self, 'Success', msg, QMessageBox.Ok, QMessageBox.Ok)

    def createAccount(self):
        account_name = self.account_name.toPlainText()
        if account_name == "":
            self.dialogW("Please enter a valid account name.")
            return
        if insert_new_account(self.con, account_name):
            self.dialogS("New account added successfully!")
            self.close()
        else:
            self.dialogW("The account already exists.")

app = QApplication(sys.argv)
window = Ui()
app.exec_()

#optimize memory
#default date
#try-excepts
#add description box
#make code extendable
#show all records
#delete record at index
#take care of sorting
#save particular account query
#add security to db