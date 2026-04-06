from flask import Flask, jsonify
from flask_caching import Cache
from services.tfl_service import TFLService
from services.tfl_client import TFLClient
from utils.response_shaper import response_shaper
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = TFLClient(
    base_url="https://api.tfl.gov.uk",
    api_key=os.getenv("API_KEY"),
    line_codes=[
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
)

service = TFLService(client)

cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

@app.route('/get_station_info/<station_code>')
@cache.cached(timeout=30, key_prefix='station_%s') # 30 second cache, station data changes frequently
def get_station_data(station_code):

    station_code = station_code.upper()
    if not service.check_station_code_validity(station_code):
        return jsonify({"error": "Invalid station code"})

    predictions, statuses = asyncio.run(
        service.get_station_data(station_code)
    )

    shaped_response = response_shaper(predictions, statuses)

    return jsonify(shaped_response)

@app.route('/get_station_codes')
@cache.cached(timeout=86400) # 24 hour cache, station codes are mostly static
def get_station_codes():
    return jsonify(service.get_station_codes())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)