#!/usr/bin/env python3
"""Sample the feasibility probe set: positives per class plus background negatives.

Output: data/interim/probe_sample.parquet

Why a sampled file and not the whole pool: the probe pulls Sentinel imagery per point, and WPdx
clusters hard (25% of pool labels sit within 50 m of another label, one 0.1 deg cell holds 869). A
uniform random draw would spend the image budget on redundant chips. This sampler caps points per
cell, allocates per country, and adds background points that are provably far from any label.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/interim/probe_sample.parquet"

CLASSES = ["C1_borehole_handpump", "C2_borehole_mechanized", "C2b_borehole_standpost",
           "C3_borehole_untyped"]
PER_CLASS_POOL = 500
PER_CLASS_SAHEL = 200      # Sahel is small on purpose: it is the holdout, not the training set
N_BACKGROUND = 500
MAX_PER_CELL = 2           # 0.1 deg cell, about 11 km
BACKGROUND_MIN_DIST_M = 500.0
SEED = 20261117

R_EARTH = 6371000.0


def cell_id(df: pd.DataFrame) -> pd.Series:
    return (df["lat_deg"].round(1).astype(str) + "_" + df["lon_deg"].round(1).astype(str))


def allocate(total: int, weights: pd.Series) -> pd.Series:
    """Largest-remainder allocation of `total` across the weight index."""
    if weights.sum() == 0:
        return pd.Series(0, index=weights.index)
    raw = weights / weights.sum() * total
    base = np.floor(raw).astype(int)
    short = total - int(base.sum())
    if short > 0:
        order = (raw - base).sort_values(ascending=False).index[:short]
        base.loc[order] += 1
    return base


def sample_stratified(frame: pd.DataFrame, n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Take n points, allocated per country, capped per 0.1 deg cell, prefer newest report."""
    if frame.empty or n <= 0:
        return frame.iloc[0:0]
    frame = frame.copy()
    frame["cell"] = cell_id(frame)
    frame = frame.sort_values("report_date", ascending=False)

    quota = allocate(n, frame.groupby("country_name").size())
    picked = []
    per_cell: dict[str, int] = {}
    for country, want in quota.items():
        if want <= 0:
            continue
        block = frame[frame["country_name"] == country]
        idx = rng.permutation(block.index.to_numpy())
        taken = 0
        for i in idx:
            c = frame.at[i, "cell"]
            if per_cell.get(c, 0) >= MAX_PER_CELL:
                continue
            per_cell[c] = per_cell.get(c, 0) + 1
            picked.append(i)
            taken += 1
            if taken >= want:
                break
    # Country quota may be blocked by the cell cap; fill from the leftovers.
    if len(picked) < n:
        for i in rng.permutation(frame.index.to_numpy()):
            if len(picked) >= n:
                break
            if i in picked:
                continue
            c = frame.at[i, "cell"]
            if per_cell.get(c, 0) >= MAX_PER_CELL:
                continue
            per_cell[c] = per_cell.get(c, 0) + 1
            picked.append(i)
    return frame.loc[picked]


def sample_background(labels: pd.DataFrame, n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Random points inside the label envelope, at least BACKGROUND_MIN_DIST_M from any label.

    The envelope is the 0.5-99.5 percentile box per country, which keeps candidates near
    settlements instead of in open desert or open ocean. Permanent water is not masked here;
    the chip puller drops points on permanent water using the JRC surface water layer.
    """
    tree = BallTree(np.radians(labels[["lat_deg", "lon_deg"]].to_numpy()), metric="haversine")
    rows = []
    countries = labels["country_name"].value_counts()
    per_country = allocate(n, countries)
    for country, want in per_country.items():
        d = labels[labels["country_name"] == country]
        lat_lo, lat_hi = d["lat_deg"].quantile([0.005, 0.995])
        lon_lo, lon_hi = d["lon_deg"].quantile([0.005, 0.995])
        got = 0
        tries = 0
        while got < want and tries < want * 200:
            tries += 1
            cand = np.array([[rng.uniform(lat_lo, lat_hi), rng.uniform(lon_lo, lon_hi)]])
            dist, _ = tree.query(np.radians(cand), k=1)
            if dist[0, 0] * R_EARTH < BACKGROUND_MIN_DIST_M:
                continue
            rows.append({"lat_deg": cand[0, 0], "lon_deg": cand[0, 1],
                         "country_name": country})
            got += 1
        if got < want:
            print(f"  background {country}: {got} of {want} after {tries} tries")
    out = pd.DataFrame(rows)
    out["class"] = "C5_background_negative"
    out["water_source"] = pd.NA
    out["water_tech"] = pd.NA
    out["report_date"] = pd.NaT
    return out


def main() -> int:
    rng = np.random.default_rng(SEED)
    pool = pd.read_parquet(ROOT / "data/interim/wpdx_train_pool.parquet")
    sahel = pd.read_parquet(ROOT / "data/interim/wpdx_sahel.parquet")
    pool["split_group"] = pool["country_name"]
    sahel["split_group"] = sahel["country_name"]

    parts = []
    for cls in CLASSES:
        a = sample_stratified(pool[pool["class"] == cls], PER_CLASS_POOL, rng)
        a["scope"] = "train_pool"
        b = sample_stratified(sahel[sahel["class"] == cls], PER_CLASS_SAHEL, rng)
        b["scope"] = "sahel_holdout"
        print(f"{cls}: pool {len(a)}, sahel {len(b)}")
        parts += [a, b]

    labels = pd.concat([pool, sahel], ignore_index=True)
    bg = sample_background(labels, N_BACKGROUND, rng)
    bg["split_group"] = bg["country_name"]
    bg["scope"] = "background"
    print(f"C5_background_negative: {len(bg)}")
    parts.append(bg)

    keep = ["class", "scope", "split_group", "country_name", "adm1", "lat_deg", "lon_deg",
            "report_date", "water_source", "water_tech", "status"]
    out = pd.concat(parts, ignore_index=True)
    out = out.reindex(columns=[c for c in keep if c in out.columns])
    out.insert(0, "point_id", [f"p{i:05d}" for i in range(len(out))])
    out.to_parquet(OUT, index=False)

    print(f"\nwritten {OUT.relative_to(ROOT)}: {len(out):,} points")
    print(out.groupby(["scope", "class"], observed=True).size().to_string())
    print(f"\ncountries: {out['country_name'].nunique()}")
    print(out.groupby("scope", observed=True)["report_date"].agg(["min", "median", "max"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
