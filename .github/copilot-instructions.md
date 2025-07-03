# Copilot Coding Agent Instructions for FreshBytes API

## Project Overview
- This is a Django REST Framework (DRF) e-commerce backend for FreshBytes, using a custom user model and SQLite for development.
- Major entities: User, Seller, Product, Category, SubCategory, Reviews, Promo, Cart, CartItem, Order, OrderItem.
- Data model and relationships are documented in `FreshBytes/ERD_Visual.md` (Mermaid ERD).

## Key Architectural Patterns
- **App Structure:**
  - All business logic and models are in `FreshBytes/api/`.
  - Django project settings and entry points are in `FreshBytes/FreshBytes/`.
- **Custom User Model:**
  - Defined in `api/models.py` as `User` (not Django's default `auth.User`).
  - `user_id` is a custom string PK, auto-generated in the model's `save()`.
- **Serializers:**
  - All major models have a corresponding DRF serializer in `api/serializers.py`.
  - Validation logic is implemented in serializer methods (e.g., price checks, promo validation).
- **Services:**
  - Business logic helpers are in `api/services.py` (e.g., updating product promo flags).

## Developer Workflows
- **Run the API:**
  - `python manage.py runserver` from the `FreshBytes` directory.
- **Migrations:**
  - `python manage.py makemigrations api`
  - `python manage.py migrate`
- **Database:**
  - SQLite file: `FreshBytes/db.sqlite3`.
  - Inspect with SQLite CLI or GUI tools.
- **Testing:**
  - Tests are in `api/tests.py`.
  - Run with `python manage.py test api`.

## Project Conventions
- **ID Generation:**
  - Custom PKs (e.g., `user_id`, `seller_id`) are generated in model `save()` methods.
- **Soft Deletes:**
  - Most models have `is_active` and `is_deleted` flags for soft deletion.
- **Timestamps:**
  - All models use `created_at` and `updated_at` fields.
- **Password Storage:**
  - Passwords are currently stored as plain text (security risk; see `User` model).
- **Promo Logic:**
  - Promo validation is handled in `PromoSerializer`.

## Integration Points
- **No external payment/shipping integrations yet.**
- **No authentication endpoints implemented; user management is custom.**

## Examples
- See `api/serializers.py` for DRF patterns and validation.
- See `api/models.py` for custom ID logic and model relationships.
- See `FreshBytes/ERD_Visual.md` for a full data model overview.

---


## Best Practices
- **Security:**
  - Always hash passwords before saving to the database. Never store plain text passwords.
  - Validate and sanitize all user input in serializers and views.
  - Use Django’s built-in authentication and permissions where possible, or document custom logic clearly.
- **Django REST Framework:**
  - Use `ModelSerializer` for standard CRUD, and override methods for custom validation or representation.
  - Prefer `SerializerMethodField` for computed or related fields.
  - Keep business logic out of serializers—use services in `api/services.py` for complex operations.
- **Migrations:**
  - Always create and apply migrations for model changes. Never edit the database schema manually.
  - Keep migration files in version control.
- **Testing:**
  - Write tests for all new endpoints and business logic in `api/tests.py`.
  - Use DRF’s APIClient for integration tests.
- **Code Style:**
  - Follow PEP8 and Django conventions for Python code.
  - Use descriptive variable and method names.
  - Document non-obvious logic with comments or docstrings.
- **Documentation:**
  - Update `FreshBytes/ERD_Visual.md` and this file when making significant changes to models or workflows.
  - Keep the README up to date with setup and usage instructions.

For new features, follow the patterns in `api/models.py` and `api/serializers.py`. Update the ERD and add tests in `api/tests.py` for all new business logic.
