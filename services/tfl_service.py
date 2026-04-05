import asyncio
import requests
import xmltodict

class TFLService:
    def __init__(self, client):
        self.client = client

    async def get_station_data(self, station_code):
        predicitons = await self.client.fetch_all_predictions(station_code)
        status = await self.client.get_line_status_from_prediction()

        print(predicitons)
        print(status)
        return (predicitons, status)