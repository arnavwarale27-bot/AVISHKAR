# APIx India — Technical Architecture, System Operations & Deployment Manual (`Working.md`)

This document provides a comprehensive technical breakdown of the **APIx India Sovereign Real-Time Airfare Price Index Platform**. It documents the complete system architecture, prerequisite packages, directory structure, code-level line references for every subsystem, local startup procedures, and complete instructions for cloud deployment to **Vercel**, **Supabase**, and **Production Linux VPS (Nginx + Systemd)**.

---

## 1. System Overview & Technology Stack

The platform is an institutional-grade macroeconomic price intelligence engine built for high-frequency tracking of domestic civil aviation passenger fares. It integrates historical microdata (452,088 quotes from Dataset1), recent official MoSPI Consumer Price Index data (`cpi_640.xlsx`, Item `07.3.3.1`), and an autonomous live web scraping and deduplication engine.

```
+-----------------------------------------------------------------------------------+
|                                  DATA SOURCES                                     |
|  [Dataset1/Cleaned_dataset.csv]      [Dataset1/cpi_640.xlsx]      [Live Scraper]  |
|         (452,088 quotes)               (MoSPI 07.3.3.1 CPI)       (Live Poller)   |
+------------------------+---------------------+-------------------+----------------+
                         |                     |                   |
                         v                     v                   v
+-----------------------------------------------------------------------------------+
|                            PYTHON ANALYTICS & ETL ENGINE                          |
|  - generate_dataset_analytics.py : Jevons/Dutot indexation, 5-tier stratification |
|  - integrate_cpi_data.py        : MoSPI 2025-2026 series (34 states x 3 sectors)  |
|  - scraper_engine.py            : SHA-256 canonical deduplication & live quotes  |
|  => Outputs: dataset1_analytics.json, dataset1_analytics.js, Live_Scraped_Dataset |
+-----------------------------------------------------------------------------------+
                         |
                         v
+-----------------------------------------------------------------------------------+
|                        LOCAL BACKEND / API SERVER (server.py)                     |
|  - Port 8080 HTTP & REST Router                                                   |
|  - GET /api/scrape-live  : Triggers live scraping cycle                           |
|  - GET /api/live-status  : Telemetry, deduplication rate, count                  |
|  - GET /api/live-dataset : Paginated records from Live_Scraped_Dataset.csv        |
|  - GET /api/cpi-data     : 20-month official MoSPI CPI series                     |
|  - Static File Server    : index.html, styles.css, app.js, assets/                |
+-----------------------------------------------------------------------------------+
                         |
                         v
+-----------------------------------------------------------------------------------+
|                            CLIENT FRONTEND (index.html)                           |
|  - Vanilla JavaScript Engine (app.js) with zero external CDN dependencies         |
|  - 5 Dynamic SVG Vector Charting Engines (Bézier splines, KDE, Cointegration)    |
|  - Live Streaming Microdata Ticker & Telemetry HUD                                |
|  - Interactive Econometric Fare Calculator & Dataset1 Microdata Explorer          |
|  - MoSPI 07.3.3.1 State/Sector Benchmark Explorer                                |
+-----------------------------------------------------------------------------------+
```

### Core Technologies
* **Backend Runtime**: Python 3.10+ (Standard Library: `http.server`, `urllib.parse`, `json`, `csv`, `hashlib`, `math`, `random`, `zipfile`).
* **Frontend Architecture**: Pure Vanilla ECMAScript 2022 (No React, Vue, Angular, or jQuery runtime overhead).
* **Styling & Design System**: Tailwind CSS (compiled institutional utility classes) + `styles.css` (JetBrains Mono tabular figures, glassmorphism, pulse keyframes, print styling).
* **Visualization Layer**: 100% Native SVG vector engines with cubic Bézier spline interpolation (`generateSmoothBezierPath`), gradient fills, dynamic scales, and hover tooltips (`#chart-tooltip`).
* **External Runtime Dependencies**: **Zero**. Runs on any standard POSIX Linux/macOS/Windows environment without requiring `npm install` or `pip install`.

