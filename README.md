# Deluxe Pizza & Chicken Inn Web App

Modern full-stack food ordering app built with Django, Django templates, Tailwind CSS, Alpine.js, PostgreSQL-ready setup, and DRF APIs.

## Features

- Landing page with hero, CTA, sticky header, and announcement banners.
- Dynamic menu from admin (categories, products, variants, images).
- Cart and checkout flow with M-Pesa/COD selection.
- Order success and tracking by tracking code.
- Django admin + custom dashboard with order/revenue/popular item cards.
- REST API endpoints:
  - `/api/products/`
  - `/api/orders/`
  - `/api/cart/`

## Quick Start

1. Install dependencies:
   - `python -m pip install -r requirements.txt`
2. Copy env:
   - `copy .env.example .env`
3. Migrate:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
4. Create admin user:
   - `python manage.py createsuperuser`
5. Run server:
   - `python manage.py runserver`

## M-Pesa Integration Note

`orders/services.py` currently has a safe placeholder `simulate_mpesa_stk_push`. Replace with Daraja STK push logic for production.

## Deployment

- Backend: Render/Railway
- Database: PostgreSQL
- Static/media: Cloudinary or S3
