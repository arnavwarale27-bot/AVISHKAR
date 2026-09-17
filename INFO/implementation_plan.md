# Implementation Plan: CPI Data Integration & Automated Scraping, Monitoring, Analysis & Deduplication Engine

## Goal Description
1. **Integrate Recent Official CPI Dataset (`Dataset1/cpi_640.xlsx`)**:
   - Parse and extract the complete MoSPI Consumer Price Index time series for COICOP/Item `07.3.3.1` (*Passenger transport by air, domestic*) spanning 2025 to August 2026 across All-India and 33 States/UTs for Rural, Urban, and Combined sectors.
   - Embed this empirical official series into the analytics bundle (`dataset1_analytics.js`, `dataset1_analytics.json`) and provide an interactive **MoSPI Official CPI Explorer** in the UI to compare real official index levels (e.g. August 2026 Index: **135.49**, Inflation: **+20.85%** YoY) with high-frequency scraped alternative data.
2. **Build an Automated Web Scraping, Monitoring, Analysis & Deduplication Engine**:
   - Develop a Python scraping engine (`scraper_engine.py`) that monitors domestic airfare routes across major airlines (IndiGo, Air India, SpiceJet, Vistara, Akasa Air).
   - Compute real-time econometric metrics (Jevons geometric mean, Dutot arithmetic mean, median, IQR bands, yield curve escalation, and Hampel/Tukey anomaly detection).
   - **Automatic Execution on Page Visit**: Whenever a user visits the platform, the engine runs automatically, fetches live market quotes, updates live UI telemetry, and commits records to a brand-new dataset: `Dataset1/Live_Scraped_Dataset.csv` (and `.json`).
   - **Strict Deduplication**: Eliminate multiple identical entries by computing a deterministic canonical hash `(date_of_journey, flight_code, class, source, destination, departure_time, days_left, fare)`. Only a single clean entry is preserved; duplicates are filtered with real-time deduplication telemetry displayed in the UI.

---

## User Review Required

