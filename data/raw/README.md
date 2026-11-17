# data/raw

Data as delivered by the source. Never edited in place. Contents are git-ignored.

## wpdx/

- `wpdx_basic_2026-11-17.csv` — full WPdx-Basic export from Socrata dataset `jfkt-jmqa`,
  `accessType=DOWNLOAD`. 491 MB, 706,294 rows, 31 columns. Retrieved 2026-11-17. The Socrata legacy
  export endpoint carries a deprecation header with sunset 2026-12-22, so a refetch after that date
  needs the replacement API.
- Point report dates in the raw file run from 1998-12-15 to 2024-12-01. Senegal has no records.

Filtering and class assignment: `scripts/wpdx_filter.py`, output in `data/interim/`.
