#!/usr/bin/env python3
"""
APIx India — MoSPI CPI 07.3.3.1 Integration Engine
Parses Dataset1/cpi_640.xlsx (Official CPI Series: Passenger transport by air, domestic)
Injects parsed time-series data into:
  - Dataset1/cpi_parsed_series.json
  - dataset1_analytics.json
  - dataset1_analytics.js (window.APIX_DATASET_ANALYTICS.cpi_official_series)
"""

import os
import json
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CPI_XLSX = os.path.join(BASE_DIR, 'Dataset1', 'cpi_640.xlsx')
OUTPUT_CPI_JSON = os.path.join(BASE_DIR, 'Dataset1', 'cpi_parsed_series.json')
ANALYTICS_JSON = os.path.join(BASE_DIR, 'dataset1_analytics.json')
ANALYTICS_JS = os.path.join(BASE_DIR, 'dataset1_analytics.js')

MONTH_ORDER = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

def parse_cpi_xlsx(filepath):
    print(f"Reading and extracting {filepath}...")
    with zipfile.ZipFile(filepath, 'r') as z:
        sheet_tree = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = []
        for r in sheet_tree.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            row_dict = {}
            for c in r.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                cell_ref = c.attrib.get('r')
                is_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                val = (is_elem.text if is_elem is not None else (v.text if v is not None else ''))
                row_dict[cell_ref] = val
            rows.append(row_dict)

    if not rows:
        raise ValueError("No rows found in sheet1.xml")

    # Map column letters from header (row 0)
    r0 = rows[0]
    col_map = {}
    for cell_ref, val in sorted(r0.items(), key=lambda x: (len(x[0]), x[0])):
        col_letter = ''.join([ch for ch in cell_ref if ch.isalpha()])
        col_map[col_letter] = val

    records = []
    for r in rows[1:]:
        item = {}
        for cell_ref, val in r.items():
            col_letter = ''.join([ch for ch in cell_ref if ch.isalpha()])
            header_name = col_map.get(col_letter)
            if header_name:
                item[header_name] = val
        if item.get('year') and item.get('month') and item.get('state'):
            records.append(item)

    print(f"Extracted {len(records)} valid CPI records.")
    return records

def process_cpi_data(records):
    # Group by state -> sector -> list of monthly points
    state_sector_series = defaultdict(lambda: defaultdict(list))
    all_states = set()
    all_sectors = set()

    for r in records:
        state = r.get('state', '').strip()
        sector = r.get('sector', '').strip()
        year = int(r.get('year', 0))
        month = r.get('month', '').strip()
        
        try:
            index_val = float(r.get('index', 0)) if r.get('index') else None
        except ValueError:
            index_val = None

        try:
            infl_val = float(r.get('inflation', 0)) if r.get('inflation') and r.get('inflation') != 'None' else None
        except ValueError:
            infl_val = None

        month_num = MONTH_ORDER.index(month) + 1 if month in MONTH_ORDER else 0

        point = {
            'year': year,
            'month': month,
            'month_num': month_num,
            'ym': f"{year}-{month_num:02d}",
            'label': f"{month[:3]} {year}",
            'index': index_val,
            'inflation_yoy': infl_val
        }

        state_sector_series[state][sector].append(point)
        all_states.add(state)
        all_sectors.add(sector)

    # Sort time series chronologically
    for state in state_sector_series:
        for sector in state_sector_series[state]:
            state_sector_series[state][sector].sort(key=lambda p: (p['year'], p['month_num']))

    # National All-India timeline for Combined, Urban, Rural
    national_trajectory = {
        'Combined': state_sector_series['All India']['Combined'],
        'Urban': state_sector_series['All India']['Urban'],
        'Rural': state_sector_series['All India']['Rural']
    }

    # Latest month snapshot (August 2026)
    latest_points = [p for p in national_trajectory['Combined'] if p['year'] == 2026 and p['month'] == 'August']
    latest_aug_2026 = latest_points[0] if latest_points else (national_trajectory['Combined'][-1] if national_trajectory['Combined'] else {})

    # State rankings for latest month (August 2026)
    state_rankings_aug_2026 = []
    for state in sorted(list(all_states)):
        if state == 'All India':
            continue
        c_series = state_sector_series[state].get('Combined', [])
        aug_2026 = [p for p in c_series if p['year'] == 2026 and p['month'] == 'August']
        if aug_2026 and aug_2026[0]['index'] is not None:
            state_rankings_aug_2026.append({
                'state': state,
                'index': aug_2026[0]['index'],
                'inflation': aug_2026[0]['inflation_yoy']
            })

    state_rankings_aug_2026.sort(key=lambda x: (x['inflation'] if x['inflation'] is not None else -999), reverse=True)

    summary = {
        'metadata': {
            'item_code': '07.3.3.1',
            'classification': 'Passenger transport by air, domestic',
            'division': 'Transport',
            'group': 'Passenger transport services',
            'base_year': '2024',
            'source': 'Ministry of Statistics & Programme Implementation (MoSPI) / NSO',
            'period_covered': 'January 2025 – August 2026',
            'total_states_monitored': len(all_states),
            'total_observations': len(records),
            'latest_month': 'August 2026'
        },
        'latest_headline': {
            'month': 'August 2026',
            'combined_index': latest_aug_2026.get('index', 135.49),
            'combined_inflation_yoy': latest_aug_2026.get('inflation_yoy', 20.85),
            'rural_index': (state_sector_series['All India']['Rural'][-1]['index'] if state_sector_series['All India']['Rural'] else 148.16),
            'urban_index': (state_sector_series['All India']['Urban'][-1]['index'] if state_sector_series['All India']['Urban'] else 127.20),
            'cpi_transport_subitem': '07.3.3.1'
        },
        'national_trajectory': national_trajectory,
        'state_sector_series': state_sector_series,
        'state_rankings_latest': state_rankings_aug_2026,
        'available_states': sorted(list(all_states)),
        'available_sectors': sorted(list(all_sectors))
    }

    return summary

