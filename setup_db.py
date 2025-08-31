import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect("mydb.sqlite")
cursor = conn.cursor()

# Create the 'users' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    state TEXT,
    email TEXT,
    status TEXT,
    confirm_email BOOLEAN
)
""")

# Insert dummy data
cursor.execute("INSERT INTO users (username, first_name, last_name, state, email, status, confirm_email) VALUES (?, ?, ?, ?, ?, ?, ?)",
               ("user1", "Alice", "Smith", "California", "alice@example.com", "active", True))
cursor.execute("INSERT INTO users (username, first_name, last_name, state, email, status, confirm_email) VALUES (?, ?, ?, ?, ?, ?, ?)",
               ("user2", "Bob", "Johnson", "California", "bob@example.com", "active", True))

conn.commit()
conn.close()

print("Database setup complete!")
import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect("mydb.sqlite")
cursor = conn.cursor()

# Create the 'users' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    state TEXT,
    email TEXT,
    status TEXT,
    confirm_email BOOLEAN
)
""")

# Insert dummy data
cursor.execute("INSERT INTO users (username, first_name, last_name, state, email, status, confirm_email) VALUES (?, ?, ?, ?, ?, ?, ?)",
               ("user1", "Alice", "Smith", "California", "alice@example.com", "active", True))
cursor.execute("INSERT INTO users (username, first_name, last_name, state, email, status, confirm_email) VALUES (?, ?, ?, ?, ?, ?, ?)",
               ("user2", "Bob", "Johnson", "California", "bob@example.com", "active", True))

conn.commit()
conn.close()

print("Database setup complete!")
