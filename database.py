# For my DB im going to use SQLite for right now and go to Mango if needed...
# SQLite is best for this instance because its already included with Python, so there wont be any new packages installed
import sqlite3
from pathlib import Path

# Assign the name of the DB
database_name = str(Path(__file__).resolve().with_name("portfolio.db"))

def get_connection():
    connection = sqlite3.connect(database_name)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_db():
    """
    FUTURE
    """

    # create connect to SQL database
    connection = get_connection()

    # We also need to create a cursor
    # a cursor allows us to execute SQL commands
    cursor = connection.cursor()

    # We need to create a table to store portfolios and their information
    # Each port should have a unique id and name
    cursor.execute('''CREATE TABLE IF NOT EXISTS portfolio (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)''')
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL REFERENCES portfolio(id),
            ticker TEXT NOT NULL,
            shares REAL NOT NULL,
            purchase_price REAL NOT NULL,
            current_price REAL NOT NULL
        )
    """)
    # Bear with me
    # I have never used DB

    # save db changes
    connection.commit()

    # Close connection
    connection.close()

# next we need to create a function that creates a portfolio in our db
def create_portfolio(name): # we should take name as the param
    """
    Future
    """

    # First we need to prevent users from creating new ports with empty names
    if not name or not name.strip():
        raise ValueError("Name cannot be empty")

    # Connect to db
    connection = get_connection()
    cursor = connection.cursor()

    # Insert port name into our table
    # We will use '?' placeholder to safely pass the users input into SQL
    cursor.execute('''INSERT INTO portfolio (name) VALUES (?)''', (name.strip(),))

    # commit
    connection.commit()

    # close connection
    connection.close()

    return True

# We need to create several getters and setters for our main project
# the first one will be get port
def get_portfolios():
    """
    FUTURE
    """

    # establish connection
    connection = get_connection()
    # in the future, I should create a function for this

    # retrieve ports in alphabetical order
    portfolios = connection.execute("SELECT * FROM portfolio ORDER BY name").fetchall()

    # close connection and return
    connection.close()
    return portfolios

# Next we need to get a single portfolio
def get_portfolio(portfolio_id):
    """
    FUTURE
    """

    connection = get_connection()
    portfolio = connection.execute("SELECT * FROM portfolio WHERE id = ?", (portfolio_id,)).fetchone()

    # close and return
    connection.close()
    return portfolio

# add holding
def add_holding(portfolio_id, ticker, shares, purchase_price, current_price):
    """
    FUTURE
    :param portfolio_id:
    :param ticker:
    :param shares:
    :param purchase_price:
    :param current_price:
    :return:
    """

    # create connection
    connection = get_connection()
    # insert investment into holding table
    # I had to break it out like this becasue I kept screwing it up
    connection.execute(""" 
                       INSERT INTO holdings
                       (portfolio_id, ticker, shares,
                        purchase_price, current_price)
                       VALUES (?, ?, ?, ?, ?)
                       """, (
                           portfolio_id,
                           ticker,
                           shares,
                           purchase_price,
                           current_price
                       ))

    # commit info and close
    connection.commit()
    connection.close()

# next we need to retrieve the holdings
def get_holdings(portfolio_id):
    """
    FUTURE
    :param portfolio_id:
    :return:
    """

    # establish connection and define holdings
    connection = get_connection()

    holdings = connection.execute(
        "SELECT * FROM holdings WHERE portfolio_id = ?",
        (portfolio_id,)
    ).fetchall()


    connection.close()
    return holdings

# we need to do something similar to portfolio and portfolios here
def get_holding(holding_id):
    """
    FUTURE
    :param holding_id:
    :return:
    """

    connection = get_connection()
    holding = connection.execute(
        "SELECT * FROM holdings WHERE id = ?",
        (holding_id,)
    ).fetchone()

    # close conn
    connection.close()
    return holding

# update holdings:
# this is prob one of the most important functions
def update_holding(holding_id, ticker, shares, purchase_price, current_price):
    """
    FUTURE
    :param holding_id:
    :param ticker:
    :param shares:
    :param purchase_price:
    :param current_price:
    :return:
    """

    connection = get_connection()

    # Update the holding at the ID to match the new values
    connection.execute("""
                       UPDATE holdings
                       SET ticker = ?,
                           shares = ?,
                           purchase_price = ?,
                           current_price = ?
                       WHERE id = ?
                       """, (
        ticker,
        shares,
        purchase_price,
        current_price,
        holding_id
    ))

    # commit and close
    connection.commit()
    connection.close()

# lastly we need to create delete holding
def delete_holding(holding_id):
    """
    FUTURE
    :param holding_id:
    :return:
    """

    connection = get_connection()

    # Delete the holding id
    connection.execute("""
                       DELETE FROM holdings WHERE id = ?""", (holding_id,)
    )

    # commit and close
    connection.commit()
    connection.close()


