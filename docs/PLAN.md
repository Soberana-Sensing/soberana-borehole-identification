# Plan — Water Borehole Identification, Sahel

Working order for this project. Binding until replaced. Scoped 2026-11-17.

## Question

Can free Sentinel-1 and Sentinel-2 data locate water boreholes in the Sahel, with Senegal as the
primary target country? Answer it per class, not as one verdict. A negative result for one class is
a result.

## Why classes first

A borehole is a shaft. Nothing of it shows from orbit. What shows is the surface signature: apron,
compound, pump house, solar array, water tower, trampled ground, irrigated plot. Those signatures
differ by orders of magnitude in size. So feasibility is a per-class question and the classes must
stay separate through data prep, training and reporting.

## Classes

| ID | Class | Surface signature | Expected at 10 m |
|----|-------|-------------------|------------------|
| C1 | `borehole_handpump` | Concrete apron ~2-3 m, handpump ~0.5 m, often a small fence | Not separable. Malawi UAV study needed 30 cm WorldView-3 and still struggled on unprotected points (van den Homberg et al., 2020) |
| C2 | `borehole_mechanized` | Pump house, fenced yard, solar array, generator pad, sometimes a water tower | Plausible. Compound and tower carry 3-10 m features |
| C3 | `borehole_untyped` | Borehole recorded, technology unrecorded; mix of C1 and C2 footprints | Bounded by C1 and C2 outcomes |
| C4 | `borehole_fed_irrigation` | Dry-season green plot, NDVI anomaly, NDWI moisture signal, wet soil in Sentinel-1 | Most plausible. Area-level, not point-level. Bazzi et al. 2021 and Gao et al. 2018 map irrigated plots with Sentinel-1 and Sentinel-2 |
| C5 | `background_negative` | Random points outside known water point buffers | Baseline class, must be sampled far from any water point |

C4 is derived, never present in WPdx. Build it from Sentinel-2 NDVI and NDWI seasonality around known
boreholes, then from unlabeled space where a borehole is suspected.

## Data inventory

| Item | Detail | Date |
|------|--------|------|
| WPdx-Basic | Socrata `jfkt-jmqa`, 706,294 raw rows, 576,803 after bbox and coordinate cleaning | retrieval 2026-11-17 |
| WPdx Sahel subset | 3,141 points: Burkina Faso 807, Niger 1,465, Mali 780, Gambia 130, Chad 45, Mauritania 14, Senegal 0 | report dates 2003-02-15 to 2022-03-04, median 2014-11-16 |
| WPdx training pool | 263,877 points: Nigeria 123,160, Uganda 99,607, Ethiopia 12,352, Kenya 32,874, Benin 8,597, Malawi 1,956, Ghana 1,198, Burkina Faso 807, Mali 780, Niger 1,465 | report dates 1998-12-15 to 2024-12-01, median 2015-01-27 |
| Senegal DGPRE PROGRES | >8,000 water points, on formal request | access not yet requested |
| ANADS inventory | `SEN-DGPRE-EROH-2013-V1.0`, Kaolack, Kaffrine, Thiès | survey 2013, earlier round 2007 |
| Papers | 7 PDFs in `docs/scientific-literature/`, text in `.extracted/` | retrieved 2026-11-17 |

Senegal has no WPdx records at all. Train on the label-rich dryland countries, validate on Senegal.

## Phases

### Phase 1 — labels and sampling (started 2026-11-17)

1. WPdx filtered to classes, de-duplicated on 5-decimal cells per class. Done, `scripts/wpdx_filter.py`.
2. Sample positives per class, geographically clustered and split by region not by point. Point-level
   splits leak: neighbouring points share the same imagery.
3. Sample C5 negatives: random points at least 500 m from any water point.
4. Request DGPRE access and download the ANADS 2013 inventory.

Gate: at least 500 positives per class that has a chance (C2, C3, C4) plus matching negatives.

### Phase 2 — feasibility probe

1. Sentinel-2 L2A chips, 256x256, 10 m, year matched to WPdx report date, dry season. Two seasons per
   site: end of dry season and end of wet season.
2. Sentinel-1 GRD VV/VH composites over the same windows.
3. Per class, eyeball 50 chips and compute simple separability: NDVI, NDWI, NDBI, SAR backscatter, and
   a kNN on frozen embeddings.
4. Write the verdict per class with numbers, not impressions.

Gate: a class is worth modelling only if a frozen-embedding kNN beats the C5 baseline by more than
10 points AUROC.

### Phase 3 — model

Only for classes that pass Phase 2. Patch classifier first, then object detection if C2 structures
resolve. Transfer from Clay or Prithvi embeddings, plus the Alberta Wells benchmark as a structural
prior for small cleared pads.

### Phase 4 — Senegal validation and extrapolation

Validate on ANADS points and on field-verified sightings. Report precision at fixed recall, per class.
Map candidates outside known registries, which is the actual product: undocumented boreholes.

## Non-goals

- Point detection of bare handpumps from Sentinel-2. Documented as infeasible unless Phase 2
  contradicts the literature.
- Mapping wells and traditional `céanes`. Different signature, different class if wanted later.
- Commercial imagery until free-data feasibility is settled.

## Papers

Retrieved 2026-11-17, texts in `docs/scientific-literature/.extracted/`.

| File | Use |
|------|-----|
| `malawi-uav-water-points-2020.pdf` | Resolution floor for water point detection, why handpumps fail |
| `alberta-wells-2024.pdf` | Small-pad detection benchmark, imbalance handling, splits by region |
| `sdg6-from-space-2024.pdf` | DINO embeddings on Sentinel-2 patches over Africa, kNN baseline |
| `undocumented-wells-ml-2024.pdf` | Undocumented well detection, oversampling and data fusion |
| `illegal-wells-iran-2025.pdf` | Sentinel-1 and Sentinel-2 fusion for unauthorized wells, GIS scoring |
| `irrigated-areas-s1-s2-2021.pdf` | Plot-scale irrigated area mapping, C4 method |
| `irrigation-s1-timeseries-2018.pdf` | Sentinel-1 time series metrics for irrigation, C4 features |
