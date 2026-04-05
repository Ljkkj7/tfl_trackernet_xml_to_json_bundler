import aiohttp
from aiohttp import ClientSession
import asyncio
import requests
import xmltodict

class TFLClient:
    def __init__(self, base_url, api_key, line_codes):
        self.base_url = base_url
        self.api_key = api_key
        self.line_codes = line_codes

    async def get_prediction_detailed(self, session, station_code, line_code):
        url = f'{self.base_url}/trackernet/PredictionDetailed/{line_code}/{station_code}'
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=4), headers={'app_key': self.api_key}) as response:
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
            print(f'Request Failed: {line_code} - {e}')
        return None
    
    async def fetch_all_predictions(self, station_code):

        self.dict_array = []

        async with ClientSession() as session:

            tasks = [
                self.get_prediction_detailed(session, station_code, line_code) 
                for line_code in self.line_codes
            ]
            results = await asyncio.gather(*tasks)
            print(results)
            self.dict_array = [result for result in results if result]

        print(self.dict_array)
        return self.dict_array

    def get_line_status_from_prediction(self):
        '''
        Fetches line status data for all lines serving the given station.
        '''

        self.line_status_array = []

        try:
            response = requests.get(f'{self.base_url}/trackernet/LineStatus', timeout=2, headers={'app_key': self.api_key})           
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
        except Exception as e:
            print(f'Request Failed: {e}')
        return self.line_status_array
