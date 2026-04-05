import asyncio
import requests
import xmltodict
from utils.station_code_unpacker import unpack_station_codes

class TFLService:
    def __init__(self, client):
        self.client = client

    async def get_station_data(self, station_code):
        predicitons = await self.client.fetch_all_predictions(station_code)
        status = await self.client.get_line_status_from_prediction()

        return (predicitons, status)

    def get_station_codes(self):
        return unpack_station_codes()