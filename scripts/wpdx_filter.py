#!/usr/bin/env python3
"""Filter WPdx-Basic into Sahel training pools and borehole classes.

Input:  data/raw/wpdx/wpdx_basic_2026-11-17.csv (Socrata export, 706,294 rows)
Output: data/interim/wpdx_sahel.parquet
        data/interim/wpdx_train_pool.parquet
        data/interim/wpdx_summary.csv

Class definitions live in docs/PLAN.md. Do not change them here alone.
"""

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/wpdx/wpdx_basic_2026-11-17.csv"
OUT = ROOT / "data/interim"

SAHEL = ["Senegal", "Mali", "Burkina Faso", "Niger", "Chad", "Mauritania", "Gambia",
         "Guinea-Bissau"]
# Dryland countries with dense WPdx coverage; transfer-training pool for the Sahel target.
TRAIN_POOL = ["Nigeria", "Ghana", "Benin", "Burkina Faso", "Mali", "Niger", "Ethiopia",
              "Kenya", "Uganda", "Malawi", "Chad", "Gambia", "Mauritania"]

KEEP = ["#source", "#lat_deg", "#lon_deg", "#report_date", "#status_id", "#water_source",
        "#water_tech", "#country_name", "#adm1", "#adm2", "#install_year", "#management",
        "#pay", "#status"]

HAND_PUMP = re.compile(
    r"hand\s*pump|afridev|afridive|afrideve|aferdive|india\s*(mark|mk)\s*(ii|2|iii|3)?|"
    r"mark\s*(ii|2|3)\b|vergnet|\bpump\s*#?\s*6\b|pump_n_6|nira|bush\s*pump|"
    r"blue\s*pump|foot\s*pump|lever\s*pump|rope\s*pump|volanta|petite\s*pompe|"
    r"pompe\s*a\s*motricite\s*humaine|mono\s*pump|tara\s*pump|sweet\s*water|"
    r"super\s*mono|n\s*6\b",
    re.I)
# Tap stands and water posts. Fed by a scheme, so the surface signature is a stand,
# not a borehole head. Kept as its own class: PEA and kiosks are the village supply
# points we care about in the Sahel.
STANDPOST = re.compile(
    r"poste[s]?\s*d'?\s*eaux?\s*autonome[s]?|\bpea\b|kiosk|kiosque|borne\s*fontaine|"
    r"stand\s*post|stand\s*pipe|standpipe|public\s*tap|tap\s*stand|tapstand|"
    r"water\s*kiosk|fontainier|yard\s*tap|household\s*connection",
    re.I)
MECHANIZED = re.compile(
    r"motoris|motoriz|electrical|electric|submersible|solar|mechani[sz]ed|diesel|"
    r"generator|grid|immersed|immers[ée]|power\s*pump|centrifugal|turbine",
    re.I)
BOREHOLE = re.compile(r"bore\s*hole|bor[eé]hole|tube\s*well|tubewell|forage|"
                      r"mechanized\s*borehole|non-mechanized\s*borehole", re.I)
# Dug wells and céanes are a different surface signature from a drilled borehole.
WELL = re.compile(r"\bwell\b|\bceane\b|c[ée]ane|puits", re.I)

_IDENT = re.compile(r"[\s_\-/,.()]+")


def norm(value) -> str:
    """Lowercase, fold accents and collapse separators.

    WPdx free text mixes underscores, hyphens, accents and stray punctuation across
    surveys. `Pompe à motricité humaine` and `Pompe a motricite humaine` are the same
    handpump and must match the same pattern; `India_Mark_II` and `india mark ii` too.
    """
    if not isinstance(value, str):
        return ""
    folded = unicodedata.normalize("NFKD", value)
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return _IDENT.sub(" ", folded.lower()).strip()


def classify(source, tech) -> str:
    """Return one of the five label classes."""
    s = norm(source)
    t = norm(tech)
    both = f"{s} {t}"
    if HAND_PUMP.search(both):
        return "C1_borehole_handpump"
    if STANDPOST.search(t) or STANDPOST.search(s):
        return "C2b_borehole_standpost"
    # A bare "gravity" tech is a gravity-fed scheme: tap stands piped from a source
    # uphill, no borehole head at the point unless the text says so.
    if t.startswith("gravity") and not BOREHOLE.search(both):
        return "other_water_point"
    if MECHANIZED.search(both):
        return "C2_borehole_mechanized" if BOREHOLE.search(both) else "other_water_point"
    if BOREHOLE.search(both):
        return "C3_borehole_untyped"
    if WELL.search(s):
        return "other_water_point"
    return "other_water_point"


def load() -> pd.DataFrame:
    df = pd.read_csv(RAW, usecols=KEEP, low_memory=False)
    df = df.rename(columns=lambda c: c.lstrip("#"))
    df["lat_deg"] = pd.to_numeric(df["lat_deg"], errors="coerce")
    df["lon_deg"] = pd.to_numeric(df["lon_deg"], errors="coerce")
    df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce", format="mixed")
    df = df.dropna(subset=["lat_deg", "lon_deg"])
    df = df[df["lat_deg"].between(-35, 37) & df["lon_deg"].between(-18, 52)]
    df["class"] = [classify(s, t) for s, t in zip(df["water_source"], df["water_tech"])]
    df["wpdx_class"] = df["class"]
    return df


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load()
    df["country_name"] = df["country_name"].astype("string")

    sahel = df[df["country_name"].isin(SAHEL)].copy()
    pool = df[df["country_name"].isin(TRAIN_POOL)].copy()

    # Same physical point reported by several surveys. Keep the newest report per
    # 5-decimal cell (~1 m) and class, so a point cannot straddle two classes.
    key = ["lat_deg", "lon_deg", "class"]
    for frame in (sahel, pool):
        frame["lat_r"] = frame["lat_deg"].round(5)
        frame["lon_r"] = frame["lon_deg"].round(5)
    sahel = (sahel.sort_values("report_date")
             .drop_duplicates(subset=["lat_r", "lon_r", "class"], keep="last"))
    pool = (pool.sort_values("report_date")
            .drop_duplicates(subset=["lat_r", "lon_r", "class"], keep="last"))

    sahel.to_parquet(OUT / "wpdx_sahel.parquet", index=False)
    pool.to_parquet(OUT / "wpdx_train_pool.parquet", index=False)

    summary = (pd.concat([sahel.assign(scope="sahel"), pool.assign(scope="train_pool")])
               .groupby(["scope", "country_name", "class"]).size()
               .rename("n").reset_index())
    summary.to_csv(OUT / "wpdx_summary.csv", index=False)

    print(f"rows read: {len(df):,}")
    print(f"sahel: {len(sahel):,}   train_pool: {len(pool):,}")
    print(summary.to_string(index=False))
    for frame, name in ((sahel, "sahel"), (pool, "train_pool")):
        d = frame["report_date"].dropna()
        if len(d):
            print(f"{name} report dates: {d.min().date()} to {d.max().date()}, "
                  f"median {d.median().date()}, {len(d):,} dated of {len(frame):,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
