# Project Brief & Product Requirements Document (PRD)

**Project Name**: APIx India — Real-time Airfare Price Index for India  
**Subtitle**: Automated Airfare Intelligence for CPI Augmentation  
**Institutional Purview**: National Statistical Office (NSO) / Ministry of Statistics & Programme Implementation (MoSPI), Government of India  
**Document Version**: 1.0 (Official Specification)  
**Status**: Approved Prototype / Engineering Baseline  
**Classification**: Government Statistical Intelligence & Econometric Research  

---

## 1. Executive Summary & Problem Statement

### 1.1 Context
In India, the Consumer Price Index (CPI) compiled by the Central Statistics Office (CSO) under MoSPI relies heavily on periodic, manual field enumeration schedules. Under the *Transport and Communication* group (COICOP item classification **5.3.01: Air Transport**), rapid algorithmic price adjustments by domestic airlines present a significant measurement challenge. Traditional monthly or bi-monthly field surveys fail to capture:
1. **Intraday Dynamic Yield Pricing**: Fares that change minute-by-minute based on real-time load factors.
2. **Advance Purchase Horizon Escalation**: Severe non-linear price variations between 45-day early booking ($T+45$) and walk-up / emergency purchase ($T+1$).
3. **Multi-Channel Price Dispersion**: Discrepancies between direct airline NDC/GDS APIs and Online Travel Aggregator (OTA) meta-search feeds.

### 1.2 Proposed Solution: APIx India
APIx India is an automated, sovereign statistical intelligence engine designed to continuously harvest, clean, deduplicate, normalize, and aggregate high-frequency airfare observations across all scheduled domestic Indian routes. It outputs a continuous, quality-adjusted **Airfare Price Index (APIx)** that functions as:
- A high-frequency leading economic indicator for national inflation telemetry.
- An experimental, non-binding microdata augment for official NSO CPI Transport sub-index compilation (providing a **15–19 day predictive lead window** ahead of traditional gazette publication).

*Crucial Boundary*: **APIx India is strictly an econometric analytical instrument, not a commercial flight-booking or consumer price comparison utility.**

---

## 2. Target Personas & Primary Use Cases

| Persona | Role & Organization | Primary Job-to-be-Done | Key Modules Used |
|---|---|---|---|
| **Macroeconomist / NSO Statistician** | National Statistical Office (MoSPI), RBI Monetary Policy Committee | Validate high-frequency price trends against headline CPI; evaluate econometric co-integration and Laspeyres basket weighting. | Overview Dashboard, Methodology & CPI Augmentation, National Bulletin Generator |
| **Data Quality & Pipeline Engineer** | Sovereign Cloud Analytics & NIC Data Center | Monitor automated scraping health, API rate limits, schema pass rates, deduplication efficiency, and quarantine logs. | Data Quality & Anomaly Surveillance, Ingestion Telemetry |
| **Aviation Policy Researcher** | Directorate General of Civil Aviation (DGCA), Ministry of Civil Aviation (MoCA) | Inspect city-pair route volatility, carrier pricing spreads, monopoly routes vs competitive trunk corridors, and advance purchase curves. | Route Analytics, Advance Purchase Matrix, Carrier Intelligence |
| **Market Surveillance Officer** | Competition Commission of India (CCI) / MoSPI Outlier Cell | Investigate sudden algorithmic price surges (e.g., festival gouging, post-cyclone capacity shocks) vs genuine structural fuel-surcharge shifts. | Anomaly Detection & Winsorization Queue |

---

