# 📝 Smart Contacts API

## 📖 Description
**Smart Contacts API** is a high-performance **RESTful backend built with FastAPI**. 
It provides a solution for managing personal contacts, featuring **secure authentication** and advanced 
**search capabilities**, including a dedicated birthday tracking system.

**Designed as a pet project to demonstrate backend architecture and best practices.**


## 🛠 Technologies
- **Backend:** Python 3.12, FastAPI
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL
- **Migrations:** Alembic
- **Dependency Management:** Poetry
- **Auth:** JWT (Access & Refresh tokens), Passlib (Bcrypt)
- **Deployment:** Docker & Docker Compose

## 🚀 Features
- **Authentication:** OAuth2 + JWT (access & refresh tokens), password hashing with bcrypt.
- **Contacts:** Full CRUD with search.
- **Validation:** Pydantic schemas for data integrity.
- **DevOps:** Dockerization with Dockerfile, docker-compose.yml and implemented healthcheck.
- **API Docs:** Swagger (OpenAPI) auto-generated documentation. 

## ⚙️ Installation & Setup
1. **Prerequisites:** Python 3.12+, Docker
2. **Clone the repo:**
   ```bash
   git clone https://github.com/pradivliany/fastapi-smart-contacts
   cd fastapi-smart-contacts
   ```
3. Create .env file from .env.example
4. Build and run containers:
   ```bash
   docker-compose build
   docker-compose up -d
   ```
5. Access the API Documentation: Open your browser and navigate to http://127.0.0.1:5000/docs

## 👤 Author:
   - GitHub: https://github.com/pradivliany
   - Email: yaroslavpradyvlianyi@gmail.com
   - LinkedIn: https://www.linkedin.com/in/yaroslav-pradyvlianyi/
