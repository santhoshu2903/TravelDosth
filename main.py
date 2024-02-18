#import python sql and tkinter libraries
from datetime import datetime
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
    AvailableSeats INT NOT NULL,
    FOREIGN KEY (BusID) REFERENCES Buses(BusID),
    FOREIGN KEY (RouteID) REFERENCES Routes(RouteID),
    PRIMARY KEY (ScheduleID)
);

CREATE TABLE IF NOT EXISTS Bookings (
    BookingID INT AUTO_INCREMENT,
    UserID INT,
    ScheduleID INT,
    Seats INT,
    TotalPrice DECIMAL(10, 2) NOT NULL,
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
        self.style.configure("Treeview.Heading", font=(None, 15,'bold'), padding=[10, 10],bg="transparent")

        #treeview column configuration
        self.style.configure("Treeview",rowheight=40 ,font=(None, 15), padding=[10, 10],anchor="center")

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
        welcome_image=Image.open("images\welcome.png") 
        welcome_image=ImageTk.PhotoImage(welcome_image)
        welcome_image_label=Label(self.root,image=welcome_image)
        welcome_image_label.photo=welcome_image
        welcome_image_label.pack()


        #welcome page button
        welcome_button=Button(self.root,text="Welcome",command=self.main_welcome_page,font=("times new roman",20,"bold"),bd=0,cursor="hand2")
        welcome_button.place(x=450,y=350)

        # #account detiails page button
        # account_details_button=Button(self.root,text="Account Details",command=self.account_details_page,font=("times new roman",20,"bold"),bd=0,cursor="hand2")
        # account_details_button.place(x=450,y=450)



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

        #bus schudel frame
        bus_schedule_frame=Frame(self.root,bg="white")
        bus_schedule_frame.place(x=0,y=170,width=1332,height=530)

        #scroll bar
        scroll_x=Scrollbar(bus_schedule_frame,orient=HORIZONTAL)
        scroll_y=Scrollbar(bus_schedule_frame,orient=VERTICAL)

        #table from location ,to location ,date , available seats, price ,
        self.bus_schedule_table=ttk.Treeview(bus_schedule_frame,columns=("Id","from_location","to_location","date"),xscrollcommand=scroll_x.set,yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM,fill=X)
        scroll_y.pack(side=RIGHT,fill=Y)

        scroll_x.config(command=self.bus_schedule_table.xview)
        scroll_y.config(command=self.bus_schedule_table.yview)

        self.bus_schedule_table.heading("Id", text="Schedule Id", anchor=CENTER)
        self.bus_schedule_table.heading("from_location", text="From Location", anchor=CENTER)
        self.bus_schedule_table.heading("to_location", text="To Location", anchor=CENTER)
        self.bus_schedule_table.heading("date", text="Date", anchor=CENTER)

        self.bus_schedule_table["show"] = "headings"

        self.bus_schedule_table.pack(fill=BOTH, expand=1)

        # insert data into table from schedules table
        try:
            # Create a new cursor
            with self.db.cursor() as cursor:
                cursor.execute("SELECT * FROM Schedules")
                rows = cursor.fetchall()
                for row in rows:
                    routeid = row[2]
                    cursor.execute("SELECT * FROM Routes WHERE RouteID=%s", (routeid,))
                    route = cursor.fetchone()
                    self.bus_schedule_table.insert("", END, values=(route[0],route[1], route[2], row[5]))

        except Exception as e:
            messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)
        
        #align columns to center
        self.bus_schedule_table.column("Id", anchor=CENTER)
        self.bus_schedule_table.column("from_location", anchor=CENTER)
        self.bus_schedule_table.column("to_location", anchor=CENTER)
        self.bus_schedule_table.column("date", anchor=CENTER)
        
        #book button
        book_button=Button(self.root,text="Book",command=self.booking_page,font=("times new roman",15,"bold"),bg="white",fg="black",cursor="hand2")
        book_button.place(x=600,y=700,width=100,height=30)



    #book ticket
    def booking_page(self):
        #get row data
        row=self.bus_schedule_table.focus()
        content=self.bus_schedule_table.item(row)
        row=content["values"]

        #store from and to
        self.from_location=row[1]
        self.to_location=row[2]
        self.date=row[3]

        #bus type


        #store current schedule id
        self.current_schedule_id=row[0]

        #check if any row is selected
        if len(row)==0:
            messagebox.showerror("Error","Please select a row",parent=self.root)
        else:  
            #clean the screen
            for child in self.root.winfo_children():
                child.destroy()

            # set the dimensions
            self.root.geometry("1332x745")

            #heading frame
            heading_frame=Frame(self.root,bg="white")
            heading_frame.place(x=0,y=0,width=1332,height=50)

            #Select Bus label
            select_bus_label=Label(heading_frame,text="Select Bus",font=("times new roman",20,"bold"),bg="white",fg="black")
            select_bus_label.place(x=600,y=10)

            #back button left top button
            back_button=Button(heading_frame,text="Back",command=self.main_welcome_page,font=("times new roman",12),bg="white",fg="black",cursor="hand2")
            back_button.place(x=10,y=10)

            #sign in/sign up button top right corner
            if self.login_success:
                sign_in_button = Button(heading_frame, text="Account Details", command=self.account_details_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
                sign_in_button.place(x=1180, y=7)
            else:
                sign_in_button = Button(heading_frame, text="Sign In / Sign Up", command=self.login_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
                sign_in_button.place(x=1180, y=7)

            #schedule frame
            schedule_frame=Frame(self.root,bg="#ADD8E6")
            schedule_frame.place(x=0,y=50,width=1332,height=80)

            #from location label
            from_location_label=Label(schedule_frame,font=("times new roman",20,"bold"),bg="#ADD8E6",fg="black")
            from_location_label.place(x=300,y=20)

            #fill the from_location_label
            from_location_label.config(text=row[1])

            #to location label
            to_location_label=Label(schedule_frame,font=("times new roman",20,"bold"),bg="#ADD8E6",fg="black")
            to_location_label.place(x=650,y=20)

            #fill the to_location_label
            to_location_label.config(text=row[2])

            #date label
            date_label=Label(schedule_frame,font=("times new roman",20,"bold"),bg="#ADD8E6",fg="black")
            date_label.place(x=1000,y=20)

            #fill the date_label
            date_label.config(text=row[3])

            #bus details frame
            bus_details_frame=Frame(self.root,bg="white")
            bus_details_frame.place(x=0,y=130,width=1332,height=550)

            #scroll bar
            scroll_x=Scrollbar(bus_details_frame,orient=HORIZONTAL)
            scroll_y=Scrollbar(bus_details_frame,orient=VERTICAL)

            #table schedule id,bus type, departure time,arrival time,price,available seats
            self.bus_details_table=ttk.Treeview(bus_details_frame,columns=("Id","bus_type","departure_time","arrival_time","price","available_seats"),xscrollcommand=scroll_x.set,yscrollcommand=scroll_y.set)
            scroll_x.pack(side=BOTTOM,fill=X)
            scroll_y.pack(side=RIGHT,fill=Y)

            scroll_x.config(command=self.bus_details_table.xview)
            scroll_y.config(command=self.bus_details_table.yview)

            self.bus_details_table.heading("Id", text="Schedule Id", anchor=CENTER)
            self.bus_details_table.heading("bus_type", text="Bus Type", anchor=CENTER)
            self.bus_details_table.heading("departure_time", text="Departure Time", anchor=CENTER)
            self.bus_details_table.heading("arrival_time", text="Arrival Time", anchor=CENTER)
            self.bus_details_table.heading("price", text="Price", anchor=CENTER)
            self.bus_details_table.heading("available_seats", text="Available Seats", anchor=CENTER)

            self.bus_details_table["show"] = "headings"

            self.bus_details_table.pack(fill=BOTH, expand=1)

            # insert data into table from schedules table
            try:
                # Create a new cursor
                with self.db.cursor() as cursor:
                    cursor.execute("SELECT * FROM Schedules WHERE RouteID=%s AND Date=%s", (row[0], row[3]))
                    rows = cursor.fetchall()
                    for row in rows:
                        #bus details
                        busid = row[1]
                        cursor.execute("SELECT * FROM Buses WHERE BusID=%s", (busid,))
                        bus = cursor.fetchone()
                        bus_type = bus[3]
                        departure_time = row[3]
                        arrival_time = row[4]
                        price = row[6]
                        available_seats = row[7]
                        self.bus_details_table.insert("", END, values=(row[0],bus_type, departure_time, arrival_time, price, available_seats))

            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)
            
            #align columns to center
            self.bus_details_table.column("Id", anchor=CENTER)  
            self.bus_details_table.column("bus_type", anchor=CENTER)
            self.bus_details_table.column("departure_time", anchor=CENTER)
            self.bus_details_table.column("arrival_time", anchor=CENTER)
            self.bus_details_table.column("price", anchor=CENTER)
            self.bus_details_table.column("available_seats", anchor=CENTER)

            #table heading font size configure
            self.bus_details_table.config()

            #confirm booking button
            confirm_booking_button=Button(self.root,text="Select Seat",command=self.select_seat,font=("times new roman",15,"bold"),bg="white",fg="black",cursor="hand2")
            confirm_booking_button.place(x=600,y=700,width=200,height=30)


    #select_seat
    def select_seat(self):

        row=self.bus_details_table.focus()
        content=self.bus_details_table.item(row)
        row=content["values"]
        self.scheduleid=row[0]


        #store buy type
        self.bus_type=row[1]

        #store current price
        self.current_price=row[4]
       
        #check if any row is selected
        if len(row)==0:
            messagebox.showerror("Error","Please select a row",parent=self.root)
        else: 
            busid=None
            #get bus id
            try:
                # Create a new cursor
                with self.db.cursor() as cursor:
                    cursor.execute("SELECT * FROM Schedules WHERE ScheduleID=%s", (self.scheduleid,))
                    row = cursor.fetchone()
                    busid = row[1]
            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

            bus_type = None
            capacity = None

            #bus detials
            try:
                # Create a new cursor
                with self.db.cursor() as cursor:
                    cursor.execute("SELECT * FROM Buses WHERE BusID=%s", (busid,))
                    row = cursor.fetchone()
                    bus_type = row[3]
                    capacity = row[2]
            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

            #clean the screen
            for child in self.root.winfo_children():
                child.destroy()

            # set the dimensions
            self.root.geometry("1332x745")

            #heading frame
            heading_frame=Frame(self.root,bg="white")
            heading_frame.place(x=0,y=0,width=1332,height=50)

            #Select Bus label
            select_bus_label=Label(heading_frame,text="Select Seat",font=("times new roman",20,"bold"),bg="white",fg="black")
            select_bus_label.place(x=600,y=10)

            #back button left top button
            back_button=Button(heading_frame,text="Back",command=self.main_welcome_page,font=("times new roman",12),bg="white",fg="black",cursor="hand2")
            back_button.place(x=10,y=10)

            #sign in/sign up button top right corner
            if self.login_success:
                sign_in_button = Button(heading_frame, text="Account Details", command=self.account_details_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
                sign_in_button.place(x=1180, y=7)
            else:
                sign_in_button = Button(heading_frame, text="Sign In / Sign Up", command=self.login_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
                sign_in_button.place(x=1180, y=7)

            #bus details frame
            bus_details_frame=Frame(self.root,bg="#ADD8E6")
            bus_details_frame.place(x=0,y=50,width=1332,height=80)

            #bus id
            bus_id_label=Label(bus_details_frame,text="Bus Id",font=("times new roman",20,"bold"),bg="#ADD8E6",fg="black")
            bus_id_label.place(x=300,y=20)

            #fill the bus_id_label
            bus_id_label.config(text=busid)

            #bus type label
            bus_type_label=Label(bus_details_frame,text="Bus Type",font=("times new roman",20,"bold"),bg="#ADD8E6",fg="black")
            bus_type_label.place(x=650,y=20)

            #fill the bus_type_label
            bus_type_label.config(text=bus_type)

            #capacity label
            capacity_label=Label(bus_details_frame,text="Capacity",font=("times new roman",20,"bold"),bg="#ADD8E6",fg="black")
            capacity_label.place(x=1000,y=20)

            #fill the capacity_label
            capacity_label.config(text=capacity)

            #seat frame
            seat_frame=Frame(self.root,bg="white")
            seat_frame.place(x=0,y=130,width=1332,height=550)

            #display bus image  
            bus_image=Image.open("images/bus.png")
            bus_image=ImageTk.PhotoImage(bus_image)
            bus_image_label=Label(seat_frame,image=bus_image)
            bus_image_label.photo=bus_image
            bus_image_label.place(x=10,y=20)



            # now 48 checkboxes to select seats number
            self.seat_number = []

            # seat 1
            var1 = IntVar()
            self.seat_number.append(var1)
            seat1 = Checkbutton(seat_frame, variable=var1, onvalue=1, offvalue=0, cursor="hand2", bg="#29aae2")
            seat1.place(x=290, y=340, width=20, height=20)

            # seat 2
            var2 = IntVar()
            self.seat_number.append(var2)
            seat2 = Checkbutton(seat_frame, variable=var2, onvalue=2, offvalue=0, cursor="hand2", bg="#0170bf")
            seat2.place(x=290, y=300, width=20, height=20)

            # seat 3
            var3 = IntVar()
            self.seat_number.append(var3)
            seat3 = Checkbutton(seat_frame, variable=var3, onvalue=3, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat3.place(x=290, y=225, width=20, height=20)

            # seat 4
            var4 = IntVar()
            self.seat_number.append(var4)
            seat4 = Checkbutton(seat_frame, variable=var4, onvalue=4, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat4.place(x=290, y=185, width=20, height=20)

            # similar
            # seat 5
            var5 = IntVar()
            self.seat_number.append(var5)
            seat5 = Checkbutton(seat_frame, variable=var5, onvalue=5, offvalue=0, cursor="hand2", bg="#29aae2")
            seat5.place(x=370, y=340, width=20, height=20)

            # seat 6
            var6 = IntVar()
            self.seat_number.append(var6)
            seat6 = Checkbutton(seat_frame, variable=var6, onvalue=6, offvalue=0, cursor="hand2", bg="#0170bf")
            seat6.place(x=370, y=300, width=20, height=20)

            # seat 7
            var7 = IntVar()
            self.seat_number.append(var7)
            seat7 = Checkbutton(seat_frame, variable=var7, onvalue=7, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat7.place(x=370, y=225, width=20, height=20)

            # seat 8
            var8 = IntVar()
            self.seat_number.append(var8)
            seat8 = Checkbutton(seat_frame, variable=var8, onvalue=8, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat8.place(x=370, y=185, width=20, height=20)

            # similar
            # seat 9
            var9 = IntVar()
            self.seat_number.append(var9)
            seat9 = Checkbutton(seat_frame, variable=var9, onvalue=9, offvalue=0, cursor="hand2", bg="#29aae2")
            seat9.place(x=450, y=340, width=20, height=20)

            # seat 10
            var10 = IntVar()
            self.seat_number.append(var10)
            seat10 = Checkbutton(seat_frame, variable=var10, onvalue=10, offvalue=0, cursor="hand2", bg="#0170bf")
            seat10.place(x=450, y=300, width=20, height=20)

            # seat 11
            var11 = IntVar()
            self.seat_number.append(var11)
            seat11 = Checkbutton(seat_frame, variable=var11, onvalue=11, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat11.place(x=450, y=225, width=20, height=20)

            # seat 12
            var12 = IntVar()
            self.seat_number.append(var12)
            seat12 = Checkbutton(seat_frame, variable=var12, onvalue=12, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat12.place(x=450, y=185, width=20, height=20)

            # similar
            # seat 13
            var13 = IntVar()
            self.seat_number.append(var13)
            seat13 = Checkbutton(seat_frame, variable=var13, onvalue=13, offvalue=0, cursor="hand2", bg="#29aae2")
            seat13.place(x=530, y=340, width=20, height=20)

            # seat 14
            var14 = IntVar()
            self.seat_number.append(var14)
            seat14 = Checkbutton(seat_frame, variable=var14, onvalue=14, offvalue=0, cursor="hand2", bg="#0170bf")
            seat14.place(x=530, y=300, width=20, height=20)

            # seat 15
            var15 = IntVar()
            self.seat_number.append(var15)
            seat15 = Checkbutton(seat_frame, variable=var15, onvalue=15, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat15.place(x=530, y=225, width=20, height=20)

            # seat 16
            var16 = IntVar()
            self.seat_number.append(var16)
            seat16 = Checkbutton(seat_frame, variable=var16, onvalue=16, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat16.place(x=530, y=185, width=20, height=20)

            # similar
            # seat 17
            var17 = IntVar()
            self.seat_number.append(var17)
            seat17 = Checkbutton(seat_frame, variable=var17, onvalue=17, offvalue=0, cursor="hand2", bg="#29aae2")
            seat17.place(x=610, y=340, width=20, height=20)

            # seat 18
            var18 = IntVar()
            self.seat_number.append(var18)
            seat18 = Checkbutton(seat_frame, variable=var18, onvalue=18, offvalue=0, cursor="hand2", bg="#0170bf")
            seat18.place(x=610, y=300, width=20, height=20)

            # seat 19
            var19 = IntVar()
            self.seat_number.append(var19)
            seat19 = Checkbutton(seat_frame, variable=var19, onvalue=19, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat19.place(x=610, y=225, width=20, height=20)

            # seat 20
            var20 = IntVar()
            self.seat_number.append(var20)
            seat20 = Checkbutton(seat_frame, variable=var20, onvalue=20, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat20.place(x=610, y=185, width=20, height=20)

            # similar
            # seat 21
            var21 = IntVar()
            self.seat_number.append(var21)
            seat21 = Checkbutton(seat_frame, variable=var21, onvalue=21, offvalue=0, cursor="hand2", bg="#29aae2")
            seat21.place(x=690, y=340, width=20, height=20)

            # seat 22
            var22 = IntVar()
            self.seat_number.append(var22)
            seat22 = Checkbutton(seat_frame, variable=var22, onvalue=22, offvalue=0, cursor="hand2", bg="#0170bf")
            seat22.place(x=690, y=300, width=20, height=20)

            # seat 23
            var23 = IntVar()
            self.seat_number.append(var23)
            seat23 = Checkbutton(seat_frame, variable=var23, onvalue=23, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat23.place(x=690, y=225, width=20, height=20)

            # seat 24
            var24 = IntVar()
            self.seat_number.append(var24)
            seat24 = Checkbutton(seat_frame, variable=var24, onvalue=24, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat24.place(x=690, y=185, width=20, height=20)

            # similar
            # seat 25
            var25 = IntVar()
            self.seat_number.append(var25)
            seat25 = Checkbutton(seat_frame, variable=var25, onvalue=25, offvalue=0, cursor="hand2", bg="#29aae2")
            seat25.place(x=770, y=340, width=20, height=20)

            # seat 26
            var26 = IntVar()
            self.seat_number.append(var26)
            seat26 = Checkbutton(seat_frame, variable=var26, onvalue=26, offvalue=0, cursor="hand2", bg="#0170bf")
            seat26.place(x=770, y=300, width=20, height=20)

            # seat 27
            var27 = IntVar()
            self.seat_number.append(var27)
            seat27 = Checkbutton(seat_frame, variable=var27, onvalue=27, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat27.place(x=770, y=225, width=20, height=20)

            # seat 28
            var28 = IntVar()
            self.seat_number.append(var28)
            seat28 = Checkbutton(seat_frame, variable=var28, onvalue=28, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat28.place(x=770, y=185, width=20, height=20)

            # similar
            # seat 29
            var29 = IntVar()
            self.seat_number.append(var29)
            seat29 = Checkbutton(seat_frame, variable=var29, onvalue=29, offvalue=0, cursor="hand2", bg="#29aae2")
            seat29.place(x=850, y=340, width=20, height=20)

            # seat 30
            var30 = IntVar()
            self.seat_number.append(var30)
            seat30 = Checkbutton(seat_frame, variable=var30, onvalue=30, offvalue=0, cursor="hand2", bg="#0170bf")
            seat30.place(x=850, y=300, width=20, height=20)

            # seat 31
            var31 = IntVar()
            self.seat_number.append(var31)
            seat31 = Checkbutton(seat_frame, variable=var31, onvalue=31, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat31.place(x=850, y=225, width=20, height=20)

            # seat 32
            var32 = IntVar()
            self.seat_number.append(var32)
            seat32 = Checkbutton(seat_frame, variable=var32, onvalue=32, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat32.place(x=850, y=185, width=20, height=20)

            # similar
            # seat 33
            var33 = IntVar()
            self.seat_number.append(var33)
            seat33 = Checkbutton(seat_frame, variable=var33, onvalue=33, offvalue=0, cursor="hand2", bg="#29aae2")
            seat33.place(x=930, y=340, width=20, height=20)

            # seat 34
            var34 = IntVar()
            self.seat_number.append(var34)
            seat34 = Checkbutton(seat_frame, variable=var34, onvalue=34, offvalue=0, cursor="hand2", bg="#0170bf")
            seat34.place(x=930, y=300, width=20, height=20)

            # seat 35
            var35 = IntVar()
            self.seat_number.append(var35)
            seat35 = Checkbutton(seat_frame, variable=var35, onvalue=35, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat35.place(x=930, y=225, width=20, height=20)

            # seat 36
            var36 = IntVar()
            self.seat_number.append(var36)
            seat36 = Checkbutton(seat_frame, variable=var36, onvalue=36, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat36.place(x=930, y=185, width=20, height=20)

            # similar
            # seat 37
            var37 = IntVar()
            self.seat_number.append(var37)
            seat37 = Checkbutton(seat_frame, variable=var37, onvalue=37, offvalue=0, cursor="hand2", bg="#29aae2")
            seat37.place(x=1010, y=340, width=20, height=20)

            # seat 38
            var38 = IntVar()
            self.seat_number.append(var38)
            seat38 = Checkbutton(seat_frame, variable=var38, onvalue=38, offvalue=0, cursor="hand2", bg="#0170bf")
            seat38.place(x=1010, y=300, width=20, height=20)

            # seat 39
            var39 = IntVar()
            self.seat_number.append(var39)
            seat39 = Checkbutton(seat_frame, variable=var39, onvalue=39, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat39.place(x=1010, y=225, width=20, height=20)

            # seat 40
            var40 = IntVar()
            self.seat_number.append(var40)
            seat40 = Checkbutton(seat_frame, variable=var40, onvalue=40, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat40.place(x=1010, y=185, width=20, height=20)

            # similar
            # seat 41
            var41 = IntVar()
            self.seat_number.append(var41)
            seat41 = Checkbutton(seat_frame, variable=var41, onvalue=41, offvalue=0, cursor="hand2", bg="#29aae2")
            seat41.place(x=1090, y=340, width=20, height=20)

            # seat 42
            var42 = IntVar()
            self.seat_number.append(var42)
            seat42 = Checkbutton(seat_frame, variable=var42, onvalue=42, offvalue=0, cursor="hand2", bg="#0170bf")
            seat42.place(x=1090, y=300, width=20, height=20)

            # seat 43
            var43 = IntVar()
            self.seat_number.append(var43)
            seat43 = Checkbutton(seat_frame, variable=var43, onvalue=43, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat43.place(x=1090, y=225, width=20, height=20)

            # seat 44
            var44 = IntVar()
            self.seat_number.append(var44)
            seat44 = Checkbutton(seat_frame, variable=var44, onvalue=44, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat44.place(x=1090, y=185, width=20, height=20)

            # similar
            # seat 45
            var45 = IntVar()
            self.seat_number.append(var45)
            seat45 = Checkbutton(seat_frame, variable=var45, onvalue=45, offvalue=0, cursor="hand2", bg="#29aae2")
            seat45.place(x=1170, y=340, width=20, height=20)

            # seat 46
            var46 = IntVar()
            self.seat_number.append(var46)
            seat46 = Checkbutton(seat_frame, variable=var46, onvalue=46, offvalue=0, cursor="hand2", bg="#0170bf")
            seat46.place(x=1170, y=300, width=20, height=20)

            # seat 47
            var47 = IntVar()
            self.seat_number.append(var47)
            seat47 = Checkbutton(seat_frame, variable=var47, onvalue=47, offvalue=0, cursor="hand2", bg="#ffb11c")
            seat47.place(x=1170, y=225, width=20, height=20)

            # seat 48
            var48 = IntVar()
            self.seat_number.append(var48)
            seat48 = Checkbutton(seat_frame, variable=var48, onvalue=48, offvalue=0, cursor="hand2", bg="#ffd71c")
            seat48.place(x=1170, y=185, width=20, height=20)

            #create a dictionary of variables 1:seat1
            self.seat_dict={}
            for i in range(1,49):
                self.seat_dict[i]=self.seat_number[i-1]

            


            #check if seat already booked from seats table and disable seat
            try:
                # Create a new cursor and get seat number with scheduleid into list
                with self.db.cursor() as cursor:
                    cursor.execute("SELECT SeatNumber FROM Seats WHERE ScheduleID=%s", (self.scheduleid,))
                    rows = cursor.fetchall()
                    #store into booked_seats list
                    for row in rows:
                        seat=row[0]
                        #disable seat from dictionary
                        self.seat_dict[seat].set(1)

            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)



    




            #confirm booking button
            confirm_booking_button=Button(self.root,text="Confirm Booking",command=self.confirm_booking,font=("times new roman",15,"bold"),bg="white",fg="black",cursor="hand2")
            confirm_booking_button.place(x=600,y=700,width=200,height=30)


#get selected seats
    def confirm_booking(self):
        #print all selected seats
        self.selected_seats=[]
        for i in self.seat_number:
            if i.get()!=0:
                self.selected_seats.append(i.get())

        # print(selected_seats)
        #show a message box to confirm booking seats selected selected seats list
        answer=messagebox.askyesno("Confirm Booking","Do you want to book these seats? /n ",parent=self.root)
        if answer==True:
            #insert data into database
            try:
               #open confirmation pafe
                self.confirmation_page()

            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)
        
    #confirmation page
    def confirmation_page(self):
        #check if logged in user
        if not self.login_success:
            #ask book with guest credentials
            answer=messagebox.askyesno("Confirm Booking","Do you want to book as guest?",parent=self.root)
            if answer==True:
                #open confirmation pafe
                self.guest=True
                self.login_success=True
                self.confirmation_page()
            else:
                #open login page
                self.login_page()


        #clear screen
        for child in self.root.winfo_children():
            child.destroy()

        # set the dimensions
        self.root.geometry("1332x745")

        # bg white
        self.root.config(bg="white")

        #heading frame
        heading_frame=Frame(self.root,bg="white")
        heading_frame.place(x=0,y=0,width=1332,height=50)

        #Confirmation Page Label
        confirmation_page_label=Label(heading_frame,text="Confirmation Page",font=("times new roman",20,"bold"),bg="white",fg="black")
        confirmation_page_label.place(x=600,y=10)

        #back button left top button
        back_button=Button(heading_frame,text="Back",command=self.main_welcome_page,font=("times new roman",12),bg="white",fg="black",cursor="hand2")
        back_button.place(x=10,y=10)

        #sign in/sign up button top right corner
        if self.login_success:
            sign_in_button = Button(heading_frame, text="Account Details", command=self.account_details_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
            sign_in_button.place(x=1180, y=7)
        else:
            sign_in_button = Button(heading_frame, text="Sign In / Sign Up", command=self.login_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
            sign_in_button.place(x=1180, y=7)

        #confirmation frame
        confirmation_frame=Frame(self.root,bg="#ADD8E6")
        confirmation_frame.place(x=0,y=50,width=1332,height=60)

        #Booking Details
        booking_details_label=Label(confirmation_frame,text="Booking Details",font=("times new roman",20,"bold"),bg="#ADD8E6",fg="black")
        booking_details_label.place(x=600,y=10)

        #Display Details Frame
        display_details_frame=Frame(self.root,bg="white")
        display_details_frame.place(x=0,y=110,width=1332,height=550)

        #Route Label
        route_label=Label(display_details_frame,text="Route :",font=("times new roman",20,"bold"),bg="white",fg="black")
        route_label.place(x=100,y=20)

        #from and to location label
        from_to_location_label=Label(display_details_frame,text="From - To",font=("times new roman",20),bg="white",fg="black")
        from_to_location_label.place(x=350,y=20)

        #fill the from_to_location_label
        from_to_location_label.config(text=self.from_location+" - "+self.to_location)

        #date label
        date_label=Label(display_details_frame,text="Date : ",font=("times new roman",20,"bold"),bg="white",fg="black")
        date_label.place(x=100,y=70)


        #Date label
        date_label=Label(display_details_frame,text=self.date,font=("times new roman",20),bg="white",fg="black")
        date_label.place(x=350,y=70)

        #bus type label
        bus_type_label=Label(display_details_frame,text="Bus Type : ",font=("times new roman",20,"bold"),bg="white",fg="black")
        bus_type_label.place(x=100,y=120)

        #bus type label
        bus_type_label=Label(display_details_frame,text=self.bus_type,font=("times new roman",20),bg="white",fg="black")
        bus_type_label.place(x=350,y=120)

        #seat number label
        seat_number_label=Label(display_details_frame,text="Seats : ",font=("times new roman",20,"bold"),bg="white",fg="black")
        seat_number_label.place(x=100,y=170)

        #seat number label
        seat_number_label=Label(display_details_frame,font=("times new roman",20),bg="white",fg="black")
        seat_number_label.place(x=350,y=170)

        #fill the seat_number_label
        #convert the list to a string
        seat_number_string=",".join([ str(i) for i in self.selected_seats])
        seat_number_label.config(text=seat_number_string)

        #Total Seats Count label
        total_seats_count_label=Label(display_details_frame,text="Total Seats : ",font=("times new roman",20,"bold"),bg="white",fg="black")
        total_seats_count_label.place(x=100,y=220)

        #Total Seats Count label
        total_seats_count_label=Label(display_details_frame,text=len(self.selected_seats),font=("times new roman",20),bg="white",fg="black")
        total_seats_count_label.place(x=350,y=220)

        #Total Price label
        total_price_label=Label(display_details_frame,text="Total Price : ",font=("times new roman",20,"bold"),bg="white",fg="black")
        total_price_label.place(x=100,y=270)

        #Total Price label
        total_price_label=Label(display_details_frame,text=str(len(self.selected_seats)*float(self.current_price))+ " USD",font=("times new roman",20),bg="white",fg="black")
        total_price_label.place(x=350,y=270)

        #passenger details 
        #passenger email address
        passenger_email_address_label=Label(display_details_frame,text="Email Address : ",font=("times new roman",20,"bold"),bg="white",fg="black")
        passenger_email_address_label.place(x=100,y=320)

        #passenger email address entry
        self.passenger_email_address_entry=Entry(display_details_frame,font=("times new roman",15),bg="lightgray",fg="black")
        self.passenger_email_address_entry.place(x=350,y=320,width=250,height=30)

        #passenger contact number
        passenger_contact_number_label=Label(display_details_frame,text="Contact Number : ",font=("times new roman",20,"bold"),bg="white",fg="black")
        passenger_contact_number_label.place(x=100,y=370)

        #passenger contact number entry
        self.passenger_contact_number_entry=Entry(display_details_frame,font=("times new roman",15),bg="lightgray",fg="black")
        self.passenger_contact_number_entry.place(x=350,y=370,width=250,height=30)


        #payment type dropdown
        payment_type_label=Label(display_details_frame,text="Payment Type : ",font=("times new roman",20,"bold"),bg="white",fg="black")
        payment_type_label.place(x=100,y=420)

        #payment type dropdown
        self.payment_type=StringVar()

        #payment type dropdown
        payment_type_dropdown=ttk.Combobox(display_details_frame,textvariable=self.payment_type,font=("times new roman",15),state="readonly",justify=CENTER)
        payment_type_dropdown["values"]=("Cash","Credit / Debit Card","Net Banking","UPI","Paytm","PhonePe","Google Pay","BHIM","Paypal")
        payment_type_dropdown.place(x=350,y=420,width=250,height=30)
        payment_type_dropdown.current(0)


        #for loop for number seats selected passenger full name
        self.passenger_full_name_entry=[]
        for i in range(len(self.selected_seats)):
            #passenger full name
            passenger_full_name_label=Label(display_details_frame,text="Passenger " +str(i)+ " Full Name : ",font=("times new roman",20,"bold"),bg="white",fg="black")
            passenger_full_name_label.place(x=700,y=20+(i*50))

            #passenger full name entry
            passenger_full_name_entry=Entry(display_details_frame,font=("times new roman",15),bg="lightgray",fg="black")
            passenger_full_name_entry.place(x=1000,y=20+(i*50),width=250,height=30)

            #append passenger_full_name_entry
            self.passenger_full_name_entry.append(passenger_full_name_entry)

        #confirm payment button
        confirm_payment_button=Button(self.root,text="Confirm Payment",command=self.confirm_payment,font=("times new roman",15,"bold"),bg="white",fg="black",cursor="hand2")
        confirm_payment_button.place(x=600,y=700,width=200,height=30)


    #confirm payment
    def confirm_payment(self):
        self.email = self.passenger_email_address_entry.get()
        self.contact_number = self.passenger_contact_number_entry.get()
        self.payment_type = self.payment_type.get()
        self.passengers_full_name = [i.get() for i in self.passenger_full_name_entry]



        #check if email address is valid
        if self.email=="":
            messagebox.showerror("Error","Email Address is required",parent=self.root)
        elif not re.match("[^@]+@[^@]+\.[^@]+",self.email):
            messagebox.showerror("Error","Invalid Email Address",parent=self.root)
        
        #check if contact number is valid
        elif self.contact_number=="":
            messagebox.showerror("Error","Contact Number is required",parent=self.root)
        elif not re.match("[0-9]{10}",self.contact_number):
            messagebox.showerror("Error","Invalid Contact Number",parent=self.root)
        
        #check if payment type is selected
        elif self.payment_type=="":
            messagebox.showerror("Error","Payment Type is required",parent=self.root)

        #check if passenger full name is entered
        elif self.passengers_full_name=="":
            messagebox.showerror("Error","Passenger Full Name is required",parent=self.root)
        elif len(self.passengers_full_name)!=len(self.selected_seats):
            messagebox.showerror("Error","Please enter all passenger full name",parent=self.root)


        
    
        
        #check if all passenger full name is entered
        elif self.guest==True:
            #ask to login
            answer=messagebox.askyesno("Confirm Booking","Do you want to login?",parent=self.root)
            if answer==True:
                #open login page
                self.login_page()
            else:
                #create user
                #check if user is already created with same email address
                try:
                    user=None
                    #check if user already exists
                    with self.db.cursor() as cursor:
                        cursor.execute("SELECT * FROM Users WHERE Email=%s", (self.email,))
                        user = cursor.fetchone()


                    #if user exists
                    if user!=None:
                        #show error message
                        messagebox.showerror("Error","User already exists with this email address",parent=self.root)
                        #login page
                        self.login_page()
                    else:

                        try:
                            username=self.email.split("@")[0]
                            #insert into users table Username,Password,Email,FullName,ContactNumber,Role,RegistrationDate and store userid
                            with self.db.cursor() as cursor:
                                #insert and store userid
                                cursor.execute("insert into users(Username,Password,Email,FullName,ContactNumber,Role) values(%s,%s,%s,%s,%s,%s)",(username,"123456",self.email,self.passengers_full_name[0],self.contact_number,"Customer"))
                                #commit
                                self.db.commit()
                                #show success message
                                messagebox.showinfo("Success","User created successfully",parent=self.root)

                        except Exception as e:
                            messagebox.showerror("Error",f"Error due to: Users {str(e)}",parent=self.root)


                        #get userid from users table
                        try:
                            #get userid
                            with self.db.cursor() as cursor:
                                cursor.execute("SELECT UserID FROM Users WHERE Email=%s", (self.email,))
                                userid = cursor.fetchone()
                                self.userid=userid[0]
                        except Exception as e:
                            messagebox.showerror("Error",f"Error due to: Users {str(e)}",parent=self.root)

                except Exception as e:
                    messagebox.showerror("Error",f"Error due to: {str(e)}",parent=self.root)


        #store into database
        try:

            #create connection
            self.conn=self.db.cursor()
            #get the current date and time
            current_date_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            #get the passenger full name
            passenger_full_name_string=",".join([ str(i.get()) for i in self.passenger_full_name_entry])

            #get the selected seats
            selected_seats_string=",".join([ str(i) for i in self.selected_seats])

            try: 
                #insert into seats scheduleid, seatnumber,isbooked
                for i in self.selected_seats:
                    with  self.db.cursor() as cursor:
                        cursor.execute("insert into seats(ScheduleID,SeatNumber,IsBooked) values(%s,%s,%s)",(self.scheduleid,str(i),1))
                        #commit
                        self.db.commit()

            except Exception as e:
                messagebox.showerror("Error",f"Error due to: seats {str(e)}",parent=self.root)

            try:
                #insert into bookings table userid,scheduleid,seats,totalprice,booking date, status and store bookingid
                with self.db.cursor() as cursor:
                    cursor.execute("insert into bookings(UserID,ScheduleID,Seats,TotalPrice,Status) values(%s,%s,%s,%s,%s)",(self.userid,self.scheduleid,len(self.selected_seats),len(self.selected_seats)*float(self.current_price),"Confirmed"))
                    self.bookingid=cursor.lastrowid
                    #commit
                    self.db.commit()
                    
                print(self.bookingid)
            except Exception as e:
                messagebox.showerror("Error",f"Error due to: bookings {str(e)}",parent=self.root)


            try:
                #insert into payments table bookingid,userid,amount,paymentdate,paymentmethod,transactionstatus
                with self.db.cursor() as cursor:
                    cursor.execute("insert into payments(BookingID,UserID,Amount,PaymentMethod,TransactionStatus) values(%s,%s,%s,%s,%s)",(self.bookingid,self.userid,len(self.selected_seats)*float(self.current_price),self.payment_type,"Successful"))
                #commit
                self.db.commit()    
            except Exception as e:
                messagebox.showerror("Error",f"Error due to: payments {str(e)}",parent=self.root)


    #         #show success message
    #         messagebox.showinfo("Success","Booking Confirmed",parent=self.root)

    #         #open main welcome page
    #         self.main_welcome_page()
        except Exception as e:
            messagebox.showerror("Error",f"Error due to: {str(e)}",parent=self.root)
    



        #clearn the
        for child in self.root.winfo_children():
            child.destroy()
        
        # set the dimensions
        self.root.geometry("1332x745")

        # bg white
        self.root.config(bg="white")

        #heading frame
        heading_frame=Frame(self.root,bg="white")
        heading_frame.place(x=0,y=0,width=1332,height=50)

        #Payment Confirmed
        payment_confirmed_label=Label(heading_frame,text="Payment Confirmed",font=("times new roman",20,"bold"),bg="white",fg="black")
        payment_confirmed_label.place(x=600,y=10)

        #back button left top button
        back_button=Button(heading_frame,text="Back",command=self.main_welcome_page,font=("times new roman",12),bg="white",fg="black",cursor="hand2")
        back_button.place(x=10,y=10)

        #sign in/sign up button top right corner
        if self.login_success:
            sign_in_button = Button(heading_frame, text="Account Details", command=self.account_details_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
            sign_in_button.place(x=1180, y=7)
        else:
            sign_in_button = Button(heading_frame, text="Sign In / Sign Up", command=self.login_page, font=("times new roman", 12), bg="white", fg="black", cursor="hand2")
            sign_in_button.place(x=1180, y=7)

        #confirmation frame
        confirmation_frame=Frame(self.root,bg="#ADD8E6")
        confirmation_frame.place(x=0,y=50,width=1332,height=60)

        #Booking Details
        booking_details_label=Label(confirmation_frame,text="Booking Details",font=("times new roman",20,"bold"),bg="#ADD8E6",fg="black")
        booking_details_label.place(x=600,y=10)


        

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