import requests
import xmltodict
import asyncio
import aiohttp
from aiohttp import ClientSession
from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from station_codes import unpack_station_codes

load_dotenv()

app = Flask(__name__)

class APIBundle:
    def __init__(self):
        '''
        Initialises the APIBundle class.
        Sets the base URL, API key, line codes, and an empty dictionary array.
        '''
        self.base_url = 'https://api.tfl.gov.uk'
        self.api_key = os.getenv('API_KEY')
        self.line_codes = [
            'B',
            'C',
            'D',
            'H',
            'J',
            'M',
            'N',
            'P',
            'V',
            'W'
        ]

    async def get_prediction_detailed(self, station_code):
        '''
        Fetches prediction data for all lines serving the given station.
        '''

        self.dict_array = []
        
        async with ClientSession() as session:

            # Create list of tasks to run concurrently
            tasks = [
                self._fetch_prediction(session, line_code, station_code)
                for line_code in self.line_codes
            ]

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)
            self.dict_array = [r for r in results if r is not None]
        return self.dict_array
    
    async def _fetch_prediction(self, session, line_code, station_code):
        '''
        Fetches prediction data for a single line serving the given station.
        '''
        url = f'{self.base_url}/trackernet/PredictionDetailed/{line_code}/{station_code}?app_key={self.api_key}'
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                if response.status == 200:
                    content = await response.read()
                    parsed_xml = xmltodict.parse(content)
                    root = parsed_xml.get('ROOT', {})
                    return {
                        'Line': root.get('Line'),
                        'LineName': root.get('LineName'),
                        'WhenCreated': root.get('WhenCreated'),
                        'Station': root.get('S')
                    }
                else:
                    print(f'Skipping: {line_code} - {response.status}')
        except Exception as e:
            print(f'Request Failed: {line_code} - Timeout')
        return None

    def get_line_status_from_prediction(self):
        '''
        Fetches line status data for all lines serving the given station.
        '''

        self.line_status_array = []

        try:
            response = requests.get(f'{self.base_url}/trackernet/LineStatus?app_key={self.api_key}', timeout=2)              
            if response.status_code == 200:
                parsed_xml = xmltodict.parse(response.content)
                print(parsed_xml.keys())
                root = parsed_xml.get('ArrayOfLineStatus', {})

                cleaned_data = {
                    'LineStatus' : root.get('LineStatus')
                }

                station_lines = []

                for item in self.dict_array:
                    if item['LineName'] == 'Circle, Hammersmith & City Line':
                        station_lines.append('Circle')
                        station_lines.append('Hammersmith & City')
                    else:
                        station_lines.append(item['LineName'].replace(' Line', ''))

                print(station_lines)

                # Iterate over line status and only append if line name matches
                for item in cleaned_data['LineStatus']:
                    print(item['Line']['@Name'], station_lines)
                    if item['Line']['@Name'] in station_lines:
                        self.line_status_array.append(item)
           
            else:
                print(f'Skipping: {response.status_code}')
        except requests.exceptions.RequestException as e:
            print(f'Request Failed: {e}')
        return self.line_status_array
    
    def jsonify_response_shaper(self, predictions, statuses):
        '''
        Shapes the response into a JSON format.
        '''
        shaped_response = {
            "station": None,
            "last_updated": None,
            "lines": []
        }

        line_map = [{} for _ in range(len(statuses))]

        shaped_response["station"] = predictions[0]["Station"]["@N"]
        shaped_response["last_updated"] = predictions[0]["Station"]["@CurTime"]

        for i, line in enumerate(statuses):
            line_map[i]["name"] = line["Line"]["@Name"]
            line_map[i]["status"] = line["Status"]["@Description"]
            line_map[i]["status_details"] = line.get("@StatusDetails") or None
            line_map[i]["platforms"] = []
        
        shaped_response["lines"] = line_map

        for line_index, prediction in enumerate(predictions):
            platforms = prediction["Station"]["P"]
            platform_map = [{} for _ in range(len(platforms))]

            for platform_index, platform in enumerate(platforms):
                print(platform)
                trains = platform.get("T")

                if not trains:
                    continue

                if isinstance(trains, dict):
                    trains = [trains]

                train_map = [{} for _ in range(len(trains))]

                for train_index, train in enumerate(trains):
                    train_map[train_index]['destination'] = train.get('@Destination')
                    train_map[train_index]['current_position'] = train.get('@Location')
                    train_map[train_index]['eta_seconds'] = train.get('@SecondsTo')

                platform_map[platform_index]['platform'] = platform['@N']
                platform_map[platform_index]['trains'] = train_map
            
            if line_index < len(shaped_response['lines']):
                shaped_response['lines'][line_index]['platforms'] = platform_map
            else:
                break
        return shaped_response

    def get_station_codes(self):
        station_codes = unpack_station_codes()
        return jsonify(station_codes)


    def run_bundler(self, station_code):
        asyncio.run(self.get_prediction_detailed(station_code))
        self.get_line_status_from_prediction()
        response = self.jsonify_response_shaper(self.dict_array, self.line_status_array)
        return jsonify(response)


@app.route('/get_station_info/<station_code>')
def get_station_info(station_code):
    return APIBundle().run_bundler(station_code)

@app.route('/get_station_codes')
def get_station_codes():
    return APIBundle().get_station_codes()

if __name__ == '__main__':
    app.run(debug=True)