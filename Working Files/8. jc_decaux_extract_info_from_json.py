import requests
import traceback
import datetime
import time
import os
import dbinfo
import json
from sqlalchemy import create_engine

def stations_to_db(text):
    stations = json.loads(text)

    print(type(stations), len(stations))
    
    for station in stations:
        print(type(station))

        vals = (station.get('address'), int(station.get('banking')), int(station.get('bike_stands')), 
                station.get('name'), station.get('status'))
        print(vals)


def main():
    USER = "denissemenov"
    PASSWORD = "897641579123"
    PORT = "3306"
    DB = "dbbikes"
    URI = "127.0.0.1"

    connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)

    engine = create_engine(connection_string, echo = True)
    
    try:
        r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})
        stations_to_db(r.text)
        time.sleep(5*60)
    except:
        print(traceback.format_exc())

main()   