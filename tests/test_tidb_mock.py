import pytest
import os
from unittest.mock import patch, MagicMock
import mysql.connector
from TiDB import TiDB, PASS, TESTDB_NAME

@pytest.fixture
def mock_connection():
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_conn

@pytest.fixture
def tidb_instance(mock_connection):
    return TiDB()

def test_initialization(tidb_instance, mock_connection):
    assert tidb_instance.connection == mock_connection
    assert tidb_instance.database is None

def test_initialization_with_database(mock_connection):
    tidb = TiDB(database="test_db")
    assert tidb.database == "test_db"
    assert mock_connection.database == "test_db"

def test_get_connection(tidb_instance, mock_connection):
    assert tidb_instance.get_connection() == mock_connection

def test_close(tidb_instance, mock_connection):
    tidb_instance.close()
    mock_connection.close.assert_called_once()

def test_use_without_argument(tidb_instance):
    tidb_instance.database = "current_db"
    assert tidb_instance.use(None) == "current_db"

def test_use_with_argument(tidb_instance, mock_connection):
    assert tidb_instance.use("new_db") == True
    assert tidb_instance.database == "new_db"
    assert mock_connection.database == "new_db"

def test_use_with_error(tidb_instance, mock_connection):
    mock_connection.database = MagicMock(side_effect=mysql.connector.Error("Test error"))
    assert tidb_instance.use("error_db") == False

def test_execute_query_success(tidb_instance, mock_connection):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("result1",), ("result2",)]
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    result = tidb_instance.execute_query("SELECT * FROM test_table")
    assert result == [("result1",), ("result2",)]

def test_execute_query_error(tidb_instance, mock_connection):
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = mysql.connector.Error("Test error")
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    with pytest.raises(ValueError, match="Error executing query: Test error"):
        tidb_instance.execute_query("SELECT * FROM non_existent_table")

def test_commit(tidb_instance, mock_connection):
    tidb_instance.commit()
    mock_connection.commit.assert_called_once()

def test_rollback(tidb_instance, mock_connection):
    tidb_instance.rollback()
    mock_connection.rollback.assert_called_once()

def test_initialization_error():
    with patch('mysql.connector.connect', side_effect=mysql.connector.Error("Connection error")):
        with pytest.raises(SystemExit):
            TiDB()