# Vehicle Parking Management System (Flask Web Application)

## Overview
This project is a web-based Vehicle Parking Management System built using Flask. It enables users to reserve and release parking spots, while providing administrators with tools to manage parking lots, spots, and user activities.

The system is designed to automate parking operations, improve efficiency, and provide real-time visibility into parking availability and usage.

---

## Features

### User Features
- User registration, login, and logout with secure authentication  
- View available parking lots and spots  
- Reserve and release parking spots  
- Track parking history including duration and cost  

### Admin Features
- Create, update, and delete parking lots  
- Automatically generate parking spots based on lot capacity  
- Monitor spot availability (Available / Occupied)  
- View user activity and reservation history  
- Search functionality for users, lots, and parking records  

---

## System Design

### Architecture
The application follows the Model-View-Controller (MVC) architecture:

- Models: Define database structure using SQLAlchemy ORM  
- Routes (Controllers): Handle user requests and business logic  
- Templates (Views): Render dynamic UI using Jinja2  

Database interactions are managed using SQLite through SQLAlchemy ORM :contentReference[oaicite:0]{index=0}  

---

### Database Design

Key entities:

- User: Stores user credentials and profile details  
- ParkingLot: Represents parking areas with capacity and pricing  
- ParkingSpot: Tracks individual spot availability  
- Reservation: Maintains booking details including time and cost  

The schema establishes relationships between users, spots, and reservations for efficient tracking :contentReference[oaicite:1]{index=1}  

---

## Core Functionality

- Role-based access control for Admin and User dashboards  
- Real-time reservation system with automatic spot allocation  
- Dynamic cost calculation based on parking duration  
- Reservation history tracking for both users and admins  
- Flash messaging system for better user experience  

---

## Additional Features
- Responsive UI built with Bootstrap  
- Search functionality for efficient data retrieval  
- Timezone-aware calculations (IST)  
- Interactive dashboard for monitoring parking status  

---

## Technologies Used
- Python (Flask)  
- Flask-SQLAlchemy (ORM)  
- Flask-Login (Authentication)  
- SQLite (Database)  
- HTML, CSS, Bootstrap, Jinja2  

---

## Development Approach
The project was implemented incrementally using milestone-based development, covering:

- Database schema design and relationships  
- Authentication and role-based access  
- Admin and user dashboards  
- Reservation and cost calculation logic  

Milestone-based implementation ensured modular development and testing at each stage :contentReference[oaicite:2]{index=2}  

---

## Key Learnings
- Designing scalable web applications using MVC architecture  
- Implementing authentication and role-based access control  
- Managing relational databases using ORM  
- Building full-stack applications with Flask  
- Handling real-world workflows such as reservations and cost computation  

---

## Future Improvements
- Integration of REST APIs for external services  
- Payment gateway integration  
- Real-time monitoring using WebSockets  
- Deployment on cloud platforms  

---

## Author
Nitish Bhatt  
BS Data Science and Applications (IIT Madras) + B.Tech Mechanical Engineering (GBPUAT)
