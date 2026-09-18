# APIx India — Production Deployment Guide (Vercel & Supabase)

This turnkey guide walks you through deploying the **APIx India Aviation Analytics & Web Scraping Platform** to **Supabase** (persistent PostgreSQL database & deduplicated data store) and **Vercel** (global Edge CDN frontend & serverless Python API).

---

## Architecture Summary

```
                       ┌──────────────────────────────────────────────┐
                       │          Vercel Global Edge Network          │
                       │                                              │
                       │  • HTML5 / Tailwind / Vanilla JS Dashboard   │
                       │  • dataset1_analytics.js (Aggregated Corpus) │
                       │  • Dynamic SVG Vector Chart Engines          │
                       └───────────────┬──────────────────────────────┘
                                       │
                      Static Frontend  │  REST API Calls (/api/scrape-live)
                                       │
                                       ▼
                       ┌──────────────────────────────────────────────┐
                       │         Vercel Serverless Functions          │
                       │         (/api/index.py - Python 3.12)        │
                       │                                              │
                       │  • Corridor flight inventory scraping        │
                       │  • Canonical SHA-256 deduplication           │
                       │  • Econometric calculations (Jevons, Dutot)  │
                       └───────────────┬──────────────────────────────┘
                                       │
                                       │ HTTPS REST API
                                       │ (Header: Prefer: resolution=ignore-duplicates)
                                       ▼
                       ┌──────────────────────────────────────────────┐
                       │            Supabase Cloud Database           │
                       │                (PostgreSQL 16)               │
                       │                                              │
                       │  • Table: apix_live_quotes (UNIQUE hash)     │
                       │  • Table: apix_cpi_series (MoSPI 07.3.3.1)   │
                       │  • Table: apix_scraper_telemetry             │
                       │  • High-performance B-tree indexes & RLS     │
                       └──────────────────────────────────────────────┘
```

---

## Step 1: Set Up Supabase Database (3 Minutes)