## 3. System Architecture & High-Frequency Data Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. DATA SOURCES & INGESTION                                                 │
│    Direct Airline NDC APIs / GDS Feeds: IndiGo, Air India, AIX, Akasa, SG   │
│    Aggregator Feeds (OTAs): MakeMyTrip, Cleartrip, EaseMyTrip, ixigo        │
│    Target Frequency: 15-minute polling cycles | Daily Throughput: ~140,000+  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. INGESTION, TAX SEPARATION & NORMALIZATION                                │
│    - Base fare vs User Development Fee (UDF), PSF & Fuel Surcharge split    │
│    - Cabin class standardization: Economy Non-Stop, Single Adult Traveller  │
│    - ISO-8601 UTC/IST timestamp synchronization & SHA-256 microdata hashing │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. DEDUPLICATION & OUTLIER TRIMMING (SURVEILLANCE)                          │
│    - MD5/PNR flight-code cross-matching across multi-source OTA redundancy   │
│    - Tukey 1.5× IQR fence on route-horizon clusters                          │
│    - Double Asymmetric Winsorization [p ∈ 1.0%, 97.5%] to clip fake errors   │
│    - Hampel X-bar filter (3.0σ) for dynamic event surge isolation            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. STATISTICAL AGGREGATION & INDEX COMPILATION                              │
│    - 5-Tier Advance Purchase Horizon Stratification (T+1, T+7, T+15, T+30, 45│
│    - Micro-level unweighted geometric mean (Jevons elementary aggregates)   │
│    - Macro-level basket aggregation via DGCA ASK-weighted Laspeyres-Fisher   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. ANALYTICAL SERVING & EXPORT LAYER                                        │
│    - Overview Dashboard with interactive 95% confidence bands               │
│    - CPI Augmentation cross-spectral correlation engine                     │
│    - Automated PDF/CSV Gazette Bulletin generation & MoSPI Sovereign Vault  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Mathematical Formulation & Econometric Methodology

### 4.1 Elementary Price Aggregation (Jevons Micro-aggregation)
For a specific city-pair route $i$, airline carrier $k$, and departure horizon $h \in \{T+1, T+7, T+15, T+30, T+45\}$ observed at time $t$:
$$P_{i, t, h}^- = \left( \prod_{m=1}^{M} p_{k, m} \right)^{1/M}$$
*Where $M$ represents verified non-stop seat inventory quotes collected across observation windows.*

### 4.2 Advance Purchase Horizon Stratification
The composite route price $P_{i, t}$ is weighted across the 5 empirical booking horizons according to DGCA booking lead-time density ($\sum_{h} \lambda_h = 1.000$):
$$P_{i, t} = \sum_{h \in H} \lambda_h \cdot P_{i, t, h}^-$$
- **$T+1$ (Emergency / Walk-up)**: $\lambda_{T+1} = 0.140$
- **$T+7$ (Short-lead business)**: $\lambda_{T+7} = 0.320$
- **$T+15$ (Intermediate plan)**: $\lambda_{T+15} = 0.260$
- **$T+30$ (Advanced personal)**: $\lambda_{T+30} = 0.180$
- **$T+45$ (Early discount apex)**: $\lambda_{T+45} = 0.100$

### 4.3 National Macro-Index Compilation (Chained Modified Laspeyres)
The aggregate National Airfare Price Index ($\text{APIx}_t$) is compiled across $N = 48$ representative domestic trunk city-pairs using Available Seat-Kilometer (ASK) capacity weights ($w_i$):
$$\text{APIx}_t = \left[ \frac{\sum_{i=1}^{N} w_i \cdot P_{i, t}}{\sum_{i=1}^{N} w_i \cdot P_{i, 0}} \right] \times 100$$
- **Base Period**: $T_0 = \text{Jan 1 – Jan 31, 2023}$ ($P_{i, 0} = 100.00$)
- **Capacity Weight Reference**: Directorate General of Civil Aviation (DGCA) annual operational statistics ($w_i$ summing to 1.0000 across 94.6% domestic scheduled ASK).

---

## 5. Feature Requirements & Functional Specification

### 5.1 Persistent Header & Sovereign Navigation
- **Branding**: Official Government of India (MoSPI / NSO) institutional context banner with sovereign indicator and demonstration data badge.
- **Telemetry Indicators**: Real-time IST data freshness timestamp, scheduled batch polling cadence (15-minute intervals), and national ASK monitored percentage (94.6%).
- **Key Navigation Items**:
  1. *Overview Dashboard*
  2. *Airfare Price Index*
  3. *Route Analytics*
  4. *Airline Analytics*
  5. *Advance Purchase Matrix*
  6. *Data Pipeline & Sources*
  7. *Quality & Anomalies*
  8. *CPI Augmentation*
  9. *Methodology & Formulae*
- **Actions**: "Generate National Bulletin" (PDF/CSV report trigger) and analyst authentication node.

### 5.2 Module 1: Overview Dashboard
- **Top Metric Cards**:
  - `Headline APIx`: e.g., **112.8** (+6.4% YoY, +2.1% MoM, +0.8% WoW).
  - `30-Day Moving Mean Fare`: e.g., **₹5,420** with IQR bounds and base variance.
  - `Monitored City-Pairs`: **48 Routes** covering 87.2% total traffic.
  - `Daily Ingestion Harvest`: **~142,850 fare quotes** across 9 multi-source nodes.
  - `Data Pipeline Inventory`: **94.6% Scanned** with <120ms average telemetry latency.
  - `Sovereign Integrity Index`: **93/100 (Grade A Validated)** under MoSPI-QAF-2023.
- **National Trajectory Trendline Chart**:
  - Dual-axis graph (Index values on left, estimated average basket fare on right).
  - Base switchers: Base 2023=100 vs Base 2019=100.
  - Interval toggles: Daily, 7-Day Moving Average, Weekly, Monthly.
  - 95% econometric confidence envelope ribbon ($\pm 1.38$ index points).
  - Milestone annotations: Seasonal festival surges (Diwali peak), adverse weather groundings (Cyclone Dana).
- **Spatial Route Connectivity Matrix**:
  - Hub-and-spoke geometric topology linking Delhi, Mumbai, Bengaluru, Kolkata, Hyderabad, Chennai, Goa, Ahmedabad.
  - Priority Trunk City-Pair Surveillance Table sorting by ASK capacity weight with real-time volatility categorization.
- **Automated Pipeline Microservice Architecture**: Visual 6-stage telemetry cards showing live throughput, error rates, and deduplication stats.

### 5.3 Module 2: Route Analytics & Horizon Pricing
- **Route Filter Selector**: Single/bidirectional selection across trunk and regional sectors (e.g., `DEL ⇄ BOM`, `DEL ⇄ BLR`, `BOM ⇄ BLR`).
- **Carrier Trajectory Multi-Line Chart**:
  - Overlay comparing individual airline medians (IndiGo, Air India, Akasa Air, SpiceJet) against the composite basket.
  - Flight departure bank analysis: Morning Corporate Bank (06:00–09:30), Midday Leisure Valley (11:00–16:00), Evening Peak (17:30–21:30).
- **Yield Escalation Curve ($T+1$ to $T+45$)**:
  - Bar visualization depicting steep price decay as booking horizons lengthen (e.g., $T+1$ ₹8,200 vs $T+45$ ₹4,300).
  - Tabular breakdown across carriers by advance window.
- **Statistical Density & Winsorization**:
  - Box-whisker percentile breakdown ($P_{10}, P_{25}, P_{50}, P_{75}, P_{90}$).
  - Visual clipping cutoff indicator ($₹14,500+$ Extreme Surge Trimmed).
- **Audited Microdata Log**:
  - Tabular inspection of individual scraped quotes containing Carrier Code, Departure Time, Advance Window, Base Fare, Taxes/UDF, Ingestion Source (NDC API vs OTA Feed), Validation State, and SHA-256 Microdata Hash.

### 5.4 Module 3: Data Quality, Ingestion & Anomaly Surveillance
- **Sovereign Quality Score Card**: Composite index (93.4/100) benchmarked against MoSPI Quality Assurance Framework (MoSPI-QAF-2023).
- **Source-Wise Telemetry Grid**: Real-time status for 5 domestic airlines and 4 primary OTAs (MakeMyTrip, Cleartrip, EaseMyTrip, ixigo) detailing:
  - Origin Connection Type (Direct NDC, Amadeus GDS, Web Navitaire Poller, Aggregator Feed).
  - Synchronization Status (`OPERATIONAL`, `DEGRADED (RATE LIMIT)`).
  - 24-Hour Quote Volume, OD Depth, Mean Query Latency, and Schema Validation Pass Rate.
- **Scraping Resilience & Completeness**:
  - 30-day historical success rate chart against pipeline latency.
  - Trunk route by time-of-day coverage matrix heatmap identifying low-frequency gaps.
- **Airfare Anomaly Investigation Queue**:
  - Rule-based algorithmic flag log identifying events requiring statistical clearance.
  - Formula classification: Hampel Rolling Median, Tukey IQR Floor, 3.5-Sigma Peak Filter, Seasonal Multiplier.
  - Action workflow: `APPROVED (WEIGHT CAP)`, `EXCLUDED FROM INDEX`, `UNDER MANUAL REVIEW`, `VALIDATED SURGE`.

### 5.5 Module 4: Methodology & CPI Augmentation
- **Formal Equation Display**: Institutional TeX-styled presentation of elementary aggregation and capacity weighting equations.
- **Trimming Protocol Specifications**: Documentation of IQR fences, Winsorization thresholds, and Kalman imputation models.
- **12-Month Econometric Correlation Benchmarking**:
  - Comparative plot of synthetic APIx-M (monthly rollup) vs official CPI Transport sub-group index (Item 5.3.01) vs Headline General CPI.
  - Empirical statistics: Pearson correlation coefficient ($r = 0.884, p < 0.0001$), Granger causality test ($F = 18.42, p = 0.0028$), and Mean Absolute Percentage Error ($\text{MAPE} = 2.14\%$).
  - Leading Indicator Telemetry showing an empirical **15.8 to 19.4 days advance signal lead** over official NSO gazette publication.
- **Route Stratification Matrix**: Classification of the 48 monitored pairs into Tier-1 Metro Hubs (58.4% ASK weight), Metro-to-Tier-2 Growth (29.2% ASK weight), and Regional RCS-UDAN (12.4% ASK weight).
- **Compliance & Transparency Downloads**: Whitepaper PDF (4.2 MB), Python/R Core Scripts, Model Weight Matrix (CSV), and verification checksums.

---

## 6. Non-Functional Requirements (NFRs)

### 6.1 Performance & Latency
- **Sub-Second Dashboard Rendering**: Client-side rendering of dense SVG econometric charts and route tables must execute in under 400ms on standard desktop browsers.
- **Batch Processing Throughput**: Backend ingestion pipeline must sustain 250+ quotes/second peak during synchronous batch query sweeps.
- **Data Freshness**: Aggregated sub-index cache invalidation every 15 minutes.

### 6.2 Data Integrity, Auditability & Security
- **Immutable Microdata Hashing**: Every ingested fare quote must generate a deterministic SHA-256 cryptographic signature based on `[timestamp, flight_number, departure_date, base_fare, carrier_code]`.
- **Zero Raw Data Modification**: Original observation rows must remain write-protected in raw storage (`AWS-DEL-GOV-01`); outlier clipping applies weights ($w_i = 0$), never record deletion.
- **Statutory Disclaimers**: Continuous UI watermarking: `"DEMONSTRATION STATISTICAL DATA ONLY — PROTOTYPE ECONOMETRIC ENGINE — NOT A CONSUMER BOOKING SERVICE"`.

### 6.3 Accessibility & Institutional Design Standards
- **Color Contrast & Theme**: Strict conformance to WCAG 2.1 AA standards; deep navy institutional background accents (`#0B192C`) paired with high-contrast tabular typography (`Inter`, `JetBrains Mono`).
- **No Reliance on Color Alone**: All warning badges, outlier tags, and operational states must pair color accents with explicit textual status labels and icon glyphs.
- **Responsive Analytical Density**: Optimized primarily for 1440px desktop workstations (NSO economist monitors), responsive down to 1024px tablet/laptop viewing.

---

## 7. Implementation Roadmap & Milestones

| Phase | Milestone | Scope & Deliverables | Timeline | Status |
|---|---|---|---|---|
| **Phase 1** | **System Architecture & High-Fidelity UI Prototyping** | Complete interactive desktop UI prototype covering Overview, Route Analytics, Data Quality, and Methodology screens with design tokens and MoSPI econometric styling. | Month 1–2 | **Completed (v1.0 Ready)** |
| **Phase 2** | **Scraping Pipeline & Sovereign Data Lake Setup** | Deployment of scheduled headless poller microservices across 5 domestic carriers and 4 OTAs; PostgreSQL/TimescaleDB time-series storage; SHA-256 integrity validation. | Month 3–4 | Scheduled |
| **Phase 3** | **Econometric Engine & Winsorization Service** | Implementation of automated Tukey IQR fences, Hampel surge filtering, and Jevons/Laspeyres index mathematical calculators in Python/R. | Month 5–6 | Scheduled |
| **Phase 4** | **CPI Transport Co-integration Testbench** | 6-month shadow execution alongside NSO official field enumerators; correlation benchmarking against official Item 5.3.01 CPI releases; DGCA weight recalibration. | Month 7–9 | Scheduled |
| **Phase 5** | **National Statistical Gateway Production Release** | Government Cloud deployment (NIC MeghRaj / AWS GovCloud); role-based RBAC access for MoSPI, RBI, and DGCA analysts; automated gazette bulletin export. | Month 10–12 | Target Release |

---

*Authored by the High-Frequency Alternative Data Working Group for the National Statistical Office (NSO), MoSPI, Government of India.*