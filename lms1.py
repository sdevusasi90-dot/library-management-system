import sqlite3
import re
from datetime import datetime

conn=sqlite3.connect("library11.db")
cur=conn.cursor()

cur.execute("PRAGMA foreign_keys = ON")

#-----------TABLES-------
# ----login
cur.execute("""CREATE TABLE IF NOT EXISTS login(
            username TEXT PRIMARY KEY,
            password TEXT ,
            role TEXT,
            Address text,
            email text,
            phone text
            )""")
#books
cur.execute("""CREATE TABLE IF NOT EXISTS books(
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            quantity INTEGER)""")
#request
cur.execute("""CREATE TABLE IF NOT EXISTS requestbook(
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            book_id INTEGER,
            reqst_date TEXT,
            status TEXT DEFAULT "pending",
            FOREIGN KEY(username) REFERENCES login(username),
            FOREIGN KEY(book_id) REFERENCES books(book_id) )""")
#----issue------
cur.execute("""CREATE TABLE IF NOT EXISTS issue_books
            (issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username text,
            book_id integer,
            issue_date TEXT,
            FOREIGN KEY(username) REFERENCES login(username),
            foreign key (book_id) references books(book_id)
            )""")
#-----return 
cur.execute("""CREATE TABLE IF NOT EXISTS return_books(
          return_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username text,
            book_id INTEGER,
            return_date text,
            fine INTEGER,
            FOREIGN KEY(username) REFERENCES login(username),
            foreign key (book_id) references books(book_id)
            )""")

conn.commit()
#-------validation------
def validusername(u):
   if len(u)<=8:
      return False
   if not re.match("^[A-Za-z0-9]+$" , u):
      return False
   
   return True

def validpassword(p):
   if len(p)<6:
      return False
   if not re.search("[0-9]",p):
      return False
   
   return True
   


#_----------REGISTER USER-----------
def register():
    u=input("username: ")
    if not validusername(u):
       print("invalid username,Username must contain more than 8 characters and must contain a number")
       return
    p=input("password: ")
    if not validpassword(p):
       print("password must contain numbers and minimum 6 characters")
       return
       
    role=input("role(admin/user): ")

    addr=input("enter your adress: ")
    email=input("Enter your email: ")
    phn=input("Enter phone number: ")
    try:
     cur.execute("INSERT INTO login(username,password,role,address,email,phone) VALUES (?,?,?,?,?,?)",(u,p,role,addr,email,phn))
     conn.commit()
     print("user registerd successfully")
    except:
       print("username already exist")  
conn.commit()
#-----------login-------
def login():
    u=input("username: ")
    p=input("password: ")
    cur.execute("SELECT role FROM login WHERE username=? AND password=?",(u,p))
    data=cur.fetchone()
    if data:
        print("login successful")
        return u,data[0]
        
           
    else:
       print("invalid user")
       return None,None
conn.commit()
#-------ADD BOOK-------
def add_book():
   #book_id=int(input("enter book id: "))
   title=input("Title: ")
   author=input("Author: ")
   qty=input("Quantity: ")

   cur.execute("INSERT INTO books(title,author,quantity) VALUES(?,?,?)",(title,author,qty))
   conn.commit()
   print( "book added successfully")

#--------VIEW BOOKS---------
def view_book():
   print(".......BOOKS.....")
   cur.execute("SELECT * FROM books")
   print("book id  Name   quantity")
   print("=====================================")
   for i in cur.fetchall():
      print(i)
   print("======================================")
#---------SEARCH BOOKS-------
def search():
  try: 
   name=input("enter title:")
   cur.execute("SELECT * FROM books WHERE title like ?", ('%'+name+'%',))
   data=cur.fetchall()
   if data:
    print("search results\n")
    for i in data :
      print(i)
   else:
      print("no such book")   
  except:
     print("error") 
#-----------REQUEST BOOK--------
def requestbook(username):
  try:
    
    print(username)
    print("\n REQUEST BOOK")
    print("Available book: \n")
    view_book()
    book_id=int(input("enter book id to request: "))

    #name=input("enter book name:")
    cur.execute("SELECT * FROM books WHERE book_id=?",(book_id,))
    book=cur.fetchone()
    if not book:
      print("book does not exist")
      return
    if book[3] ==0:
      print("book not available")
      return
    cur.execute("select * from login where username=?",(username,))
    if not cur.fetchone():
       print("user not found")
       return
    date=str(datetime.now().date()) 
    cur.execute("""insert into requestbook(username,book_id,reqst_date) values(?,?,?)""",
               (username,book_id,date))
    conn.commit()
    print("request send to admin")
  except Exception as e:
     print("Error requesting book.",e)  
#----------view REQUEST BOOK-------
def view_request():
   print("\n ******view requests*****")
   cur.execute("select request_id,username,book_id from requestbook where status ='pending'")
   data=cur.fetchall()
   if not data:
      print("no pending requests")
      return
   print("\n PENDING REQUESTS")
   print("requestid*** username**** bookid")
   print("===========================================")
   for i in data:
      print(i)
   conn.commit() 
   print("==========================================")  
