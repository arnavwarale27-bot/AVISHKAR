# APIx India — User Workflow & Operational Guide (`UserWorkflow.md`)

This guide explains how end-users (economists, statistical officers, aviation analysts, policy makers, and researchers) interact with and utilize the **APIx India Sovereign Real-Time Airfare Price Index Platform**.

---

## 1. Quick-Start & Navigation Overview

When you navigate to the platform (`http://localhost:8080/index.html` or your production domain), the persistent top navigation bar provides instant access to the core analytical screens:

```
+-------------------------------------------------------------------------------------------------------+
|  [MoSPI Logo] APIx India | Sovereign Real-time Airfare Price Index           IST 14:30:00 (Today)     |
+-------------------------------------------------------------------------------------------------------+
|  Overview Dashboard  |  Route Analytics  |  Quality & Anomalies  |  CPI Augmentation  |  Gazette [o]  |
+-------------------------------------------------------------------------------------------------------+
```

### Key Navigation Links
1. **Overview Dashboard** (`#overview-dashboard`): National airfare price indices, live autonomous web scraping console, 30-day index trajectory, and national route flow map.
2. **Route Analytics** (`#route-analytics`): Corridor-specific pricing, carrier dispersion charts, advance purchase matrix, continuous KDE density curves, econometric fare calculator, and microdata explorer.
3. **Quality & Anomalies** (`#quality-&-anomalies`): Pipeline ingestion telemetry, 30-day harvest completion & latency chart, and the Hampel/Tukey statistical anomaly queue.
4. **CPI Augmentation** (`#cpi-augmentation`): Official MoSPI CPI (Item `07.3.3.1`) benchmark explorer across 34 States/UTs, rural-urban divergence, and high-frequency predictive lead curves.
5. **Export & Bulletins** (`#export-&-bulletins`): Official sovereign gazette modal, printer-optimized executive briefs, and microdata CSV downloads.

---

## 2. Workflow 1: Macroeconomic Airfare Inflation Surveillance (Overview Dashboard)

The **Overview Dashboard** is designed for macroeconomists and statistical officers needing immediate visibility into national air passenger transport inflation.

```
+-------------------------------------------------------------------------------------------------------+
|  LIVE SCRAPING CONSOLE [Active • Auto-Scrapes On Visit]                                               |
|  [Total Processed: 148]  [Duplicates Eliminated: 18]  [Unique Stored: 130]  [Jevons Fare: ₹7,420]     |
|  [Trigger Live Scrape Now (Button)]  [Export Scraped Dataset (CSV)]                                   |
|  Streaming Microdata Table (Flashing green row for fresh ingestions)                                  |
+-------------------------------------------------------------------------------------------------------+
```

### Step-by-Step Actions:
1. **Observe Automatic Live Ingestion**:
   - As soon as the page loads, the **Live Scraping & Monitoring Engine** triggers an automatic polling cycle.
   - The HUD counters update automatically:
     - **Total Quotes Processed**: Cumulative raw quotes pulled from live corridors.
     - **Duplicates Eliminated**: Redundant queries purged by canonical SHA-256 deduplication.
     - **Unique Records Stored**: Verified clean quotes written to `Dataset1/Live_Scraped_Dataset.csv`.
     - **Live Jevons Geom Mean**: Instantaneous geometric mean fare of current market quotes.
   - The live feed table displays incoming observations, highlighting new arrivals with a soft emerald flash animation.
2. **Trigger an On-Demand Scrape**:
   - Click **"Trigger Live Scrape Now"** to poll flight corridors on demand.
   - The engine polls 24–36 corridor quotes, filters out identical entries, commits unique records, and updates all charts.
3. **Export the Scraped Dataset**:
   - Click **"Export Scraped Dataset (CSV)"** to download the clean deduplicated CSV (`Dataset1/Live_Scraped_Dataset.csv`).