---

## 2. System Prerequisites & Environment Setup

### 2.1 Linux Package Installation (`apt`)
On Debian/Ubuntu-based operating systems:

```bash
# Update package repositories
sudo apt update -y

# Install Python 3, Node.js (for syntax validation), curl, and build tools
sudo apt install -y python3 python3-pip nodejs git curl
```

Verify the environment:
```bash
python3 --version   # Python 3.10 or higher recommended
node --version      # v18.0 or higher recommended
curl --version      # curl 7.80+
```

### 2.2 Python Environment
Because the backend uses the Python Standard Library exclusively (`http.server`, `urllib`, `hashlib`, `json`, `csv`, `zipfile`, `xml.etree`), **no third-party pip packages are mandatory to run the server or scraper**.

If you wish to use a virtual environment for standard isolation:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Project Directory Map & File Registry

```
/run/media/blblx/Volume/AVISHKAR/
│
├── server.py                               # Main HTTP & REST API server (136 lines)
├── scraper_engine.py                       # Live web scraping & SHA-256 deduplication engine (402 lines)
├── integrate_cpi_data.py                   # MoSPI CPI 07.3.3.1 extraction & bundling script (209 lines)
├── generate_dataset_analytics.py           # Dataset1 452k microdata econometric aggregator (565 lines)
├── build_site.py                           # HTML compilation script injecting dynamic SVG canvases (881 lines)
├── app.js                                  # Interactive client controller & 5 dynamic SVG chart engines (2,406 lines)
├── styles.css                              # Design system tokens, JetBrains Mono tabular rules, print CSS (125 lines)
├── index.html                              # Compiled production HTML single-page dashboard (185 KB)
├── dataset1_analytics.json                 # Pre-computed econometric analytics bundle (2.2 MB)
├── dataset1_analytics.js                   # Client-side JavaScript bundle defining window.APIX_DATASET_ANALYTICS (1.6 MB)
│
├── Dataset1/
│   ├── Cleaned_dataset.csv                 # 452,088 cleaned historical quotes (49.1 MB)
│   ├── Scraped_dataset.csv                 # 452,088 raw scraped quotes (48.6 MB)
│   ├── cpi_640.xlsx                        # Official MoSPI CPI workbook covering COICOP 07.3.3.1 (1.0 MB)
│   ├── cpi_parsed_series.json              # Extracted 20-month MoSPI CPI time series across 34 States/UTs (427 KB)
│   ├── Live_Scraped_Dataset.csv            # Real-time deduplicated dataset populated by scraper (growing)
│   ├── Live_Scraped_Dataset.json           # JSON export of live scraped observations
│   └── live_scraper_telemetry.json         # Real-time poller telemetry & deduplication stats
│
└── assets/
    └── logo.svg                            # Sovereign MoSPI / NSO Lion Capital emblem
```

---

## 4. Code-Level Subsystem Walkthrough & Line References

### 4.1 Backend Server & REST API Router ([`server.py`](file:///run/media/blblx/Volume/AVISHKAR/server.py))
The backend is a multi-threaded HTTP server utilizing `http.server.HTTPServer` with custom routing and CORS headers.

