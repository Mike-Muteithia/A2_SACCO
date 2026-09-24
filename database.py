import sqlite3
import os

DB_NAME = "sacco.db"

def get_connection():
    """Establishes and returns a safe connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    # Enable foreign key constraints for SQLite
    conn.execute("PRAGMA foreign_keys = 1")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Creates the database schema if the tables do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Members Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            date_registered DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Savings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings (
            savings_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            balance REAL DEFAULT 0.0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (member_id) ON DELETE CASCADE
        )
    ''')

    # Loans Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT CHECK(status IN ('Pending', 'Approved', 'Rejected')) DEFAULT 'Pending',
            balance REAL NOT NULL,
            FOREIGN KEY (member_id) REFERENCES members (member_id) ON DELETE CASCADE
        )
    ''')

    # Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            transaction_type TEXT CHECK(transaction_type IN ('Deposit', 'Withdrawal', 'Loan Repayment')) NOT NULL,
            amount REAL NOT NULL,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (member_id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully.")

def execute_query(query, params=()):
    """Helper function to execute INSERT/UPDATE/DELETE queries safely."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def fetch_query(query, params=(), fetchone=False):
    """Helper function to execute SELECT queries safely."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetchone:
            return cursor.fetchone()
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()