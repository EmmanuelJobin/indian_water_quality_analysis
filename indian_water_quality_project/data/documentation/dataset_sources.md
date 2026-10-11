# Dataset Sources and Provenance Documentation

**Project Topic:** Geographic and Temporal Analysis of Surface Water Quality in India Using Historical and Official Water-Quality Data  
**Course:** DSC 513 - Introduction to Data Science (M.Tech)  
**Date of Acquisition:** August 23, 2026  
**Investigator:** M.Tech Data Science Research Group  

---

## 1. Official National Water Data Portal (NWDP) / Central Pollution Control Board (CPCB) Data

### Overview
Official government water quality data produced by the **Central Pollution Control Board (CPCB)**, Ministry of Environment, Forest and Climate Change (MoEFCC), and disseminated through the **National Water Data Portal (NWDP)** / National Water Informatics Centre (NWIC), Department of Water Resources, River Development and Ganga Rejuvenation, Ministry of Jal Shakti, Government of India.

### A. Surface Water Quality (Manual - Physical Parameters)
* **Dataset Name:** Surface Water Quality (Manual - Physical Parameters), Central Pollution Control Board (CPCB)
* **Publishing Organization:** Central Pollution Control Board (CPCB) / National Water Informatics Centre (NWIC)
* **Source Portal:** National Water Data Portal (NWDP)
* **Direct Portal URL:** [https://nwdp.nwic.gov.in/dataset/surface-water-quality-manual-physical-parameters-cpcb](https://nwdp.nwic.gov.in/dataset/surface-water-quality-manual-physical-parameters-cpcb)
* **API Package Identifier:** `surface-water-quality-manual-physical-parameters-cpcb` (ID: `c547abaa-fbdc-4f46-b152-dc023be0c75c`)
* **Download Date:** August 23, 2026
* **Data Format:** CSV (Comma-Separated Values)
* **Distribution Scheme:** 104 state-wise and epoch-wise CSV files (covering 36 States/UTs across monitoring epochs 1961–2020 and 2021–2025)
* **Actual Empirical Temporal Coverage:** January 10, 2018 to December 31, 2021 (Monthly/Periodic sampling events)
* **License / Open Data Policy:** Government of India Open Data Policy / National Data Sharing and Accessibility Policy (NDSAP)
* **Key Monitored Parameters:** Electrical Conductivity ($\mu\text{S/cm}$), Turbidity (NTU), Colour, Odour, Total Solids (mg/L), Temperature ($^\circ\text{C}$).
* **Geospatial Attributes:** Station Name, State, State LGD Code, District, District LGD Code, Tehsil, Decimal Latitude, Decimal Longitude (EPSG:4326 / WGS84).

### B. Surface Water Quality (Manual - Chemical Parameters)
* **Dataset Name:** Surface Water Quality (Manual - Chemical Parameters), Central Pollution Control Board (CPCB)
* **Publishing Organization:** Central Pollution Control Board (CPCB) / NWIC
* **Source Portal:** National Water Data Portal (NWDP)
* **Direct Portal URL:** [https://nwdp.nwic.gov.in/dataset/surface-water-quality-manual-chemical-parameters-cpcb](https://nwdp.nwic.gov.in/dataset/surface-water-quality-manual-chemical-parameters-cpcb)
* **API Package Identifier:** `surface-water-quality-manual-chemical-parameters-cpcb` (ID: `d54d7702-d21f-408f-8dc0-2665bde47201`)
* **Download Date:** August 23, 2026
* **Data Format:** CSV
* **Distribution Scheme:** 106 state-wise and epoch-wise CSV files (covering 36 States/UTs)
* **Actual Empirical Temporal Coverage:** January 1, 2018 to July 1, 2024 (Core coverage: 2018–2021, with 82 records in 2023–2024)
* **License / Open Data Policy:** Government of India Open Data Policy (NDSAP)
* **Key Monitored Parameters:** Potential of Hydrogen (pH), Dissolved Oxygen (mg/L), Ammonia-N (mgN/L), Nitrate-N (mgN/L), Arsenic (mg/L), Cadmium (mg/L), Iron (mg/L), Mercury (mg/L), Lead (mg/L), Total Dissolved Solids (mg/L), Total Alkalinity, Calcium Hardness, Magnesium Hardness.
* **Geospatial Attributes:** Station Name, State, District, Tehsil, Latitude, Longitude, Basin, River, Tributary.

### C. Surface Water Quality (Manual - Biological Parameters)
* **Dataset Name:** Surface Water Quality (Manual - Biological Parameters), Central Pollution Control Board (CPCB)
* **Publishing Organization:** Central Pollution Control Board (CPCB) / NWIC
* **Source Portal:** National Water Data Portal (NWDP)
* **Direct Portal URL:** [https://nwdp.nwic.gov.in/dataset/surface-water-quality-manual-biological-parameters-cpcb](https://nwdp.nwic.gov.in/dataset/surface-water-quality-manual-biological-parameters-cpcb)
* **API Package Identifier:** `surface-water-quality-manual-biological-parameters-cpcb` (ID: `e97bcc1b-895e-4eb9-a826-09d52f7b5ca0`)
* **Download Date:** August 23, 2026
* **Data Format:** CSV
* **Distribution Scheme:** 105 state-wise and epoch-wise CSV files
* **Actual Empirical Temporal Coverage:** January 1, 2018 to December 31, 2021
* **License / Open Data Policy:** Government of India Open Data Policy (NDSAP)
* **Key Monitored Parameters:** Biochemical Oxygen Demand (BOD) (mg/L), Fecal Coliform (MPN/100mL), Total Coliform (MPN/100mL), Chemical Oxygen Demand (COD) (mg/L).
* **Geospatial Attributes:** Station Name, State, District, Tehsil, Latitude, Longitude.

---

## 2. Historical Kaggle Water Quality Dataset

### Overview
A historical secondary compilation of water quality records from India widely used in online benchmarking, derived from scanned/digitized CPCB annual water quality status bulletins.

* **Dataset Name:** Indian Water Quality Data
* **Repository Platform:** Kaggle
* **Publisher / Uploader:** Anbarivan (`anbarivan`)
* **Direct Source URL:** [https://www.kaggle.com/datasets/anbarivan/indian-water-quality-data](https://www.kaggle.com/datasets/anbarivan/indian-water-quality-data)
* **Direct Download URL:** [https://www.kaggle.com/api/v1/datasets/download/anbarivan/indian-water-quality-data](https://www.kaggle.com/api/v1/datasets/download/anbarivan/indian-water-quality-data)
* **Download Date:** August 23, 2026
* **Primary Data File:** `water_dataX.csv`
* **Data Format:** CSV (Encoded in Latin-1 / CP1252)
* **Original Data Producer:** Central Pollution Control Board (CPCB) Historical Annual Water Quality Reports (digitized / scraped)
* **License / Terms:** Database Contents License (DbCL) / Community Data License Agreement / Public Domain dedication on Kaggle (unspecified academic open use).
* **Actual Empirical Temporal Coverage:** 2003 to 2014 (12 unique years; aggregated annual means)
* **Monitored Variables:** Station Code, Locations, State, Temperature, Dissolved Oxygen (D.O.), pH, Conductivity, Biochemical Oxygen Demand (B.O.D.), Nitrate-N + Nitrite-N, Fecal Coliform, Total Coliform (Mean), Year.
* **Geospatial Attributes:** Station Code (integer identifier), Text Location string (`LOCATIONS`), Text State string (`STATE`). **No geographic coordinates (Latitude/Longitude are completely absent)**.

---

## 3. Provenance and Metadata Summary Matrix

| Attribute | Kaggle Historical Dataset | Official NWDP CPCB (Physical) | Official NWDP CPCB (Chemical) | Official NWDP CPCB (Biological) |
| :--- | :--- | :--- | :--- | :--- |
| **Custodian Organization** | Kaggle Community Contributor | CPCB / NWIC (Govt. of India) | CPCB / NWIC (Govt. of India) | CPCB / NWIC (Govt. of India) |
| **Data Authority Tier** | Secondary / Derived (Scraped) | Primary Official National Portal | Primary Official National Portal | Primary Official National Portal |
| **Raw File Format** | 1 CSV (`water_dataX.csv`) | 104 State-wise CSVs | 106 State-wise CSVs | 105 State-wise CSVs |
| **Raw Storage Location** | `data/raw/kaggle/` | `data/raw/nwdp_cpcb/physical/` | `data/raw/nwdp_cpcb/chemical/` | `data/raw/nwdp_cpcb/biological/` |
| **Temporal Range** | 2003–2014 (Annual means) | 2018–2021 (Event-level) | 2018–2024 (Event-level) | 2018–2021 (Event-level) |
| **Temporal Granularity** | Annual Aggregates | Monthly / Bi-monthly samples | Monthly / Bi-monthly samples | Monthly / Bi-monthly samples |
| **Spatial Coordinate System** | None (Absent) | WGS84 (Decimal Lat/Long) | WGS84 (Decimal Lat/Long) | WGS84 (Decimal Lat/Long) |
| **Total Monitored Stations** | 321 Station Codes | 3,989 Monitoring Stations | 4,017 Monitoring Stations | 3,959 Monitoring Stations |
| **Number of Records** | 1,991 rows | 94,159 rows | 109,683 rows | 107,537 rows |
| **Data Quality Status** | Contains OCR bugs & pH outliers | Government QA/QC format | Government QA/QC format | Government QA/QC format |
| **License Type** | Open (Community Kaggle) | Open Government Data (NDSAP) | Open Government Data (NDSAP) | Open Government Data (NDSAP) |
