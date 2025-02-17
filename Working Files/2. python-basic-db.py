import dbinfo
import requests
import pymysql
import sqlalchemy as sqla
from sqlalchemy import create_engine, text
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

connection_string = "mysql+pymysql://{}:{}@{}:{}".format(USER, PASSWORD, URI, PORT)

engine = create_engine(connection_string, echo = True)

sql = text(f"CREATE DATABASE IF NOT EXISTS {DB}")

with engine.connect() as connection:
    connection.execute(sql)

with engine.connect() as connection:
    result = connection.execute(text("SHOW VARIABLES;"))
    for row in result:
        print(row)
