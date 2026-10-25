# Formal Academic Presentation Guide & Speaker Notes

- **Project Title:** Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data
- **Student Name:** Emmanuel Jobin
- **Register Number:** 2026EMAI20054
- **Course:** DSC 513 – Introduction to Data Science (IIIT Kottayam)
- **Presentation File:** `CPCB_Water_Quality_Mini_Project_Presentation.pptx` (18 Slides, 16:9 Widescreen, with embedded Speaker Notes)

---

## Slide 1 — Title Slide

- What to say: Good morning/afternoon Professor and classmates. My name is Emmanuel Jobin (Register Number 2026EMAI20054). Today I am presenting my DSC 513 Introduction to Data Science mini project titled 'Geographic and Seasonal Analysis of Surface Water Quality in India Using CPCB Monitoring Data'.
- Project Scope: This study uses R and R Markdown to inspect, clean, analyze, and model 315 official CPCB/NWDP CSV files (311,379 raw rows consolidated into 109,422 station-date records across 4,017 stations in 36 States/UTs) alongside a supplementary 1,990-row historical Kaggle dataset (2003–2014).
- Likely Lecturer Question: Why did you choose surface water quality in India? -> Because CPCB monitors thousands of river and lake stations nationwide, providing a rich, real-world multi-file dataset with realistic data-quality challenges (encoding, OCR errors, missing values, skewed distributions) ideal for demonstrating an end-to-end R data science workflow.

---

## Slide 2 — Introduction and Motivation

- What to say: Surface-water quality measures the suitability of rivers and lakes for aquatic ecosystems and human use. We focus on four primary CPCB indicators: Dissolved Oxygen (DO), Biochemical Oxygen Demand (BOD), pH, and Electrical Conductivity (EC).
- Why these four parameters: DO and BOD capture the oxygen balance of a river (healthy water needs DO >= 4 mg/L and BOD <= 3 mg/L), pH measures acid-base balance (6.5–8.5), and EC measures dissolved ionic load.
- Why geographic and seasonal dimensions: Water quality is not uniform across India—it varies across states and shifts between low-flow summer months and high-flow monsoon months.
- Likely Lecturer Question: Why are DO and BOD inversely related? -> Because aerobic bacteria consume dissolved oxygen in the water column while breaking down organic sewage (measured by BOD).

---

## Slide 3 — Problem Statement and Objectives

- What to say: Raw government monitoring files cannot be analyzed directly without careful auditing and preprocessing. We organized the project around 9 concrete objectives spanning data inspection, cleaning, exploratory analysis, non-parametric hypothesis testing, historical state-level comparison, and beginner-level linear regression.
- Why state objectives as questions to investigate: In data science, we formulate clear analytical objectives first and let the empirical data determine the findings rather than assuming conclusions in advance.
- Likely Lecturer Question: Why did you include both parametric (Mean/SD) and non-parametric (Median/IQR) statistics in Objective 3? -> Because environmental variables like BOD and EC are heavily right-skewed, so the mean is pulled upward by extreme values whereas the median and IQR represent typical water conditions.

---

## Slide 4 — Expected Analysis vs. Actual Findings

- What to say: This table summarizes what each research question was designed to investigate versus what we actually found in the data, along with the honest methodological limitations.
- Key highlights to emphasize:
- 1. During file inspection, we discovered 1 biological CSV file misplaced inside the chemical folder, and 89 rows in Kaggle where pH was > 14 due to column shifts in the raw archive.
- 2. In seasonal analysis, monsoon dilution lowers median BOD from 2.40 mg/L (Pre-Monsoon) to 2.10 mg/L (Monsoon), while median DO shifts slightly from 6.80 to 6.70 mg/L (p = 5.48e-24).
- 3. In linear regression, BOD has a statistically significant negative association with DO (slope = -0.1784), explaining 23.7% of test-set DO variance (Test RMSE = 1.6508 mg/L), which is a modest single-predictor fit.

---

## Slide 5 — Dataset Description

- What to say: Our project uses two verified local datasets. The primary dataset consists of 315 official CPCB/NWDP CSV files totaling 311,379 raw rows across Physical (104 files), Chemical (106 files), and Biological (105 files) categories. Because the three category folders record different parameters for the same station and timestamp, consolidating them by (station, sample_datetime) produces 109,422 unique station-date observations across 22 columns.
- Supplementary dataset: The Kaggle dataset (water_dataX.csv) has 1,991 raw rows (1,990 after removing 1 exact duplicate) and 12 columns covering 2003–2014.
- Likely Lecturer Question: Why did 311,379 raw CPCB rows become 109,422 rows in the master table? -> Because Physical, Chemical, and Biological measurements for the same station visit were stored in three separate category folders. Merging on station + timestamp aligns pH/EC, DO, and BOD into a single row per sampling event.

---

## Slide 6 — Project Workflow

