# Scientific literature

Papers for this project. PDFs stay local and are git-ignored; extracted text lives in `.extracted/`
and is git-ignored too, because it is only a read convenience for agents. Both are regenerate from the
source DOIs.

Read papers as text, never as an uploaded PDF:

```bash
./soberana-borehole-identification-venv/bin/python scripts/pdftext.py \
  docs/scientific-literature/<paper>.pdf
```

Use the venv, not system Python: the `pymupdf` engine decodes CID-keyed fonts that the built-in
parser cannot.

## Router

Which paper answers which question. Retrieved 2026-11-17.

| Question | Paper |
|----------|-------|
| Can a handpump be seen at all, and at what resolution | `malawi-uav-water-points-2020.pdf` |
| How to benchmark small well-pad detection, handle imbalance, split by region | `alberta-wells-2024.pdf` |
| Sentinel-2 patch embeddings across Africa, kNN baseline | `sdg6-from-space-2024.pdf` |
| Undocumented wells, oversampling and data fusion choices | `undocumented-wells-ml-2024.pdf` |
| Sentinel-1 plus Sentinel-2 fusion for unauthorized wells | `illegal-wells-iran-2025.pdf` |
| Plot-scale irrigated area mapping | `irrigated-areas-s1-s2-2021.pdf` |
| Sentinel-1 time-series metrics for irrigation | `irrigation-s1-timeseries-2018.pdf` |

## Set as of 2026-11-17

Seven papers, all open access, all downloaded:

| File | Source |
|------|--------|
| `alberta-wells-2024.pdf` | arXiv 2410.09032 |
| `sdg6-from-space-2024.pdf` | arXiv 2411.19093 |
| `malawi-uav-water-points-2020.pdf` | IJGI 9(10):592, doi 10.3390/ijgi9100592 |
| `undocumented-wells-ml-2024.pdf` | Remote Sens. 16(12):2116, doi 10.3390/rs16122116 |
| `illegal-wells-iran-2025.pdf` | Sci. Rep. 15, doi 10.1038/s41598-025-91188-5 |
| `irrigated-areas-s1-s2-2021.pdf` | Remote Sens. 13(13):2584, doi 10.3390/rs13132584 |
| `irrigation-s1-timeseries-2018.pdf` | Remote Sens. 10(9):1495, doi 10.3390/rs10091495 |

MDPI blocks direct download from this host. The copies above came through the Wayback Machine; if a
file is missing, refetch with `https://web.archive.org/web/2025id_/<mdpi pdf url>`.

## Still to find

- Senegal-specific borehole imagery work, if it exists.
- Papers on detecting water towers or elevated tanks from satellite imagery.
- Any study that maps boreholes from Sentinel data in the Sahel, positive or negative.
