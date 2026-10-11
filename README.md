# Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data

**Course:** Introduction to Data Science (DSC 513)  
**Academic Degree:** M.Tech in Computer Science / Data Science, IIIT Kottayam  
**Author:** Emmanuel Jobin  

---

## Project Overview

This repository contains the complete R code, datasets, exploratory analysis, publication-quality visualizations, and reproducible R Markdown reports for the M.Tech Data Science project investigating surface water quality dynamics across India.

The project evaluates official **Central Pollution Control Board (CPCB) / National Water Data Portal (NWDP)** monitoring data (315 raw CSV files, >300,000 observations, 4,017 geocoded stations across 36 States/UTs) alongside a historical **Kaggle** baseline (2003–2014) to characterize spatial heterogeneity, monsoon dilution effects, and decadal trends.

---

## Repository Structure

```text
.
├── indian_water_quality_project/
│   ├── R/
│   │   ├── 01_data_inspection.R               # Dataset inventory & schema profiling
│   │   ├── 02_data_cleaning.R                 # Data cleaning, range validation & audit
│   │   └── 03_exploratory_analysis.R          # EDA, hypothesis testing & visualizations
│   ├── data/
│   │   ├── raw/
│   │   │   ├── nwdp_cpcb/                     # 315 official CPCB raw CSV files
│   │   │   └── kaggle/                        # Historical Kaggle dataset
│   │   └── processed/                         # Cleaned harmonized datasets
│   ├── figures/                               # 10 high-resolution publication plots (300 DPI)
│   ├── reports/
│   │   ├── indian_water_quality_analysis.html # Standalone interactive HTML report
│   │   ├── indian_water_quality_analysis.pdf  # Compiled PDF report
│   │   └── data_cleaning_audit_summary.csv    # Cleaning audit impact table
│   ├── submission/
│   │   └── DSC_513_Mini_Project_Submission.zip# Complete submission archive
│   ├── indian_water_quality_analysis.Rmd       # Reproducible R Markdown report source
│   └── README.md                              # Detailed project guide & viva prep
├── Docs/                                      # Course documentation & project abstract
└── .gitignore
```

---

## Quick Start & Reproduction

### Prerequisites
* R (Version 4.4+)
* RStudio
* Required R packages:
  ```r
  install.packages(c("readr", "dplyr", "tidyr", "ggplot2", "knitr", "rmarkdown", "stringr"))
  ```

### Running the Analysis
From terminal or RStudio console:
```bash
# 1. Inspect datasets and schemas
Rscript indian_water_quality_project/R/01_data_inspection.R

# 2. Run data cleaning pipeline
Rscript indian_water_quality_project/R/02_data_cleaning.R

# 3. Generate exploratory plots & hypothesis tests
Rscript indian_water_quality_project/R/03_exploratory_analysis.R
```

### Rendering Reports
```bash
# Render interactive HTML report
Rscript -e 'rmarkdown::render("indian_water_quality_project/indian_water_quality_analysis.Rmd", output_format = "html_document")'

# Render PDF report
Rscript -e 'rmarkdown::render("indian_water_quality_project/indian_water_quality_analysis.Rmd", output_format = "pdf_document")'
```

---

## Key Findings

1. **Compliance:** Nationwide median Dissolved Oxygen is $6.80\text{ mg/L}$, with $90.8\%$ of records meeting CPCB Class C standards ($\ge 4.0\text{ mg/L}$).
2. **Organic Pollution:** Biochemical Oxygen Demand (BOD) exhibits heavy right-skewness ($Median = 2.30\text{ mg/L}$, $Max = 1,315\text{ mg/L}$), reflecting acute localized municipal and industrial discharge pockets.
3. **Monsoon Dilution:** Monsoon streamflow significantly dilutes organic pollution and re-aerates river basins ($p = 5.48 \times 10^{-24}$, Wilcoxon Rank-Sum Test).
4. **Oxygen Depletion Dynamics:** Non-linear modeling reveals steep DO depletion when BOD exceeds $5–10\text{ mg/L}$.
