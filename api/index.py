#!/usr/bin/env python3
"""
APIx India — Vercel Serverless Function Handler
Handles real-time cloud API requests on Vercel:
  - GET /api/scrape-live   : Executes corridor scraping & deduplication cycle
  - GET /api/live-status   : Returns current scraper telemetry and yield statistics
  - GET /api/live-dataset  : Fetches recent verified quotes from Supabase or local store
  - GET /api/cpi-data      : Returns official MoSPI CPI domestic airfare time series (07.3.3.1)
"""

import os
import sys
import json
import csv
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

# Add project root to sys.path so modules and datasets are discovered
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scraper_engine import ScrapingEngine, DATASET_DIR, LIVE_CSV, TELEMETRY_JSON

CPI_JSON = os.path.join(DATASET_DIR, 'cpi_parsed_series.json')

# Initialize persistent instance in serverless memory
engine = ScrapingEngine()

class handler(BaseHTTPRequestHandler):
    def end_headers(self):
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

        # 1. Endpoint: /api/scrape-live
        if path.endswith('/scrape-live') or path.endswith('/scrape_live'):
            count = int(query.get('count', [24])[0])
            try:
                telemetry = engine.run_cycle(count=count)
                self.send_json_response(200, {
                    'status': 'success',
                    'message': (
                        f"Scraped {telemetry['latest_batch_summary']['total_scraped_in_batch']} quotes. "
                        f"Eliminated {telemetry['latest_batch_summary']['duplicates_eliminated_in_batch']} duplicates. "
                        f"Stored {telemetry['latest_batch_summary']['unique_records_retained']} unique clean records."
                    ),
                    'telemetry': telemetry
                })
            except Exception as e:
                self.send_json_response(500, {'status': 'error', 'message': str(e)})
            return

        # 2. Endpoint: /api/live-status
        elif path.endswith('/live-status') or path.endswith('/live_status'):
            # If Supabase is connected, attempt to fetch live count
            if engine.supabase_url and engine.supabase_key:
                try:
                    url = f"{engine.supabase_url}/rest/v1/apix_scraper_telemetry?select=*&order=run_timestamp.desc&limit=1"
                    headers = {
                        'apikey': engine.supabase_key,
                        'Authorization': f"Bearer {engine.supabase_key}"
                    }
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        items = json.loads(resp.read().decode('utf-8'))
                        if items:
                            t_db = items[0]
                            self.send_json_response(200, {
                                'engine_status': 'ACTIVE_STREAMING',
                                'storage_backend': 'Supabase PostgreSQL Cloud',
                                'last_scrape_timestamp': t_db.get('run_timestamp'),
                                'total_unique_records_in_dataset': engine.total_records,
                                'historical_duplicates_eliminated': engine.duplicates_eliminated_historical,
                                'latest_telemetry': t_db
                            })
                            return
                except Exception:
                    pass

            # Fallback to local / tmp telemetry file
            target_file = engine.telemetry_json if os.path.exists(engine.telemetry_json) else TELEMETRY_JSON
            if os.path.exists(target_file):
                with open(target_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(200, data)
            else:
                self.send_json_response(200, {
                    'engine_status': 'ACTIVE_READY',
                    'storage_backend': 'Vercel Serverless Runtime',
                    'total_unique_records_in_dataset': engine.total_records,
                    'historical_duplicates_eliminated': engine.duplicates_eliminated_historical
                })
            return

        # 3. Endpoint: /api/live-dataset
        elif path.endswith('/live-dataset') or path.endswith('/live_dataset'):
            limit = min(int(query.get('limit', [100])[0]), 500)
            carrier = query.get('carrier', ['ALL'])[0]

            # Priority: Fetch from Supabase PostgreSQL if configured
            if engine.supabase_url and engine.supabase_key:
                try:
                    carrier_filter = f"&airline=eq.{urllib.parse.quote(carrier)}" if carrier != 'ALL' else ""
                    url = f"{engine.supabase_url}/rest/v1/apix_live_quotes?select=*&order=scraped_at.desc&limit={limit}{carrier_filter}"
                    headers = {
                        'apikey': engine.supabase_key,
                        'Authorization': f"Bearer {engine.supabase_key}"
                    }
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        records = json.loads(resp.read().decode('utf-8'))
                        self.send_json_response(200, {
                            'total': len(records),
                            'returned': len(records),
                            'source': 'Supabase PostgreSQL Cloud',
                            'records': records
                        })
                        return
                except Exception as e:
                    print(f"Supabase query fallback: {e}")

            # Fallback: Read from local CSV
            target_csv = engine.live_csv if os.path.exists(engine.live_csv) else LIVE_CSV
            records = []
            if os.path.exists(target_csv):
                with open(target_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if carrier == 'ALL' or r.get('airline') == carrier:
                            records.append(r)
            records.reverse()
            self.send_json_response(200, {
                'total': len(records),
                'returned': len(records[:limit]),
                'source': 'Local Runtime CSV',
                'records': records[:limit]
            })
            return

        # 4. Endpoint: /api/cpi-data
        elif path.endswith('/cpi-data') or path.endswith('/cpi_data'):
            cpi_path = os.path.join(DATASET_DIR, 'cpi_parsed_series.json')
            if os.path.exists(cpi_path):
                with open(cpi_path, 'r', encoding='utf-8') as f:
                    cpi_data = json.load(f)
                self.send_json_response(200, cpi_data)
            else:
                self.send_json_response(404, {'status': 'error', 'message': 'MoSPI CPI dataset not found'})
            return

        # Unmatched API route
        self.send_json_response(404, {
            'status': 'not_found',
            'available_endpoints': [
                '/api/scrape-live',
                '/api/live-status',
                '/api/live-dataset',
                '/api/cpi-data'
            ]
        })

    def send_json_response(self, code, data):
        body = json.dumps(data, default=str).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(body)
