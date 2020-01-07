import pandas as pd
import datetime
import platform
import pymysql
import random
from tabulate import tabulate
import os

conn = pymysql.connect(
    host="localhost",
    user="root",
    passwd="1234",
    db="bank")

c = conn.cursor()

Cdate = datetime.datetime.now()
Cdate = str(Cdate)[0:10]

#function to create a new account

def New_customer_entry():

    accno= int(random.randrange(100000000, 999999999))

    name=input("enter the customer name: ")

    age=int(input("enter age of customer: "))

    occupation=input("enter the customer occupation: ")

    address=input("enter address of the customer: ")

    mobileno=int(input("enter mobile number: "))

    aadharno=int(input("enter the aadhar number: "))

    amt=float(input("enter the deposit amount: "))

    acctype=input("enter the account type[s/c]: ")

    if acctype.lower() == "s":
        acctype = "savings"
    else:
        acctype = "current"

    try:
        sql = f"INSERT INTO account VALUES({accno},'{name}',{age},'{occupation}','{address}',{mobileno},{aadharno},{amt},'{acctype}','{Cdate}');"
        c.execute(sql)
        conn.commit()
        print(f"Your account is created and {accno} is your account number")
    except:
        print("\nHy! duplicate value not allowed")

#function to display account details

def view_Customers():

    s= int(input("enter account no: "))
    data = pd.read_sql(f"select * from account where accno = {s};", conn, columns = ['Account No','Name','Age','Occupation','Address','Mobile No','Aadhar No','Balance','Account Type','Date'])
    print(tabulate(data, showindex=False, tablefmt="fancy_grid", headers='keys', numalign='right'))


#--------------------------------------------------------------
#function to modify address or mobile of customer
#--------------------------------------------------------------

def modify_account():
    accno=int(input("Enter the account no: "))
    print("Select the option to update: ")
    print("1. address")
    print("2. mobile")
    ch=int(input("Enter the choice: "))
    if ch==1:
        Naddress=input("enter the new address")
        query="update account set address="+"'"+Naddress+"'"+"where accno="+str(accno)
        cursor=conn.cursor()
        cursor.execute(query)
        conn.commit()
    elif ch==2:
        Nmobileno=input("enter new mobile no:")
        query= f"update account set mobileno= {Nmobileno} where accno= {accno};"
        cursor=conn.cursor()
        cursor.execute(query)
        conn.commit()
    else:
        print("wrong operation")
        runAgain()
#------------------------------------------------------------
#function to deposit/withdrawal amount in a given account
#------------------------------------------------------------
def Daily_transaction():
    print('date:', Cdate)
    taccno = int(input('Please enter the account number: '))
    df=pd.read_sql(f"select amt from account where accno={taccno};",conn)
    balance = str(int(df.loc[0][0]))
    #transaction date is the current date 
    #tran date=CurDt
    tamount = int(input("Enter the amount: "))
    tran_type=input("enter the transaction type [d/w]: ")
    description=input("enter the transaction description: ")
    if tran_type.upper() == 'D':
        #creating new balance amount by adding current deposit amt
        tran_type = "Deposit"
        query = f"UPDATE account set amt = amt + {tamount} where accno = {taccno};"
        c.execute(query)
        conn.commit()        
        #using exceptions for validation
        try:
            #a query command to select records from both account and transaction table
            #according to account number-wise
            sql = f"insert into transaction values({taccno},{tamount},'{Cdate}','{tran_type}','{description}',{balance});"
            c.execute(sql)
            conn.commit()
        except:
            print("\n transaction didn't succeed")  #error message
    elif tran_type.upper()=='W':
        #creating new balance amount by subtracting current withdrawal amount
        query=f"UPDATE account set amt = amt - {tamount} where accno={taccno};"
        c.execute(query)
        tran_type = "Withdraw"
        #convert list L into a tuple
        #using exceptions for validations
        try:
            sql = f"insert into transaction values({taccno},{tamount},'{Cdate}','{tran_type}','{description}',{balance});"
            c.execute(sql)
            conn.commit()
        except:
            print("\n transaction didn't succeed")  #error message
            runAgain()
