import sqlalchemy as sqla
from sqlalchemy import create_engine
import pymysql

USER = "denissemenov"
PASSWORD = "897641579123"
PORT = "3306"
DB = "dbbikes"
URI = "127.0.0.1"

connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)

engine = create_engine(connection_string, echo = True)

with engine.connect() as connection:
    result = connection.execute(sqla.text("SELECT COUNT(*) from station;"))
    num_stations = result.fetchall()
    print('The number of stations is {}'.format(num_stations[0][0]))

    result = connection.execute(sqla.text("SELECT * FROM station where address = 'Smithfield North';"))
    print(result.fetchall())

    connection.execute(sqla.text("CREATE TABLE temp_station AS SELECT DISTINCT * FROM station;"))
    connection.execute(sqla.text("DROP TABLE station;"))
    connection.execute(sqla.text("RENAME TABLE temp_station TO station;"))

    result = connection.execute(sqla.text("SELECT * FROM station where address = 'Smithfield North';"))
    print(result.fetchall())

    result = connection.execute(sqla.text("SELECT * FROM station where bikestands > 20;"))
    print(result.fetchall())