### 1.1 Create a Supabase Project
1. Go to [https://supabase.com](https://supabase.com) and log in or create a free account.
2. Click **"New Project"**.
3. Enter project details:
   - **Name**: `apix-india` (or any preferred name)
   - **Database Password**: Choose a strong password (save it safely).
   - **Region**: Select **South Asia (Mumbai)** for optimal latency to Indian flight corridors.
   - **Pricing Plan**: Free Tier.
4. Click **"Create new project"** and wait ~1–2 minutes for database provisioning.

---

### 1.2 Execute the Database Schema
1. In your Supabase project dashboard, navigate to the **SQL Editor** (icon `>_` on the left sidebar).
2. Click **"New query"**.
3. Open the file [`supabase_schema.sql`](./supabase_schema.sql) in this repository, copy the entire SQL script, and paste it into the Supabase SQL editor.
4. Click **"Run"** (or press `Ctrl+Enter`).
5. You should see `Success. No rows returned`.

> [!NOTE]
> This creates:
> - `apix_live_quotes`: Live quotes table with `record_hash VARCHAR(16) UNIQUE` to enforce strict zero-duplicate storage.
> - `apix_cpi_series`: Official MoSPI domestic airfare inflation time series.
> - `apix_scraper_telemetry`: Scraper execution audit log.
> - `v_apix_live_summary` and `v_apix_corridor_benchmark`: Analytical views.
> - Row-Level Security (RLS) policies allowing public read and authenticated/serverless insert.

---

### 1.3 Copy Your Project API Credentials
1. In Supabase, go to **Project Settings** (gear icon on bottom left) -> **API**.
2. Copy two values:
   - **Project URL**: e.g., `https://your-project-id.supabase.co`
   - **anon / public key**: e.g., `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - *(Optional for elevated access)*: Under **service_role secret**, click reveal and copy the secret key.

---

## Step 2: Seed Supabase with Initial Data (1 Minute)

Run the included [`seed_supabase.py`](./seed_supabase.py) script from your terminal to populate your new Supabase database with the official MoSPI CPI monthly data and initial verified quotes:

```bash
python3 seed_supabase.py --url https://<YOUR_PROJECT_ID>.supabase.co --key <YOUR_SUPABASE_KEY>
```

*Example output:*
```
=================================================================
Connecting to Supabase at: https://xyz.supabase.co
=================================================================
▶ Seeding MoSPI CPI Time Series (07.3.3.1)...
  ✓ Successfully seeded 20 MoSPI CPI monthly records into 'apix_cpi_series'!

▶ Seeding Deduplicated Live Quotes from Live_Scraped_Dataset.csv...
  Found 1200 deduplicated quotes to sync in batches of 100...
  • Batch 1: synced 100/1200 quotes...
  ...
  ✓ Finished quote sync: 1200/1200 records processed into 'apix_live_quotes'.

▶ Seeding Scraping Telemetry Audit Log...
  ✓ Successfully logged initial telemetry into 'apix_scraper_telemetry'!

🎉 Supabase database seeding complete! You can view your tables in the Supabase Table Editor.
```

---

## Step 3: Deploy to Vercel

You have two convenient options to deploy to Vercel:

### Option A: Direct CLI Deployment (Recommended — 60 Seconds)

You are already logged in to Vercel CLI (`harshalrandhave72-8853`). You can deploy directly from your terminal:

1. **Initial Project Link & Staging Deploy**:
   ```bash
   npx vercel
   ```
   When prompted:
   - `Set up and deploy?` → **Y**
   - `Which scope do you want to deploy to?` → Select your active account (`bb-x` or `harshalrandhave72-8853`)
   - `Link to existing project?` → **N**
   - `What's your project's name?` → `apix-india`
   - `In which directory is your code located?` → `./` (press Enter)
   - `Want to modify settings?` → **N**

2. **Set Environment Variables on Vercel**:
   Add your Supabase credentials to Vercel:
   ```bash
   npx vercel env add SUPABASE_URL production
   # (Paste your https://xyz.supabase.co URL when prompted)

   npx vercel env add SUPABASE_KEY production
   # (Paste your Supabase API key when prompted)
   ```

3. **Deploy to Production**:
   ```bash
   npx vercel --prod
   ```
   Vercel will output your live URL, e.g.:
   `https://apix-india.vercel.app`

---

### Option B: Deploy via GitHub (Continuous Deployment)

Your code is already connected to GitHub: `https://github.com/harshal4o4/AVISHKAR.git`.

1. **Commit and Push Recent Changes**:
   ```bash
   git add .
   git commit -m "Configure Vercel serverless deployment and Supabase database integration"
   git push origin main
   ```

2. **Import Project in Vercel Dashboard**:
   - Go to [https://vercel.com/new](https://vercel.com/new).
   - Find **`harshal4o4/AVISHKAR`** in the repository list and click **Import**.
   - **Framework Preset**: Select **Other** (or Leave as auto-detected).
   - **Root Directory**: `./`.
   - Under **Environment Variables**, add:
     - `SUPABASE_URL` = `https://<YOUR_PROJECT_ID>.supabase.co`
     - `SUPABASE_KEY` = `<YOUR_SUPABASE_KEY>`
   - Click **Deploy**.

---

## Step 4: Verify Your Live Deployment

Once Vercel finishes deploying:

1. **Open your production URL**: e.g., `https://apix-india.vercel.app`
2. **Verify Static Dashboard**:
   - The interactive SVG price indices, carrier distribution bars, econometric sliders, and corridor benchmark tables load instantly.
3. **Verify API Endpoints**:
   - Visit `https://apix-india.vercel.app/api/cpi-data` (returns MoSPI 2025–2026 series).
   - Visit `https://apix-india.vercel.app/api/live-status` (returns live scraper status).
   - Visit `https://apix-india.vercel.app/api/scrape-live?count=24` (triggers an instant corridor scrape, runs canonical SHA-256 deduplication, and commits verified records to Supabase).
4. **Check Supabase Table Editor**:
   - Navigate to Supabase **Table Editor** -> `apix_live_quotes`.
   - Observe live quotes arriving in real-time with unique `record_hash` keys.
   - Any duplicate quotes are automatically eliminated at the database level!

---

## Environment Variables Reference

| Variable Name | Required | Purpose | Example Value |
| :--- | :---: | :--- | :--- |
| `SUPABASE_URL` | **Yes** | Supabase Project REST Endpoint | `https://abcdefghijklm.supabase.co` |
| `SUPABASE_KEY` | **Yes** | Supabase `anon` public key or `service_role` key | `eyJhbGciOiJIUzI1NiIsInR5...` |
| `VERCEL` | Auto | Set automatically by Vercel runtime | `1` |

---

## Local Development (Zero Breaking Changes)

You can continue running the project locally at any time without cloud credentials:

```bash
# Start local integrated development server
python3 server.py 8080
```
- Open `http://localhost:8080/index.html`
- Local mode automatically persists data to `Dataset1/Live_Scraped_Dataset.csv`.
- If you export `SUPABASE_URL` and `SUPABASE_KEY` locally in your shell, it will also sync live to Supabase!