4. **Analyze the National Airfare Index Trajectory Graph**:
   - **Switch Frequency**: Click **`Daily`**, **`Weekly`**, or **`Monthly`** to adjust time aggregation.
   - **Recalibrate Base Year**:
     - Click **`Base 2023=100`** (standard post-pandemic benchmark; current headline ~`112.80`).
     - Click **`Base 2019=100`** (pre-pandemic reference; re-indexes trajectory to ~`151.20`).
   - **Inspect 7-Day Moving Average**: Observe the dashed overlay line (`#traj-ma-path`) smoothing daily volatility.
   - **Review Fleet Shock Callouts**: Hover over vertical event markers:
     - *Oct 11*: Dussehra Holiday Surge (+8.4%).
     - *Oct 24*: Cyclone Dana Grounding (+9.2% East Corridor).
     - *Oct 28*: Diwali National Peak Surge (+18.6%).
   - **Crosshair Hover Inspection**: Move your cursor anywhere across the graph canvas. A high-precision floating tooltip displays:
     - Calendar Date and Day Index
     - Headline Index & 7-Day Moving Average
     - Jevons Geometric Mean Fare (INR)
     - Underlying Microdata Sample Count
   - **Export 30-Day Series**: Click **`Series`** to export the entire daily index timeline to CSV.
5. **Switch Sampling Basket Scopes**:
   - Use the **"Sampling Scope"** dropdown in the top control bar to switch between:
     - *Domestic Trunk 48 Pairs (87.2% Traffic)*
     - *All-India Composite (Full 72 Pairs)*
     - *Regional UDAN 24 Pairs*
   - Laspeyres weights and headline figures recalculate immediately.

---

## 3. Workflow 2: Corridor-Specific Competition & Advance Purchase Yield (Route Analytics)

The **Route Analytics** view enables airline yield managers, competition regulators (CCI), and procurement teams to analyze corridor-specific price dynamics.

```
+-------------------------------------------------------------------------------------------------------+
|  ROUTE PICKER: [ DEL ⇄ BOM (Delhi ⇄ Mumbai) v ]   [ Bi-directional ]  [ DEL → BOM ]  [ BOM → DEL ]    |
|  [Route Index: 114.2]  [Median Fare: ₹6,712]  [IQR: ±₹2,218]  [Share: 4.23%]  [Non-stop: 19,113]     |
+-------------------------------------------------------------------------------------------------------+
```

### Step-by-Step Actions:
1. **Select a City-Pair Corridor**:
   - Open the **Route Picker** dropdown (`#routePicker`) to choose from 21 top domestic pairs (e.g. `DEL ⇄ BOM`, `BLR ⇄ DEL`, `BOM ⇄ BLR`, `DEL ⇄ CCU`, etc.).
   - The entire dashboard recalculates instantaneously for that corridor.
2. **Filter by Journey Direction**:
   - Click **`Bi-directional Average`** for combined corridor statistics.
   - Click **`DEL → BOM`** or **`BOM → DEL`** to examine directional pricing asymmetries (e.g. business traveler return patterns).
3. **Analyze Carrier Price Dispersion**:
   - Examine the **Carrier Price Trajectory Chart**:
     - Branded curves illustrate pricing trajectories for **IndiGo** (Deep Blue), **Air India** (Saffron), **Vistara** (Purple), **SpiceJet** (Red), **Akasa Air** (Sky Blue), and the **Composite Basket** (Bold Navy).
     - Shaded amber region marks the **Diwali Surge Window**.
     - Hover over any airline node to view that carrier's median fare and verified quote volume.
4. **Evaluate the Advance Purchase Horizon Curve ($T+1$ to $T+45$)**:
   - Inspect the advance purchase bars:
     - **T+1 (Walk-Up Fares)**: High surge premium (often +40% to +85% above baseline).
     - **T+7 (1 Week)**: Initial yield compression.
     - **T+15 (2 Weeks)**: Standard corporate booking window.
     - **T+30 (1 Month)**: Moderate apex discount.
     - **T+45 (Apex Discount)**: Maximum promotional discounts.
5. **Inspect the Continuous Price KDE & Winsorization Graph**:
   - Below the horizon matrix, the **Continuous KDE Distribution SVG** plots the empirical probability density of fares on that corridor.
   - The dark primary marker line identifies the exact **P50 Median Fare**.
   - The red-shaded zone on the right highlights the **99th Percentile Winsorization Cutoff**, visually showing where predatory surge pricing is capped.
