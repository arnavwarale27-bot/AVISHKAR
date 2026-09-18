#!/usr/bin/env python3
"""
APIx India — Supabase Data Seed & Sync Utility
Populates Supabase PostgreSQL tables with:
  1. MoSPI Domestic CPI (07.3.3.1) time-series from Dataset1/cpi_parsed_series.json
  2. Verified deduplicated live airfare quotes from Dataset1/Live_Scraped_Dataset.csv
  3. Historical scraping engine telemetry from Dataset1/live_scraper_telemetry.json

Usage:
  python3 seed_supabase.py --url https://<PROJECT_REF>.supabase.co --key <ANON_OR_SERVICE_KEY>
  Or set environment variables:
  export SUPABASE_URL=https://<PROJECT_REF>.supabase.co
  export SUPABASE_KEY=<ANON_OR_SERVICE_KEY>
  python3 seed_supabase.py
"""

import os
import sys
import csv
import json
import argparse
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'Dataset1')
CPI_JSON = os.path.join(DATASET_DIR, 'cpi_parsed_series.json')
LIVE_CSV = os.path.join(DATASET_DIR, 'Live_Scraped_Dataset.csv')
TELEMETRY_JSON = os.path.join(DATASET_DIR, 'live_scraper_telemetry.json')

def post_supabase(base_url, table, payload, key, on_conflict_header='resolution=ignore-duplicates'):
    """Sends an HTTP POST to Supabase PostgREST endpoint using standard library urllib."""
    url = f"{base_url.rstrip('/')}/rest/v1/{table}"
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'apikey': key,
        'Authorization': f"Bearer {key}",
        'Content-Type': 'application/json',
        'Prefer': f"{on_conflict_header}, return=minimal"
    }
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        return e.code, err_msg
    except Exception as e:
        return 500, str(e)

