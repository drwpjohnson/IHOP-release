# Li & Tong experimental data — see the canonical description

**The single canonical description of this data now lives in `Records/data_inventory.md`** (section "Data files — the single canonical record", plus §4 layout, §4b cleaning rules, and the C₀ row map). This file is a pointer so the description is not maintained in two places.

## Files here

- `DataFromLi&Tong.xlsx` — the original multi-tab workbook (**source of record**).
- `LiTong_experimental_data_tidy.csv` — plain-text long-format snapshot of exactly what the model uses.
- `extract_tidy_data.py` — regenerates the CSV deterministically from the workbook (reuses the reproducers' loaders).

## Regenerate

```
python extract_tidy_data.py     # with DataFromLi&Tong.xlsx present -> rewrites LiTong_experimental_data_tidy.csv
```

## The one thing to know before reading C₀ from the workbook

C₀ is at **row 14 for `Microspheres Glass Beads Li`** and **row 8 for the other three sheets**. Read the C₀ *cell*, not the header text. Full provenance (including the two Tong favorable columns with no C₀ in the sheet) is in `Records/data_inventory.md`.
