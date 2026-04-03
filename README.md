# TfL Trackernet XML-to-JSON Bundler

A Flask REST API that aggregates live London Underground train prediction data from TfL's legacy Trackernet XML API, parsing and transforming multi-line XML responses into a single, clean JSON payload per station.

Built as a backend portfolio project demonstrating real-world API integration, XML parsing, and response shaping.

---

## Overview

TfL's Trackernet API exposes train prediction and line status data as XML — one request per Underground line. This service abstracts that complexity behind a single endpoint: pass in a station code and receive a unified JSON object containing live train predictions and current line statuses for every line serving that station.

---

## Features

- **Multi-line aggregation** — fans out requests across all 10 Underground line codes and collects valid responses
- **XML-to-JSON transformation** — parses TfL's XML responses using `xmltodict` and extracts relevant fields
- **Line status correlation** — fetches the TfL LineStatus feed and cross-references it against the lines serving the queried station
- **Response shaping** — maps predictions and statuses into a structured, frontend-ready JSON schema
- **Graceful error handling** — skips non-200 responses and request exceptions without crashing, logging failures per line

---

## Tech Stack

| Layer         | Technology         |
| ------------- | ------------------ |
| Web framework | Flask              |
| HTTP client   | `requests`         |
| XML parsing   | `xmltodict`        |
| Config        | `python-dotenv`    |
| Data source   | TfL Trackernet API |

---

## Getting Started

### Prerequisites

- Python 3.8+
- A [TfL API key](https://api-portal.tfl.gov.uk/)

### Installation

```bash
git clone https://github.com/Ljkkj7/tfl_trackernet_xml_to_json_bundler.git
cd tfl_trackernet_xml_to_json_bundler
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
API_KEY=your_tfl_api_key_here
```

### Running the server

```bash
python app.py
```

The server runs on `http://localhost:5000` by default.

---

## API Reference

### `GET /get_station_info/<station_code>`

Returns aggregated live train predictions and line statuses for a given station.

**Parameters**

| Parameter      | Type     | Description                                           |
| -------------- | -------- | ----------------------------------------------------- |
| `station_code` | `string` | TfL Trackernet station code (e.g. `RAT` for Waterloo) |

**Example Request**

```
GET /get_station_info/RAT
```

**Example Response**

```json
{
  "station": "Waterloo",
  "last_updated": "14:32:05",
  "lines": [
    {
      "name": "Jubilee",
      "status": "Good Service",
      "status_details": null,
      "platforms": [
        {
          "platform": "Eastbound",
          "trains": [
            {
              "destination": "Stratford",
              "current_position": "At Platform",
              "eta_seconds": "45"
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Architecture

```
GET /get_station_info/<station_code>
        │
        ▼
 APIBundle.run_bundler()
        │
        ├── get_prediction_detailed(station_code)
        │       └── Iterates all 10 line codes
        │           └── Calls /trackernet/PredictionDetailed/{line}/{station}
        │           └── Parses XML → extracts ROOT fields
        │
        ├── get_line_status_from_prediction()
        │       └── Calls /trackernet/LineStatus
        │       └── Filters statuses to lines serving this station
        │
        └── jsonify_response_shaper(predictions, statuses)
                └── Merges predictions + statuses into unified schema
                └── Returns Flask jsonify() response
```

---

## Notes

- Station codes follow TfL's Trackernet convention (not the same as the main TfL Unified API codes)
- Requests use a 2-second timeout per line to avoid hanging on non-serving lines
- If a line does not serve the queried station, TfL returns a non-200 response — these are skipped silently

---

## Planned Improvements

- [ ] Add caching layer (e.g. Flask-Caching or Redis) to reduce redundant Trackernet calls
- [ ] Expose a `/lines` endpoint listing all valid line codes
- [ ] Add a `/stations` endpoint for station code lookup
- [x] Migrate to async requests (e.g. `httpx` with `asyncio`) to parallelise the 10 per-line calls
- [ ] Containerise with Docker

---

## Related Projects

This API is intended to serve as the backend for a React Native mobile app providing a unified live departure view for London Underground stations — currently in development.

---

## License

MIT

---

## Station Codes

- All station codes can be found in the TFL API documentation.
  [Trackernet Data Services Guide](https://content.tfl.gov.uk/trackernet-data-services-guide-beta.pdf)

- They also can be found in this github Gist - Credit: kutraschke
  [TFL Station Codes](https://gist.github.com/kurtraschke/b5ae285f0dc0c196952b2d0ef17f2484)