* **Lines 26–36**: `APIxRequestHandler`: Overrides `end_headers` to inject `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, and `Access-Control-Allow-Headers: Content-Type`.
* **Lines 47–58 (`/api/scrape-live`)**: Triggers `engine.run_cycle(count=24)`. Runs corridor scraping, executes strict SHA-256 deduplication, updates `Live_Scraped_Dataset.csv`, and returns JSON response with batch statistics.
* **Lines 61–73 (`/api/live-status`)**: Reads `Dataset1/live_scraper_telemetry.json` and returns real-time engine telemetry (total records, historical duplicates eliminated, Jevons mean, timestamp).
* **Lines 76–94 (`/api/live-dataset`)**: Reads `Dataset1/Live_Scraped_Dataset.csv`, supports `?limit=N` and `?carrier=NAME` query filters, reverses order so most recent observations appear first, and returns records as JSON.
* **Lines 97–104 (`/api/cpi-data`)**: Returns the full MoSPI CPI series from `Dataset1/cpi_parsed_series.json`.
* **Lines 106–107**: Calls `super().do_GET()` to serve static files (`index.html`, `styles.css`, `app.js`, etc.).
* **Lines 118–136**: `run(port=8080)`: Starts server and prints accessible endpoints.

---

### 4.2 Live Scraping & Deduplication Engine ([`scraper_engine.py`](file:///run/media/blblx/Volume/AVISHKAR/scraper_engine.py))
Handles real-time inventory monitoring, canonical deduplication, and streaming econometric analysis.

* **Lines 25–36**: `AIRPORT_HUBS`: Dictionary of top 10 domestic hubs (DEL, BOM, BLR, HYD, CCU, MAA, AMD, PNQ, GOI, GAU).
* **Lines 38–57**: `CORRIDORS`: 18 bilateral trunk and regional flight pairs with flight durations.
* **Lines 59–66**: `CARRIERS`: Market share weights and base pricing multipliers for IndiGo (6E), Air India (AI), Vistara (UK), SpiceJet (SG), Akasa Air (QP), and AirAsia (I5).
* **Lines 89–93**: `get_record_hash()`:
  ```python
  canonical_str = f"{date_of_journey}|{flight_code}|{travel_class}|{source}|{destination}|{departure_time}|{int(fare)}"
  return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()[:16]
  ```
  Generates a deterministic 16-character SHA-256 signature for any airfare quote.
* **Lines 94–129**: `ScrapingEngine.__init__()` & `_load_existing_dataset()`: Loads all existing hashes into an in-memory set (`self.existing_hashes`) to guarantee zero duplicate writes across restarts.
* **Lines 130–220**: `scrape_corridor_quotes()`: Simulates live inventory polling across corridors and advance booking windows ($T+1$ to $T+45$).
* **Lines 225–303**: `deduplicate_and_analyze()`:
  - **Lines 246–255**: Evaluates incoming hashes against `self.existing_hashes` and `seen_in_this_batch`. If matched, increments `batch_duplicates` and drops the quote immediately.
  - **Lines 257–273**: Computes real-time Jevons geometric mean ($P^J = \exp(\frac{1}{n} \sum \ln p_i)$), Dutot arithmetic mean, Median (P50), IQR band ([P25, P75]), and Tukey anomaly fences.
  - **Lines 275–285**: Assigns `jevons_index` (Base ₹6,400 = 100.0) and flags `FLAGGED_SURGE` or `FLAGGED_DISCOUNT`.
* **Lines 305–350**: `commit_to_dataset()`: Appends unique clean records to `Live_Scraped_Dataset.csv` and updates `live_scraper_telemetry.json`.
* **Lines 352–385**: `run_cycle()`: Orchestrates the entire scrape-dedup-analyze-commit pipeline.

---

### 4.3 MoSPI CPI Data Integration ([`integrate_cpi_data.py`](file:///run/media/blblx/Volume/AVISHKAR/integrate_cpi_data.py))
Parses official NSO Consumer Price Index workbook for Item Code `07.3.3.1` (*Passenger transport by air, domestic*).

* **Lines 20–80**: Direct XML/ZIP extraction of `Dataset1/cpi_640.xlsx` without external dependencies.
* **Lines 89–104**: Chronological structuring of 1,880 monthly rows covering Jan 2025 – Aug 2026.
* **Lines 105–136**: Generates state rankings for August 2026 and national trajectories across Combined, Urban, and Rural sectors.
* **Lines 150–205**: Writes `Dataset1/cpi_parsed_series.json` and updates `dataset1_analytics.json` and `dataset1_analytics.js`.

---

### 4.4 Static Site & Dynamic SVG Template Generator ([`build_site.py`](file:///run/media/blblx/Volume/AVISHKAR/build_site.py))
Compiles the four Stitch HTML dashboard screens into a unified production `index.html`.

* **Lines 184–250**: Defines the 5 dynamic SVG canvas templates:
  - `svg1_replacement`: `#chart-national-trajectory` (viewBox `0 0 1000 240`)
  - `svg3_replacement`: `#chart-carrier-dispersion` (viewBox `0 0 700 240`)
  - `svg4_replacement`: `#chart-density-kde` (viewBox `0 0 800 100`)
  - `svg5_replacement`: `#chart-quality-latency` (viewBox `0 0 600 200`)
  - `svg6_replacement`: `#chart-cpi-cointegration` (viewBox `0 0 700 220`)
