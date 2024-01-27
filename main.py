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


        #sign in/ sign up button top right corner
        sign_in_button=Button(menu_frame,text="Sign In / Sign Up",command=self.sign_in_page,font=("times new roman",12),bg="white",fg="black",cursor="hand2")
        sign_in_button.place(x=1180,y=7)

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
    def sign_in_page(self):
        pass


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
        sign_out_button=Button(menu_frame,text="Sign Out",command=self.main_welcome_page,font=("times new roman",12),bg="white",fg="black",cursor="hand2")
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
        











#-------------------------------------------------------------------------------------------------------------

#starter code 
if __name__ == "__main__":
    root = Tk()
    application = busTicketReservation(root)
    root.mainloop()