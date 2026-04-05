import aiohttp
import xmltodict

class TFLClient:
    def __init__(self, base_url, api_key, line_codes):
        self.base_url = base_url
        self.api_key = api_key
        self.line_codes = line_codes

    async def get_prediction_detailed(self, station_code):
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
    
    async def fetch_all_predictions(self, station_code):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.get_prediction_detailed(line_code, station_code) 
                for line_code in self.line_codes
            ]
            results = await asyncio.gather(*tasks)
            return [result for result in results if result is not None]
