import cx_Oracle
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_service = os.getenv('DB_SERVICE')

    dsn_tns = cx_Oracle.makedsn(db_host, db_port, service_name=db_service)
    conn = cx_Oracle.connect(user=db_user, password=db_password, dsn=dsn_tns)
    return conn
