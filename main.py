#import python sql and tkinter libraries
import mysql.connector as mysql
from tkinter import *
from tkinter import messagebox                                                  
from PIL import ImageTk, Image
import os 
import re


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
        self.root.geometry("1350x750+0+0")

        #create a frame for welcome image
        welcome_image=Image.open("images/welcome.png") 
        welcome_image=ImageTk.PhotoImage(welcome_image)
        welcome_image_label=Label(self.root,image=welcome_image)
        welcome_image_label.photo=welcome_image
        welcome_image_label.pack()


#-------------------------------------------------------------------------------------------------------------

#starter code 
if __name__ == "__main__":
    root = Tk()
    application = busTicketReservation(root)
    root.mainloop()