#!/usr/bin/env python3
"""
APIx India — Integrated Web Application & Live Scraping Server
Combines static asset serving with real-time REST endpoints:
  - GET /api/scrape-live     : Trigger automated scraping & deduplication cycle
  - GET /api/live-status     : Current live scraping telemetry & deduplication stats
  - GET /api/live-dataset    : Retrieve records from Dataset1/Live_Scraped_Dataset.csv
  - GET /api/cpi-data        : Retrieve official MoSPI CPI (07.3.3.1) time series
"""

import os
import sys
import json
import csv
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from scraper_engine import ScrapingEngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'Dataset1')
LIVE_CSV = os.path.join(DATASET_DIR, 'Live_Scraped_Dataset.csv')
CPI_JSON = os.path.join(DATASET_DIR, 'cpi_parsed_series.json')

engine = ScrapingEngine()

class APIxRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS and disable caching for API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API: Trigger live scraping cycle on page visit / poller
        if path == '/api/scrape-live':
            count = int(query.get('count', [24])[0])
            try:
                telemetry = engine.run_cycle(count=count)
                self.send_json_response(200, {
                    'status': 'success',
                    'message': f"Scraped {telemetry['latest_batch_summary']['total_scraped_in_batch']} quotes. Eliminated {telemetry['latest_batch_summary']['duplicates_eliminated_in_batch']} duplicates. Committed {telemetry['latest_batch_summary']['unique_records_retained']} clean unique records.",
                    'telemetry': telemetry
                })
            except Exception as e:
                self.send_json_response(500, {'status': 'error', 'message': str(e)})
            return

        # 2. API: Get current live scraping telemetry
        elif path == '/api/live-status':
            telemetry_path = os.path.join(DATASET_DIR, 'live_scraper_telemetry.json')
            if os.path.exists(telemetry_path):
                with open(telemetry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(200, data)
            else:
                self.send_json_response(200, {
                    'engine_status': 'INITIALIZING',
                    'total_unique_records_in_dataset': engine.total_records,
                    'historical_duplicates_eliminated': engine.duplicates_eliminated_historical
                })
            return

        # 3. API: Get records from Live_Scraped_Dataset.csv
        elif path == '/api/live-dataset':
            limit = int(query.get('limit', [100])[0])
            carrier = query.get('carrier', ['ALL'])[0]
            records = []
            if os.path.exists(LIVE_CSV):
                with open(LIVE_CSV, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if carrier == 'ALL' or r.get('airline') == carrier:
                            records.append(r)
            
            # Return most recent records first
            records.reverse()
            self.send_json_response(200, {
                'total': len(records),
                'returned': len(records[:limit]),
                'records': records[:limit]
            })
            return

        # 4. API: Get official MoSPI CPI dataset
        elif path == '/api/cpi-data':
            if os.path.exists(CPI_JSON):
                with open(CPI_JSON, 'r', encoding='utf-8') as f:
                    cpi_data = json.load(f)
                self.send_json_response(200, cpi_data)
            else:
                self.send_json_response(404, {'status': 'error', 'message': 'CPI dataset not parsed yet'})
            return

        # Default: Serve static files
        super().do_GET()

    def send_json_response(self, code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(body)

def run(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIxRequestHandler)
    print(f"APIx India Server running at http://localhost:{port}/")
    print("Endpoints:")
    print(f"  - Web App:      http://localhost:{port}/index.html")
    print(f"  - Scrape API:   http://localhost:{port}/api/scrape-live")
    print(f"  - Telemetry:    http://localhost:{port}/api/live-status")
    print(f"  - Live Dataset: http://localhost:{port}/api/live-dataset")
    print(f"  - MoSPI CPI:    http://localhost:{port}/api/cpi-data")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port=port)
