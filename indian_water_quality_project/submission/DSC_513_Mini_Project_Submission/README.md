# Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data

**Course:** Introduction to Data Science (DSC 513)  
**Academic Degree:** M.Tech in Computer Science / Data Science, IIIT Kottayam  
**Student Name:** Emmanuel Jobin  
**Register / Roll Number:** 2026EMAI20054  
**Project Topic:** Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data  
**Repository Version:** 2.1.0 (Audited & Validated Submission Pipeline)  
**Date:** October 2026  

---

## 1. Project Overview & Research Context

Surface water pollution across India's river basins, lakes, and coastal water bodies is driven by municipal sewage discharge, industrial effluent outfalls, and seasonal runoff. The **Central Pollution Control Board (CPCB)**, Ministry of Environment, Forest and Climate Change (MoEFCC), and the **National Water Data Portal (NWDP)** systematically monitor surface water quality across the country.

This data science mini-project investigates:
1. **Spatial Heterogeneity:** State-level and basin-level variations in water quality indicators across India.
2. **Seasonal Dynamics:** Monsoon dilution effects versus pre-monsoon summer pollutant concentrations.
3. **Indicator Relationships:** Non-linear interactions between Dissolved Oxygen (DO), Biochemical Oxygen Demand (BOD), Potential of Hydrogen (pH), and Electrical Conductivity (EC).
4. **Historical Baseline Comparison:** Decadal comparison between historical baseline data (2003–2014) and modern regulatory monitoring (2018–2021).

### Key Monitored Parameters
* **Dissolved Oxygen (DO):** Minimum acceptable aquatic ecosystem standard is $\ge 4.0\text{ mg/L}$ (CPCB Class C).
* **Biochemical Oxygen Demand (BOD):** Maximum permissible organic pollution load is $\le 3.0\text{ mg/L}$ (CPCB Class C).
* **Potential of Hydrogen (pH):** Acceptable range for surface water is $6.5 \le \text{pH} \le 8.5$.
* **Electrical Conductivity (EC):** Ionic carrier indicator measured in $\mu\text{S/cm}$.

---

## 2. Dataset Provenance & Structure

The project acquires data from two distinct local sources:

### Primary Source: Official CPCB / NWDP Monitoring Data
* **Disseminating Portal:** National Water Data Portal (NWDP / NWIC, Ministry of Jal Shakti)
* **Custodian:** Central Pollution Control Board (CPCB)
* **Format:** 315 state-wise CSV files (56.1 MB raw) categorized into:
  - **Physical:** 104 CSV files (94,159 records)
  - **Chemical:** 106 CSV files (109,683 records)
  - **Biological:** 105 CSV files (107,537 records)
* **Total Observations:** 311,379 raw records
* **Temporal Span:** 2018–2021 (with select stations through 2024)
* **Geographic Coverage:** 100% georeferenced with WGS84 decimal latitude and longitude across 4,017 monitoring stations covering all 36 States and Union Territories of India.

### Supporting Historical Dataset: Kaggle Indian Water Quality Data
* **Repository:** `anbarivan/indian-water-quality-data` (`water_dataX.csv`)
* **Format:** 1 CSV file (1,991 rows, 12 columns, Latin-1 encoding)
* **Temporal Span:** 2003–2014 (12 years of annualized station summary means)
* **Role:** Macro-level historical baseline for state-level temporal comparisons.

> **Methodological Note:** Direct row-level merging of Kaggle and CPCB data is methodologically invalid due to a 4-year temporal disconnect (2014 to 2018), aggregation differences (annual means vs. high-frequency periodic event sampling), and coordinate absence in the Kaggle file. Consequently, datasets are analyzed independently and compared only at the aggregated state level.

---

## 3. Directory Structure

```text
indian_water_quality_project/
│
├── data/
│   ├── raw/
│   │   ├── nwdp_cpcb/
│   │   │   ├── physical/                      # 104 state-wise raw CSV files
│   │   │   ├── chemical/                      # 106 state-wise raw CSV files
│   │   │   └── biological/                    # 105 state-wise raw CSV files
│   │   └── kaggle/
│   │       └── water_dataX.csv                # Raw Kaggle historical CSV
│   │
│   └── processed/
│       ├── kaggle_water_quality_clean.csv     # Cleaned Kaggle baseline (1,990 rows)
│       └── nwdp_cpcb_master_water_quality.csv # Harmonized CPCB master table (109,422 rows)
│
├── R/
│   ├── 01_data_inspection.R                  # Raw schema profiling & inventory script
│   ├── 02_data_cleaning.R                     # Preprocessing, range checking & audit script
│   └── 03_exploratory_analysis.R              # EDA, hypothesis testing & figure generator
│
├── figures/                                   # 11 publication-quality 300 DPI plots
│   ├── 01_missingness_overview.png
│   ├── 02_cpcb_geographic_stations_map.png
│   ├── 03_water_quality_distributions.png
│   ├── 04_state_dissolved_oxygen_boxplot.png
│   ├── 05_seasonal_bod_variation.png
│   ├── 06_correlation_matrix.png
│   ├── 07_decadal_historical_comparison.png
│   ├── 08_do_vs_bod_relationship.png
│   ├── 09_cleaning_before_after_ph.png
│   ├── 10_state_observation_counts.png
│   └── 11_four_parameter_distributions.png
│
├── reports/
│   ├── indian_water_quality_analysis.html     # Self-contained rendered HTML report
│   ├── indian_water_quality_analysis.pdf      # Compiled PDF report
│   ├── data_cleaning_audit_summary.csv        # Preprocessing audit table
│   └── dataset_summary.csv                    # Empirical dataset summary
│
├── submission/                                # Ready-to-submit standalone bundle
│   └── DSC_513_Mini_Project_Submission.zip    # Submission archive
│
├── indian_water_quality_analysis.Rmd          # Main reproducible R Markdown report
├── .Rprofile                                  # Project environment configuration
└── README.md                                  # Project documentation
```