* **Lines 252–295**: Uses Regex substitutions to cleanly swap out the mockup static SVGs with our dynamic SVG templates.
* **Lines 68–176**: Inserts `live_scraper_console_html` into the Overview dashboard.
* **Lines 350–450**: Inserts `cpi_official_explorer_html` into the CPI Augmentation view.
* **Lines 450–590**: Inserts `calculator_html` (Econometric Calculator) and `dataset_explorer_html` (Microdata Explorer) into Route Analytics.
* **Lines 805–815**: Inserts `#chart-tooltip` floating element before `</body>`.

---

### 4.5 Interactive Client Controller & Dynamic SVG Engines ([`app.js`](file:///run/media/blblx/Volume/AVISHKAR/app.js))
Controls UI interactivity and renders all 5 dynamic SVG graphs.

* **Lines 8–23**: `DOMContentLoaded` listener invoking:
  `initNavigation()`, `initTelemetryClock()`, `initScopeSelector()`, `initRoutePicker()`, `initAnomalyQueue()`, `initBulletinModal()`, `initMicrodataExport()`, `initEconometricCalculator()`, `initDatasetExplorer()`, `initRawScrapedInspector()`, `updateInitialRouteAnalytics()`, `initLiveScrapingEngine()`, `initCpiExplorer()`, and `initDynamicCharts()`.
* **Lines 27–100**: `initNavigation()`: Client-side router switching active views (`#view-overview`, `#view-route`, `#view-quality`, `#view-methodology`).
* **Lines 159–204**: `initScopeSelector()`: Recalculates index weights when switching between Domestic Trunk 48, All-India Composite 72, and Regional UDAN 24, re-rendering `#chart-national-trajectory`.
* **Lines 210–450**: `initRoutePicker()` & `updateRouteAnalyticsView()`: Handles corridor selection (e.g. `DEL ⇄ BOM`), updates KPI cards, advance purchase bars, and invokes `renderCarrierDispersionChart()` and `renderDensityKdeChart()`.
* **Lines 1145–1248**: `initLiveScrapingEngine()`: Automatically triggers `/api/scrape-live` on page load, animates streaming quote rows with `.row-newly-ingested`, and updates deduplication metrics.
* **Lines 1250–1365**: `initCpiExplorer()`: Populates state/sector dropdowns, updates MoSPI headline cards, renders the 20-month table, and calls `renderCpiCointegrationChart()`.
* **Lines 1373–1400**:
  - `generateSmoothBezierPath(points)`: Computes cubic Bézier control points ($CP_1, CP_2$) to render continuous curves without polygon jaggedness.
  - `generateAreaPath(points, bottomY)`: Closes path along baseline for smooth gradient fills.
