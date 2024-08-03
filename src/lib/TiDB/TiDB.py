import mysql.connector
import os

TIDB_PASS = os.getenv('TIDB_PASS')

class TiDB:
    def __init__(self, autocommit:bool = True):
        self.connection = mysql.connector.connect(
            host="gateway01.us-east-1.prod.aws.tidbcloud.com",
            port=4000,
            user="2s5azfALGtC83jk.root",
            password=TIDB_PASS,
            database="test",
            ssl_ca="/etc/ssl/cert.pem",
            ssl_verify_cert=True,
            ssl_verify_identity=True
            autocommit=autocommit
        )
        
    def get_connection(self):
        return self.connection
    
    def close(self):
        self.connection.close()
        
    def execute_query(self, query):
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
        return result
    
    def commit(self):
        self.connection.commit()
        
    def rollback(self):
        self.connection.rollback()


# def test():
#     db = TiDB()
#     player = ("1", 1, 1)
#     db.execute_query("INSERT INTO players (id, coins, goods) VALUES (%s, %s, %s)", player)
    