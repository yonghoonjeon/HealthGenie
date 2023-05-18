import psycopg2

def my_db_setting():  
    return psycopg2.connect(
    host = 'localhost', # find it from my_setting.spy in HealthGeinie directory
    database = 'pha',
    user = 'postgres',
    password = '0847')