- What to say: Our workflow follows a modular, reproducible 7-stage pipeline: Data Loading -> Inspection -> Cleaning & Preprocessing -> Exploratory Data Analysis -> Basic Linear Regression -> Evaluation & Sensitivity Checks -> Conclusion.
- Why modular scripts: Separating inspection (01_data_inspection.R), cleaning (02_data_cleaning.R), and analysis/modelling (03_exploratory_analysis.R and the .Rmd report) ensures that raw data are never overwritten and every number in the final HTML and PDF reports can be reproduced from scratch.

---

## Slide 7 — Data Inspection and Quality Problems

- What to say: Before cleaning, we audited all files and documented seven concrete data-quality problems. On the left table, you can see the exact counts; on the right, Figure 1 shows parameter-wise missingness in the CPCB Master table.
- Critical example to highlight: In the Kaggle dataset, 89 rows had pH values between 69 and 748 because conductivity values were shifted into the pH column in the raw source. Before cleaning, those 89 rows inflated the mean pH to an impossible 27.68! Similarly, in CPCB, pH (1.9% missing), DO (11.4% missing), and BOD (23.0% missing) have strong coverage, whereas Electrical Conductivity is 56.0% missing and trace heavy metals exceed 60% missing.
- Likely Lecturer Question: Why did you keep DO = 0 mg/L (98 rows) while removing DO > 25 mg/L (11 rows)? -> Because DO = 0 mg/L is physically real in anoxic, heavily polluted sewage stretches, whereas DO > 25 mg/L is physically impossible under open-air surface water conditions.

---

## Slide 8 — Data Cleaning and Preprocessing

- What to say: This slide explains the exact R implementation of our cleaning pipeline and shows the visual proof of its impact.
- Code explanation: First, we strip whitespace and convert string placeholders like 'NAN' or '-' into proper R NA values before calling as.numeric(). Second, using ifelse(), we set physically impossible values (such as pH < 0 or > 14, and DO > 25 mg/L) to NA_real_ instead of dropping the entire row. That way, a station visit with a corrupted pH reading still contributes its valid DO and BOD measurements.
- Visual proof (Figure 2): The right plot shows Kaggle pH before and after range validation. Removing the 89 corrupted pH > 14 values restores the distribution from an impossible range (up to 748) to a clean bell-shaped distribution centered at Mean = 7.23 (Median = 7.30).

---

## Slide 9 — Exploratory Data Analysis: Distributions

- What to say: We examined the distributions of all four primary parameters using both parametric (Mean, SD) and non-parametric (Median, IQR) metrics.
- Key insight: Look at BOD in the table: its Median is 2.30 mg/L (within the 3.0 mg/L CPCB Class C threshold), but its Mean is 5.76 mg/L (more than double the median!) with a standard deviation of 16.26 mg/L. Similarly, Electrical Conductivity has a median of 395 uS/cm but a mean of 3,474.5 uS/cm due to estuarine and industrial brines. This severe right-skewness is why we plot BOD and EC on a log10 scale in Figure 3 and use non-parametric rank tests for inference.

---

## Slide 10 — Geographic and Seasonal Analysis

- What to say: This slide presents our geographic and seasonal analyses. On the left (Figure 7), state-wise boxplots show that while most states maintain median DO above 6.0 mg/L, industrialized states like Maharashtra and Telangana experience frequent hypoxic drops below the 4.0 mg/L threshold. A Kruskal-Wallis test across the top 6 states confirms highly significant differences in BOD (Chi-squared = 11,725.65, p < 2.2e-16).
- On the right (Figure 8), seasonal BOD boxplots show that Southwest Monsoon rainfall (June–September) dilutes organic waste, lowering median BOD from 2.40 mg/L in Pre-Monsoon to 2.10 mg/L in Monsoon. Meanwhile, the Wilcoxon Rank-Sum test on DO between Pre-Monsoon (6.80 mg/L) and Monsoon (6.70 mg/L) is statistically significant (W = 3.61e8, p = 5.48e-24).
- Important limitation to mention: Because the Kaggle dataset only contains annual summaries without sampling months, seasonal analysis is performed exclusively on the timestamped CPCB dataset.

---

## Slide 11 — Relationships Between Water-Quality Variables

- What to say: Next, we examined how water-quality parameters interact. Figure 9 plots Dissolved Oxygen against BOD across the CPCB archive. It shows a clear inverse relationship: when BOD is low (<= 3 mg/L), DO is healthy (6–9 mg/L), but as BOD exceeds 10 mg/L, DO drops steeply toward hypoxia.
- Figure 10 displays the Spearman rank correlation matrix: DO and BOD have rho = -0.34, Conductivity and BOD have rho = +0.25, and pH and DO have rho = +0.12.
- Correlation vs. Causation: We explicitly note that correlation in observational monitoring data measures statistical association, not causation, because confounding factors like water temperature, flow rate, and industrial mixing also affect oxygen levels.

---

## Slide 12 — Why Use Machine Learning?

