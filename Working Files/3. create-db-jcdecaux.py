import dbinfo
import requests
import json
import sqlalchemy as sqla
from sqlalchemy import create_engine
import traceback
import glob
import os
from pprint import pprint
import simplejson as json
import time
from IPython.display import display

USER = "denissemenov"
PASSWORD = "897641579123"
PORT = "3306"
DB = "dbbikes"
URI = "127.0.0.1"

connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{URI}:{PORT}/{DB}"

engine = create_engine(connection_string, echo=True)

with engine.connect() as connection:
    result = connection.execute(sqla.text("SHOW VARIABLES;"))
    for row in result:
        print(row)

    sql = """
    CREATE TABLE IF NOT EXISTS station (
        address VARCHAR(256), 
        banking INTEGER,
        bikestands INTEGER,
        name VARCHAR(256),
        status VARCHAR(256)
    );
    """
    connection.execute(sqla.text(sql))

    tab_structure = connection.execute(sqla.text("SHOW COLUMNS FROM station;"))
    columns = tab_structure.fetchall()
    print(columns)

    sql = """
    CREATE TABLE IF NOT EXISTS availability (
        number INTEGER,
        available_bikes INTEGER,
        available_bike_stands INTEGER,
        last_update DATETIME
    );
    """
    connection.execute(sqla.text(sql))
