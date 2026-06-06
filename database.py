import sqlite3
from datetime import datetime

DATABASE = "crm.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()


    # tickets table
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS tickets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))  
        )
    """)

    # Notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            note_text TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
        )
    """)

    # Counter table for ticket ID generation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_counter(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count INTEGER DEFAULT 0
        )
    
    """)

    cursor.execute("""
        INSERT INTO ticket_counter(count)
        SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM ticket_counter)
    """)

    conn.commit()
    conn.close()

def generate_ticket_id():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE ticket_counter SET count = count + 1")
    conn.commit()
    cursor.execute("SELECT count FROM ticket_counter")
    count = cursor.fetchone()[0]
    conn.close()
    return f"TKT-{str(count).zfill(3)}" 