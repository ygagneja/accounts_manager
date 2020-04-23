import sqlite3
from sqlite3 import Error

def sql_connection():
    try:
        con = sqlite3.connect('./db/main.db')
        return con
    except Error:
        print(Error)

def create_tables(con):
    cursorObj = con.cursor()
    cursorObj.execute("create table if not exists accounts(account_name text PRIMARY KEY)")
    cursorObj.execute("create table if not exists records(date text, account_name text, amount integer, c_d integer, FOREIGN KEY (account_name) REFERENCES accounts (account_name))")
    con.commit()

def insert_new_account(con, account):
    try:
        cursorObj = con.cursor()
        cursorObj.execute("INSERT INTO accounts VALUES('" + account + "')")
        con.commit()
        return True
    except Error:
        return False

def insert_new_record(con, date, account, amount, c_d):
    try:
        cursorObj = con.cursor()
        cursorObj.execute("INSERT INTO records VALUES('" + date + "', '" + account + "', " + str(amount) + ", " + str(c_d) + ")")
        con.commit()
        return True
    except Error:
        print(Error)
        return False

def fetch_accounts(con):
    cursorObj = con.cursor()
    cursorObj.execute("SELECT * FROM accounts")
    rows = cursorObj.fetchall()
    accounts = []
    for row in rows:
        accounts.append(row[0])
    return accounts

def fetch_records_account(con, account):
    cursorObj = con.cursor()
    cursorObj.execute("SELECT * FROM records WHERE account_name='" + account + "'")
    rows = cursorObj.fetchall()
    data = []
    credit, debit, overall = 0, 0, 0
    for row in rows:
        if not row[3]:
            credit += row[2]
        else:
            debit += row[2]
        data.append(list(row))
    return (data, credit, debit, credit - debit)

def delete_account_and_records(con, account):
    cursorObj = con.cursor()
    cursorObj.execute("DELETE FROM accounts WHERE account_name='" + account + "'")
    cursorObj.execute("DELETE FROM records WHERE account_name='" + account + "'")
    con.commit()