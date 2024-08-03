import mysql.connector
import os

TIDB_PASS = os.getenv('TIDB_PASS')

connection = mysql.connector.connect(
  host = "gateway01.us-east-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "2s5azfALGtC83jk.root",
  password = TIDB_PASS,
  database = "test",
  ssl_ca = "/etc/ssl/cert.pem",
  ssl_verify_cert = True,
  ssl_verify_identity = True
)

