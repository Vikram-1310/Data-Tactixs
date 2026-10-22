# RookieRebels — Member 1: Data Analytics

This package contains Member 1's data-analysis module, tests, a small synthetic
CSV for immediate local testing, and a script to build a road-network dataset
from OpenStreetMap for Vijayawada.

## Folder structure

```text
rookierebels_member1/
├── data/roads.csv
├── src/__init__.py
├── src/data_analysis.py
├── tests/test_data_analysis.py
├── scripts/build_osm_dataset.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup (Windows PowerShell)

From this folder, run:

```powershell
py -m pip install -r requirements.txt
py -m pytest tests/test_data_analysis.py -v
```

The sample `data/roads.csv` has 12 **fictional** road segments for testing. It
is not actual Vijayawada road data.

## Build the OpenStreetMap road-network CSV

Run:

```powershell
py scripts/build_osm_dataset.py
```

Internet access is required. The public Overpass server can be temporarily busy;
if it returns 502/429, wait and retry later. The generated road connections
are from OpenStreetMap, while `travel_time_min`, `congestion`, and `blocked`
are simulation values, not live traffic observations.

Give attribution to OpenStreetMap contributors and review ODbL requirements
before sharing or publishing derived datasets. The network may include one-way
roads; the route optimizer should preserve edge direction rather than assuming
all roads are bidirectional.

## Function interface

- `load_roads(path="data/roads.csv")` returns a validated Pandas DataFrame.
- `analyze_traffic(roads)` returns:
  - `total_roads`
  - `blocked_roads`
  - `average_active_road_travel_time_min` (None if all roads are blocked)
  - `congestion_counts` with `low`, `medium`, and `high`

## Scope boundary

Member 1 owns data preparation, validation, traffic statistics, and tests.
Member 2 owns route optimization. Member 3 owns the Streamlit dashboard and
integration. Coordinate the function interface with teammates before merging.