* **Lines 1405–1436**: `showChartTooltip(evt, htmlContent)`: Clamped viewport positioning for floating tooltip `#chart-tooltip`.
* **Lines 1445–1678**: `renderNationalTrajectoryChart(scope, baseYear, freq)`:
  - Renders 30-day index timeline from `national_summary.timeline_30d`.
  - Re-scales line based on base year (Base 2023 = 100.0 vs Base 2019 = 134.04).
  - Plots 7-day moving average dashed path (`#traj-ma-path`).
  - Marks event callouts (Dussehra, Cyclone Dana, Diwali Peak).
  - Crosshair tracking on `#traj-hit-overlay`.
* **Lines 1683–1865**: `renderCarrierDispersionChart(selectedRouteKey, activeData)`:
  - Plots individual curves for IndiGo, Air India, Vistara, SpiceJet, Akasa Air, and Composite Basket.
  - Highlights Diwali Surge Window.
* **Lines 1870–1960**: `renderDensityKdeChart(selectedRouteKey, activeData)`:
  - Computes Gaussian mixture KDE across the route's price domain.
  - Draws shaded 99th percentile Winsorization cutoff zone and median reference line.
* **Lines 1965–2090**: `renderQualityLatencyChart()`:
  - Draws 30 daily completion rate bars (99.4%–100.0%) and latency overlay line (78–124ms).
* **Lines 2095–2270**: `renderCpiCointegrationChart(selectedState, selectedSector)`:
  - Plots 20 months of official MoSPI CPI (Item 07.3.3.1) vs APIx leading indicator (+17.6 day lead).
* **Lines 2275–2405**: `initDynamicCharts()`: Hooks event listeners to frequency buttons, base year switchers, and time series CSV export.

---

## 5. How to Run Locally

### 5.1 Start the Server
From the project root directory:

```bash
python3 server.py 8080
```

To run it as a persistent background daemon:
```bash
nohup python3 server.py 8080 > server.log 2>&1 &
```

### 5.2 Access the Web Platform
Open your browser and navigate to:
```
http://localhost:8080/index.html
```

### 5.3 Test REST API Endpoints Directly
```bash
# Trigger a live scrape cycle (deduplicates and appends 24 quotes)
curl -s http://localhost:8080/api/scrape-live | jq .

# Check live engine telemetry and deduplication rate
curl -s http://localhost:8080/api/live-status | jq .

# Fetch the latest 10 deduplicated quotes
curl -s "http://localhost:8080/api/live-dataset?limit=10" | jq .

# Retrieve official MoSPI CPI series
curl -s http://localhost:8080/api/cpi-data | jq .latest_headline
```

### 5.4 Rebuilding the Site / Compiling Assets
If you modify any template strings in `build_site.py`:
```bash
python3 build_site.py
```
This regenerates `index.html` (size: ~185 KB).

---

## 6. Cloud Deployment Guide: Vercel

Vercel is ideal for hosting the static frontend assets (`index.html`, `styles.css`, `app.js`, `assets/`) while running the backend endpoints as **Python Serverless Functions**.

### 6.1 Vercel Directory Layout
Organize the project for Vercel:

```
project-root/
│
├── api/                                    # Vercel Serverless Python Functions
│   ├── scrape_live.py                      # Handles GET /api/scrape-live
│   ├── live_status.py                      # Handles GET /api/live-status
│   ├── live_dataset.py                     # Handles GET /api/live-dataset
│   └── cpi_data.py                         # Handles GET /api/cpi-data
│
├── public/                                 # Static Assets served directly by Vercel CDN
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── dataset1_analytics.js
│   ├── dataset1_analytics.json
│   ├── assets/
│   │   └── logo.svg
│   └── Dataset1/
│       ├── cpi_parsed_series.json
│       ├── live_scraper_telemetry.json
│       └── Live_Scraped_Dataset.csv
│
├── scraper_engine.py
├── vercel.json                             # Vercel configuration file
└── requirements.txt                        # Python dependencies (minimal/empty)
```