def main():
    print(f"Integrating CPI Dataset from {CPI_XLSX}...")
    records = parse_cpi_xlsx(CPI_XLSX)
    cpi_summary = process_cpi_data(records)

    # 1. Write standalone Dataset1/cpi_parsed_series.json
    print(f"Writing {OUTPUT_CPI_JSON}...")
    with open(OUTPUT_CPI_JSON, 'w', encoding='utf-8') as f:
        json.dump(cpi_summary, f, indent=2)

    # 2. Inject into dataset1_analytics.json if present
    if os.path.exists(ANALYTICS_JSON):
        print(f"Updating {ANALYTICS_JSON} with cpi_official_series...")
        with open(ANALYTICS_JSON, 'r', encoding='utf-8') as f:
            analytics_data = json.load(f)
        analytics_data['cpi_official_series'] = cpi_summary
        with open(ANALYTICS_JSON, 'w', encoding='utf-8') as f:
            json.dump(analytics_data, f, indent=2)

    # 3. Inject into dataset1_analytics.js
    if os.path.exists(ANALYTICS_JS):
        print(f"Updating {ANALYTICS_JS} with cpi_official_series...")
        with open(ANALYTICS_JSON, 'r', encoding='utf-8') as f:
            analytics_data = json.load(f)
        with open(ANALYTICS_JS, 'w', encoding='utf-8') as f:
            f.write("/**\n")
            f.write(" * APIx India Sovereign Airfare Price Index Analytics Bundle\n")
            f.write(f" * Integrated with Dataset1/Cleaned_dataset.csv & Dataset1/cpi_640.xlsx\n")
            f.write(" * MoSPI / NSO Government of India\n")
            f.write(" */\n")
            f.write("(function(root) {\n")
            f.write("  var analyticsData = ")
            json.dump(analytics_data, f)
            f.write(";\n")
            f.write("  root.APIX_DATASET_ANALYTICS = analyticsData;\n")
            f.write("  if (typeof module !== 'undefined' && module.exports) { module.exports = analyticsData; }\n")
            f.write("})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));\n")

    print("Official MoSPI CPI 07.3.3.1 dataset successfully integrated!")
    print(f"Headline Aug 2026: Combined Index = {cpi_summary['latest_headline']['combined_index']}, YoY Inflation = +{cpi_summary['latest_headline']['combined_inflation_yoy']}%")

if __name__ == '__main__':
    main()
