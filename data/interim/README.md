# data/interim

Reshaped intermediates derived from `raw/`. Contents are git-ignored except the class summary.

- `wpdx_sahel.parquet` — WPdx points in Senegal, Mali, Burkina Faso, Niger, Chad, Mauritania,
  Gambia, Guinea-Bissau. 3,141 rows after de-duplication. Report dates 2003-02-15 to 2022-03-04,
  median 2014-11-16.
- `wpdx_train_pool.parquet` — dryland countries with dense WPdx coverage, used as the transfer
  training pool. 263,877 rows. Report dates 1998-12-15 to 2024-12-01, median 2015-01-27.
- `wpdx_summary.csv` — tracked. Row counts by scope, country and class.

Regenerate with `./soberana-borehole-identification-venv/bin/python scripts/wpdx_filter.py`.
Class definitions: `docs/PLAN.md`.