#-----------APPROVE REQUEST--------
def approve_reqst():
  try:
   print("\n view requests")
   
   cur.execute("""SELECT request_id,username,book_id FROM requestbook 
       WHERE status='pending' """)
   
   data = cur.fetchall()
   if not data:
      print("No pendinig requests")
      return
   print("pending requests")
   print("requestid*** username**** bookid")
   print("================================================")
   for i in data:
      print(i)
   print("==================================================")   
   requestid= int(input("enter request id to approve: "))
   cur.execute("select username,book_id from requestbook where request_id=? and status='pending'",(requestid,))
   result=cur.fetchone()
  # print(result)
   if not result:
      print("invalid request id")
      return
   book_id=result[1]
   
   #print(book_id)
   cur.execute("select quantity from books where book_id=?",(book_id,))
   data=cur.fetchone()
   #print(data)
   qty=data[0]
   if qty<= 0:
      print("book out of stock ")
      return
   #  insert into issue table
   username,book_id=result
   date=str(datetime.now().date())
   cur.execute("INSERT INTO issue_books(username,book_id,issue_date) values(?,?,?)",(username,book_id,date))
   cur.execute("update requestbook set status='approved' where request_id=?",(requestid,))     
   cur.execute("update books set quantity=quantity-1 where book_id=?",(book_id,))
   conn.commit()
   print("request approved and book issued")
  except Exception as e:
     print("Error issuing book",e ) 

#--------return book--------
def return_book(username):
 try:
   print("ISSUED BOOK\n") 
   
   print("===============================================================")
   cur.execute("SELECT * FROM issue_books WHERE username=?",(username,))
   
   data=cur.fetchall()
   if not data:
      print("no issued book")
      return
   print("issued books\n")
   print("issue1d  user   bookid   date")
   print("==================================================================") 
   for i in data:
      print(i)
   print("==================================================================")    
   bookid=int(input("enter book id to return: "))

   cur.execute("SELECT issue_date from issue_books where username=? AND book_id=?",(username,bookid))
   row=cur.fetchone()
   #print(row)
   if not row:
      print ("invalid request")
      return
   #print(row[0])   
   issuedate=datetime.strptime(row[0],"%Y-%m-%d")
   #print(issuedate)
   today=datetime.today()
   #print(today)
   days=(today-issuedate).days
   #print(days)
   fine=0
   if days >3:
         fine=(days-3)*5

   cur.execute(""" INSERT INTO return_books(username,book_id,return_date,fine) 
                  VALUES(?,?,?,?)
            """,(username,bookid,str(today.date()),fine))
   cur.execute("DELETE FROM issue_books WHERE username =? AND book_id=?",(username,bookid))
   cur.execute("UPDATE books SET quantity=quantity+1 WHERE book_id=?",(bookid,))  
   conn.commit()  
      
   print("returned success fully")
   print("fine: ",fine)
#       # username=username
#       # request_id=row[0]
#       # issue_date=row[1]
#    issuedateobj=datetime.strptime(issue_date,"%Y-%m-%d")  
#    returndate=datetime.today()

#    days=(returndate-issuedateobj).days 
#    fine=0
#    if days>3:
#       fine=(days-3)*5

#    cur.execute("""
#    INSERT INTO return_book(issue_id,issue_date,return_date,fine)VALUES(?,?,?,?,?)
# """,(issue_date,returndate.strftime("%Y-%m-%d"),fine))
#    cur.execute("DELETE FROM issue_books WHERE issue_id=? ",(issue))   
#    cur.execute("UPDATE books SET quantity=quantity+1 WHERE book_id=?",(book,))  
#    conn.commit()
#    print("book returned")
#    print("fine is = ",fine)
 except Exception as e:
    print("something went wrong",e)

      

#-----------MAIN MENU-------
while True:
   print("******------LIBRARY SYSTEM--------**") 
   print("1.register")
   print("2.login")
   print("3.exit")     

   ch=input("choice: ")   

   if ch=="1":
      register()
   elif ch=="2":
      username,role=login()
      if role=="admin":

         #----------ADMIN MENU--------
         
            while True:
              print("\n ******** ADMIN ********")
              print("1.Add book")
              print("2.view book")
              print("3.view requests")
              print("4.Approve requests")
      #print("5.return book")
              print("5.logout")
              a=int(input("Enter your Choice: "))
              if a == 1:
                add_book()
              if   a == 2:
                 view_book()
              if a==3:
               view_request()
              if a==4:
               approve_reqst()
   #   if ch==5:
   #      return_book()      
              if a== 5:
               break      
      elif role=="user":
          while True:
         #--------USER MEMU--------
         
             print("\n USER MENU")
             print("1.Search book")
             print("2.view book")
             print("3.request book")
             print("4.Return Book")
             print("5.logout")
             b=int(input("Choice: "))
             if b == 1:
               search()
             if   b == 2:
              view_book()
             if b==3:
              requestbook(username)
             if b==4:
               return_book(username)
   #   if ch ==5:
   #      return_book()      
             if b== 5:
                 break  
   elif ch=="3":
     break              
conn.close()