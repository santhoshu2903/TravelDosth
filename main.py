#import python sql and tkinter libraries
from tkinter import ttk
import mysql.connector as mysql
from tkinter import *
from tkinter import messagebox                                                  
from PIL import ImageTk, Image
import os 
import re
from tkcalendar import DateEntry, Calendar


#create database path for mysql connection
db = mysql.connect(
    host='localhost', 
    port=3306,
    user='root',
    passwd='root',
    database='btr'
)

#connect mysql server
conn=db.cursor()

# Combined SQL for creating all tables
create_tables_queries = """
CREATE TABLE IF NOT EXISTS Users (
    UserID INT AUTO_INCREMENT,
    Username VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    FullName VARCHAR(255),
    ContactNumber VARCHAR(15),
    Role ENUM('Admin', 'Customer') NOT NULL,
    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (UserID)
);

CREATE TABLE IF NOT EXISTS Buses (
    BusID INT AUTO_INCREMENT,
    BusNumber VARCHAR(50) NOT NULL,
    Capacity INT NOT NULL,
    BusType VARCHAR(50),
    PRIMARY KEY (BusID)
);

CREATE TABLE IF NOT EXISTS Routes (
    RouteID INT AUTO_INCREMENT,
    StartPoint VARCHAR(255) NOT NULL,
    EndPoint VARCHAR(255) NOT NULL,
    Distance INT,
    EstimatedTime VARCHAR(50),
    PRIMARY KEY (RouteID)
);

CREATE TABLE IF NOT EXISTS Schedules (
    ScheduleID INT AUTO_INCREMENT,
    BusID INT,
    RouteID INT,
    DepartureTime TIME NOT NULL,
    ArrivalTime TIME NOT NULL,
    Date DATE NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (BusID) REFERENCES Buses(BusID),
    FOREIGN KEY (RouteID) REFERENCES Routes(RouteID),
    PRIMARY KEY (ScheduleID)
);

CREATE TABLE IF NOT EXISTS Bookings (
    BookingID INT AUTO_INCREMENT,
    UserID INT,
    ScheduleID INT,
    SeatNumber INT,
    BookingDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Status ENUM('Confirmed', 'Cancelled') NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (ScheduleID) REFERENCES Schedules(ScheduleID),
    PRIMARY KEY (BookingID)
);

CREATE TABLE IF NOT EXISTS Seats (
    SeatID INT AUTO_INCREMENT,
    ScheduleID INT,
    SeatNumber VARCHAR(10) NOT NULL,
    IsBooked BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (ScheduleID) REFERENCES Schedules(ScheduleID),
    PRIMARY KEY (SeatID)
);

CREATE TABLE IF NOT EXISTS Payments (
    PaymentID INT AUTO_INCREMENT,
    BookingID INT,
    UserID INT,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    PaymentMethod VARCHAR(50),
    TransactionStatus ENUM('Successful', 'Failed') NOT NULL,
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    PRIMARY KEY (PaymentID)
);

CREATE TABLE IF NOT EXISTS Feedback (
    FeedbackID INT AUTO_INCREMENT,
    UserID INT,
    BookingID INT,
    Rating INT CHECK (Rating >= 1 AND Rating <= 5),
    Comments TEXT,
    SubmissionDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID),
    PRIMARY KEY (FeedbackID)
);
"""
#create tables
conn.execute(create_tables_queries)

#close connection
conn.close()

