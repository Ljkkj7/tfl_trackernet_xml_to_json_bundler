import asyncio
import requests
import xmltodict
from utils.station_code_unpacker import unpack_station_codes

class TFLService:
    def __init__(self, client):
        self.client = client

    async def get_station_data(self, station_code):
        predictions = await self.client.fetch_all_predictions(station_code)
        status = self.client.get_line_status_from_prediction()

        return (predictions, status)

    def get_station_codes(self):
        return unpack_station_codes()

    def check_station_code_validity(self, station_code):
        return station_code in self.get_station_codes()