- What to say: In Section 7 of our report, we introduce a beginner-level machine learning model using Simple Linear Regression. A regression model learns a relationship from training data to predict a continuous target variable from a predictor variable.
- Why DO from BOD: Measuring 5-day BOD in a laboratory takes 5 days of incubation, whereas understanding how organic load relates to Dissolved Oxygen is central to water quality management. Both variables are numeric and measured in mg/L.
- Why an 80:20 train-test split: If we evaluate a model on the same data used to fit it, we risk overfitting. Holding out 20% of the data as a test set lets us measure true out-of-sample prediction error.

---

## Slide 13 — Linear Regression: Model and Code

- What to say: Here is the exact R code used to train and test our linear regression model. First, we filter for non-missing DO and BOD pairs with BOD <= 50 mg/L. Second, we set set.seed(513) and sample 80% of indices for train_data and keep the remaining 20% in test_data.
- How lm() and predict() work: lm(dissolved_oxygen_mg_l ~ bod_mg_l, data = train_data) estimates the intercept (7.0745 mg/L) and slope (-0.1784 mg/L per mg/L of BOD) using only the training set. Then predict(do_lm_model, newdata = test_data) computes the predicted DO values for the 15,974 unseen test rows.
- Likely Lecturer Question: Why did you pass newdata = test_data inside predict()? -> Because omitting newdata would return fitted values on the training set instead of evaluating predictions on the held-out test set.

---

## Slide 14 — Training, Testing, and Model Evaluation

- What to say: This slide summarizes all verified numbers from our model evaluation. Out of 80,223 complete (DO, BOD) pairs, applying our analytical cutoff of BOD <= 50 mg/L retains 79,867 pairs (99.56%), split into 63,893 training rows and 15,974 testing rows.
- How to explain the metrics: On the unseen test set, the model achieves Test R² = 0.2370 (explaining 23.7% of DO variance), Test RMSE = 1.6508 mg/L, and Test MAE = 1.1750 mg/L. Notice that Train R² (0.2499) and Test R² (0.2370) match closely, confirming zero overfitting. However, we describe this accuracy as modest rather than high because a single variable (BOD) cannot capture physical factors like water temperature or river turbulence.

---

## Slide 15 — Actual vs. Predicted Values

- What to say: Figure 12 compares Actual Dissolved Oxygen on the horizontal axis against Predicted Dissolved Oxygen on the vertical axis for all 15,974 test-set observations.
- Key features to point out to the lecturer:
- 1. The dashed orange line is the 1:1 reference line where Predicted DO equals Actual DO.
- 2. Notice the flat horizontal ceiling at Y = 7.07 mg/L: because BOD cannot be negative and our slope is negative (-0.1784), the highest possible prediction from 7.0745 - 0.1784 * BOD occurs when BOD = 0, giving 7.0745 mg/L. That visually explains why a single linear predictor cannot predict supersaturated DO values above 7.1 mg/L.

---

## Slide 16 — Sensitivity Checks and Limitations

- What to say: We performed two important sensitivity checks to test the assumptions of our primary regression model.
- First, in Sensitivity Check 1, we fitted the exact same model on all 80,223 complete pairs without the BOD <= 50 mg/L cutoff. Including the 356 extreme observations (0.44% of the data, where BOD reaches up to 486 mg/L) flattens the slope by more than half (from -0.1784 to -0.0849) and lowers Test R² from 0.2370 to 0.1598. Why? Because Dissolved Oxygen cannot physically drop below 0 mg/L, so extreme BOD points sit along a flat floor near zero and pull the linear OLS line upward.
- Second, in Sensitivity Check 2, we addressed station-level data leakage by splitting the 2,978 distinct stations 80:20 (2,382 training stations vs. 596 unseen test stations). The slope (-0.1719) and intercept (7.0576) remain nearly identical, with Test RMSE = 1.5429 mg/L and Test R² = 0.3369, showing that the linear relationship generalizes across stations.

---

## Slide 17 — Key Findings and Conclusion

- What to say: To conclude, we separate our findings into descriptive/inferential conclusions on the left and predictive machine learning conclusions on the right. Every objective stated at the start of the report was empirically tested and verified.
- Key takeaway: While 90.8% of CPCB surface-water samples meet the basic Class C oxygen threshold (>= 4.0 mg/L), localized organic pollution pockets create severe right-skewed BOD spikes. Simple Linear Regression captures the negative association between BOD and DO (explaining 23.7% of variance with RMSE = 1.65 mg/L), while highlighting why multi-parameter non-linear models are needed for higher accuracy.

---

## Slide 18 — Future Improvements and References

- What to say: Finally, Slide 18 outlines four practical directions for future work—adding physical predictors like water temperature, using non-linear models that respect the zero-DO floor, applying basin/time-blocked cross-validation, and automating QA checks—alongside our verified data sources and regulatory references.
- Closing statement: Thank you for your attention. I am happy to answer any questions and demonstrate the live R Markdown code or rendered HTML/PDF reports.

---
