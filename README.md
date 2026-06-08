# Support CRM System

A full-stack Customer Support Ticketing CRM built for the Datastraw Technologies Hiring Assessment.

The application allows support teams to create, manage, search, filter, and update customer support tickets through a simple and responsive web interface.

## Live Application

**Deployed on Render**

https://datastraw-crm-z841.onrender.com

---

## Features

### Ticket Management

* Create support tickets
* Auto-generated ticket IDs (TKT-001, TKT-002, ...)
* Customer information management
* Detailed ticket view

### Search & Filtering

* Search tickets by:

  * Ticket ID
  * Customer Name
  * Customer Email
  * Subject
  * Description
* Filter tickets by status:

  * Open
  * In Progress
  * Closed
  * Reopened

### Ticket Updates

* Update ticket status
* Add notes/comments
* Automatic timestamp tracking
* Ticket history management

### Additional Enhancements

* Reopen count tracking
* Responsive UI
* Real-time ticket updates
* SQLite database persistence

---

## Tech Stack

### Backend

* FastAPI
* Python 3

### Frontend

* HTML
* JavaScript
* Tailwind CSS

### Database

* SQLite3

### Deployment

* Render

---

## Project Structure

```text
datastraw-crm/
│
├── main.py
├── database.py
├── models.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── templates/
│
└── static/
```

---

## Database Design

### Tickets Table

| Field          | Description                 |
| -------------- | --------------------------- |
| id             | Primary Key                 |
| ticket_id      | Unique Ticket Identifier    |
| customer_name  | Customer Name               |
| customer_email | Customer Email              |
| subject        | Issue Title                 |
| description    | Issue Description           |
| status         | Open / In Progress / Closed |
| reopen_count   | Number of Reopens           |
| created_at     | Creation Timestamp          |
| updated_at     | Last Updated Timestamp      |

### Notes Table

| Field      | Description    |
| ---------- | -------------- |
| id         | Primary Key    |
| ticket_id  | Related Ticket |
| note_text  | Comment / Note |
| created_at | Timestamp      |

---

## API Endpoints

### Create Ticket

```http
POST /api/tickets
```

### Get All Tickets

```http
GET /api/tickets
```

Optional Query Parameters:

```text
?search=keyword
?status=Open
```

### Get Ticket Details

```http
GET /api/tickets/{ticket_id}
```

### Update Ticket

```http
PUT /api/tickets/{ticket_id}
```

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/amey-gif/datastraw-crm
cd datastraw-crm
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=crm.db
```

### 6. Run Application

```bash
uvicorn main:app --reload
```

Application will be available at:

```text
http://localhost:8000
```

---

## Environment Variables

Example `.env.example`

```env
DATABASE_URL=crm.db
```

---

## Challenges Faced

* Designing a simple but scalable ticket workflow
* Implementing efficient search and filtering
* Managing SQLite database persistence
* Building a responsive user interface
* Deploying a full-stack FastAPI application on Render

---

## Future Improvements

* User Authentication
* Role-Based Access Control
* Ticket Assignment System
* Email Notifications
* Ticket Priorities
* Dashboard Analytics
* File Attachments

---

## Author

**Amey Parab**

Built as part of the Datastraw Technologies Internship Assessment.
