import sqlalchemy as sqla
from sqlalchemy import create_engine
import traceback
import glob
import os
from pprint import pprint
import simplejson as json
import requests
import time
from IPython.display import display
import traceback
import datetime
import time
import os
import dbinfo
import pymysql


def stations_to_db(text, in_engine):
    stations = json.loads(text)

    print(type(stations), len(stations))
    
    for station in stations:
        print(type(station))

        with in_engine.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(sqla.text("""
                    INSERT INTO station (address, banking, bikestands, name, status)
                    VALUES (:address, :banking, :bikestands, :name, :status);
                """), {
                    "address": station.get('address'),
                    "banking": int(station.get('banking')),
                    "bikestands": int(station.get('bike_stands')),
                    "name": station.get('name'),
                    "status": station.get('status'),
                })
                transaction.commit()
            except Exception as e:
                transaction.rollback()
                print('Error inserting:', e)

USER = "denissemenov"
PASSWORD = "897641579123"
PORT = "3306"
DB = "dbbikes"
URI = "127.0.0.1"

connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)

engine = create_engine(connection_string, echo = True)

with engine.connect() as connection:
    connection.execute(sqla.text("CREATE DATABASE IF NOT EXISTS dbbikes"))

    connection.execute(sqla.text('''
        CREATE TABLE IF NOT EXISTS station (
        address VARCHAR(256), 
        banking INTEGER,
        bikestands INTEGER,
        name VARCHAR(256),
        status VARCHAR(256));
        '''))

try:
    r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})
    stations_to_db(r.text, engine)
    
    with engine.connect() as connection:
        result = connection.execute(sqla.text("SHOW COLUMNS FROM station;"))
        rows = result.fetchall()

    print(rows) 
except:
    print(traceback.format_exc())