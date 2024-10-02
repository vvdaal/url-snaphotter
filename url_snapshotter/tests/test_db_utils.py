import pytest
import os
from db_utils import DatabaseManager
from logger_utils import setup_logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

@pytest.fixture
def db_manager():
    """Fixture to initialize the DatabaseManager with an in-memory database."""
    # Set the environment variable to use an in-memory database for testing
    os.environ['USE_IN_MEMORY_DB'] = 'true'
    
    # Initialize the logger in debug mode
    logger = setup_logger(debug=True)
    logger.debug("Initializing DatabaseManager with in-memory SQLite database")

    # Initialize the DatabaseManager
    db_manager = DatabaseManager()
    
    # Cleanup: Clear the environment variable after tests
    yield db_manager

    del os.environ['USE_IN_MEMORY_DB']

def test_tables_exist(db_manager):
    """Test that the required tables exist in the database."""
    session = db_manager.get_session()
    
    try:
        # Use the engine to create a connection and execute the query
        with db_manager.engine.connect() as connection:
            # Check if 'snapshots' table exists
            result = connection.execute(text("SELECT 1 FROM snapshots LIMIT 1"))
            assert result.fetchone() is not None, "Table 'snapshots' was not created or accessible"
            
            # Check if 'url_snapshots' table exists
            result = connection.execute(text("SELECT 1 FROM url_snapshots LIMIT 1"))
            assert result.fetchone() is not None, "Table 'url_snapshots' was not created or accessible"
            
    except SQLAlchemyError as e:
        # If an error occurs (table not existing), the test will fail with the error message
        pytest.fail(f"Tables not found or accessible: {e}")
    finally:
        session.close()
