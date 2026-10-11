# Kaggle Dataset Analysis Report: Indian Water Quality Data

**Dataset Name:** Indian Water Quality Data  
**Platform Source:** Kaggle (`anbarivan/indian-water-quality-data`)  
**Raw File:** `data/raw/kaggle/water_dataX.csv`  
**Evaluation Date:** August 23, 2026  
**Audience:** DSC 513 Course Evaluation & Project Research Group  

---

## 1. Executive Overview

The Kaggle dataset titled *"Indian Water Quality Data"* is an open-access tabular dataset containing historical water quality measurements from monitoring stations across India. Comprehensive empirical inspection confirms that the file consists of **1,991 rows** and **12 columns** covering the period **2003 to 2014**. The observations represent annualized summary metrics (mean values) derived from historical Central Pollution Control Board (CPCB) monitoring bulletins.

```
Total Rows:               1,991
Total Columns:            12
Temporal Period:          2003 – 2014 (12 discrete years)
Duplicate Rows:           1 duplicate observation
Unique Stations:          321 unique station codes
Unique Text Locations:    666 unique location strings
Unique State Strings:     203 distinct string entries (heavily uncleaned)
Coordinate Availability:  0% (No Latitude or Longitude columns exist)
```

---

## 2. Comprehensive Column-Level Specification

The table below presents the exact schema, storage types, semantic definitions, missingness counts, missingness percentages, and cardinality derived directly from the raw data.

| Column Name | Raw Data Type | Semantic Meaning & Units | Missing Count | Missing % | Unique Values |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `STATION CODE` | `object` (Alphanumeric) | Unique station identifier code | 122 | 6.13% | 321 |
| `LOCATIONS` | `object` (String) | Descriptive monitoring station/waterbody location | 184 | 9.24% | 666 |
| `STATE` | `object` (String) | Indian State / UT name | 761 | 38.22% | 203 |
| `Temp` | `object` (Float string) | Water Temperature ($^\circ\text{C}$) | 92 | 4.62% | 179 |
| `D.O. (mg/l)` | `object` (Float string) | Dissolved Oxygen ($\text{mg/L}$) | 31 | 1.56% | 166 |
| `PH` | `object` (Float string) | Potential of Hydrogen (pH units: 0–14) | 8 | 0.40% | 266 |
| `CONDUCTIVITY (µmhos/cm)` | `object` (Float string) | Electrical Conductivity ($\mu\text{mhos/cm} = \mu\text{S/cm}$) | 25 | 1.26% | 1,005 |
| `B.O.D. (mg/l)` | `object` (Float string) | Biochemical Oxygen Demand ($\text{mg/L}$) | 43 | 2.16% | 408 |
| `NITRATENAN N+ NITRITENANN (mg/l)` | `object` (Float string) | Total Nitrate + Nitrite Nitrogen ($\text{mg/L}$) | 225 | 11.30% | 507 |
| `FECAL COLIFORM (MPN/100ml)` | `object` (Float string) | Fecal Coliform Bacteria ($\text{MPN/100 mL}$) | 316 | 15.87% | 870 |
| `TOTAL COLIFORM (MPN/100ml)Mean` | `object` (Float string) | Total Coliform Bacteria Mean ($\text{MPN/100 mL}$) | 132 | 6.63% | 1,095 |
| `year` | `int64` (Integer) | Calendar Year of annual summary (2003–2014) | 0 | 0.00% | 12 |

> *Note on Missing Value Detection:* In addition to standard standard empty cells / `NA`, string literals such as `"NAN"`, `"NA"`, `"N/A"`, and whitespace blanks were evaluated and included in the total missing count.

---

## 3. Geographic and Temporal Structure

### Geographic Breakdown
1. **Spatial Coordinates:** **Completely absent**. No latitude or longitude coordinates are provided, making direct spatial point GIS mapping impossible without external geocoding of location strings.
2. **State Granularity (`STATE`):** 761 rows (38.22%) have missing state values. Furthermore, the `STATE` column contains 203 distinct raw strings due to severe typographical inconsistency, embedded newlines, trailing spaces, and compound strings (e.g., `'MAHARASHTRA'`, `'MAHARASHTRA '`, `'TAMILNADU'`, `'TAMIL NADU'`, `'ORISSA'`, `'ODISHA'`).
3. **District & River Attributes:** There is no isolated `District`, `Basin`, or `River` column. River names are embedded arbitrarily within the `LOCATIONS` text field (e.g., `'SABARMATI AT AHMEDABAD'`, `'GANGA AT VARANASI'`).
4. **Monitoring Stations:** 321 unique `STATION CODE` values exist, with 122 missing codes.

### Temporal Structure
1. **Observation Frequency:** Observations are reported on an **annual basis**.
2. **Date Range:** 2003 to 2014 (12 discrete years).
3. **Temporal Distribution:**
   * 2003: 49 records
   * 2004: 84 records
   * 2005: 83 records
   * 2006: 100 records
   * 2007: 144 records
   * 2008: 188 records
   * 2009: 180 records
   * 2010: 227 records
   * 2011: 223 records
   * 2012: 247 records
   * 2013: 244 records
   * 2014: 230 records
   *(Reflects the steady expansion of the CPCB National Water Quality Monitoring Programme (NWMP) over time).*

---

## 4. Empirical Statistical and Data-Quality Anomalies

Inspection of parsed numerical values revealed several severe anomalies and data corruption issues:

### A. Catastrophic pH Outliers
* **Theoretical Domain:** Standard chemical scale is $0.0 \le \text{pH} \le 14.0$. Normal river surface waters range between $6.5$ and $8.5$.
* **Empirical Values in Dataset:** Minimum = $0.0$, Maximum = $67,115.0$, Mean = $112.09$.
* **Impossible Values:** **89 rows** contain $\text{pH} > 14.0$, with values such as $705.0$, $11,100.0$, and $67,115.0$.
* **Root Cause Analysis:** Column misalignment during automated PDF report scraping or OCR conversion. Bacteriological coliform counts or conductivity values were shifted left into the pH column.

### B. Corrupted Header Artifacts
* The column header `NITRATENAN N+ NITRITENANN (mg/l)` contains explicit `NAN` substring interpolations. This indicates an upstream string replacement script replaced `NaN` indiscriminately across the raw table headers during table extraction (`"NITRATE N+ NITRITE N"` $\rightarrow$ `"NITRATENAN N+ NITRITENANN"`).

### C. Coliform Extreme Skewness
* `FECAL COLIFORM`: Minimum = $0.0$, Maximum = $272,521,616.0$ MPN/100mL, Median = $221.0$.
* `TOTAL COLIFORM`: Minimum = $0.0$, Maximum = $511,090,873.0$ MPN/100mL, Median = $468.0$.
* While raw untreated sewage discharge can produce millions of coliform counts, the distribution is extremely heavy-tailed and requires log10 transformation prior to statistical analysis.

### D. Duplicate Observation
* Exactly 1 identical duplicate row was detected in the raw dataset (Index row 1,985 vs 1,986).

---

## 5. Summary and Role in Course Project

| Feature | Assessment |
| :--- | :--- |
| **Strengths** | Compact, historical 12-year longitudinal span (2003–2014), covers standard water parameters (DO, BOD, pH, Conductivity, Coliforms). |
| **Limitations** | Zero coordinates (no lat/long), coarse annual aggregates, 38.2% missing states, corrupted pH values in 89 rows, OCR header defects. |
| **Project Role** | **Supporting / Historical Baseline Dataset** (to be used for long-term historical trend comparisons after data cleaning and outlier truncation). |
