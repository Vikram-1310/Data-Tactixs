"""Load, validate, and summarize the RookieRebels road dataset."""
from pathlib import Path
import math
import pandas as pd

REQUIRED_COLUMNS = [
    "road_id", "from_node", "to_node", "distance_km",
    "travel_time_min", "congestion", "blocked"
]
CONGESTION_LEVELS = {"low", "medium", "high"}


def _parse_blocked(value):
    """Convert common CSV boolean representations to bool; reject anything else."""
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        raise ValueError("Column 'blocked' contains a missing value.")
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Invalid blocked value: {value!r}. Use true/false.")


def load_roads(path="data/roads.csv"):
    """
    Load and validate roads from CSV.

    Returns:
        pandas.DataFrame: cleaned records with boolean `blocked`.
    Raises:
        FileNotFoundError: if path does not exist.
        ValueError: if required columns or values are invalid.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Road dataset not found: {path}")

    roads = pd.read_csv(path)
    roads.columns = [str(c).strip() for c in roads.columns]

    missing = sorted(set(REQUIRED_COLUMNS) - set(roads.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    # Keep only the agreed contract columns; ignore extras safely.
    roads = roads[REQUIRED_COLUMNS].copy()

    for column in ("road_id", "from_node", "to_node"):
        roads[column] = roads[column].astype("string").str.strip()
        if roads[column].isna().any() or roads[column].eq("").any():
            raise ValueError(f"Column '{column}' contains missing or empty values.")

    if roads["road_id"].duplicated().any():
        duplicates = roads.loc[roads["road_id"].duplicated(), "road_id"].tolist()
        raise ValueError(f"Duplicate road_id values: {duplicates}")

    for column in ("distance_km", "travel_time_min"):
        roads[column] = pd.to_numeric(roads[column], errors="coerce")
        if roads[column].isna().any():
            raise ValueError(f"Column '{column}' contains missing or non-numeric values.")
        if not roads[column].map(math.isfinite).all():
            raise ValueError(f"Column '{column}' must contain finite numbers.")
        if (roads[column] <= 0).any():
            raise ValueError(f"Column '{column}' must contain values greater than zero.")

    roads["congestion"] = roads["congestion"].astype("string").str.strip().str.lower()
    if roads["congestion"].isna().any() or not roads["congestion"].isin(CONGESTION_LEVELS).all():
        bad = roads.loc[~roads["congestion"].isin(CONGESTION_LEVELS), "congestion"].tolist()
        raise ValueError(f"Invalid congestion values: {bad}. Use low, medium, or high.")

    roads["blocked"] = roads["blocked"].map(_parse_blocked).astype(bool)

    if roads.empty:
        raise ValueError("Road dataset is empty.")

    return roads


def analyze_traffic(roads):
    """
    Summarize traffic in a previously validated roads DataFrame.

    Average travel time excludes blocked roads. Congestion counts include all
    rows so the counts describe the complete dataset.
    """
    missing = sorted(set(REQUIRED_COLUMNS) - set(roads.columns))
    if missing:
        raise ValueError(f"Road DataFrame is missing required columns: {', '.join(missing)}")

    blocked = roads["blocked"].map(_parse_blocked)
    active = roads.loc[~blocked]
    active_times = pd.to_numeric(active["travel_time_min"], errors="coerce")
    average_time = float(active_times.mean()) if not active_times.empty else None

    congestion = roads["congestion"].astype("string").str.strip().str.lower()
    counts = {level: int((congestion == level).sum()) for level in ("low", "medium", "high")}

    return {
        "total_roads": int(len(roads)),
        "blocked_roads": int(blocked.sum()),
        "average_active_road_travel_time_min": average_time,
        "congestion_counts": counts,
    }
