-- =====================================================================
-- APIx India — Sovereign Airfare Microdata & Econometrics Platform
-- Database Schema for Supabase (PostgreSQL 15 / 16)
-- 
-- Features:
--  1. Strict Deduplication: UNIQUE(record_hash) eliminates duplicate quotes.
--  2. MoSPI CPI Time Series: Stores official domestic aviation inflation series (07.3.3.1).
--  3. Scraping Telemetry: Audits scraper execution, duplicates dropped, and yield metrics.
--  4. High-Performance B-tree Indexes on route corridors and timestamps.
--  5. Row-Level Security (RLS) configured for public reads and backend inserts.
-- =====================================================================

-- 1. Table: apix_live_quotes (Deduplicated Live Market Inventory)
CREATE TABLE IF NOT EXISTS public.apix_live_quotes (
    id BIGSERIAL PRIMARY KEY,
    record_hash VARCHAR(16) UNIQUE NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    date_of_journey DATE NOT NULL,
    journey_day VARCHAR(16),
    airline VARCHAR(64) NOT NULL,
    carrier_code VARCHAR(8),
    flight_code VARCHAR(16) NOT NULL,
    class VARCHAR(32) NOT NULL,
    source VARCHAR(32) NOT NULL,
    destination VARCHAR(32) NOT NULL,
    departure_time VARCHAR(16) NOT NULL,
    arrival_time VARCHAR(16),
    duration_hours NUMERIC(6,2),
    stops VARCHAR(16),
    days_left INTEGER,
    fare NUMERIC(10,2) NOT NULL,
    jevons_index NUMERIC(8,2),
    anomaly_status VARCHAR(32) DEFAULT 'VALIDATED_NORMAL',
    scraped_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- Indexing for live queries & corridor analytics
CREATE UNIQUE INDEX IF NOT EXISTS idx_quotes_record_hash ON public.apix_live_quotes(record_hash);
CREATE INDEX IF NOT EXISTS idx_quotes_route_date ON public.apix_live_quotes(source, destination, date_of_journey);
CREATE INDEX IF NOT EXISTS idx_quotes_airline ON public.apix_live_quotes(airline);
CREATE INDEX IF NOT EXISTS idx_quotes_scraped_at ON public.apix_live_quotes(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_quotes_fare ON public.apix_live_quotes(fare);

-- 2. Table: apix_cpi_series (Official MoSPI Domestic Airfare Price Indices)
CREATE TABLE IF NOT EXISTS public.apix_cpi_series (
    id SERIAL PRIMARY KEY,
    item_code VARCHAR(16) DEFAULT '07.3.3.1',
    classification VARCHAR(128) DEFAULT 'Passenger transport by air, domestic',
    year INTEGER NOT NULL,
    month VARCHAR(16) NOT NULL,
    month_num INTEGER NOT NULL,
    ym VARCHAR(7) UNIQUE NOT NULL,
    label VARCHAR(16) NOT NULL,
    combined_index NUMERIC(8,2) NOT NULL,
    combined_inflation_yoy NUMERIC(6,2),
    rural_index NUMERIC(8,2),
    urban_index NUMERIC(8,2),
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cpi_ym ON public.apix_cpi_series(ym);

-- 3. Table: apix_scraper_telemetry (Audit & Yield Telemetry Log)
CREATE TABLE IF NOT EXISTS public.apix_scraper_telemetry (
    id BIGSERIAL PRIMARY KEY,
    run_timestamp TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()),
    engine_status VARCHAR(32) DEFAULT 'ACTIVE_STREAMING',
    quotes_scraped INTEGER NOT NULL,
    duplicates_eliminated INTEGER NOT NULL,
    unique_committed INTEGER NOT NULL,
    deduplication_rate_pct NUMERIC(6,2),
    dutot_mean NUMERIC(10,2),
    jevons_geom_mean NUMERIC(10,2),
    median_p50 NUMERIC(10,2),
    iqr NUMERIC(10,2),
    upper_fence NUMERIC(10,2),
    anomalies_detected INTEGER DEFAULT 0,
    client_source VARCHAR(64) DEFAULT 'vercel_serverless'
);

CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON public.apix_scraper_telemetry(run_timestamp DESC);

-- 4. Analytical Views for Instant Querying
CREATE OR REPLACE VIEW public.v_apix_live_summary AS
SELECT 
    COUNT(*) AS total_unique_quotes,
    ROUND(AVG(fare), 2) AS dutot_mean_fare,
    ROUND(EXP(AVG(LN(GREATEST(fare, 1)))), 2) AS jevons_geom_fare,
    COUNT(DISTINCT airline) AS active_airlines,
    COUNT(DISTINCT (source || '-' || destination)) AS monitored_corridors,
    MAX(scraped_at) AS latest_scrape_time
FROM public.apix_live_quotes;

CREATE OR REPLACE VIEW public.v_apix_corridor_benchmark AS
SELECT 
    source,
    destination,
    COUNT(*) AS quote_volume,
    ROUND(MIN(fare), 0) AS min_fare,
    ROUND(AVG(fare), 2) AS mean_fare,
    ROUND(MAX(fare), 0) AS max_fare,
    COUNT(DISTINCT airline) AS carrier_count
FROM public.apix_live_quotes
GROUP BY source, destination
ORDER BY quote_volume DESC;

-- 5. Row-Level Security (RLS) Configuration
ALTER TABLE public.apix_live_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apix_cpi_series ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.apix_scraper_telemetry ENABLE ROW LEVEL SECURITY;

-- Read Access: Allow anonymous public read for live dashboard visualization
DROP POLICY IF EXISTS "Allow public read access on apix_live_quotes" ON public.apix_live_quotes;
CREATE POLICY "Allow public read access on apix_live_quotes"
    ON public.apix_live_quotes FOR SELECT
    TO anon, authenticated
    USING (true);

DROP POLICY IF EXISTS "Allow public read access on apix_cpi_series" ON public.apix_cpi_series;
CREATE POLICY "Allow public read access on apix_cpi_series"
    ON public.apix_cpi_series FOR SELECT
    TO anon, authenticated
    USING (true);

DROP POLICY IF EXISTS "Allow public read access on apix_scraper_telemetry" ON public.apix_scraper_telemetry;
CREATE POLICY "Allow public read access on apix_scraper_telemetry"
    ON public.apix_scraper_telemetry FOR SELECT
    TO anon, authenticated
    USING (true);

-- Insert Access: Allow serverless functions (anon & service_role) to insert data
DROP POLICY IF EXISTS "Allow insert on apix_live_quotes" ON public.apix_live_quotes;
CREATE POLICY "Allow insert on apix_live_quotes"
    ON public.apix_live_quotes FOR INSERT
    TO anon, authenticated, service_role
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow insert on apix_cpi_series" ON public.apix_cpi_series;
CREATE POLICY "Allow insert on apix_cpi_series"
    ON public.apix_cpi_series FOR INSERT
    TO anon, authenticated, service_role
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow insert on apix_scraper_telemetry" ON public.apix_scraper_telemetry;
CREATE POLICY "Allow insert on apix_scraper_telemetry"
    ON public.apix_scraper_telemetry FOR INSERT
    TO anon, authenticated, service_role
    WITH CHECK (true);
