"""
Converts the raw Open-Meteo archive JSON (real ERA5 reanalysis rainfall for
Balaghat, MP) into a clean CSV used by generate_synthetic.py.

Source: Open-Meteo Historical Weather API (archive-api.open-meteo.com),
backed by ECMWF ERA5 reanalysis. Free, no API key. Coordinates: 21.83N,
80.23E (MOIL Balaghat mine). This is REAL rainfall data, not synthetic.
"""
import json
import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "rainfall_balaghat_raw.json")
OUT_PATH = os.path.join(BASE_DIR, "data", "processed", "rainfall_balaghat.csv")


def main():
    with open(RAW_PATH, "r") as f:
        data = json.load(f)

    dates = data["daily"]["time"]
    rain = data["daily"]["precipitation_sum"]

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "rainfall_mm"])
        for d, r in zip(dates, rain):
            writer.writerow([d, r if r is not None else 0.0])

    print(f"Wrote {len(dates)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
