import mysql.connector
import os
import sys

sys.path.append(os.path.abspath("../Colorize"))
from Colorize import Colorize


"""TiDB connection class"""
PASS = os.getenv("TIDB_PASS")


class TiDB:
    """Do basic CRUD operations."""

    def __init__(
        self, password: str = PASS, database: str = "", autocommit: bool = True
    ):
        self.color = Colorize()
        try:
            self.connection = mysql.connector.connect(
                host="gateway01.us-east-1.prod.aws.tidbcloud.com",
                port=4000,
                user="2s5azfALGtC83jk.root",
                password=password,
                ssl_ca="/etc/ssl/cert.pem",
                ssl_verify_cert=True,
                ssl_verify_identity=True,
                autocommit=autocommit,
                connection_timeout=3000,
            )
            self.database = None
            if database:
                self.connection.database = database
                self.database = database
        except mysql.connector.Error as err:
            print(
                self.color.error(f"Something went wrong connecting to database: {err}")
            )

    def get_connection(self):
        return self.connection

    def close(self):
        self.connection.close()

    def use(self, database_name: None):
        """Without an argument, return name of current database. With argument, use it."""
        if database_name is None:
            return self.database
        try:
            self.connection.database = database_name
            self.database = database_name
            return True
        except mysql.connector.Error as err:
            print(
                self.color.error(
                    f"Something went wrong switching to database {database_name}: {err}"
                )
            )
            return False

    def execute_query(self, query):
        try:
            with self.connection.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
            return result
        except mysql.connector.Error as err:
            raise ValueError(f"Error executing query: {err}\nQuery:\n{query}")

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()