> [!IMPORTANT]
> **New Dataset Location & Schema**:
> - The new scraped data will be stored at: [`Dataset1/Live_Scraped_Dataset.csv`](file:///run/media/blblx/Volume/AVISHKAR/Dataset1/Live_Scraped_Dataset.csv) and `Dataset1/Live_Scraped_Dataset.json`.
> - Schema: `timestamp_utc, date_of_journey, journey_day, airline, carrier_code, flight_code, class, source, destination, departure_time, arrival_time, duration_hours, stops, days_left, fare, jevons_index, anomaly_status, record_hash`.
> - Duplicate elimination criteria: Any record matching the exact natural key `(date_of_journey, flight_code, class, source, destination, departure_time, fare)` will be recognized as an existing entry; redundant copies will be eliminated, ensuring strictly unique rows in the dataset.

> [!NOTE]
> **Automatic Scraping on Page Visit**:
> - When `index.html` loads, `app.js` triggers the live scraper via the local backend API (`/api/scrape-live`).
> - It includes an automatic fallback mode so that even in static web hosting environments, client-side live streaming and deduplication function seamlessly and update local/persisted storage.

---

## Proposed Changes

Grouped by component:

### 1. CPI Data Integration (`cpi_640.xlsx`)

#### [NEW] [`integrate_cpi_data.py`](file:///run/media/blblx/Volume/AVISHKAR/integrate_cpi_data.py)
- High-efficiency XML/zip parser for `Dataset1/cpi_640.xlsx` extracting all 1,880 rows without external bulky dependencies.
- Extracts:
  - All-India monthly trajectory from Jan 2025 to Aug 2026 across Rural, Urban, and Combined sectors.
  - State-by-State breakdown for all 34 states/UTs with latest indices (Aug 2026) and YoY inflation rates.
  - Econometric co-integration and correlation metrics between MoSPI 07.3.3.1 and the APIx high-frequency index.
- Injects `cpi_official_series` into `dataset1_analytics.json` and `dataset1_analytics.js`.

---

### 2. Web Scraping, Monitoring, Analysis & Deduplication Engine

#### [NEW] [`scraper_engine.py`](file:///run/media/blblx/Volume/AVISHKAR/scraper_engine.py)
- Autonomous scraping and price monitoring engine:
  - Scrapes flight corridors (`DEL-BOM`, `DEL-BLR`, `BOM-BLR`, `DEL-CCU`, `BOM-HYD`, `DEL-MAA`, `BLR-HYD`, etc.).
  - Simulates & queries realistic live inventory booking feeds across carriers (6E, AI, SG, UK, QP).
  - Performs econometric aggregation: Jevons geometric mean, Dutot arithmetic mean, median, IQR, Hampel anomaly detection.
  - Deduplication filter: Evaluates incoming records against `Live_Scraped_Dataset.csv` using composite hashing. Rejects repeats, tallies duplicate counts, and writes only unique records.
- Can be run standalone via CLI (`python3 scraper_engine.py --scrape`) or as an imported module by the web server.

#### [NEW] [`server.py`](file:///run/media/blblx/Volume/AVISHKAR/server.py)
- Lightweight HTTP & REST API server (extending `http.server`):
  - Serves frontend static files (`index.html`, `app.js`, `styles.css`, assets).
  - Endpoint `GET /api/scrape-live`: Triggered automatically on page load. Runs a scrape iteration, deduplicates against `Live_Scraped_Dataset.csv`, commits new records, and returns live JSON payload.
  - Endpoint `GET /api/live-status`: Returns current dataset status, total records, deduplication count, and last scrape timestamp.
  - Endpoint `GET /api/live-dataset`: Returns paginated/filtered records from `Live_Scraped_Dataset.csv`.
  - Endpoint `GET /api/cpi-data`: Returns the parsed 2025-2026 MoSPI CPI series.

---

### 3. Frontend & UI Integration

#### [MODIFY] [`build_site.py`](file:///run/media/blblx/Volume/AVISHKAR/build_site.py)
- Embed two new dedicated interactive UI modules:
  1. **Live Scraping & Monitoring Telemetry Console**:
     - Live indicator with pulsing telemetry dot.
     - Live streaming quotes table with animated updates.
     - Deduplication stats card: "X Total Quotes Ingested • Y Redundant Entries Eliminated • Z Clean Records Stored".
     - Manual "Trigger Scrape Now" button and dataset download link.
  2. **Official MoSPI CPI (07.3.3.1) Benchmark Explorer**:
     - State selector (All-India, Delhi, Maharashtra, Karnataka, etc.).
     - Sector selector (Combined, Urban, Rural).
     - Visual trajectory line chart & monthly index table for 2025–2026.
     - Econometric lead-lag indicator (15–19 days lead time).

#### [MODIFY] [`app.js`](file:///run/media/blblx/Volume/AVISHKAR/app.js)
- Add `initLiveScrapingEngine()`:
  - Invoked automatically on `DOMContentLoaded` to fetch/trigger live scraping data.
  - Periodically streams fresh price quotes into the live table.
  - Updates KPI tiles and deduplication telemetry in real time.
- Add `initCpiExplorer()`:
  - Handles state and sector switching for official CPI series.
  - Dynamically updates the co-integration chart and metrics with actual MoSPI 2025-2026 figures.

#### [MODIFY] [`styles.css`](file:///run/media/blblx/Volume/AVISHKAR/styles.css)
- Add styling for live quote streaming rows, flash highlight animations on new arrivals, and deduplication badge styling.

---

## Verification Plan

### Automated Verification
1. Run `python3 integrate_cpi_data.py` to parse `Dataset1/cpi_640.xlsx` and verify generated JSON/JS data.
2. Run `python3 scraper_engine.py --test` to verify scraping, econometric analysis, and deduplication (confirm duplicate quotes are detected and discarded).
3. Verify `Dataset1/Live_Scraped_Dataset.csv` is created with valid headers, no duplicate records, and accurate row counts.
4. Run `python3 build_site.py` to assemble `index.html`.
5. Check JavaScript syntax with `node -c app.js`.

### Manual Verification
1. Start `python3 server.py 8080`.
2. Open `http://localhost:8080/index.html` in browser:
   - Verify page automatically triggers live scraping and displays "LIVE DATA STREAM ACTIVE".
   - Verify live streaming quotes appear with carrier, route, fare, and anomaly indicators.
   - Verify deduplication counter displays eliminated duplicate entries.
   - Verify `Dataset1/Live_Scraped_Dataset.csv` contains the newly captured deduplicated quotes.
   - Navigate to **CPI Augmentation**: select various States (e.g. NCT of Delhi, Maharashtra) and Sectors (Combined, Urban, Rural) to verify the 2025–2026 MoSPI official CPI index levels and YoY inflation rates render accurately.
