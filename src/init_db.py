import mysql.connector
from mysql.connector import Error
import os

def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created successfully.")
    except Error as e:
        print(f"Error creating database: {e}")

def create_tables(cursor, sql_statements):
    try:
        for statement in sql_statements.split(';'):
            if statement.strip():
                cursor.execute(statement)
        print("Tables created successfully.")
    except Error as e:
        print(f"Error creating tables: {e}")

def main():
    db_name = "test"
    schema_file = "createdb.sql"
    
    # Check if the schema file exists
    if not os.path.exists(schema_file):
        print(f"Error: Schema file '{schema_file}' not found.")
        return

    # Read the SQL schema from file
    sql_statements = read_sql_file(schema_file)

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_username",
            password="your_password"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create the database
            create_database(cursor, db_name)
            
            # Switch to the new database
            cursor.execute(f"USE {db_name}")
            
            # Create tables
            create_tables(cursor, sql_statements)
            
            # Commit changes
            connection.commit()
            
            # Verify table creation
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("Tables in the database:")
            for table in tables:
                print(table[0])
                
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    main()