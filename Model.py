# %%
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib as plt
import joblib
import pickle

# %%
df=pd.read_csv("final_merged_data.csv")

# %%
df.info()

# %%
df.shape

# %%
df['day'].unique()


# %%
"""
#https://saturncloud.io/blog/pandas-get-day-of-week-from-date-type-column/#2
"""

# %%
df['date']=pd.to_datetime(df[['year','month','day']],errors='coerce')
print(df['date'])

# %%
# https://pandas.pydata.org/docs/reference/api/pandas.DatetimeIndex.dayofweek.html
df['day_of_week']=df['date'].dt.dayofweek

# %%
print(df['day_of_week'].unique())

# %%
df['is_weekday'] = df['day_of_week'].apply(lambda x: 0 if x < 5 else 1)

# %%
df['is_weekday'].unique()

# %%
"""
### Feature Selection for the model
- Windspeed and precipitation fields are missing
- Precipitation can be calculated by humidity and pressure levels
- But the precipitation value cannot be calculated accurately as it also requires additional features such as dew point, wind speed
- So these fields are not incorporated in the model 
"""

# %%
features=['station_id','max_air_temperature_celsius','max_relative_humidity_percent','hour','day_of_week']
target='num_bikes_available'


# %%
X = df[features]
y = df[target]

# %%
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# %%
model = LinearRegression()
model.fit(X_train, y_train)

# %%
y_pred = model.predict(X_test)

# %%
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")
print(f"R² Score: {r2}")

# %%
print("\nModel Coefficients:")
for feature, coef in zip(features, model.coef_):
    print(f"{feature}: {coef}")
print(f"Intercept: {model.intercept_}")

# %%
model_filename = "bike_availability_model.joblib"
joblib.dump(model, model_filename)

# %%
print(f"Model saved to {model_filename}")
model_filename = "bike_availability_model.pkl"
with open(model_filename, "wb") as file:
    pickle.dump(model, file)

print(f"Model saved to {model_filename}")

# %%
df['station_id'].unique()

# %%
"""
### Analysis of the model so far
- The r2 score is near to 0 and mean absolute error is very large
- Therefore also testing the random forest model
"""

# %%
regressor = RandomForestRegressor(n_estimators=100,random_state=0)
regressor = regressor.fit(X_train, y_train)
score = regressor.score( X_test,y_test)
score

# %%
y_pred_rf = regressor.predict(X_test)
mac = mean_absolute_error(y_test, y_pred_rf)
r2 = r2_score(y_test, y_pred_rf)
print(f"MAE: {mac}, R²: {r2}")

# Feature importances:
importances = regressor.feature_importances_
for feature, imp in zip(features, importances):
    print(f"{feature}: {imp}")

# %%
importances = regressor.feature_importances_
feature_imp_df = pd.DataFrame({'Feature': features, 'Gini Importance': importances}).sort_values('Gini Importance', ascending=False) 
print(feature_imp_df)


# %%
"""
### Analysis of Random Forest Regressor
- The r2 and mae values looks good
- Feature importance also looks good
- Better fit than linear

"""

# %%
