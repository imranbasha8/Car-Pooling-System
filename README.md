# 🚗 Car Pooling System (Django + MySQL)

A web-based **Car Pooling System** built with Django that connects **drivers** and **passengers**.  
Drivers can list their rides, and passengers can search, book, and share journeys easily.

---

## ✨ Features

- 👤 **Role-based users**: Driver & Passenger dashboards  
- 🚘 **Driver features**:  
  - Add car details (vehicle papers, images, seat availability, price)  
  - Manage ride requests and bookings  

- 🧳 **Passenger features**:  
  - Search rides by date & location  
  - Book available seats  
  - Submit feedback after ride completion  

- ⚙️ **Booking management**:  
  - Seat availability check  
  - Validations (booking date, available seats, secure uploads)  

- 🔒 **Security**:  
  - Environment variables for database credentials  
  - Validated file/image uploads  

---

## 🛠️ Tech Stack

- **Backend**: Django (Python)  
- **Database**: MySQL  
- **Frontend**: HTML, CSS, Bootstrap  
- **Version Control**: Git & GitHub  

---

## 📂 Project Setup

1. **Clone the repository**  

Create a virtual environment :
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On Linux/Mac

Install dependencies :
pip install -r requirements.txt

Set up environment variables : 
DB_USER=root
DB_PASSWORD=yourpassword

Apply migrations: 
python manage.py migrate 

Run the development server :
python manage.py runserver