def seed_cpi(base_url, key):
    print("▶ Seeding MoSPI CPI Time Series (07.3.3.1)...")
    if not os.path.exists(CPI_JSON):
        print(f"  [!] Missing {CPI_JSON}")
        return 0

    with open(CPI_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    traj = data.get('national_trajectory', {})
    combined_list = traj.get('Combined', [])
    rural_dict = {item['ym']: item['index'] for item in traj.get('Rural', [])}
    urban_dict = {item['ym']: item['index'] for item in traj.get('Urban', [])}

    records = []
    for item in combined_list:
        ym = item['ym']
        records.append({
            'item_code': '07.3.3.1',
            'classification': 'Passenger transport by air, domestic',
            'year': item['year'],
            'month': item['month'],
            'month_num': item['month_num'],
            'ym': ym,
            'label': item['label'],
            'combined_index': float(item['index']),
            'combined_inflation_yoy': float(item['inflation_yoy']) if item.get('inflation_yoy') is not None else None,
            'rural_index': float(rural_dict.get(ym, 0)) if ym in rural_dict else None,
            'urban_index': float(urban_dict.get(ym, 0)) if ym in urban_dict else None
        })

    if not records:
        print("  [!] No CPI records found.")
        return 0

    code, resp = post_supabase(base_url, 'apix_cpi_series', records, key, on_conflict_header='resolution=merge-duplicates')
    if code in (200, 201, 204):
        print(f"  ✓ Successfully seeded {len(records)} MoSPI CPI monthly records into 'apix_cpi_series'!")
        return len(records)
    else:
        print(f"  [X] Failed seeding CPI (HTTP {code}): {resp}")
        return 0

def seed_quotes(base_url, key, batch_size=100):
    print("▶ Seeding Deduplicated Live Quotes from Live_Scraped_Dataset.csv...")
    if not os.path.exists(LIVE_CSV):
        print(f"  [!] Missing {LIVE_CSV}")
        return 0

    quotes = []
    with open(LIVE_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            quotes.append({
                'record_hash': r['record_hash'],
                'timestamp_utc': r['timestamp_utc'],
                'date_of_journey': r['date_of_journey'],
                'journey_day': r.get('journey_day', ''),
                'airline': r['airline'],
                'carrier_code': r.get('carrier_code', ''),
                'flight_code': r['flight_code'],
                'class': r['class'],
                'source': r['source'],
                'destination': r['destination'],
                'departure_time': r['departure_time'],
                'arrival_time': r['arrival_time'],
                'duration_hours': float(r['duration_hours']) if r.get('duration_hours') else None,
                'stops': r['stops'],
                'days_left': int(r['days_left']) if r.get('days_left') else None,
                'fare': float(r['fare']),
                'jevons_index': float(r['jevons_index']) if r.get('jevons_index') else None,
                'anomaly_status': r.get('anomaly_status', 'VALIDATED_NORMAL')
            })

    total = len(quotes)
    print(f"  Found {total} deduplicated quotes to sync in batches of {batch_size}...")

    synced = 0
    for i in range(0, total, batch_size):
        batch = quotes[i:i + batch_size]
        code, resp = post_supabase(base_url, 'apix_live_quotes', batch, key, on_conflict_header='resolution=ignore-duplicates')
        if code in (200, 201, 204):
            synced += len(batch)
            print(f"  • Batch {i // batch_size + 1}: synced {synced}/{total} quotes...")
        else:
            print(f"  [X] Batch {i // batch_size + 1} error (HTTP {code}): {resp}")

    print(f"  ✓ Finished quote sync: {synced}/{total} records processed into 'apix_live_quotes'.")
    return synced

def seed_telemetry(base_url, key):
    print("▶ Seeding Scraping Telemetry Audit Log...")
    if not os.path.exists(TELEMETRY_JSON):
        print(f"  [!] Missing {TELEMETRY_JSON}")
        return 0

    with open(TELEMETRY_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    batch = data.get('latest_batch_summary', {})
    econ = batch.get('econometrics', {})

    telemetry_record = [{
        'engine_status': data.get('engine_status', 'ACTIVE_STREAMING'),
        'quotes_scraped': batch.get('total_scraped_in_batch', 48),
        'duplicates_eliminated': batch.get('duplicates_eliminated_in_batch', 0),
        'unique_committed': batch.get('unique_records_retained', 48),
        'deduplication_rate_pct': batch.get('deduplication_rate_pct', 0.0),
        'dutot_mean': econ.get('dutot_mean'),
        'jevons_geom_mean': econ.get('jevons_geom_mean'),
        'median_p50': econ.get('median_p50'),
        'iqr': econ.get('iqr'),
        'upper_fence': econ.get('upper_fence'),
        'anomalies_detected': econ.get('anomalies_detected', 0),
        'client_source': 'initial_dataset_seed'
    }]

    code, resp = post_supabase(base_url, 'apix_scraper_telemetry', telemetry_record, key)
    if code in (200, 201, 204):
        print("  ✓ Successfully logged initial telemetry into 'apix_scraper_telemetry'!")
        return 1
    else:
        print(f"  [X] Failed seeding telemetry (HTTP {code}): {resp}")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Seed Supabase PostgreSQL with APIx India Datasets")
    parser.add_argument('--url', help='Supabase Project URL (e.g. https://xyz.supabase.co)')
    parser.add_argument('--key', help='Supabase anon or service_role Key')
    args = parser.parse_args()

    supabase_url = args.url or os.environ.get('SUPABASE_URL')
    supabase_key = args.key or os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_ANON_KEY') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("=================================================================")
        print("APIx India — Supabase Seed Utility")
        print("=================================================================")
        print("Error: Missing SUPABASE_URL or SUPABASE_KEY.")
        print("\nPlease run with arguments or set environment variables:")
        print("  python3 seed_supabase.py --url https://<PROJECT_REF>.supabase.co --key <YOUR_KEY>")
        print("Or:")
        print("  export SUPABASE_URL=https://<PROJECT_REF>.supabase.co")
        print("  export SUPABASE_KEY=<YOUR_KEY>")
        print("  python3 seed_supabase.py")
        print("=================================================================")
        sys.exit(1)

    print("=================================================================")
    print(f"Connecting to Supabase at: {supabase_url}")
    print("=================================================================")
    seed_cpi(supabase_url, supabase_key)
    print()
    seed_quotes(supabase_url, supabase_key)
    print()
    seed_telemetry(supabase_url, supabase_key)
    print()
    print("🎉 Supabase database seeding complete! You can view your tables in the Supabase Table Editor.")

if __name__ == '__main__':
    main()
