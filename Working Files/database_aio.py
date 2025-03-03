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
from datetime import datetime, timezone
import time
import sys
import dbinfo
import pymysql

#My own local connection (Denis) - If you plan to run this code, modify the login details
USER = "denissemenov"
PASSWORD = "897641579123"
PORT = "3306"
DB = "dbbikes"
URI = "127.0.0.1"

#Connection string and engine to connect to database - reusable
connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)
engine = create_engine(connection_string, echo = True)

def create_db(engine):
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

def station_to_db(station_api, engine):
	stations = json.loads(station_api)

	print(type(stations), len(stations))
	
	for station in stations:
		print(type(station))

		#Obtain Position for cleaner SQL input
		position = station.get('position')

		with engine.connect() as connection:
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

				transaction.commit()
			except Exception as e:
				transaction.rollback()
				print('Error inserting:', e)

def availability_to_db(avail_api, engine):
	availability = json.loads(avail_api)
	timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	for station in availability:

		with engine.connect() as connection:
			try:
				transaction = connection.begin()

				connection.execute(sqla.text("""
					INSERT INTO availability (number, available_bikes, available_bike_stands, last_update)
					VALUES (:number, :available_bikes, :available_bike_stands, :last_update);
					"""), {
					"number": station.get('number'),
					"available_bikes": int(station.get('available_bikes')),
					"available_bike_stands": int(station.get('available_bike_stands')),
					"last_update": timestamp,
				})
				transaction.commit()
			except Exception as e:
				transaction.rollback()
				print('Error inserting: ', e)

#My own local directory (Denis) - If you plan to run this code, modify the directory
dir = "C:/Users/Denis/Desktop/Trimester_2/C30830 - Software Engineering/AmazonWS/data"
				
def write_to_file(text):
    if not os.path.exists(dir):
        os.makedirs(dir)
        print(f"Folder '{dir}' created!")
    else:
        print(f"Folder '{dir}' already exists.")

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(dir, f"bikes_{now}.txt")

    with open(file_path, "w") as f:
        f.write(text)

    print(f"File saved to: {file_path}")

def fetch_api():
	try:
		r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})
		return r.text
	except:
		print(traceback.format_exc())

def webscrape_to_db_and_download(engine):
	while True:
		try:
			data = fetch_api()
			write_to_file(data)
			availability_to_db(data, engine)
			time.sleep(5*60)
		except Exception as e:
			print('Error:', e)

def main():
	def interface():
		print('***********************************************')
		print('Database All-In-One interface')
		print('***********************************************')
		print('Actions:')
		print('    1. Create stations & availability tables')
		print('    2. Insert station data into database')
		print('    3. Start webscraper')
		print('    4. Exit programme')
		print('***********************************************')
		command = int(input('Select action: '))
		return command
	
	action = interface()
	data = fetch_api()

	while action != 3 and action != 4:
		if action == 1:
			create_db(engine)
			action = interface()
		elif action == 2:
			station_to_db(data, engine)
			action = interface()
	
	if action == 3:
		webscrape_to_db_and_download(engine)
	elif action == 4:
		print('Goodbye!')
		sys.exit(0)

main()