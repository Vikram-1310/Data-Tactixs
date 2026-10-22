import pandas as pd
import pytest

from src.data_analysis import load_roads, analyze_traffic


def test_load_roads_returns_expected_columns_and_boolean(tmp_path):
    path = tmp_path / "roads.csv"
    path.write_text(
        "road_id,from_node,to_node,distance_km,travel_time_min,congestion,blocked\n"
        "R1,A,B,1.0,2.0,low,false\n",
        encoding="utf-8",
    )
    roads = load_roads(path)
    assert list(roads.columns) == [
        "road_id", "from_node", "to_node", "distance_km",
        "travel_time_min", "congestion", "blocked"
    ]
    assert roads.loc[0, "blocked"] is False or roads.loc[0, "blocked"] == False


def test_load_roads_rejects_missing_column(tmp_path):
    path = tmp_path / "roads.csv"
    path.write_text("road_id,from_node,to_node\nR1,A,B\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required columns"):
        load_roads(path)


def test_load_roads_rejects_nonpositive_distance(tmp_path):
    path = tmp_path / "roads.csv"
    path.write_text(
        "road_id,from_node,to_node,distance_km,travel_time_min,congestion,blocked\n"
        "R1,A,B,0,2.0,low,false\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="greater than zero"):
        load_roads(path)


def test_load_roads_rejects_invalid_congestion(tmp_path):
    path = tmp_path / "roads.csv"
    path.write_text(
        "road_id,from_node,to_node,distance_km,travel_time_min,congestion,blocked\n"
        "R1,A,B,1.0,2.0,extreme,false\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Invalid congestion"):
        load_roads(path)


def test_analyze_traffic_counts_sample_dataset():
    roads = load_roads("data/roads.csv")
    result = analyze_traffic(roads)
    assert result["total_roads"] == 12
    assert result["blocked_roads"] == 1
    assert result["congestion_counts"] == {"low": 5, "medium": 4, "high": 3}
    assert result["average_active_road_travel_time_min"] is not None


def test_analyze_traffic_returns_none_if_all_roads_blocked():
    roads = pd.DataFrame({
        "road_id": ["R1"],
        "from_node": ["A"],
        "to_node": ["B"],
        "distance_km": [1.0],
        "travel_time_min": [2.0],
        "congestion": ["low"],
        "blocked": [True],
    })
    result = analyze_traffic(roads)
    assert result["average_active_road_travel_time_min"] is None
