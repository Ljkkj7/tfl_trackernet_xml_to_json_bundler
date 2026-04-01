# TFL Aggregator

## Description

This is a Flask application that aggregates data from the Transport for London (TFL) API. 

It converts the XML data from the API into a more digestable JSON format and returns it to the user.

It serves a purpose to bring the useful TrackerNet legacy API into a more modern format.

At the moment - It only serves information about current arrivals at each platform at the station. In future I plan to add bundled detailed arrival information inside a different endpoint & JSON object.

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

- `API_KEY` - Your TFL API key
- It is free to register for an API key at [TFL API](https://api.tfl.gov.uk/)

## Usage

```bash
python core.py
```

## API Endpoints

- `GET /get_station_info/<station_code>` - Get live prediction information for all lines & platforms at a given station on the underground

## Station Codes

- All station codes can be found in the TFL API documentation.
[Trackernet Data Services Guide](https://content.tfl.gov.uk/trackernet-data-services-guide-beta.pdf)

- They also can be found in this github Gist - Credit: kutraschke
[TFL Station Codes](https://gist.github.com/kurtraschke/b5ae285f0dc0c196952b2d0ef17f2484)  