### 6.2 `vercel.json` Configuration
Create `vercel.json` in the root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    },
    {
      "src": "public/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/scrape-live",
      "dest": "/api/scrape_live.py"
    },
    {
      "src": "/api/live-status",
      "dest": "/api/live_status.py"
    },
    {
      "src": "/api/live-dataset",
      "dest": "/api/live_dataset.py"
    },
    {
      "src": "/api/cpi-data",
      "dest": "/api/cpi_data.py"
    },
    {
      "src": "/(.*)",
      "dest": "/public/$1"
    }
  ]
}
```

### 6.3 Example Serverless Function: `api/scrape_live.py`
```python
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add root directory to sys.path so scraper_engine can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scraper_engine import ScrapingEngine

engine = ScrapingEngine()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            telemetry = engine.run_cycle(count=24)
            response_body = json.dumps({
                'status': 'success',
                'telemetry': telemetry
            }).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_body)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
```

### 6.4 Deploying via Vercel CLI
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy to production
vercel --prod
```

---

## 7. Cloud Deployment Guide: Supabase

Supabase provides a hosted PostgreSQL database, Row-Level Security, Edge Functions (Deno), and Realtime WebSocket streaming for airfare microdata quotes.

### 7.1 PostgreSQL Schema for Airfare Microdata
Execute the following migration in your Supabase SQL Editor:

```sql
-- 1. Table for Live Scraped & Deduplicated Airfare Microdata
CREATE TABLE public.apix_live_quotes (
    id BIGSERIAL PRIMARY KEY,
    record_hash VARCHAR(16) UNIQUE NOT NULL,      -- Canonical SHA-256 natural key
    timestamp_utc TIMESTAMPTZ DEFAULT NOW(),
    date_of_journey DATE NOT NULL,
    journey_day VARCHAR(10) NOT NULL,
    airline VARCHAR(50) NOT NULL,
    carrier_code VARCHAR(5) NOT NULL,
    flight_code VARCHAR(15) NOT NULL,
    class VARCHAR(25) NOT NULL,
    source VARCHAR(5) NOT NULL,
    destination VARCHAR(5) NOT NULL,
    departure_time VARCHAR(20),
    arrival_time VARCHAR(20),
    duration_hours NUMERIC(5,2),
    stops VARCHAR(15),
    days_left INTEGER NOT NULL,
    fare NUMERIC(10,2) NOT NULL,
    jevons_index NUMERIC(7,2),
    anomaly_status VARCHAR(25) DEFAULT 'VALIDATED_NORMAL',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for high-speed corridor queries and deduplication lookups
CREATE INDEX idx_apix_hash ON public.apix_live_quotes(record_hash);
CREATE INDEX idx_apix_corridor ON public.apix_live_quotes(source, destination, date_of_journey);
CREATE INDEX idx_apix_carrier ON public.apix_live_quotes(carrier_code, class);

-- 2. Table for MoSPI Official CPI Series (COICOP 07.3.3.1)
CREATE TABLE public.apix_cpi_series (
    id SERIAL PRIMARY KEY,
    state VARCHAR(60) NOT NULL,
    sector VARCHAR(20) NOT NULL,                  -- Combined / Urban / Rural
    year INTEGER NOT NULL,
    month VARCHAR(15) NOT NULL,
    month_num INTEGER NOT NULL,
    year_month VARCHAR(7) NOT NULL,               -- e.g. '2026-08'
    cpi_index NUMERIC(6,2),
    inflation_yoy NUMERIC(6,2),
    UNIQUE(state, sector, year_month)
);

-- 3. Table for Live Ingestion Telemetry
CREATE TABLE public.apix_scraper_telemetry (
    id SERIAL PRIMARY KEY,
    timestamp_utc TIMESTAMPTZ DEFAULT NOW(),
    total_processed INTEGER NOT NULL,
    duplicates_eliminated INTEGER NOT NULL,
    unique_stored INTEGER NOT NULL,
    jevons_geom_mean NUMERIC(10,2),
    headline_index NUMERIC(6,2)
);

-- 4. Enable Row-Level Security (RLS)
ALTER TABLE public.apix_live_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apix_cpi_series ENABLE ROW LEVEL SECURITY;

-- Allow public anonymous read access (institutional public dashboard)
CREATE POLICY "Public Read Access" ON public.apix_live_quotes FOR SELECT USING (true);
CREATE POLICY "Public Read Access CPI" ON public.apix_cpi_series FOR SELECT USING (true);
```

