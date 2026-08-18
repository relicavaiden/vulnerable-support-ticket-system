import pytest

from app import create_app

@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test.db"

    return create_app({
        "TESTING": True,
        "DATABASE": str(database_path),
        "SECRET_KEY": "test-secret-key",
    })