#-------------------------------------------------------------------------
#function to display statement of a account between two dates
#------------------------------------------------------------------------
def account_statement_datewise():
    accno=int(input("Enter the account number of the customer: "))
    start = input("Enter starting date [yyyy-mm-dd]: ")
    end = input("Enter ending date [yyyy-mm-dd]: ")
    try:
        #a query command to select record from account and transaction table according to
        #account no and within a date range
        sql= f"select account.accno,account.name,transaction.dt_tran,transaction.tran_amt,transaction.tran_type,transaction.balance,transaction.description from account INNER JOIN transaction ON account.accno=transaction.accno and transaction.accno={accno} and transaction.dt_tran between '{start}' and '{end}';"
        c.execute(sql)
        res=c.fetchall()
        i=0
        for x in res:     
            i=i+1
            a=res[0][0]    #accno
            b=res[0][1]    #account holder's name
            print("\n\naccno",accno)
            print("="*100)
            print("statements from",start,'to',end)
            print("="*100)
            print("{0:<15}{1:<30}{2:<17}{3:<25s}{4:<17s}".format("date","description","amt","deposit/withdrawal","balance"))
            print("="*100)
            for x in range(0,i):
                print("{0:10s}{1:30s}{2:17s}{3:30s}{4:<17s}".format(str(res[x][2]),str(res[x][6]),str(res[x][3]),str(res[x][6]),str(res[x][5])))
                print("="*100)
                #reading account table data into a dataframe
                df=pd.read_sql("select amt from account where accno="+str(accno),conn)
                balance=int(df["amt"])
                print("                                         available balance=",balance)
    except:
        print("\nHey! no transaction in account")
#----------------------------------------------------
#function to display all transactions of an account
#------------------------------------------------------
def account_statement():
    print("please enter the details to view the transaction details: ")
    accno=int(input("enter the accno of the customer: "))
    try:
        df= pd.read_sql(f"select account.accno, account.name, transaction.dt_tran, transaction.tran_amt,transaction.tran_type,transaction.balance,transaction.description from account INNER JOIN transaction ON account.accno = transaction.accno and transaction.accno={accno};", conn)
        print(tabulate(df, showindex=False, tablefmt="fancy_grid", headers='keys'))
    except:
        print("\nHey! no transaction in account")
#------------------------------------------------------
#function to run program till user wants 
#--------------------------------------------------------
def runAgain():
    runAgn=input("\ndo you want to continue Y/N:")
    if(runAgn.lower()=='y'):
        if(platform.system()=="Windows"):
            print(os.system('cls'))
            MenuSet()
        else:
            print(os.system('clear'))
            MenuSet()
    else:
        print("bye have a nice day")
        c.close()
    conn.close()

#function to display the main menu

def graph():
    import matplotlib.pyplot as plt
    df = pd.read_sql("SELECT * FROM transaction;", conn)
    plt.bar(df['dt_tran'], df['tran_amt'], width=0.35)
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Transactions")
    plt.grid(which="major",linestyle="-",linewidth="0.5",color="grey")
    plt.grid(b=True,which="minor",linestyle=":",linewidth="0.5",color ="black")
    plt.show()

def MenuSet():
    try:
        opt=''
        print()
        print("================================")
        print("   Banking Transaction System    ")
        print("================================")
        print("1 : Add customer")
        print("2 : View customer details")
        print("3 : Deposit / Withdrawal of money")
        print("4 : Bank statement of a customer")
        print("5 : Bank statement of a customer between two dates")
        print("6 : Modify address or phone number of customer ")
        print("7 : Print Graph")
        opt=int(input("enter your choice: "))
        if opt==1:
            New_customer_entry()
        elif opt==2:
            view_Customers()
        elif opt==3:
            Daily_transaction()
        elif opt==4:
            account_statement()
        elif opt==5:
            account_statement_datewise()
        elif opt==6:
            modify_account()
        elif opt==7:
            graph()
        else:
            print("invalid inputs.bye")
    except ValueError:
        print("Please enter a number")
    except KeyboardInterrupt:
        print("Some error occured.")
              
#project execution starts here
MenuSet()
