"""Copy the CSVs in this folder into the snapshot block inside index.html.

Served from GitHub Pages the map reads the CSVs directly. Opened from a folder
(double-click) browsers block that, so the map uses the snapshot instead.
Run this after editing any CSV:

    python build_data.py
"""
import csv
import json
import re
from datetime import date


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def soil(path, y_col):
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            y, lat, lng = num(r[y_col]), num(r["Latitude"]), num(r["Longitude"])
            if y is None or lat is None or lng is None:
                continue
            rows.append([r["SiteID"], r["StateID"], lat, lng, y])
    return rows


def waste(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


data = {
    "built": date.today().isoformat(),
    "soil": {
        "top5": soil("mapv0_layer2_top5cm.csv", "Top5_Y"),
        "ahorizon": soil("mapv0_layer1_ahorizon.csv", "A_Y"),
    },
    "waste": waste("coal_waste_ree.csv"),
}

block = "/* SNAPSHOT-START */\nwindow.PHYTO_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n/* SNAPSHOT-END */"
html = open("index.html", encoding="utf-8").read()
new, n = re.subn(r"/\* SNAPSHOT-START \*/.*?/\* SNAPSHOT-END \*/", lambda m: block, html, flags=re.S)
if n != 1:
    raise SystemExit("snapshot markers not found in index.html")
open("index.html", "w", encoding="utf-8").write(new)
print("index.html updated:", len(data["soil"]["top5"]), "top-5 cm rows,",
      len(data["soil"]["ahorizon"]), "A-horizon rows,", len(data["waste"]), "coal waste rows")
