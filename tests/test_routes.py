import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


def test_health_check(client):
    """Test health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'


def test_query_missing_question(client):
    """Test query with missing question."""
    response = client.post('/query', json={})
    assert response.status_code == 400
    assert 'error' in response.json


def test_query_empty_question(client):
    """Test query with empty question."""
    response = client.post('/query', json={'question': ''})
    assert response.status_code == 400


def test_add_document_missing_document(client):
    """Test add-document with missing document."""
    response = client.post('/add-document', json={})
    assert response.status_code == 400
    assert 'error' in response.json


def test_add_document_empty_document(client):
    """Test add-document with empty document."""
    response = client.post('/add-document', json={'document': ''})
    assert response.status_code == 400