6. **Simulate Fares using the Econometric Calculator**:
   - Scroll to the **Econometric Route Fare & Index Calculator**:
     - Select **Origin Hub** (DEL, BOM, BLR, HYD, etc.).
     - Select **Destination Hub**.
     - Select **Carrier** (IndiGo, Air India, Vistara, SpiceJet, etc., or All Carriers).
     - Select **Cabin Tier** (Economy, Premium Economy, Business).
     - Select **Routing Stops** (Non-Stop vs 1-Stop).
     - Adjust the **Booking Horizon Slider** ($T+1$ to $T+50$ days) or click quick-select buttons.
   - Observe the live recalculation of:
     - **Dutot Arithmetic Mean**
     - **Median P50**
     - **Jevons Geometric Aggregate**
     - **IQR Spread Band** [P25 – P75]
     - **Yield Decay Premium** vs T+45
     - **Surge Anomaly Risk**
7. **Search & Audit Microdata in the Dataset1 Reference Explorer**:
   - Search across 2,512 verified microdata records by flight code (e.g. `6E-2519`, `AI-805`), carrier, or date.
   - Filter by **Carrier**, **Class**, and **Stops**.
   - Navigate through pages using **Previous / Next**.
   - Click **"Raw Scraping Pipeline Inspector"** to view a side-by-side comparison of the raw multi-line scraped string from `Scraped_dataset.csv` versus the cleaned record in `Cleaned_dataset.csv`.
   - Click **"Export Filtered Microdata (CSV)"** to save your current filtered selection.

---

## 4. Workflow 3: Data Quality, Schema Validation & Anomaly Surveillance (Quality & Anomalies)

This view provides full transparency into pipeline health and automated statistical surveillance.

```
+-------------------------------------------------------------------------------------------------------+
|  INGESTION TELEMETRY: 452,088 Quotes | Schema Pass: 100.0% | Failures: 0 | Latency: 78-124ms          |
|  [30-Day Harvest Completion Rate Bars (%) & Processing Latency Line (ms)]                             |
+-------------------------------------------------------------------------------------------------------+
```

### Step-by-Step Actions:
1. **Audit Pipeline Completion & Latency**:
   - The top metrics strip confirms:
     - **Corpus Size**: 452,088 quotes from Dataset1.
     - **Schema Pass Rate**: 100.0% compliance.
     - **Missing Fields**: 0 missing values.
   - Hover over the **30-day harvest completion bars** (`#chart-quality-latency`):
     - View the day's harvest volume, schema pass rate, and exact ingestion latency in milliseconds.
2. **Investigate Anomalies in the Surveillance Queue**:
   - Scroll to **Airfare Statistical Anomalies**:
     - The queue automatically lists quotes flagged by the **Hampel Filter (Median Absolute Deviation)** and **Tukey Fences (1.5 x IQR)**.
     - Each entry shows the Flight Code, Carrier, Route, Booking Horizon, Quoted Fare, Expected Normal Band, and Deviation (e.g. *+134.2% Holiday Surge Outlier*).
   - Test resolution actions:
     - Click **"Winsorize"**: Caps the fare at the 99th percentile threshold for index aggregation.
     - Click **"Quarantine"**: Temporarily excludes the observation from index calculation.
     - Click **"Whitelist"**: Approves the quote as legitimate peak demand.

---

## 5. Workflow 4: Official MoSPI CPI Co-Integration & Gazette Forecasting (CPI Augmentation)

This screen bridges high-frequency web scraping microdata with official macroeconomic statistics published by the National Statistical Office (NSO).

```
+-------------------------------------------------------------------------------------------------------+
|  OFFICIAL MOSPI CPI EXPLORER (ITEM 07.3.3.1 - AIR TRANSPORT)                                          |
|  State: [ All India v ]    Sector: [ Combined (Rural + Urban) v ]                                     |
|  [Aug 2026 Index: 135.49]  [YoY Inflation: +20.85%]  [Rural/Urban: 148.16 vs 127.20]  [Lead: +17.6d]  |
+-------------------------------------------------------------------------------------------------------+
```

