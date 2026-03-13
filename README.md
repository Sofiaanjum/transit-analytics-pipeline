# TTC Transit Analytics Pipeline

> **End-to-end data engineering pipeline** for Toronto Transit Commission (TTC) transit data — built with Python, Snowflake, dbt, and SQL to deliver analytics-ready datasets for transit operations analysis.

---

## Project Overview

This project simulates a **production-style data engineering pipeline** for public transit analytics, using real TTC GTFS (General Transit Feed Specification) datasets.

Raw transit data is ingested, validated, transformed, and modelled into analytics-ready tables that can power dashboards and operational insights — similar to how a data engineering team at a transit or logistics platform would build their data infrastructure.

**Key analytics this pipeline enables:**
- Route performance and trip frequency analysis
- Stop-level activity and service coverage metrics
- Schedule adherence and service frequency monitoring
- Network-wide operational reporting

---

## Architecture

```
GTFS Static Files
(routes, stops, trips, stop_times)
        │
        ▼
Python Ingestion Scripts
(load_gtfs_static.py)
  - Schema validation
  - Type coercion
  - Bulk load to Snowflake
        │
        ▼
Snowflake Raw Layer
(RAW_ROUTES, RAW_STOPS, RAW_TRIPS, RAW_STOP_TIMES)
        │
        ▼
dbt Transformation Layer
  - Staging models (cleaning + standardization)
  - Intermediate models (joins + business logic)
  - Mart models (analytics-ready tables)
        │
        ▼
Analytics Tables
(route_metrics, stop_metrics, trip_summary)
        │
        ▼
Visualization / Downstream Analysis
```

---

## Tools & Technologies

| Layer | Tool | Purpose |
|-------|------|---------|
| Ingestion | Python (pandas, PyArrow) | Load GTFS files, handle schema conversion |
| Warehouse | Snowflake | Cloud data warehouse — raw + analytics layers |
| Transformation | dbt (data build tool) | Modular SQL transformations, testing, lineage |
| Transformation | SQL | Analytics table logic and metrics calculations |
| Data Format | GTFS Static Feed | Industry-standard transit data specification |

---

## Project Structure

```
ttc-transit-analytics/
│
├── ingestion/
│   ├── load_gtfs_static.py       # Main ingestion script
│   └── schema.py                 # Schema definitions and type mappings
│
├── dbt_project/
│   ├── models/
│   │   ├── staging/              # stg_routes, stg_stops, stg_trips, stg_stop_times
│   │   ├── intermediate/         # int_trip_stop_counts, int_route_trip_counts
│   │   └── marts/                # route_metrics, stop_metrics, trip_summary
│   ├── tests/                    # dbt data quality tests
│   └── dbt_project.yml
│
├── transformations/
│   ├── trip_metrics.sql          # Trip-level aggregations
│   └── route_metrics.sql         # Route-level performance metrics
│
├── warehouse/
│   └── table_definitions.sql     # Snowflake table schemas
│
├── data/
│   └── raw_gtfs_files/           # Source GTFS .txt files
│
├── requirements.txt
└── README.md
```

---

## Data Source

**TTC GTFS Static Feed** — publicly available from the Toronto Transit Commission.

| File | Description |
|------|-------------|
| `routes.txt` | All TTC routes (bus, subway, streetcar) |
| `stops.txt` | Stop locations with coordinates |
| `trips.txt` | Individual scheduled trips per route |
| `stop_times.txt` | Arrival/departure times at each stop |

---

## Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/sofiaanjum/ttc-transit-analytics.git
cd ttc-transit-analytics
```

**2. Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Configure Snowflake credentials**
```bash
cp .env.example .env
# Add your Snowflake account, username, password, warehouse, and database
```

**4. Run ingestion pipeline**
```bash
python ingestion/load_gtfs_static.py
```
Loads raw GTFS files into Snowflake staging tables:
`RAW_ROUTES`, `RAW_STOPS`, `RAW_TRIPS`, `RAW_STOP_TIMES`

**5. Run dbt transformations**
```bash
cd dbt_project
dbt deps
dbt run
dbt test
```

---

## Analytics This Pipeline Answers

| Business Question | Model |
|-------------------|-------|
| Which TTC routes have the most scheduled trips? | `route_metrics` |
| Which stops are served most frequently? | `stop_metrics` |
| How many trips operate per route per day? | `trip_summary` |
| What is the average number of stops per trip? | `trip_metrics` |
| Which routes cover the largest number of stops? | `route_metrics` |

---

## Engineering Challenges Solved

- **Inconsistent GTFS data types** — handled via schema validation layer in `schema.py` before Snowflake load
- **Large file ingestion** — used PyArrow for efficient CSV-to-Snowflake bulk loading
- **Schema alignment** — automated type coercion between GTFS flat files and Snowflake column definitions
- **Transformation modularity** — dbt staging → intermediate → mart layering ensures clean separation of concerns and reusable models

---

## Roadmap

- [ ] Add **GTFS Realtime feeds** for live delay and vehicle position tracking
- [ ] Implement **dbt data quality tests** (not_null, unique, accepted_values)
- [ ] Schedule pipeline using **Apache Airflow**
- [ ] Build **Power BI / Metabase dashboard** for route performance monitoring
- [ ] Add **incremental dbt models** for efficient daily data refresh

---

## Author

**Sofia Ahmed** — Data Engineer  
[LinkedIn](https://www.linkedin.com/in/sofiaanjum) | [Portfolio](https://sofiaanjum.github.io/webportfolio/)  
*Azure Data Engineer Associate | Databricks Certified | AWS Cloud Practitioner*
