"""
Create data/roads.csv from OpenStreetMap road-network data for Vijayawada.

Run from the project root:
    py -m pip install osmnx pandas
    py scripts/build_osm_dataset.py

The road geometry comes from OpenStreetMap. Congestion, travel times, and
blocked-road values are simulated and are NOT live traffic measurements.
"""
from pathlib import Path
import random
import pandas as pd
import osmnx as ox

CITY = "Vijayawada, Andhra Pradesh, India"
OUTPUT = Path("data/roads.csv")
RANDOM_SEED = 42


def main():
    random.seed(RANDOM_SEED)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # The public Overpass service may be busy. Retry later if it returns 429/502.
    G = ox.graph_from_place(CITY, network_type="drive", simplify=True)
    edges = ox.graph_to_gdfs(G, nodes=False, edges=True, fill_edge_geometry=True)

    speed_by_type = {
        "motorway": 60, "trunk": 45, "primary": 35, "secondary": 30,
        "tertiary": 25, "residential": 20, "unclassified": 20,
        "service": 15, "living_street": 10,
    }
    records = []
    for (u, v, key), edge in edges.iterrows():
        length_m = float(edge.get("length", 0))
        if length_m <= 0:
            continue
        highway = edge.get("highway", "unclassified")
        if isinstance(highway, list):
            highway = highway[0] if highway else "unclassified"
        speed = speed_by_type.get(str(highway), 20)
        distance_km = length_m / 1000
        baseline_min = distance_km / speed * 60
        congestion = random.choices(
            ["low", "medium", "high"], weights=[0.45, 0.35, 0.20], k=1
        )[0]
        multiplier = {"low": 1.0, "medium": 1.5, "high": 2.2}[congestion]
        records.append({
            "road_id": f"R{len(records)+1:05d}",
            "from_node": str(u),
            "to_node": str(v),
            "distance_km": round(distance_km, 4),
            "travel_time_min": round(max(0.1, baseline_min * multiplier), 3),
            "congestion": congestion,
            "blocked": random.random() < 0.04,
        })

    columns = [
        "road_id", "from_node", "to_node", "distance_km",
        "travel_time_min", "congestion", "blocked",
    ]
    pd.DataFrame(records, columns=columns).to_csv(OUTPUT, index=False)
    print(f"Saved {len(records)} road segments to {OUTPUT}")
    print("Reminder: congestion, travel times, and blocked flags are simulated.")
    print("Preserve one-way direction in the route optimizer; OSM roads are not all bidirectional.")


if __name__ == "__main__":
    main()