#class for busTicketReservation
class busTicketReservation:
    #constructor
    def __init__(self, root):
        self.root = root
        self.root.title("Bus Ticket Reservation")
        self.root.geometry("1032x745")
        self.style=ttk.Style()
        self.style.configure('TNotebook.Tab', font=('URW Gothic L','15'), padding=[10, 10],bg="transparent")
        self.login_success=False
        self.db = mysql.connect(
                host='localhost', 
                port=3306,
                user='root',
                passwd='root',
                database='btr'
            )
        self.conn=self.db.cursor()

        #create a frame for welcome image
        welcome_image=Image.open("Bus Ticket Reservation System\TravelDosth\images\welcome.png") 
        welcome_image=ImageTk.PhotoImage(welcome_image)
        welcome_image_label=Label(self.root,image=welcome_image)
        welcome_image_label.photo=welcome_image
        welcome_image_label.pack()


        # #welcome page button
        # welcome_button=Button(self.root,text="Welcome",command=self.main_welcome_page,font=("times new roman",20,"bold"),bd=0,cursor="hand2")
        # welcome_button.place(x=450,y=350)

        #account detiails page button
        account_details_button=Button(self.root,text="Account Details",command=self.account_details_page,font=("times new roman",20,"bold"),bd=0,cursor="hand2")
        account_details_button.place(x=450,y=450)



    #main welcome page
    def main_welcome_page(self):
        #clean all the children
        for child in self.root.winfo_children():
            child.destroy()
 

        # set the dimensions
        self.root.geometry("1332x745")

        #menu bar frame
        menu_frame=Frame(self.root,bg="white")
        menu_frame.place(x=0,y=0,width=1332,height=50)

        #welcome to bus ticket reservation system
        welcome_label=Label(menu_frame,text="Welcome to Travel Planning System",font=("times new roman",20,"bold"),bg="white",fg="black")
        #center align
        welcome_label.place(x=450,y=10)


        if self.login_success:
            # Account Details button
            account_details_button = Button(menu_frame, text="Account Details", command=self.account_details_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
            account_details_button.place(x=1180, y=7)
        else:
            # Sign In / Sign Up button
            sign_in_button = Button(menu_frame, text="Sign In / Sign Up", command=self.login_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
            sign_in_button.place(x=1180, y=7)

        #frame from search bar
        search_frame=Frame(self.root,bg="#ADD8E6")
        search_frame.place(x=0,y=50,width=1332,height=120)

        #from location entry
        from_location_label=Label(search_frame,text="From",font=("times new roman",15,"bold"),bg="#ADD8E6",fg="black")
        from_location_label.place(x=130,y=20)

        from_location_entry=Entry(search_frame,font=("times new roman",15),bg="white",fg="black")
        from_location_entry.place(x=130,y=60,width=250,height=30)

        #to location entry
        to_location_label=Label(search_frame,text="To",font=("times new roman",15,"bold"),bg="#ADD8E6",fg="black")
        to_location_label.place(x=430,y=20)

        to_location_entry=Entry(search_frame,font=("times new roman",15),bg="white",fg="black")
        to_location_entry.place(x=430,y=60,width=250,height=30)

        #date entry
        date_label=Label(search_frame,text="Date",font=("times new roman",15,"bold"),bg="#ADD8E6",fg="black")
        date_label.place(x=730,y=20)

        date_entry = DateEntry(search_frame, font=("times new roman", 15), background="white", foreground="black")
        date_entry.place(x=730, y=60, width=250, height=30)

        #search button
        search_button=Button(search_frame,text="Search",font=("times new roman",15,"bold"),bg="white",fg="black",cursor="hand2")
        search_button.place(x=1030,y=60,width=100,height=30)




        

        #bus page
    def bus_page(self):
        pass

    #sign in page
    def login_page(self):
        # clear all the children
        for child in self.root.winfo_children():
            child.destroy()

        # set the dimensions
        window_width = 932
        window_height = 745
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # bg white
        self.root.config(bg="white")

        # usernamelabel
        username_label = Label(self.root, text="Username", font=("times new roman", 20, "bold"), bg="white", fg="black")
        username_label.place(x=100, y=100)

        # username entry
        self.username_entry = Entry(self.root, font=("times new roman", 15), bg="lightgray", fg="black")
        self.username_entry.place(x=100, y=150, width=250, height=30)

        # password label
        password_label = Label(self.root, text="Password", font=("times new roman", 20, "bold"), bg="white", fg="black")
        password_label.place(x=100, y=200)

        # password entry
        self.password_entry = Entry(self.root, font=("times new roman", 15), bg="lightgray", fg="black")
        self.password_entry.place(x=100, y=250, width=250, height=30)

        # sign in button
        sign_in_button = Button(self.root, text="Sign In", command=self.verify_login, font=("times new roman", 15, "bold"),
                                bg="white", fg="black", cursor="hand2")
        sign_in_button.place(x=100, y=300, width=100, height=30)

        # sign up button
        sign_up_button = Button(self.root, text="Sign Up", command=self.sign_up_page, font=("times new roman", 15, "bold"),
                                bg="white", fg="black", cursor="hand2")
        sign_up_button.place(x=250, y=300, width=100, height=30)


    #sign up page
    def sign_up_page(self):
        #clear screen
        for child in self.root.winfo_children():
            child.destroy()

        # set the dimensions
        self.root.geometry("932x745")

        # bg white
        self.root.config(bg="white")

        #first name label
        first_name_label=Label(self.root,text="First Name",font=("times new roman",20,"bold"),bg="white",fg="black")
        first_name_label.place(x=100,y=100)

        #first name entry side by side
        self.first_name_entry=Entry(self.root,font=("times new roman",15),bg="lightgray",fg="black")
        self.first_name_entry.place(x=100,y=150,width=250,height=30)

        #last name label
        last_name_label=Label(self.root,text="Last Name",font=("times new roman",20,"bold"),bg="white",fg="black")
        last_name_label.place(x=100,y=200)

        #last name entry side by side
        self.last_name_entry=Entry(self.root,font=("times new roman",15),bg="lightgray",fg="black")
        self.last_name_entry.place(x=100,y=250,width=250,height=30)

        #email label
        email_label=Label(self.root,text="Email",font=("times new roman",20,"bold"),bg="white",fg="black")
        email_label.place(x=100,y=300)

        #email entry side by side
        self.email_entry=Entry(self.root,font=("times new roman",15),bg="lightgray",fg="black")
        self.email_entry.place(x=100,y=350,width=250,height=30)

        #contact number label
        contact_number_label=Label(self.root,text="Contact Number",font=("times new roman",20,"bold"),bg="white",fg="black")
        contact_number_label.place(x=100,y=400)

        #contact number entry side by side
        self.contact_number_entry=Entry(self.root,font=("times new roman",15),bg="lightgray",fg="black")
        self.contact_number_entry.place(x=100,y=450,width=250,height=30) 

        #password entry side by side
        password_label=Label(self.root,text="Password",font=("times new roman",20,"bold"),bg="white",fg="black")
        password_label.place(x=450,y=100)

        #password entry side by side
        self.password_entry=Entry(self.root,font=("times new roman",15),bg="lightgray",fg="black")
        self.password_entry.place(x=450,y=150,width=250,height=30)

        #confirm password label
        confirm_password_label=Label(self.root,text="Confirm Password",font=("times new roman",20,"bold"),bg="white",fg="black")
        confirm_password_label.place(x=450,y=200)

        #confirm password entry side by side
        self.confirm_password_entry=Entry(self.root,font=("times new roman",15),bg="lightgray",fg="black")
        self.confirm_password_entry.place(x=450,y=250,width=250,height=30)

        #sign up button
        sign_up_button=Button(self.root,text="Sign Up",command=self.create_account,font=("times new roman",15,"bold"),bg="white",fg="black",cursor="hand2")
        sign_up_button.place(x=100,y=500,width=100,height=30)

        #back to login
        back_to_login_button=Button(self.root,text="Back to Login",command=self.login_page,font=("times new roman",15,"bold"),bg="white",fg="black",cursor="hand2")
        back_to_login_button.place(x=100,y=550,width=200,height=30)





    #account details page
    def account_details_page(self):
        #clear account
        for child in self.root.winfo_children():
            child.destroy()

        # set the dimensions
        self.root.geometry("1332x745")

        #menu bar frame
        menu_frame=Frame(self.root,bg="white")
        menu_frame.place(x=0,y=0,width=1332,height=50)

        #welcome to user name
        welcome_label=Label(menu_frame,text="Welcome to Travel Planning System",font=("times new roman",20,"bold"),bg="white",fg="black")
        #center align
        welcome_label.place(x=450,y=10)

        #signout button top right corner
        sign_out_button=Button(menu_frame,text="Sign Out",command=self.sign_out,font=("times new roman",12),bg="white",fg="black",cursor="hand2")
        sign_out_button.place(x=1180,y=7)

        #menu 2 frame
        menu2_frame=Frame(self.root,bg="#ADD8E6")
        menu2_frame.place(x=0,y=50,width=1332,height=600)

        #user notebook
        user_notebook=ttk.Notebook(menu2_frame)
        user_notebook.place(x=0,y=3,width=1332,height=600)

        #add my profile tab
        my_profile_tab=Frame(user_notebook,bg="#ADD8E6")
        user_notebook.add(my_profile_tab,text="My Profile")

        #my bookings tab
        my_bookings_tab=Frame(user_notebook,bg="#ADD8E6")
        user_notebook.add(my_bookings_tab,text="My Bookings")

        #cancel ticket tab
        cancel_ticket_tab=Frame(user_notebook,bg="#ADD8E6")
        user_notebook.add(cancel_ticket_tab,text="Cancel Ticket")

        #Update Iterenary tab
        update_iterenary_tab=Frame(user_notebook,bg="#ADD8E6")
        user_notebook.add(update_iterenary_tab,text="Update Iterenary")



        #left frame inside my profile tab for profile picture
        left_frame=Frame(my_profile_tab,bg="white")
        left_frame.place(x=0,y=0,width=400,height=550)


        #right frame inside my profile tab for user details tab
        right_frame=Frame(my_profile_tab,bg="white")
        right_frame.place(x=400,y=0,width=900,height=550)

        #a line between left and right frame
        line=Label(right_frame,bg="lightgray")
        line.place(x=0,y=0,width=2,height=550)

        #profile picture circle
        profile_picture=Image.open("Bus Ticket Reservation System/TravelDosth/images/hotel.jpg")
        profile_picture=profile_picture.resize((200,200),Image.LANCZOS)
        profile_picture=ImageTk.PhotoImage(profile_picture)
        profile_picture_label=Label(left_frame,image=profile_picture,bd=0)
        profile_picture_label.place(x=100,y=100)


        # user details in right frame
        # user name label
        user_name_label = Label(right_frame, text="User Name", font=("times new roman", 15, "bold"), bg="white", fg="black")
        user_name_label.grid(row=0, column=0, padx=10, pady=10)

        # user name entry
        user_name_entry = Entry(right_frame, font=("times new roman", 15), bg="lightgray", fg="black")
        user_name_entry.grid(row=0, column=1, padx=10, pady=10)

        # email label
        email_label = Label(right_frame, text="Email", font=("times new roman", 15, "bold"), bg="white", fg="black")
        email_label.grid(row=1, column=0, padx=10, pady=10)

        # email entry
        email_entry = Entry(right_frame, font=("times new roman", 15), bg="lightgray", fg="black")
        email_entry.grid(row=1, column=1, padx=10, pady=10)

        # full name label
        full_name_label = Label(right_frame, text="Full Name", font=("times new roman", 15, "bold"), bg="white", fg="black")
        full_name_label.grid(row=2, column=0, padx=10, pady=10)

        # full name entry
        full_name_entry = Entry(right_frame, font=("times new roman", 15), bg="lightgray", fg="black")
        full_name_entry.grid(row=2, column=1, padx=10, pady=10)

        # contact number label
        contact_number_label = Label(right_frame, text="Contact Number", font=("times new roman", 15, "bold"), bg="white", fg="black")
        contact_number_label.grid(row=3, column=0, padx=10, pady=10)

        # contact number entry
        contact_number_entry = Entry(right_frame, font=("times new roman", 15), bg="lightgray", fg="black")
        contact_number_entry.grid(row=3, column=1, padx=10, pady=10)

        # email address label
        email_address_label = Label(right_frame, text="Email Address", font=("times new roman", 15, "bold"), bg="white", fg="black")
        email_address_label.grid(row=4, column=0, padx=10, pady=10)

        # email address entry
        email_address_entry = Entry(right_frame, font=("times new roman", 15), bg="lightgray", fg="black")
        email_address_entry.grid(row=4, column=1, padx=10, pady=10)

        # update details button
        update_details_button = Button(right_frame, text="Update Details", font=("times new roman", 15, "bold"), bg="white", fg="black", cursor="hand2")
        update_details_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        



    #verify login
    def verify_login(self):
        #verify login
        username=self.username_entry.get()
        password=self.password_entry.get()



        #check if any field is empty
        if username=="" or password=="":
            messagebox.showerror("Error","All fields are required",parent=self.root)
        else:
            try:
                # Create a new cursor
                with self.db.cursor() as cursor:
                    cursor.execute("SELECT * FROM Users WHERE Username=%s AND Password=%s", (username, password))
                    row = cursor.fetchone()
                    if row is None:
                        messagebox.showerror("Error", "Invalid Username or Password", parent=self.root)
                    else:
                        self.current_user_object = row
                        #current user name
                        self.current_user_name = row[1]
                        messagebox.showinfo("Success", "Login Successful", parent=self.root)
                        self.login_success=True
                        self.main_welcome_page()

            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

            
        





    #create account
    def create_account(self):   
        #take account details
        first_name=self.first_name_entry.get()
        last_name=self.last_name_entry.get()
        email=self.email_entry.get()
        contact_number=self.contact_number_entry.get()
        password=self.password_entry.get()
        confirm_password=self.confirm_password_entry.get()

        #check if any field is empty
        if first_name=="" or last_name=="" or email=="" or contact_number=="" or password=="" or confirm_password=="":
            messagebox.showerror("Error","All fields are required",parent=self.root)
        #check if password and confirm password are same
        elif password!=confirm_password:
            messagebox.showerror("Error","Password and Confirm Password should be same",parent=self.root)
        #check if email is valid
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error","Invalid Email",parent=self.root)
        #check if contact number is valid
        elif not re.match(r"[0-9]{10}", contact_number):
            messagebox.showerror("Error","Invalid Contact Number",parent=self.root)
        #check if user already exists
        else:
            try:
                # Create a new cursor
                with self.db.cursor() as cursor:
                    cursor.execute("SELECT * FROM Users WHERE Email=%s", (email,))
                    row = cursor.fetchone()
                    if row is not None:
                        messagebox.showerror("Error", "User already exists", parent=self.root)
                    else:
                        cursor.execute("INSERT INTO Users (Username, Password, Email, FullName, ContactNumber, Role) VALUES (%s, %s, %s, %s, %s, %s)", (email, password, email, first_name + " " + last_name, contact_number, "Customer"))
                        self.db.commit()
                        messagebox.showinfo("Success", "Account created successfully", parent=self.root)
                        self.login_page()

            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

        
    #pop up window with back to login screen or booking page
    def pop_up_window(self):

        #top level window
        top=Toplevel()
        top.title("Booking Successful")

        #set the dimensions
        top.geometry("500x300")

        #back to login screen
        back_to_login_button=Button(top,text="Back to Login",command=self.login_page,font=("times new roman",15,"bold"),bg="white",fg="black",cursor="hand2")
        back_to_login_button.place(x=100,y=250,width=200,height=30)

        #back to booking page
        back_to_booking_button=Button(top,text="Back to Booking",command=self.main_welcome_page,font=("times new roman",15,"bold"),bg="white",fg="black",cursor="hand2")
        back_to_booking_button.place(x=250,y=250,width=200,height=30)


    #sign_out()
    def sign_out(self):
        self.login_success=False
        self.main_welcome_page()
        


    #update iterenary page
        


        
        

#-------------------------------------------------------------------------------------------------------------

#starter code 
if __name__ == "__main__":
    root = Tk()
    application = busTicketReservation(root)
    root.mainloop()