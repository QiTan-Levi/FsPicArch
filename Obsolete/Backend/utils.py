import pymysql as ysq
from configparser import ConfigParser


verification_codes = {}
mysql = None
fs = None

ConfigParser = ConfigParser()
ConfigParser.read('config.ini')

def init_db_connections():
    global mysql, mongodb, fs, ConfigParser
    data_host = ConfigParser.get('Database', 'Host')
    data_username = ConfigParser.get('Database', 'User')
    data_password = ConfigParser.get('Database', 'Password')
    data_databasename = ConfigParser.get('Database', 'Database')
    
    mysql = ysq.connect(
        host=data_host,
        user=data_username,
        password=data_password,
        database=data_databasename
    )
    

    return mysql

