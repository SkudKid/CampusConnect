import sqlite3 as sql

#Connect to database, or create if not existing
conn = sql.connect("campusconnect.db") #Creates file in case it's not existing
cursor = conn.cursor()

#Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''') #Create users table

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT
    priority INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''') #Create tasks table

cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    event_date TEXT,
    location TEXT,
    shared_with TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''') #Create events table

conn.commit()
conn.close()