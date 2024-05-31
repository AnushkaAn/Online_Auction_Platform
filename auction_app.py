import sqlite3
import hashlib
import datetime
import mysql.connector

def connect_dbms():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dbms_pro"
    )
    cursor=conn.cursor()
    
    if conn.is_connected():
        print("Connected to MySQL Database")
        
    return conn,cursor
        
# Function to create a connection to the SQLite database
def connect_db():
    conn = sqlite3.connect("dbms_pro.db")
    cursor = conn.cursor()

    # Create the tables if they don't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            User_FName VARCHAR(50),
            User_LName VARCHAR(50),
            User_StreetNo VARCHAR(10),
            User_StreetName VARCHAR(50),
            User_City VARCHAR(50),
            User_State VARCHAR(50),
            User_Zipcode VARCHAR(10),
            User_Country VARCHAR(50),
            User_Email VARCHAR(100) UNIQUE,
            User_PhoneNo VARCHAR(15),
            User_Password VARCHAR(100)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS administrator (
            Admin_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Admin_FName VARCHAR(50),
            Admin_LName VARCHAR(50),
            Admin_Email VARCHAR(100) UNIQUE,
            Admin_Password VARCHAR(100)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product_category (
            Prod_Cat_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Cat_Name VARCHAR(50)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product (
            Prod_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Prod_Name VARCHAR(50),
            Prod_Description TEXT,
            Prod_Start_Bid_Amount FLOAT,
            Min_Bid_Increment FLOAT,
            Seller_ID INTEGER,
            Prod_Cat_ID INTEGER,
            FOREIGN KEY (Seller_ID) REFERENCES users(User_ID),
            FOREIGN KEY (Prod_Cat_ID) REFERENCES product_category(Prod_Cat_ID)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS auction (
            Auc_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Auc_Start_Date DATE,
            Auc_Close_Date DATE,
            Auc_Reserve_Price FLOAT,
            Auc_Payment_Date DATE,
            Auc_Winner_FName VARCHAR(50),
            Auc_Winner_LName VARCHAR(50),
            Auc_Payment_Amount FLOAT,
            Auc_Item_ID INTEGER,
            FOREIGN KEY (Auc_Item_ID) REFERENCES product(Prod_ID)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bid (
            Bid_Number INTEGER PRIMARY KEY AUTOINCREMENT,
            Bid_Item_ID INTEGER,
            Bid_Price FLOAT,
            Bid_Time DATETIME,
            Bid_Date DATE,
            Bid_Comment TEXT,
            Bidder_ID INTEGER,
            Seller_ID INTEGER,
            Auc_ID INTEGER,
            FOREIGN KEY (Bid_Item_ID) REFERENCES product(Prod_ID),
            FOREIGN KEY (Bidder_ID) REFERENCES users(User_ID),
            FOREIGN KEY (Seller_ID) REFERENCES users(User_ID),
            FOREIGN KEY (Auc_ID) REFERENCES auction(Auc_ID)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            Fdb_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Fdb_Time TIME,
            Fdb_Date DATE,
            Satisfaction_Rating INTEGER,
            Shipping_Delivery VARCHAR(50),
            Seller_Cooperation INTEGER,
            Overall_Rating INTEGER,
            Seller_ID INTEGER,
            Buyer_ID INTEGER,
            FOREIGN KEY (Seller_ID) REFERENCES users(User_ID),
            FOREIGN KEY (Buyer_ID) REFERENCES users(User_ID)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS shipment (
            Shipment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Ship_Planned_Date DATE,
            Ship_Actual_Date DATE,
            Ship_Cost FLOAT,
            Ship_Item_ID INTEGER,
            FOREIGN KEY (Ship_Item_ID) REFERENCES product(Prod_ID)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payment_method (
            Pay_Method_Code INTEGER PRIMARY KEY AUTOINCREMENT,
            Pay_Method_Description VARCHAR(100),
            Auc_ID INTEGER,
            FOREIGN KEY (Auc_ID) REFERENCES auction(Auc_ID)
        )
        """
    )

    return conn, cursor


# Utility function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Function to register a new user
def register_user(cursor, conn, user_details):
    hashed_password = hash_password(user_details["password"])
    try:
        cursor.execute(
            """
            INSERT INTO users (
                User_FName, User_LName, User_StreetNo, User_StreetName,
                User_City, User_State, User_Zipcode, User_Country,
                User_Email, User_PhoneNo, User_Password
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_details["first_name"],
                user_details["last_name"],
                user_details["street_no"],
                user_details["street_name"],
                user_details["city"],
                user_details["state"],
                user_details["zipcode"],
                user_details["country"],
                user_details["email"],
                user_details["phone"],
                hashed_password,
            ),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Error: Email already in use or unique constraint violated.")
        return False


# Function to register an admin
def register_admin(cursor, conn, admin_details):
    hashed_password = hash_password(admin_details["password"])
    try:
        cursor.execute(
            """
            INSERT INTO administrator (
                Admin_FName, Admin_LName, Admin_Email, Admin_Password
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                admin_details["first_name"],
                admin_details["last_name"],
                admin_details["email"],
                hashed_password,
            ),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Error: Email already in use or unique constraint violated.")
        return False


# Function to login a user
def login_user(cursor, email, password):
    hashed_password = hash_password(password)
    cursor.execute(
        """
        SELECT * FROM users WHERE User_Email = %s AND User_Password = %s
        """,
        (email, hashed_password),
    )
    user = cursor.fetchone()
    return user


# Function to login an admin
def login_admin(cursor, email, password):
    hashed_password = hash_password(password)  # Ensure you're using hashed passwords
    cursor.execute(
        """
        SELECT * FROM administrator WHERE Admin_Email = %s AND Admin_Password = %s
        """,
        (email, hashed_password),  # Ensure to use hashed password for comparison
    )
    admin = cursor.fetchone()
    return admin


# Function to add a new auction
def add_auction(cursor, conn, start_date, close_date, reserve_price, item_id, admin_id):
    try:
        cursor.execute(
            """
            INSERT INTO auction (Auc_Start_Date, Auc_Close_Date, Auc_Reserve_Price, Auc_Item_ID)
            VALUES (%s, %s, %s, %s)
            """,
            (start_date, close_date, reserve_price, item_id),
        )
        conn.commit()  # Commit the new auction to the database

        print("Auction added successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Error: Could not add auction. Details: {e}")
        return False


# Function to add a new product
def add_product(cursor, conn, product_name, description, start_bid_amount, min_bid_increment, seller_id, category_id):
    try:
        cursor.execute(
            """
            INSERT INTO product (Prod_Name, Prod_Description, Prod_Start_Bid_Amount, Min_Bid_Increment, Seller_ID, Prod_Cat_ID)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (product_name, description, start_bid_amount, min_bid_increment, seller_id, category_id),
        )
        conn.commit()  # Commit the new product to the database

        print("Product added successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Error: Could not add product. Details: {e}")
        return False


# Function to create a new product category
def add_product_category(cursor, conn, category_name):
    try:
        cursor.execute(
            """
            INSERT INTO product_category (Cat_Name)
            VALUES (%s)
            """,
            (category_name,),
        )
        conn.commit()  # Commit the new product category

        print("Product category added successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Error: Could not add product category. Details: {e}")
        return False


# Function to place a bid
def place_bid(cursor, conn, auction_id, bid_price, bidder_id):
    try:
        current_time = datetime.datetime.now()

        # Get the product associated with the auction
        cursor.execute(
            """
            SELECT auction.Auc_Item_ID, product.Seller_ID
            FROM auction
            INNER JOIN product ON auction.Auc_Item_ID = product.Prod_ID
            WHERE auction.Auc_ID = %s
            """,
            (auction_id,),
        )

        result = cursor.fetchone()
        if not result:
            print("Error: Auction or product not found.")
            return False

        prod_id, seller_id = result

        # Insert the bid into the bid table
        cursor.execute(
            """
            INSERT INTO bid (Bid_Item_ID, Bid_Price, Bid_Time, Bid_Date, Bidder_ID, Seller_ID, Auc_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (prod_id, bid_price, current_time, current_time.date(), bidder_id, seller_id, auction_id),
        )
        conn.commit()

        print("Bid placed successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Error: Could not place bid. Details: {e}")
        return False


# Function to add feedback
def add_feedback(cursor, conn, satisfaction_rating, shipping_delivery, seller_cooperation, overall_rating, seller_id, buyer_id):
    try:
        current_time = datetime.datetime.now().time()
        current_date = datetime.date.today()

        cursor.execute(
            """
            INSERT INTO feedback (Fdb_Time, Fdb_Date, Satisfaction_Rating, Shipping_Delivery, Seller_Cooperation, Overall_Rating, Seller_ID, Buyer_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (current_time, current_date, satisfaction_rating, shipping_delivery, seller_cooperation, overall_rating, seller_id, buyer_id),
        )
        conn.commit()

        print("Feedback added successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Error: Could not add feedback. Details: {e}")
        return False


# Function to view all auctions
def view_auctions(cursor):
    cursor.execute(
        """
        SELECT auction.Auc_ID, product.Prod_Name, auction.Auc_Reserve_Price,
        auction.Auc_Start_Date, auction.Auc_Close_Date
        FROM auction
        INNER JOIN product ON auction.Auc_Item_ID = product.Prod_ID
        """
    )
    auctions = cursor.fetchall()

    if not auctions:
        print("No auctions available.")
        return []

    for auction in auctions:
        print(f"Auction ID: {auction[0]}")
        print(f"Product: {auction[1]}")
        print(f"Reserve Price: {auction[2]}")
        print(f"Start Date: {auction[3]}")
        print(f"Close Date: {auction[4]}")
        print("")

    return auctions


# Main program loop
if __name__ == "__main__":
    # Create a connection to the database
    conn, cursor = connect_dbms()

    running = True

    while running:
        print("Main Menu:")
        print("1. Admin")
        print("2. User")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":  # Admin functionality
            email = input("Enter admin email: ")
            password = input("Enter admin password: ")

            admin = login_admin(cursor, email, password)

            if not admin:
                # If admin not found, attempt to register
                print("Admin not found. Please register.")
                admin_details = {
                    "first_name": input("Enter your first name: "),
                    "last_name": input("Enter your last name: "),
                    "email": email,
                    "password": password,
                }
                if register_admin(cursor, conn, admin_details):
                    print("Admin registered successfully.")
                    admin = login_admin(cursor, email, password)
                else:
                    print("Failed to create admin.")

            if admin:
                print("Admin Menu:")
                print("1. Add Product")
                print("2. Add Auction")
                print("3. Add Product Category")
                print("4. View All Auctions")

                admin_choice = input("Choose an option: ")

                if admin_choice == "1":
                    # Admin adds a new product
                    product_name = input("Enter product name: ")
                    description = input("Enter product description: ")
                    start_bid_amount = float(input("Enter starting bid amount: "))
                    min_bid_increment = float(input("Enter minimum bid increment: "))
                    seller_id = admin[0]  # Admin is the seller
                    category_id = int(input("Enter product category ID: "))

                    add_product(cursor, conn, product_name, description, start_bid_amount, min_bid_increment, seller_id, category_id)

                elif admin_choice == "2":
                    # Admin adds a new auction
                    product_id = int(input("Enter the product ID for the auction: "))
                    reserve_price = float(input("Enter reserve price: "))
                    start_date = datetime.date.today()
                    close_date = datetime.date.today() + datetime.timedelta(days=7)

                    add_auction(cursor, conn, start_date, close_date, reserve_price, product_id, admin[0])

                elif admin_choice == "3":
                    # Admin adds a new product category
                    category_name = input("Enter category name: ")

                    add_product_category(cursor, conn, category_name)

                elif admin_choice == "4":
                    # Admin views all auctions
                    view_auctions(cursor)

        elif choice == "2":  # User functionality
            email = input("Enter your email: ")
            password = input("Enter your password: ")

            user = login_user(cursor, email, password)

            if not user:
                print("User not found. Please register.")
                user_details = {
                    "first_name": input("Enter your first name: "),
                    "last_name": input("Enter your last name: "),
                    "street_no": input("Enter your street number: "),
                    "street_name": input("Enter your street name: "),
                    "city": input("Enter your city: "),
                    "state": input("Enter your state: "),
                    "zipcode": input("Enter your zipcode: "),
                    "country": input("Enter your country: "),
                    "email": email,
                    "phone": input("Enter your phone number: "),
                    "password": password,
                }

                if register_user(cursor, conn, user_details):
                    user = login_user(cursor, email, password)  # Re-attempt login

            if user:
                print("User Menu:")
                print("1. View All Auctions")
                print("2. Place a Bid")

                user_choice = input("Choose an option: ")

                if user_choice == "1":
                    # User views all auctions
                    auctions = view_auctions(cursor)

                elif user_choice == "2":
                    # User places a bid
                    auction_id = int(input("Enter auction ID: "))
                    bid_price = float(input("Enter your bid price: "))

                    place_bid(cursor, conn, auction_id, bid_price, user[0])

        elif choice == "3":  # Exit
            running = False
            print("Exiting...")

    # Close the database connection
    conn.close()
