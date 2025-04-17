# COMP30830 GROUP PROJECT

## File Structure Components and their areas of concern (Order as appearing in the file structure):

**'instance':** Instance Folder that is created by Flask Server, this folder holds instance storage - in our case it is utilized for the 'users.db' file.  
-> The 'users.db' file handles the storage of users, it is an SQLite implementation of a database and stored user ID | Usernaame | Hashed Password.

**'machine-learning':** Holds all relevant components of the machine-learning process.  
-> The 'dublinbikes_ml_model_analysis.ipynb' is the file used for the analysis of the machine learning model.  
-> The 'bike_availability_weather_model.pkl' is the output of the above file and holds the analysis machine learning model.
-> The 'bike_availability_model.ipynb' is the file used for the creation of the machine learning model - which is different to the weather_model, however we are using the output of this model as the output of the above model outputted 'undefined' variables sometimes.
-> The 'bike_availability_model.pkl' is the output of the above file and holds the machine learning model actually used within the project. 
-> The 'final_merged_data.csv' is the file used for training the machine learning model.

**'python-database':** Holds all relevant components for the Webscrapping code and database setup and access.  
-> The 'database_aio.py' is the file used for interacting with the database, it provides a simple UI to setup, create the database and tables, run the webscrapping service which automatically updates the Database and saves the data.  
-> The 'dbinfo.py' holds API details for the above file.

**'static':** contains the folders relevant to the storage of assets, css and javascript.  
-> 'assets' holds all images, logos, etc., for access and use within the webpage.  
-> 'css' holds all css files that are dynamically imported within the use of the webpage. This folder has a global section for global css import as well as webpage specific css.  
-> 'js' holds all css files for use within the webpages.

**'templates':** contains folders relating to HTML content for every webpage.  
-> 'global' contains the header and footer which are dynamically imported into every webpage following principles of modularity.  
-> 'user-system' contains the modals for registration and login as well as the dashboard.  
-> Others: HTML files for every webpage.

**'testing':** contains the testing files used for unittesting.  
-> '__init__.py' are related to the testing code and file location.

---

## VERY IMPORTANT! - Usage of this project:

-> 'database_aio.py' and 'app.py' files contain SQL connection code. In order for this to work on local systems, you must change the credentials to a user account that has full priveleged access.  

-> 'database_aio.py' when running the Webscrapper that updates the database, files are also downloaded at every updates, the path must be configured to a path on your system OR this code can be commented out to prevent file saving temporarily.  

-> 'app.py' around line 320-360 is contained code relating to loading the bike_availability_model.pkl, depending on whether you have Windows 10, 11 or MAC OS. There is a strange bug that the path must either be "WebApp/machine-learning/bike_availability_model.pkl" or "machine-learning/bike_availability_model.pkl", we don't know why this bug happens, its system to system dependant so if the file is not loaded, attempt either of these file paths.  

-> 'bike_availability_model.pkl' and 'final_merged_data.csv' are not present within this GITHUB repo, they are too large and GITHUB will not allow their upload. The solution we came up with is to store these files on a google drive, the link is here: https://drive.google.com/drive/folders/1lp6RyDldBqh7ppAaIqpgsWorD3jHPy02?usp=sharing the files must be placed in the 'machine-learning' folder. alternatively, if we have zipped the file and uploaded it to brightspace, all the files will be intact and this can be ignored.  

-> If any other problems occur, chances are, we have encountered it and fixed it. There have been bugs that are weird that depend on the system thats running the file if something like this is happening please email: denis.semenov@ucdconnect.ie and I will response as fast as I can.
