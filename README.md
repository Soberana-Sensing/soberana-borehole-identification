# Water Borehole Identification

Identify water boreholes in the Sahel from free satellite data, with Senegal as the primary target
country. Sentinel-1 and Sentinel-2 are the preferred sensors.

A borehole is the drilled shaft, so the model targets what shows at the surface: the concrete apron,
the pump house or fenced compound, the solar array, and the water tower. Village water supply
systems in Senegal often carry a water tower, which is tall enough to anchor detection in 10 m
imagery. A bare handpump is roughly 0.5 m across and will not resolve at Sentinel-2 resolution.

Status: research phase, started 2026-11-17. Plan and class definitions in `docs/PLAN.md`. WPdx data
download and class filtering done the same day.

## Feasibility, the short form

Feasibility is a per-class question. A bare handpump will not resolve at 10 m. A motorized borehole
compound, and especially a water tower, has a fair chance. Borehole-fed irrigation is the most
promising signature, and it is an area signal, not a point signal. The classes are defined in
`docs/PLAN.md` and stay separate through training and reporting, so the answer comes out as a
verdict per class rather than one number.

## Label sources being assessed

Retrieval date for every row: 2026-11-17.

- Water Point Data Exchange (WPdx-Basic, Socrata dataset `jfkt-jmqa`). 838,209 records globally.
  Senegal has none. Sahel coverage is thin: Niger 1,388, Burkina Faso 957, Mali 819, Gambia 161,
  Chad 125, Mauritania 21. Dense pools sit nearby in Nigeria (119,508), Ethiopia (31,185), Ghana
  (21,928) and Benin (8,597), which makes them the training pool.
- Senegal DGPRE PROGRES database. More than 8,000 water points with coordinates, depth and yield.
  Access by formal request, not open download.
- ANADS microdata catalog, study `SEN-DGPRE-EROH-2013-V1.0`. DGPRE water point inventory covering
  Kaolack, Kaffrine and Thiès. An earlier round covers Fatick and Diourbel.
- GeoSenegal cartothèque. Aquifer units and some water infrastructure layers.

## Layout

| Path | Content |
|------|---------|
| `data/raw/` | data as delivered |
| `data/interim/` | reshaped intermediates |
| `data/derived/` | analysis outputs |
| `docs/` | plan, class definitions, papers |
| `scripts/` | fetch, filter, extract |
| `soberana-borehole-identification-venv/` | project Python, git-ignored |

Data contents are git-ignored; the folders and their READMEs are tracked.

## Licence

To be decided before the first publication of results.