### 7.2 Strict Deduplication Constraint in Supabase
The unique constraint on `record_hash` enforces the deduplication rule at the database engine level:
```sql
INSERT INTO public.apix_live_quotes (
    record_hash, date_of_journey, journey_day, airline, carrier_code, 
    flight_code, class, source, destination, departure_time, arrival_time, 
    duration_hours, stops, days_left, fare, jevons_index, anomaly_status
)
VALUES (
    'a1b2c3d4e5f60718', '2026-09-26', 'Saturday', 'IndiGo', '6E',
    '6E-2519', 'Economy', 'DEL', 'BOM', '06:15', '08:25',
    2.17, 'non-stop', 15, 6712.00, 104.88, 'VALIDATED_NORMAL'
)
ON CONFLICT (record_hash) DO NOTHING; -- Drops duplicate quote automatically!
```

### 7.3 Supabase Edge Function: Auto-Scrape Poller
You can deploy a Supabase Edge Function (`supabase/functions/scrape-poller/index.ts`) running on Deno that polls airline quotes on a schedule via `pg_cron`:

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

Deno.serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  // Corridor quote generator and SHA-256 hasher...
  // Inserts quotes with ON CONFLICT DO NOTHING...
  
  return new Response(JSON.stringify({ message: "Scrape cycle completed" }), {
    headers: { "Content-Type": "application/json" }
  })
})
```

---

## 8. Production Linux VPS Deployment (Nginx + Systemd)

For sovereign on-premise or cloud virtual private servers (AWS EC2, GCP Compute Engine, DigitalOcean, Hetzner, Linode):

### 8.1 Systemd Service (`/etc/systemd/system/apix.service`)
Create the systemd service file:
```ini
[Unit]
Description=APIx India Sovereign Airfare Price Index Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/apix-india
ExecStart=/usr/bin/python3 /var/www/apix-india/server.py 8080
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable apix
sudo systemctl start apix
sudo systemctl status apix
```

### 8.2 Nginx Reverse Proxy Configuration (`/etc/nginx/sites-available/apix`)
```nginx
server {
    listen 80;
    server_name apix.gov.in airfare-index.india;

    # Gzip compression for high-speed delivery of JSON & JS bundles
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;
    gzip_min_length 1000;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Disable cache for live API endpoints
        location /api/ {
            proxy_pass http://127.0.0.1:8080;
            add_header Cache-Control "no-store, no-cache, must-revalidate";
        }
    }
}
```

Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/apix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 9. Verification & Health Monitoring

To verify overall system health:
1. **Check Server Process**:
   ```bash
   curl -s -I http://localhost:8080/index.html | grep "HTTP/1.0 200 OK"
   ```
2. **Verify JavaScript Syntax**:
   ```bash
   node -c app.js
   ```
3. **Run Deduplication Stress Test**:
   ```bash
   python3 scraper_engine.py --test-dedup
   ```
4. **Confirm Live Ingestion Invariant**:
   ```python
   python3 -c "
   import csv
   with open('Dataset1/Live_Scraped_Dataset.csv') as f:
       hashes = [r['record_hash'] for r in csv.DictReader(f)]
   assert len(hashes) == len(set(hashes)), 'Duplicate hashes found!'
   print(f'Verification SUCCESS: {len(hashes)} unique observations with zero duplicates.')
   "
   ```
