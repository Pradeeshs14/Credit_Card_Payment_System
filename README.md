\# Credit Card Payment System

A full-stack credit card payment simulation system built using React, Django REST Framework, FastAPI, MySQL, and Docker.

\## Technologies Used

\* \*\*Frontend:\*\* React, Vite, Tailwind CSS

\* \*\*Backend:\*\* Django REST Framework

\* \*\*Payment Service:\*\* FastAPI

\* \*\*Database:\*\* MySQL 8.0

\* \*\*Authentication:\*\* JWT

\* \*\*API Documentation:\*\* Swagger / OpenAPI

\* \*\*Testing:\*\* Django Test Framework, Pytest, Coverage

\* \*\*Containerization:\*\* Docker, Docker Compose

\* \*\*API Testing:\*\* Postman

\## Project Features

\### User Authentication

\* User registration

\* JWT login

\* JWT token refresh

\* Logout

\* Protected API routes

\* Password encryption

\### Card Management

\* Add credit/debit cards

\* View saved cards

\* Delete saved cards

\* Card number validation

\* Expiry month validation

\* Card numbers are not stored

\* Only masked card number and last four digits are stored

\* CVV is not stored

\### Payment Processing

\* FastAPI payment service

\* Payment starts with `PENDING` status

\* Payment is simulated as `SUCCESS` or `FAILED`

\* Unique transaction ID generation

\* Payment data synchronized with Django

\### Transaction Management

\* View transaction history

\* Filter transactions by status

\* Filter transactions by amount

\* Filter transactions by date

\* Create transactions

\* Admin CSV export

\* Daily payment summary

\### Admin Panel

\* Manage users

\* View saved cards

\* View transactions

\* View payment summaries

\* View admin activity logs

\### Frontend

\* Registration page

\* Login page

\* Dashboard

\* Add Card page

\* Make Payment page

\* Transaction History page

\* Admin Dashboard

\## Project Structure

Credit_Card_Payment_System/

│

├── backend/

│ ├── admin_logs/

│ ├── cards/

│ ├── config/

│ ├── payment_service/

│ ├── transactions/

│ ├── users/

│ ├── Dockerfile

│ ├── manage.py

│ └── requirements.txt

│

├── frontend/

│ ├── public/

│ ├── src/

│ │ ├── pages/

│ │ ├── services/

│ │ ├── App.jsx

│ │ └── main.jsx

│ ├── Dockerfile

│ ├── package.json

│ └── vite.config.js

│

├── docker-compose.yml

├── .gitignore

└── README.md

\## Database

The application uses MySQL with the following main data:

\* Users

\* Cards

\* Transactions

\* Payments

\* Admin Logs

\### Card Security

Actual card numbers and CVV values are not stored in the database.

The card service stores:

\* Masked card number

\* Last four digits

\* Card type

\* Expiry month

\* Expiry year

\## API Endpoints

\### Authentication

POST /api/users/register/

POST /api/users/login/

POST /api/users/token/refresh/

POST /api/users/logout/

GET /api/users/me/

\### Cards

GET /api/cards/

POST /api/cards/

DELETE /api/cards/{id}/

\### Transactions

GET /api/transactions/

POST /api/transactions/create/

POST /api/transactions/sync/

GET /api/transactions/export-csv/

GET /api/transactions/admin/summary/

\### Admin Logs

GET /api/admin-logs/

\### FastAPI Payment Service

POST /api/payments/

GET /api/payments/{payment_id}

\## API Documentation

\### Django Swagger

http://127.0.0.1:8000/api/docs/

\### Django OpenAPI Schema

http://127.0.0.1:8000/api/schema/

\### FastAPI Swagger

http://127.0.0.1:8001/docs

\## Running with Docker

Make sure Docker Desktop is running.

From the project root:

```powershell

docker compose up -d

```

Check the containers:

```powershell

docker compose ps

```

The services use:

MySQL → localhost:3307

Django → localhost:8000

FastAPI → localhost:8001

Frontend → localhost:5173

Run Django migrations:

```powershell

docker compose exec django python manage.py migrate

```

Run Django system checks:

```powershell

docker compose exec django python manage.py check

```

Stop the containers:

```powershell

docker compose down

```

\## Local Development

\### Django

From the `backend` directory:

```powershell

python manage.py runserver

```

\### FastAPI

From the project root:

```powershell

uvicorn app.main:app --reload --app-dir payment\_service --port 8001

```

\### Frontend

From the `frontend` directory:

```powershell

npm install

npm run dev

```

\## Testing

The project includes automated tests for:

\* User authentication

\* Password encryption

\* JWT authentication

\* Card management

\* Card validation

\* Card number storage protection

\* Transaction history

\* Transaction filtering

\* CSV export

\* Admin payment summary

\* Payment success/failure

\* Payment validation

\* Payment retrieval

\### Django Tests

```powershell

python manage.py test

```

\### FastAPI Tests

```powershell

pytest payment\_service/tests/test\_payments.py -v

```

\### Coverage

```powershell

coverage run manage.py test

coverage report

```

Current test coverage:

94%

\## Security

The application implements:

\* JWT authentication

\* Protected API endpoints

\* Django password hashing

\* Input validation

\* Card number validation

\* No CVV storage

\* No full card number storage

\* Masked card information

\* Django ORM for database operations

\* Internal API key for payment-to-transaction synchronization

\## Docker Services

The Docker Compose environment contains:

mysql

django

fastapi

frontend

Docker images:

credit-card-django

credit-card-fastapi

credit-card-frontend

\## Project Status

The following major components are completed:

\* User Authentication

\* Card Management

\* Payment Processing

\* Transaction Management

\* Admin Panel

\* Admin Logs

\* React Frontend

\* Django API Documentation

\* FastAPI API Documentation

\* Automated Testing

\* Docker Setup

\* Git/GitHub Setup

\## Repository

GitHub:

https://github.com/Pradeeshs14/Credit\_Card\_Payment\_System
