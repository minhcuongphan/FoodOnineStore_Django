# FoodOnlineStore - Django Project

FoodOnlineStore is a web application built with Django that allows users to manage an online food marketplace. Vendors can list their food items, customers can browse and order, and administrators can manage the platform.

---

## Features

- **User Roles**: Vendor, Customer, and Admin.
- **Vendor Dashboard**: Manage food items, categories, and orders.
- **Customer Dashboard**: Browse food items, add to cart, and place orders.
- **Admin Panel**: Manage users, vendors, and orders.
- **Email Notifications**: Verification emails and notifications using `django-mail-queue`.
- **Cron Jobs**: Automated tasks for removing inactive users and other scheduled operations.
- **Payment Integration**: PayPal integration for secure payments.
- **Google Maps API**: Location-based features for vendors and customers.

---

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- Virtual Environment (optional but recommended)

### Build the Docker images:
docker-compose build

### Start the containers:
docker-compose up

### Access the web container
docker-compose exec web bash

### Access the db container
docker-compose exec db psql -U django_user -d django_db

### Stop all running containers:
docker-compose down

### Run migrations:

python manage.py makemigrations
python manage.py migrate

### Create a superuser:

python manage.py createsuperuser

### Cron jobs

python manage.py runcrons

### Email queue

python manage.py send_queued_messages