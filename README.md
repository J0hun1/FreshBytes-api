# FreshBytes API

A Django REST Framework (DRF) backend for the FreshBytes e-commerce platform.

## Overview
- Provides APIs for user, seller, product, category, subcategory, reviews, promo, cart, order, and related management.
- Uses a custom user model (not Django's default `auth.User`).
- Data model and relationships are documented in `FreshBytes/ERD_Visual.md` (Mermaid ERD).

## Features
- Product management (CRUD)
- Category and subcategory management
- Seller and user management
- Cart and order processing
- Review and rating system
- Promo and discount logic
- Soft delete and timestamp tracking

## Getting Started

### Prerequisites
- Python 3.10+
- pip
- (Optional) SQLite browser for inspecting the database

### Setup
1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd FreshBytes-api
   ```
2. Install dependencies:
   ```sh
   pip install -r FreshBytes/requirements.txt
   ```
3. Apply migrations:
   ```sh
   cd FreshBytes
   python manage.py makemigrations api
   python manage.py migrate
   ```
4. Run the development server:
   ```sh
   python manage.py runserver
   ```

### Database
- SQLite database file: `FreshBytes/db.sqlite3`
- ERD: `FreshBytes/ERD_Visual.md`

### Testing
- Run all tests:
  ```sh
  python manage.py test api
  ```

## Project Structure
- `FreshBytes/api/` — All business logic, models, serializers, services, and tests
- `FreshBytes/FreshBytes/` — Django project settings and entry points
- `.github/copilot-instructions.md` — AI agent and contributor guidelines

## Best Practices
- Hash passwords before saving (see `.github/copilot-instructions.md`)
- Use DRF serializers for validation
- Keep business logic in `services.py` where possible
- Update the ERD and add tests for all new features

## Limitations & TODO
- No authentication endpoints or password hashing (security risk)
- No payment, shipping, or inventory management
- No external integrations
- README and documentation should be kept up to date as the project evolves

## License
MIT
