from flask import Flask, jsonify
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

@app.route('/get_station_info/<station_code>')
def get_station_data(station_code):

    station_code = station_code.upper()
    if not check_code_validity(station_code):
        return jsonify({"error": "Invalid station code"})

    predictions, statuses = asyncio.run(
        service.get_station_data(station_code)
    )

    shaped_response = response_shaper(predictions, statuses)

    return jsonify(shaped_response)

@app.route('/get_station_codes')
def get_station_codes():
    return jsonify(service.get_station_codes())

def check_code_validity(station_code):
    station_codes = service.get_station_codes()
    return station_code in station_codes

if __name__ == '__main__':
    app.run(debug=True)