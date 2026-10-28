# Global Olympic Sports Performance Analysis — Working Project

This is a runnable Streamlit dashboard project. It includes:
- KPI cards
- Country medal comparison
- Medal trend chart
- Gold/silver/bronze composition
- Filters for season, country, and year range
- Country summary table and CSV export
- Source notes and responsible data limitations
- Optional upload of your own medal-table CSV

## Run on Windows

1. Install Python 3.10 or newer.
2. Extract the ZIP folder.
3. Open Command Prompt in this folder.
4. Run:

   ```bash
   py -m pip install -r requirements.txt
   py -m streamlit run app.py
   ```

5. Your browser should open the dashboard. If it does not, visit the local URL printed in Command Prompt (usually `http://localhost:8501`).

## Data

By default the app tries to load the public, documented CSV files:
- Medal table: https://raw.githubusercontent.com/ismayc/olympic-moderndive-data/main/data/medal_table_summary.csv
- Editions metadata: https://raw.githubusercontent.com/ismayc/olympic-moderndive-data/main/data/edition_metadata.csv

An internet connection is required for the live source. If it cannot connect, the app can use a small built-in illustrative fallback subset. That fallback is clearly labelled and is **not a full dataset**. Upload a complete source CSV from the data provider for final analysis.

Expected medal CSV fields: `year`, `season`, `country`, `gold`, `silver`, `bronze`; `total` is optional. The official source includes `year`, `season`, `country`, `gold`, `silver`, `bronze`, and `total`.

## Important analytical notes

- The project filters to Olympic editions in 1992–2026.
- 2026 is a Winter Olympic edition; there is no 2026 Summer Olympic Games edition.
- Medal table data should be used for country medal counts. Athlete-event data can count team medals once per roster member.
- The sport/athlete tab is an extension plan; the medal-table CSV itself has no sport-level detail.
- Sports investment and regional efficiency require separately sourced, comparable data. Do not fabricate figures.
- Review source documentation and license before redistribution. Dataset documentation: https://github.com/moderndive/olympicAthletes

## Files

- `app.py` — dashboard code
- `requirements.txt` — Python packages
- `README.md` — this guide
