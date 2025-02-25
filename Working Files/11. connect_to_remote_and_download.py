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
from datetime import datetime
import time
import os
import dbinfo
import pymysql


def stations_to_db(text, in_engine):
    stations = json.loads(text)

    print(type(stations), len(stations))
    
    for station in stations:
        print(type(station))

        #Obtain Position for cleaner SQL input
        position = station.get('position')

        #Format last_update string to SQL friendly format
        no_format_timestamp = station.get('last_update')
        timestamp_ms = int(no_format_timestamp)
        last_update_datetime = datetime.utcfromtimestamp(timestamp_ms / 1000)
        format_timestamp = last_update_datetime.strftime('%Y-%m-%d %H:%M:%S')

        with in_engine.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(sqla.text("""
                    INSERT INTO station (number, address, banking, bikestands, name, status, lat, lng)
                    VALUES (:number, :address, :banking, :bikestands, :name, :status, :lat, :lng);
                """), {
                    "number": station.get('number'),
                    "address": station.get('address'),
                    "banking": int(station.get('banking')),
                    "bikestands": int(station.get('bike_stands')),
                    "name": station.get('name'),
                    "status": station.get('status'),
                    "lat": position.get('lat'),
                    "lng": position.get('lng')
                })

                connection.execute(sqla.text("""
                    INSERT INTO availability (number, available_bikes, available_bike_stands, last_update)
                    VALUES (:number, :available_bikes, :available_bike_stands, :last_update);
                """), {
                    "number": station.get('number'),
                    "available_bikes": int(station.get('available_bikes')),
                    "available_bike_stands": int(station.get('available_bike_stands')),
                    "last_update": format_timestamp,
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
    transaction = connection.begin()
    try:
        connection.execute(sqla.text('''
            CREATE TABLE IF NOT EXISTS station (
                number INTEGER,                    
                address VARCHAR(256), 
                banking INTEGER,
                bikestands INTEGER,
                name VARCHAR(256),
                status VARCHAR(256),
                lat DOUBLE NOT NULL,
                lng DOUBLE NOT NULL
            );                        
            '''))
        
        connection.execute(sqla.text('''
            CREATE TABLE IF NOT EXISTS availability (
                number INTEGER,
                available_bikes INTEGER,
                available_bike_stands INTEGER,
                last_update DATETIME
            );                        
            '''))
        transaction.commit()
    except Exception as e:
                transaction.rollback()
                print('Error inserting:', e)

try:
    r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})
    stations_to_db(r.text, engine)
    
    with engine.connect() as connection:
        result = connection.execute(sqla.text("SHOW COLUMNS FROM station;"))
        rows = result.fetchall()

    print(rows) 
except:
    print(traceback.format_exc())