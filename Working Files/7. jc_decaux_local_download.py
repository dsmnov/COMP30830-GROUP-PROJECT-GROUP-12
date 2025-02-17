import requests
import traceback
import datetime
import time
import os
import dbinfo

dir = "C:/Users/Denis/Desktop/Trimester_2/C30830 - Software Engineering/AmazonWS/data"

def write_to_file(text):
    if not os.path.exists(dir):
        os.makedirs(dir)
        print(f"Folder '{dir}' created!")
    else:
        print(f"Folder '{dir}' already exists.")

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    file_path = os.path.join(dir, f"bikes_{now}.txt")

    with open(file_path, "w") as f:
        f.write(text)

    print(f"File saved to: {file_path}")

def write_to_db(text):
    return 0

def main():
    while True:
        try:
            r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})
            print(r)
            write_to_file(r.text)
            time.sleep(5 * 60)
        except:
            print(traceback.format_exc())

main()
