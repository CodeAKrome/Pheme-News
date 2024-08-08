import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


from TiDB import TiDB

# print("TiDB type:", type(TiDB))
# print("TiDB contents:", dir(TiDB))
# print("TiDB.__dict__:", TiDB.__dict__)

TESTDB_NAME = "test"
PASS = os.getenv("TIDB_PASS")


@pytest.fixture(scope="module")
def tidb_instance():
    db = TiDB(password=PASS, database=TESTDB_NAME)
    yield db
    db.close()

def test_initialization(tidb_instance):
    assert tidb_instance.connection is not None
    assert tidb_instance.database == TESTDB_NAME

def test_get_connection(tidb_instance):
    assert tidb_instance.get_connection() is not None

def test_use_without_argument(tidb_instance):
    assert tidb_instance.use(None) == TESTDB_NAME

def test_use_with_argument(tidb_instance):
    new_db_name = "test_new_db"
    tidb_instance.execute_query(f"CREATE DATABASE IF NOT EXISTS {new_db_name}")
    assert tidb_instance.use(new_db_name) == True
    assert tidb_instance.database == new_db_name
    tidb_instance.use(TESTDB_NAME)  # Switch back to original database
    tidb_instance.execute_query(f"DROP DATABASE IF EXISTS {new_db_name}")

def test_use_with_nonexistent_db(tidb_instance):
    assert tidb_instance.use("nonexistent_db") == False

def test_execute_query_success(tidb_instance):
    tidb_instance.execute_query("CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY, name VARCHAR(50))")
    tidb_instance.execute_query("INSERT INTO test_table (id, name) VALUES (1, 'Test Name')")
    result = tidb_instance.execute_query("SELECT * FROM test_table WHERE id = 1")
    assert result == [(1, 'Test Name')]
    tidb_instance.execute_query("DROP TABLE test_table")

def test_execute_query_error(tidb_instance):
    with pytest.raises(ValueError, match="Error executing query:"):
        tidb_instance.execute_query("SELECT * FROM non_existent_table")

def test_commit_and_rollback(tidb_instance):
    tidb_instance.execute_query("CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY, name VARCHAR(50))")
    
    # Test commit
    tidb_instance.connection.autocommit = False
    tidb_instance.execute_query("INSERT INTO test_table (id, name) VALUES (1, 'Test Commit')")
    tidb_instance.commit()
    result = tidb_instance.execute_query("SELECT * FROM test_table WHERE id = 1")
    assert result == [(1, 'Test Commit')]
    
    # Test rollback
    tidb_instance.execute_query("INSERT INTO test_table (id, name) VALUES (2, 'Test Rollback')")
    tidb_instance.rollback()
    result = tidb_instance.execute_query("SELECT * FROM test_table WHERE id = 2")
    assert result == []
    
    tidb_instance.execute_query("DROP TABLE test_table")
    tidb_instance.connection.autocommit = True

def test_close(tidb_instance):
    tidb_instance.close()
    with pytest.raises(Exception):  # The exact exception might vary depending on the MySQL connector
        tidb_instance.execute_query("SELECT 1")
