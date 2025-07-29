# Shopping List Backend

Web application for shopping lists

Project under development

## Getting Started

### Prerequisites
- Python 3.12+
- uv (for dependency management)

### Installation

1. Clone the repository
2. Install dependencies using uv:
```bash
uv sync
```

### Running the Application

For development (with auto-reload):
```bash
uv run uvicorn app.main:app --host localhost --port 8000 --reload
```

For production:
```bash
uv run uvicorn app.main:app --host localhost --port 8000
```

You can also run it directly if uvicorn is installed globally:
```bash
# Development
uvicorn app.main:app --host localhost --port 8000 --reload

# Production
uvicorn app.main:app --host localhost --port 8000
```

The API will be available at `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Running Tests

To run the tests, first install the test dependencies:

```bash
pip install -r requirements-test.txt
```

Then run the tests using pytest:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=app --cov-report=html
```

## Project Structure

```
app/
├── data/           # Database connection and setup
├── models.py       # Database models
├── main.py         # FastAPI application entry point
├── routers/        # API route definitions
├── service/        # Business logic
tests/
├── conftest.py     # pytest configuration and fixtures
├── test_main.py    # Tests for main application
├── test_models.py  # Tests for database models
├── test_user_service.py          # Tests for user service
├── test_shoppinglist_service.py  # Tests for shopping list service
├── test_userlistpermission_service.py  # Tests for user list permission service
├── test_user_router.py           # Tests for user API routes
├── test_shoppinglist_router.py   # Tests for shopping list API routes
├── test_userlistpermission_router.py  # Tests for user list permission API routes
```

## API Endpoints

### User Endpoints
- `GET /user/` - Get all users
- `GET /user/{user_id}` - Get a user by ID
- `POST /user/` - Create a new user
- `PATCH /user/{user_id}` - Update a user
- `DELETE /user/{user_id}` - Delete a user
- `GET /user/{user_id}/lists` - Get shopping lists for a user

### Shopping List Endpoints
- `GET /shoppinglist/` - Get all shopping lists
- `GET /shoppinglist/{list_id}` - Get a shopping list by ID
- `POST /shoppinglist/` - Create a new shopping list
- `PATCH /shoppinglist/{list_id}` - Update a shopping list
- `DELETE /shoppinglist/{list_id}` - Delete a shopping list
- `GET /shoppinglist/{list_id}/items` - Get items in a shopping list
- `POST /shoppinglist/{list_id}/items` - Add an item to a shopping list

### User List Permission Endpoints
- `GET /listperm/check` - Check if a user has access to a list
- `POST /listperm/` - Grant a user access to a list
- `DELETE /listperm/` - Revoke a user's access to a list