### Step-by-Step Actions:
1. **Select State and Sector**:
   - Select **State / Region**: Choose from **34 States and Union Territories** (e.g. *All India*, *NCT of Delhi*, *Maharashtra*, *Karnataka*, *Tamil Nadu*, *West Bengal*, *Gujarat*, etc.).
   - Select **Sector**: Choose **Combined**, **Urban**, or **Rural**.
2. **Review Official Headline Indicators**:
   - **August 2026 Index**: Official MoSPI index level (Base 2024 = 100.0).
   - **YoY Airfare Inflation**: Year-on-year percentage change vs August 2025.
   - **Rural vs Urban Divergence**: Identifies regional cost premiums (e.g. Rural index of `148.16` vs Urban `127.20` represents a +20.96 pt rural premium).
   - **APIx High-Frequency Lead**: Demonstrates the **15–19 day predictive lead window** that APIx provides over the delayed official gazette release.
3. **Analyze the 20-Month Trajectory Table**:
   - The table lists every month from **January 2025 through August 2026**.
   - Compares the official gazette figure against the APIx high-frequency synthetic match (tracking within ~0.4% error band).
4. **Inspect the MoSPI Co-Integration Graph**:
   - The SVG chart (`#chart-cpi-cointegration`) dynamically renders:
     - **Official MoSPI Line** (Secondary Blue): Official monthly gazette trajectory.
     - **APIx High-Frequency Line & Fill** (Dark Primary): High-frequency real-time signal leading the official gazette by ~17.6 days.
     - **Headline CPI Baseline** (Dotted Gray): General all-items inflation baseline.
   - Hover over any node to view exact index levels, YoY inflation rates, and the predictive lead window.

---

## 6. Workflow 5: Sovereign Gazette Bulletin & Microdata Export

The platform generates official gazette summaries formatted according to Government of India statistical standards.

```
+-----------------------------------------------------------------------------------+
|  MoSPI / NSO Official Bulletin: National Airfare Price Index (APIx) Summary       |
|  [Gazette Ref: NSO-APIX-2023-Q1]  [Headline: 112.80]  [MoM: +2.1%]  [Lead: 17.6d] |
|  Executive Statistical Abstract ...                                               |
|  [Print Gazette (Button)]      [Download Microdata CSV (Button)]                  |
+-----------------------------------------------------------------------------------+
```

### Step-by-Step Actions:
1. **Open the Bulletin Modal**:
   - Click the **"Export & Bulletins"** button in the header or top navigation bar.
2. **Review Executive Summary**:
   - Displays sovereign data center provenance (NIC MeghRaj Cloud Node DEL-NSO-04).
   - Displays MoSPI-QAF validation grade: **Grade A (93.4/100)**.
3. **Print / Export Gazette**:
   - Click **"Print Gazette"**: Invokes the browser print dialog. Custom print stylesheets (`@media print` in `styles.css`) hide all web navigation, buttons, and sidebars, outputting a clean, formatted sovereign bulletin document ready for PDF export or paper filing.
4. **Download Microdata CSV**:
   - Click **"Download Microdata CSV"** to export official observation logs directly to your local file system.

---

## 7. Troubleshooting & Common Questions

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| **Scraper HUD shows "Pending visit trigger..."** | JavaScript blocked or local server unreachable. | Ensure browser allows JavaScript; verify `python3 server.py 8080` is running. |
| **"Failed to fetch" error on live scrape** | Server port blocked or CORS restriction. | Check terminal for server logs; test endpoint with `curl http://localhost:8080/api/scrape-live`. |
| **Charts look blank or empty** | Missing dataset bundle. | Ensure `dataset1_analytics.js` is loaded in `index.html`. Check browser console for errors. |
| **State select in CPI explorer empty** | `cpi_parsed_series.json` missing. | Run `python3 integrate_cpi_data.py` to regenerate the series JSON. |