---

## 4. Required R Packages & Environment Setup

The project is built using R 4.4+ / 4.6+ with standard data science packages:

```r
install.packages(c(
  "readr",       # High-performance flat file parsing
  "dplyr",       # Data manipulation and aggregation
  "tidyr",       # Tidy data reshaping
  "ggplot2",     # Grammar of graphics visualizations
  "knitr",       # Dynamic report generation engine
  "rmarkdown",   # R Markdown compilation
  "stringr"      # String parsing and text manipulation
))
```

All required packages and dependencies are pre-configured in the project's local library (`r_libs/`), loaded automatically through `.Rprofile`.

---

## 5. How to Run the R Scripts

Run the scripts in sequential execution order from terminal or RStudio:

### Step 1: Dataset Inspection & Schema Profiling
```bash
Rscript R/01_data_inspection.R
```
* **Output:** Audits all 315 CPCB raw files and the Kaggle dataset. Identifies schemas, dimensions, missingness rates, and flags misclassified files.

### Step 2: Data Cleaning & Preprocessing Pipeline
```bash
Rscript R/02_data_cleaning.R
```
* **Output:** Standardizes column names, converts types, repairs OCR artifacts, filters impossible values (89 Kaggle $\text{pH} > 14$ and 11 CPCB $\text{DO} > 25\text{ mg/L}$), normalizes state names, creates seasonal classifications, and produces `reports/data_cleaning_audit_summary.csv`.

### Step 3: Exploratory Data Analysis & Visualization
```bash
Rscript R/03_exploratory_analysis.R
```
* **Output:** Computes summary statistics, performs non-parametric hypothesis testing (Wilcoxon Rank-Sum and Kruskal-Wallis tests), and saves all 10 high-resolution plots to `figures/`.

---

## 6. How to Knit and Generate Reports

### Opening and Knitting in RStudio
1. Launch **RStudio**.
2. Open the file `indian_water_quality_analysis.Rmd`.
3. In the editor toolbar, click the **Knit** button (or press `Ctrl+Shift+K` on Windows/Linux, `Cmd+Shift+K` on macOS).
4. Select **Knit to HTML** or **Knit to PDF**.

### Generating from Terminal / Command Line

#### Generate HTML Report
```bash
Rscript -e 'rmarkdown::render("indian_water_quality_analysis.Rmd", output_format = "html_document")'
```
* The resulting `indian_water_quality_analysis.html` is a self-contained, interactive HTML document with a floating table of contents, tabbed navigation, and interactive code folding.

#### Generate PDF Report
```bash
Rscript -e 'rmarkdown::render("indian_water_quality_analysis.Rmd", output_format = "pdf_document")'
```
* If a LaTeX installation (TinyTeX, MacTeX, or TeX Live) is detected, this compiles `indian_water_quality_analysis.pdf`.
* *Tip:* If LaTeX is not installed, open the generated HTML report in any modern web browser (Google Chrome, Safari, Microsoft Edge) and choose **File > Print > Save as PDF** with "Background graphics" enabled to obtain a clean PDF copy.

---

## 7. Key Findings Summary

1. **Overall Compliance:** The nationwide median Dissolved Oxygen is $6.80\text{ mg/L}$ ($Mean = 6.54\text{ mg/L}$), with $90.8\%$ of monitoring records satisfying the CPCB Class C threshold ($\ge 4.0\text{ mg/L}$).
2. **Organic Pollution Hotspots:** Biochemical Oxygen Demand (BOD) shows substantial right-skewness ($Median = 2.30\text{ mg/L}$, $Mean = 5.76\text{ mg/L}$, $Max = 1,315\text{ mg/L}$). State-level differences are statistically significant ($p < 2.2 \times 10^{-16}$, Kruskal-Wallis Test).
3. **Monsoon Dilution Dynamics:** Monsoon season streamflow induces significant re-aeration and dilution, reducing median BOD from $2.40\text{ mg/L}$ in pre-monsoon summer to $2.10\text{ mg/L}$ in monsoon ($p = 5.48 \times 10^{-24}$, Wilcoxon Rank-Sum Test).
4. **Inverse Oxygen Dynamics:** Non-linear modeling and Spearman rank correlation ($\rho = -0.34$) confirm that organic loading exceeding $5–10\text{ mg/L}$ BOD triggers rapid oxygen depletion toward hypoxia.
5. **Decadal Stability:** Comparing 2003–2014 Kaggle baselines with 2018–2021 CPCB monitoring indicates overall preservation of baseline DO in upper catchments and peninsular coastal regions, while urbanized corridors continue to exhibit severe localized BOD exceedances.

---

## 8. Viva Voce Preparation & Key Technical Decisions

* **Why separate Kaggle and CPCB?** Merging would contaminate instantaneous field events with annualized averages and introduce a 4-year temporal gap (2014–2018).
* **Why convert impossible pH to NA instead of deleting rows?** Discarding whole rows would discard valid measurements for DO, BOD, and Conductivity from those stations.
* **Why use Spearman instead of Pearson correlation?** Environmental water quality parameters exhibit extreme skewness and non-normal distributions; Spearman rank correlation is robust to non-linearity and heavy tails.
* **Why use Wilcoxon and Kruskal-Wallis tests?** Water quality data violates normality and homoscedasticity assumptions required by standard Student's t-test and ANOVA. Non-parametric rank tests provide valid statistical inference.
