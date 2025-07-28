import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_root_swagger_docs():
    """Test that Swagger UI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_root_redoc_docs():
    """Test that ReDoc documentation is available."""
    response = client.get("/redoc")
    assert response.status_code == 200

def test_root_openapi_docs():
    """Test that OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
