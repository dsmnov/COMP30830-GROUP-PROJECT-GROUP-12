import pymysql
from sqlalchemy import create_engine
import pandas as pd

DB_USER = "denissemenov"
DB_PASSWORD = "897641579123"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "dbbikes"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

query = "SELECT * FROM station"
df = pd.read_sql(query, engine)

print(df)

engine.dispose()



