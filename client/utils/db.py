
import cx_Oracle

ORACLE_HOST = 'localhost'
ORACLE_PORT = '1521'
ORACLE_SERVICE = 'XEPDB1'
ORACLE_USER = 'SYSTEM'
ORACLE_PASSWORD = '1234E'

def get_connection():
    dsn = cx_Oracle.makedsn(ORACLE_HOST, ORACLE_PORT, serice_name = ORACLE_SERVICE)
    connect = cx_Oracle.connect(ORACLE_USER, ORACLE_PASSWORD, dsn)

    try:
        yield connect
    finally:
        connect.close()
    