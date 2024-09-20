import pytest
from modules.database import Database

@pytest.fixture(scope='module')
def sqlite_db():
    db = Database()  # Assuming the default constructor works for an in-memory database
    yield db
    db.close_all_connections()

@pytest.fixture(scope='module')
def postgresql_db():
    db = Database()
    yield db
    db.close_all_connections()

def test_sqlite_query(sqlite_db):
    result = sqlite_db.execute_query('SELECT 1')
    assert result == [(1,)]  # Example assertion

def test_postgresql_query(postgresql_db):
    result = postgresql_db.execute_query('SELECT 1')
    assert result == [(1,)]  # Example assertion
