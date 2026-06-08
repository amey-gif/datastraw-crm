from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import CreateTicket, UpdateTicket, ReopenTicket
from database import get_db, init_db, generate_ticket_id
from datetime import datetime
import os

app = FastAPI()

# Initialize DB on startup

@app.on_event("startup")
def startup():
    init_db()

# Serve static files (HTML, JS, CSS)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root

@app.get("/")
def root():
    return FileResponse("static/index.html")

# POST /api/tickets — Create a new ticket

@app.post("/api/tickets")
def create_ticket(ticket: CreateTicket):
    conn = get_db()
    cursor = conn.cursor()

    ticket_id = generate_ticket_id()

    cursor.execute("""
        INSERT INTO tickets (ticket_id, customer_name, customer_email, subject, description)
        VALUES (?, ?, ?, ?, ?)
    """, (ticket_id, ticket.customer_name, ticket.customer_email, ticket.subject, ticket.description))

    conn.commit()
    
    # Fetch created_at of new ticket
    cursor.execute("SELECT created_at FROM tickets WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()

    return {"ticket_id": ticket_id, "created_at": row["created_at"]}


# GET /api/tickets — List all tickets

@app.get("/api/tickets")
def get_tickets(status: str = None, search: str = None):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT ticket_id, customer_name, subject, status, created_at FROM tickets WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if search:
        query += " AND (customer_name LIKE ? OR customer_email LIKE ? OR ticket_id LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# GET /api/tickets/{ticket_id} — Get single ticket

@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    ticket = cursor.fetchone()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Fetch notes for this ticket
    cursor.execute("SELECT note_text, created_at FROM notes WHERE ticket_id = ? ORDER BY created_at DESC", (ticket_id,))
    notes = cursor.fetchall()
    conn.close()

    ticket_data = dict(ticket)
    ticket_data["notes"] = [dict(note) for note in notes]

    return ticket_data


# PUT /api/tickets/{ticket_id} — Update ticket

@app.put("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, update: UpdateTicket):
    conn = get_db()
    cursor = conn.cursor()

    # Check ticket exists
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    ticket = cursor.fetchone()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket["status"] == 'Closed':
        raise HTTPException(status_code=400, detail='Ticket is closed. Use reopen endpoint instead')

    old_status = ticket["status"]        

    # Update status if provided and different
    if update.status:
        valid_statuses = ["Open", "In Progress", "Closed"]
        if update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        cursor.execute("""
            UPDATE tickets SET status = ?, updated_at = ? WHERE ticket_id = ?
        """, (update.status, datetime.now().isoformat(), ticket_id))

        # Auto note for status change
        auto_note = f"Status changed: {old_status} → {update.status}"
        cursor.execute("""
            INSERT INTO notes (ticket_id, note_text) VALUES (?, ?)
        """, (ticket_id, auto_note))

    # Add note if provided
    if update.note_text:
        cursor.execute("""
            INSERT INTO notes (ticket_id, note_text) VALUES (?, ?)
        """, (ticket_id, update.note_text))

    conn.commit()
    conn.close()

    return {"success": True, "updated_at": datetime.now().isoformat()}



# PUT /api/tickets/{ticket_id}/reopen — Reopen a closed ticket

@app.put("/api/tickets/{ticket_id}/reopen")
def reopen_ticket(ticket_id: str, reopen: ReopenTicket):
    conn = get_db()
    cursor = conn.cursor()

    # Check ticket exists
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    ticket = cursor.fetchone()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Only closed tickets can be reopened
    if ticket["status"] != "Closed":
        raise HTTPException(status_code=400, detail="Only closed tickets can be reopened.")

    # Update status to Reopened + increment reopen_count
    cursor.execute("""
        UPDATE tickets 
        SET status = 'Reopened', 
            reopen_count = reopen_count + 1,
            updated_at = ?
        WHERE ticket_id = ?
    """, (datetime.now().isoformat(), ticket_id))

    # Auto system note
    reopen_count = ticket["reopen_count"] + 1
    auto_note = f"Ticket reopened (#{reopen_count}) on {datetime.now().strftime('%d %b %Y %H:%M')}"
    cursor.execute("""
        INSERT INTO notes (ticket_id, note_text) VALUES (?, ?)
    """, (ticket_id, auto_note))

    # Add manual note if provided
    if reopen.note_text:
        cursor.execute("""
            INSERT INTO notes (ticket_id, note_text) VALUES (?, ?)
        """, (ticket_id, reopen.note_text))

    conn.commit()
    conn.close()

    return {"success": True, "status": "Reopened", "reopen_count": reopen_count}