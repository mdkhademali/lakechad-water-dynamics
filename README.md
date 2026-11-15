# Lake Chad open-water dynamics from Landsat (1990–2023)

Supplementary code and data for the manuscript *Unpacking Human Pressures and
Climate-Conflict Dynamics Driving Interconnected Vulnerabilities in Lake Chad and
Pathways to Sustainability*.

The repository contains the Google Earth Engine (GEE) scripts that extract open water
with the Modified Normalized Difference Water Index (MNDWI), the sampling design and
metrics for the accuracy assessment, and the code that draws the figures.

## Analysis in brief

| Item | Setting |
|---|---|
| Observation years | 1990, 2003, 2013, 2023 (April–June composites) |
| Sensors | Landsat 5 TM (1990), Landsat 7 ETM+ (2003), Landsat 8 OLI (2013, 2023) |
| Data | Landsat Collection 2 Level-2 surface reflectance, Tier 1, 30 m |
| Scene filter | `CLOUD_COVER < 20` (scene level); no pixel-level cloud or shadow mask |
| Composite | Median of all scenes in the window |
| Index | MNDWI = (Green − SWIR1) / (Green + SWIR1) |
| Water threshold | MNDWI > 0.2, identical for all years |
| Area | Sum of water-pixel areas inside one fixed study polygon (≈ 18,315 km²) |
| Accuracy | 100 mapped-water + 100 mapped-non-water random points per year (800 in total) |

## Repository structure

```
.
├── gee/
│   ├── 01_water_extraction_and_area.js   # composites, MNDWI, water masks, areas, reproduction check
│   ├── 02_scene_ids.js                   # scene IDs of every composite (Supplementary Table S1)
│   └── 03_accuracy_sampling.js           # stratified random reference points
├── python/
│   ├── accuracy_metrics.py               # OA, Wilson 95% CI, Kappa, UA, PA
│   └── make_figures.py                   # Figures 3, 4 and 5
├── data/
│   ├── water_area_summary.csv            # area, scenes and change from 1990
│   ├── confusion_matrices.csv            # TP, FP, FN, TN per year
│   ├── accuracy_summary.csv              # output of accuracy_metrics.py (Table 4)
│   ├── scene_ids.csv                     # output of gee/02_scene_ids.js (Table S1)
│   ├── reference_points_labelled.csv     # labelled accuracy points
│   └── study_area/                       # study-area polygon
├── figures/                              # Figures 3–5 (PNG, Figure 3 also PDF)
├── requirements.txt
└── LICENSE
```

## How to run

**1. Earth Engine scripts** (Code Editor, https://code.earthengine.google.com)

1. Upload `data/study_area/` as an Earth Engine asset and set `STUDY_AREA_ASSET` at the
   top of each script.
2. Run `gee/01_water_extraction_and_area.js`. The console prints the number of scenes and
   the water area for each year and compares them with the values reported in the
   manuscript (`Reproduction check: OK`). Set `EXPORT_MASKS = true` to export the binary
   water masks as GeoTIFF.
3. Run `gee/02_scene_ids.js` and start the export task (Tasks tab) to obtain the scene list.
4. Run `gee/03_accuracy_sampling.js` and start the export task to obtain the sampling points.
   Reference labels are then added by visual interpretation in a column `reference`
   (1 = open water, 0 = non-water; flooded vegetation and wet soil count as non-water).

The configuration block (collections, bands, dates, cloud filter) is repeated at the top of
each script and must be kept identical. Note that Earth Engine's `filterDate` excludes the
end date, so the windows end on 30 June without including that day.

**2. Python** (3.9 or newer)

```bash
pip install -r requirements.txt

# accuracy metrics (from the confusion matrices, or directly from labelled points)
python python/accuracy_metrics.py
python python/accuracy_metrics.py --points data/reference_points_labelled.csv

# figures
python python/make_figures.py
```

## Results reproduced by the code

| Year | Sensor | Scenes | Water area (km²) | Change from 1990 |
|---|---|---|---|---|
| 1990 | Landsat 5 TM | 4 | 1,860.40 | – |
| 2003 | Landsat 7 ETM+ | 4 | 1,733.56 | −126.84 km² (−6.8%) |
| 2013 | Landsat 8 OLI | 14 | 1,440.44 | −419.96 km² (−22.6%) |
| 2023 | Landsat 8 OLI | 17 | 1,427.51 | −432.89 km² (−23.3%) |

| Year | OA (%) | 95% CI (Wilson) | Kappa | Water UA (%) | Water PA (%) |
|---|---|---|---|---|---|
| 1990 | 92.0 | 87.40–95.02 | 0.84 | 91.0 | 92.9 |
| 2003 | 93.0 | 88.59–95.78 | 0.86 | 94.0 | 92.2 |
| 2013 | 91.5 | 86.81–94.63 | 0.83 | 93.0 | 90.3 |
| 2023 | 92.5 | 88.00–95.40 | 0.85 | 93.0 | 92.1 |

## Data dictionary

**`confusion_matrices.csv`**: rows of the confusion matrix are the mapped classes
(the sampling strata), columns are the reference classes.

| Column | Meaning |
|---|---|
| `year` | Observation year |
| `TP` | Mapped water, reference water |
| `FP` | Mapped water, reference non-water |
| `FN` | Mapped non-water, reference water |
| `TN` | Mapped non-water, reference non-water |

**`reference_points_labelled.csv`**: `year`, `mapped` (1 = water, 0 = non-water),
`reference` (1 = water, 0 = non-water), and the point coordinates.

**`scene_ids.csv`**: `year`, `collection`, `scene_id`, `acquisition_date`, `cloud_cover`,
`wrs_path`, `wrs_row`.

## Notes and limitations

- Accuracy metrics are sample-based and not area-adjusted. The reference labels were
  interpreted from Landsat imagery (no higher-resolution imagery is available for 1990),
  so the assessment is not fully independent of the mapped data.
- The 1990 and 2003 composites rest on four scenes each, and Landsat 7 ETM+ scenes acquired
  after 31 May 2003 contain scan-line gaps (SLC-off). The 2003 to 2013 change also spans a
  change of sensor (ETM+ to OLI).
- The maps show open water within the study polygon, not total wetland or flooded-vegetation
  extent. Estimated areas depend on the MNDWI threshold and on the season of the composite.
- Reported changes are differences between selected April–June snapshots, not a continuous
  annual record.

## License

Code is released under the MIT License (see `LICENSE`). Landsat data are provided by the
U.S. Geological Survey and are in the public domain.

## Citation

If you use this code, please cite the associated manuscript (full reference to be added on
publication).
