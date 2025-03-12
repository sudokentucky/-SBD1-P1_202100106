# utils/db.py
import cx_Oracle

def get_connection():
    print('Connecting to the Oracle Database...')
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='XE')
    conn = cx_Oracle.connect(user='SYSTEM', password='1234E', dsn=dsn_tns)
    return conn
