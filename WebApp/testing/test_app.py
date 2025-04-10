import unittest
import pytest
import json
from flask import Flask
from unittest.mock import patch, MagicMock
from WebApp.app import app
import pandas as pd

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True



    #Testing /api/stations endpoint
    @patch('WebApp.app.create_engine')
    def test_get_stations(self, mock_create_engine):
        '''
        Test /api/stations || Mock Database call to protect actual Database || Mock result supplied || Expect success code and matching parsed Data
        '''
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_connection = mock_engine.connect.return_value.__enter__.return_value

        sample_reply = [
            {'number': 1, 'name': 'test1', 'lat': 54.000, 'lng': -6},
            {'number': 2, 'name': 'test2', 'lat': 54.000, 'lng': -6}
        ]

        mock_result = MagicMock()

        mock_result.mappings.return_value = sample_reply
        mock_connection.execute.return_value = mock_result

        response = self.app.get('/api/stations')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data[0]['name'], 'test1')
        self.assertEqual(data[1]['name'], 'test2')

        mock_connection.execute.assert_called_once()



    #Testing /api/availability endpoint
    @patch('WebApp.app.create_engine')
    def test_get_availability(self, mock_create_engine):
        '''
        Test /api/availability || Mock Database call to protect actual Database || Mock result supplied || Expect success code and matching parsed Data
        '''
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_connection = mock_engine.connect.return_value.__enter__.return_value

        sample_reply = [
            {
                'number': 1,
                'bikestands': 20,
                'available_bike_stands': 5,
                'available_bikes': 15,
                'last_update': '2025-04-01T12:00:00'
            }
        ]

        mock_result = MagicMock()
        mock_result.mappings.return_value = sample_reply
        mock_connection.execute.return_value = mock_result

        response = self.app.get('/api/availability')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data[0]['available_bikes'], 15)



    #Testing /api/routes endpoint
    @patch('requests.post')
    def test_get_routes(self, mock_requests_post):
        '''
        Test /api/routes || Mock result supplied || Mock Request supplied || Expect success code and matching parsed Data || Checks URL call
        '''    
        sample_reply = {
            'encodedPolyline': 'abc123'
        }

        mock_response = MagicMock()
        mock_response.json.return_value = sample_reply
        mock_requests_post.return_value = mock_response

        sample_request = {
            'origin': {'lat': 54, 'lng': -6},
            'destination': {'lat': 53.5, 'lng': -6}
        }

        response = self.app.post('/api/routes',
                                 data=json.dumps(sample_request),
                                 content_type='application/json'
                                )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['encodedPolyline'], 'abc123')

        #Checking if the appropriate URL is called at least once
        mock_requests_post.assert_called_once()
        self.assertIn('https://routes.googleapis.com', mock_requests_post.call_args[0][0])



    #Testing /api/weather endpoint
    @patch('requests.get')
    def test_get_weather(self, mock_requests_get):
        '''
        Test /api/routes || Mock result supplied || Mock Request supplied || Expect success code and matching parsed Data || Checks URL call
        '''    
        sample_reply = '<xml>sample weather reply</xml>'

        mock_response = MagicMock()
        mock_response.text = sample_reply
        mock_requests_get.return_value = mock_response

        request_body = {
            'lat': '54.0',
            'lng': '-6.0',
            'time': '2025-04-01T12:00:00Z'
        }

        response = self.app.post('/api/weather',
                                 data=json.dumps(request_body),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('<xml>sample weather reply</xml>', response.data.decode('utf-8'))

        #Checking if URL was called
        mock_requests_get.assert_called_once()
        self.assertIn('metno-wdb2ts/locationforecast', mock_requests_get.call_args[0][0])



    #Testing /api/weather/icon endpoint
    @patch('requests.get')
    def test_get_weather_icon(self, mock_requests_get):
        '''
        Test /api/routes || Mock result supplied || Expect success code and matching parsed Data || Checks URL call
        '''    
        sample_reply = [
        {
            "name": "Dublin Airport",
            "temperature": "4",
            "symbol": "15n",
            "date": "09-04-2025",
            "reportTime": "00:00"
        },
        {
            "name": "Dublin Airport",
            "temperature": "3",
            "symbol": "15n",
            "date": "09-04-2025",
            "reportTime": "01:00"
        }
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = sample_reply
        mock_requests_get.return_value = mock_response

        response = self.app.post('/api/weather/icon', content_type='application/json')
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), '15n')

        mock_requests_get.assert_called_once()
        self.assertIn('https://prodapi.metweb.ie/observations/Dublin/today', mock_requests_get.call_args[0][0])
    


    #Testing /api/availability/prediction endpoint
    @patch('WebApp.app.get_weather_forecast')
    @patch('WebApp.app.construct_stations_datafile')
    def test_get_availability_prediction(self, mock_construct_stations_datafile, mock_get_weather_forecast):
        '''
        Test /api/routes || Mock df supplied || Mock forecast supplied || Mock query params supplied || Expects success code and parsed data correctly
        '''    
        mock_stations_df = pd.DataFrame([{
            'station_id': 42,
            'lat': 53.3498,
            'lng': -6.2603
        }])
        mock_construct_stations_datafile.return_value = mock_stations_df

        mock_weather_forecast = {
            'temperature': 15.0,
            'humidity': 80,
            'pressure': 1012
        }

        mock_get_weather_forecast.return_value = mock_weather_forecast

        query_params = {
            "date": "2025-04-01",
            "time": "09:00:00",
            "station_id": "42"
        }

        response = self.app.get('/api/availability/prediction', query_string=query_params)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn('predicted_available_bikes', data)
        self.assertEqual(data['weather'], mock_weather_forecast)

if __name__ == '__main__':
    unittest.main()