# Session Notes — DS ML Project

**Branch:** `feature/restructure-notebooks`  
**Dataset:** `assets/investments_VC.csv` — 54,294 startups, 40 features  
**Task:** 3-class classification — predict startup outcome: `closed` (0) / `operating` (1) / `acquired` (2)  
**Models planned:** Logistic Regression, Random Forest, XGBoost

---

## Project Structure (agreed)

```
DS-ml-project/
├── assets/
│   ├── investments_VC.csv              ← raw data
│   └── Supervised Learning Workflow.pdf
├── data/                               ← generated outputs (run notebooks in order)
│   ├── investments_VC_clean.csv        ← output of 01_EDA section 8
│   ├── train_set.csv / validation_set.csv / test_set.csv
│   ├── train_processed.csv / val_processed.csv / test_processed.csv
├── 01_EDA.ipynb                        ← DONE
├── 02_Research_Questions.ipynb         ← DONE
├── 03_Preprocessing.ipynb              ← DONE (pipeline working)
├── 04_Modeling.ipynb                   ← NOT YET CREATED
└── 05_Evaluation.ipynb                 ← NOT YET CREATED
```

---

## What Was Built This Session

### 01_EDA.ipynb — Exploratory Data Analysis
51 cells. Each section ends with a **→ Preprocessing Decision** box.

| Section | Topic | Key Finding |
|---------|-------|-------------|
| 1 | Target variable | 87% operating, 8% acquired, 5% closed — highly imbalanced |
| 2 | Missing values overview | missingno bar + matrix |
| 3.1 | funding_total_usd (25% null) | Fill from rounds_sum where possible; drop rows where rounds_sum=0 |
| 3.2 | Date columns (29% null) | Extract from founded_at; median impute remaining |
| 3.3 | market (16% null) | Fill with "Unknown" |
| 3.4 | country_code / state_code | Fill with "Unknown"; create geo_cluster feature |
| 4 | Outliers / log transform | All funding amounts → log1p; keep originals |
| 4.1 | secondary_market deep-dive | Very sparse (<5% non-zero); zero = no activity (not missing); stronger signal in acquired |
| 5 | Funding rounds | has_round_A/B/C binary flags; round_D_plus = sum of D–H |
| 6 | Funding timeline | days_to_first_funding (founded_at → first_funding_at) |
| 7 | Target encoding | market + country_code → acquisition/closure rate encoding |
| 8 | Export | Saves data/investments_VC_clean.csv |

**Important fixes made:**
- `pandas 2.x` StringDtype issue: all `.loc` assignments to string columns use `.astype(object).fillna().values` pattern
- Cell 3.1 replaced with user-provided comprehensive analysis (rounds_sum validation + scatter plot)

---

### 02_Research_Questions.ipynb
31 cells. Loads from `data/investments_VC_clean.csv`.

Each RQ follows: **H0/H1 → Analysis code → Written Conclusion**

| RQ | Question | Key Finding | Model Feature |
|----|----------|-------------|---------------|
| RQ1 | Does seed amount predict acquisition? | Sweet spot: 500K–2M | `log_seed` |
| RQ2 | Which industries succeed? | Semiconductors/Security 2-3× above average | `market_enc_acquired` |
| RQ3 | Does geography predict success? | Silicon Valley premium; non-USA lowest | `geo_cluster` |
| RQ4 | Does pre-seed funding help? | Angel-backed → higher acq, lower closure | `log_angel` |
| RQ5 | Does fast fundraising signal quality? | <3 months → highest acquisition rate | `days_to_first_funding` |
| RQ6 | Did founding era matter? | Crisis cohort lower; 2012+ suppressed by immaturity | `founded_year` |

**Section 7** links each finding to its model feature and flags two features not yet in the pipeline:
- `had_angel` — binary flag (angel > 0)
- `founding_era` — categorical bucket

---

### 03_Preprocessing.ipynb — sklearn Pipeline
26 cells. Pipeline is **fit on train only**, applied identically to val/test.

**Pipeline steps (in order):**

| Step | Transformer | EDA Source | What it does |
|------|-------------|-----------|--------------|
| 0 | `DTypeConverter` | — | Converts StringDtype numeric cols → float64 (pandas 2.x fix) |
| 1 | `DateFeatureExtractor` | §3.2 | Fills founded_year/month/quarter from founded_at |
| 2 | `CountryFiller` | §3.4 | Fills null country_code → "Unknown" |
| 3 | `MarketFiller` | §3.3 | Fills null market → "Unknown" |
| 4 | `GeoClusterCreator` | §3.4 | Creates geo_cluster (SiliconValley/NY/Boston/Seattle/LA/USA-Other/country/Unknown) |
| 5 | `FundingLogTransformer` | §4 | log1p on all 14 funding amount columns; adds log_ prefix cols |
| 6 | `RoundBinarizer` | §5 | has_round_A/B/C binary flags; round_D_plus = sum of D–H; drops round_D through round_H |
| 7 | `AngelFlagCreator` | RQ4 | had_angel = (angel > 0) binary flag |
| 7 | `FundingTimelineCalculator` | §6 | days_to_first_funding; median-imputes nulls |
| 8 | `TargetEncoder` | §7 | Encodes market + country_code → 4 numeric cols; drops originals |
| 9 | `DateMedianImputer` | §3.2 | Median-imputes remaining founded_year/month/quarter nulls |
| 10 | `ColumnDropper` | — | Drops: permalink, name, homepage_url, category_list, status, state_code, region, city, status_label, founded_at, first_funding_at, last_funding_at |

**Split:** Stratified 70/15/15 (train/val/test) by status_code.

**Known issues resolved this session:**
- `ValueError: could not convert string to float '2011-08'` → `DTypeConverter` step added
- `TypeError: Invalid value for dtype 'str'` → pandas 2.x StringDtype fix via `DTypeConverter`
- `MemoryError` on KNNImputer (1 GB distance matrix) → replaced with `DateMedianImputer`
- `NotFittedError` on transform → `ColumnDropper.fit()` now sets `self.fitted_ = True`

---

## Data Cleaning Decisions (before split, in EDA export)

1. Drop rows where `status` is null (11.4%)
2. Impute `funding_total_usd` from `rounds_sum` where rounds_sum > 0
3. Drop rows where `funding_total_usd` still null AND rounds_sum = 0

---

## What's Left To Do

- [ ] `04_Modeling.ipynb` — train Logistic Regression, Random Forest, XGBoost with `class_weight='balanced'`
- [ ] `05_Evaluation.ipynb` — confusion matrices, classification report, feature importance, final comparison
- [x] `had_angel` binary flag added to pipeline as step 7 (`AngelFlagCreator`) — **re-run 03_Preprocessing.ipynb to regenerate CSVs (45 → 46 features)**
- [ ] Consider adding `founding_era` categorical feature to pipeline (suggested by RQ6)
- [ ] Research remaining nulls after pipeline (null research cells added to section 4 of 03_Preprocessing)
- [x] `secondary_market` discussed and Section 4.1 added to 01_EDA.ipynb (sparsity analysis + outcome relationship)
- [ ] Commit work on `feature/restructure-notebooks` branch

---

## How to Run (in order)

```
1. 01_EDA.ipynb          → generates data/investments_VC_clean.csv
2. 02_Research_Questions.ipynb  → EDA only, no outputs needed
3. 03_Preprocessing.ipynb → generates data/train/val/test_processed.csv
4. 04_Modeling.ipynb     → (not yet created)
5. 05_Evaluation.ipynb   → (not yet created)
```
