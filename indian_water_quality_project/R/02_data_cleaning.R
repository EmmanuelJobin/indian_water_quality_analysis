# ==============================================================================
# Script: 02_data_cleaning.R
# Project: Geographic and Seasonal Analysis of Surface Water Quality in India
# Course: DSC 513 - Introduction to Data Science (M.Tech Mini Project)
# Description: Step-by-step data cleaning, standardization, type conversion, 
#              range validation, and outlier handling for Kaggle and CPCB datasets.
# ==============================================================================

# Ensure local project library is loaded if available
local({
  proj_lib <- file.path(getwd(), "r_libs")
  if (dir.exists(proj_lib) && !(proj_lib %in% .libPaths())) {
    .libPaths(c(proj_lib, .libPaths()))
  }
  proj_lib_parent <- file.path(getwd(), "indian_water_quality_project", "r_libs")
  if (dir.exists(proj_lib_parent) && !(proj_lib_parent %in% .libPaths())) {
    .libPaths(c(proj_lib_parent, .libPaths()))
  }
})

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(stringr)
})

# ------------------------------------------------------------------------------
# 1. PATH RESOLUTION
# ------------------------------------------------------------------------------
find_base_dir <- function() {
  candidates <- c(".", "indian_water_quality_project", "..")
  for (cand in candidates) {
    if (dir.exists(file.path(cand, "data", "raw", "nwdp_cpcb"))) {
      return(normalizePath(cand))
    }
  }
  stop("Could not locate data/raw/nwdp_cpcb directory.")
}

BASE_DIR <- find_base_dir()
cat("=== DSC 513: SURFACE WATER QUALITY DATA CLEANING PIPELINE ===\n")
cat(sprintf("Working Root Directory: %s\n\n", BASE_DIR))

RAW_DIR     <- file.path(BASE_DIR, "data", "raw")
PROC_DIR    <- file.path(BASE_DIR, "data", "processed")
dir.create(PROC_DIR, showWarnings = FALSE, recursive = TRUE)

# Track cleaning audit log
audit_log <- list()

# ------------------------------------------------------------------------------
# 2. CLEANING HISTORICAL KAGGLE DATASET
# ------------------------------------------------------------------------------
cat("------------------------------------------------------------------\n")
cat("PART A: Cleaning Historical Kaggle Dataset (water_dataX.csv)\n")
cat("------------------------------------------------------------------\n")

kag_raw_path <- file.path(RAW_DIR, "kaggle", "water_dataX.csv")
df_kag <- read.csv(kag_raw_path, stringsAsFactors = FALSE, 
                   fileEncoding = "latin1", check.names = FALSE)

n_raw_kag <- nrow(df_kag)
cat(sprintf("[A.1] Initial Raw Records: %d rows x %d cols\n", n_raw_kag, ncol(df_kag)))

# Step 1: Standardize Column Names
cat("[A.2] Standardizing column names to clean snake_case...\n")
new_kag_names <- c(
  "station_code", "location", "state", "temperature_c",
  "dissolved_oxygen_mg_l", "ph", "conductivity_umhos_cm",
  "bod_mg_l", "nitrate_nitrite_n_mg_l", "fecal_coliform_mpn_100ml",
  "total_coliform_mpn_100ml_mean", "year"
)
colnames(df_kag) <- new_kag_names
cat(sprintf("      Renamed columns successfully. Repaired corrupted OCR name 'NITRATENAN N+ NITRITENANN' -> 'nitrate_nitrite_n_mg_l'\n"))

# Step 2: Full Duplicate Identification & Removal
n_dups_kag <- sum(duplicated(df_kag))
cat(sprintf("[A.3] Duplicate Records Check: %d duplicate row(s) identified\n", n_dups_kag))
if (n_dups_kag > 0) {
  df_kag <- df_kag[!duplicated(df_kag), ]
  cat(sprintf("      Removed %d duplicate record(s). Remaining rows: %d\n", n_dups_kag, nrow(df_kag)))
}

# Step 3: Parse Numeric Columns and Handle Inconsistent Missing Value Codes ("NAN", "", "NA")
cat("[A.4] Converting numeric parameters and standardizing missing value markers...\n")
num_cols_kag <- c("temperature_c", "dissolved_oxygen_mg_l", "ph", "conductivity_umhos_cm",
                  "bod_mg_l", "nitrate_nitrite_n_mg_l", "fecal_coliform_mpn_100ml",
                  "total_coliform_mpn_100ml_mean", "year")

for (col in num_cols_kag) {
  raw_vals <- df_kag[[col]]
  clean_vals <- suppressWarnings(as.numeric(ifelse(raw_vals %in% c("NAN", "NA", "", "-", " "), NA, raw_vals)))
  df_kag[[col]] <- clean_vals
}

# Step 4: Validate Measurement Ranges & Handle Impossible Outliers
cat("[A.5] Range validation and scientific outlier handling...\n")
# pH must be in [0, 14] for aqueous solutions
n_bad_ph_kag <- sum(!is.na(df_kag$ph) & (df_kag$ph < 0 | df_kag$ph > 14))
cat(sprintf("      Invalid pH values detected (>14 or <0): %d\n", n_bad_ph_kag))
cat(sprintf("      Sample extreme pH values before cleaning: %s\n", 
            paste(head(df_kag$ph[!is.na(df_kag$ph) & df_kag$ph > 14], 5), collapse = ", ")))
df_kag$ph[!is.na(df_kag$ph) & (df_kag$ph < 0 | df_kag$ph > 14)] <- NA
cat(sprintf("      Converted %d impossible pH values to NA (preserved other valid parameters in these rows)\n", n_bad_ph_kag))

# DO check: DO cannot be negative; upper physical saturation is ~15-20 mg/L
n_bad_do_kag <- sum(!is.na(df_kag$dissolved_oxygen_mg_l) & (df_kag$dissolved_oxygen_mg_l < 0 | df_kag$dissolved_oxygen_mg_l > 25))
cat(sprintf("      Invalid DO values detected (>25 or <0 mg/L): %d\n", n_bad_do_kag))
df_kag$dissolved_oxygen_mg_l[!is.na(df_kag$dissolved_oxygen_mg_l) & (df_kag$dissolved_oxygen_mg_l < 0 | df_kag$dissolved_oxygen_mg_l > 25)] <- NA

# Step 5: Standardize State Names in Kaggle
cat("[A.6] Standardizing Indian State/UT names...\n")
# Clean basic strings
df_kag$state <- str_trim(df_kag$state)
df_kag$state <- ifelse(df_kag$state %in% c("", "NAN", "NA"), NA, df_kag$state)

# Regularize known states from messy strings where location was placed in state column
standardize_state <- function(st, loc) {
  if (is.na(st) || st == "") {
    # Try recovering from location
    target <- loc
  } else {
    target <- st
  }
  if (is.na(target)) return(NA_character_)
  
  target_upper <- toupper(target)
  
  if (grepl("ANDHRA PRADESH", target_upper)) return("Andhra Pradesh")
  if (grepl("ARUNACHAL PRADESH", target_upper)) return("Arunachal Pradesh")
  if (grepl("ASSAM", target_upper)) return("Assam")
  if (grepl("BIHAR", target_upper)) return("Bihar")
  if (grepl("CHHATTISGARH", target_upper)) return("Chhattisgarh")
  if (grepl("GOA", target_upper)) return("Goa")
  if (grepl("GUJARAT", target_upper)) return("Gujarat")
  if (grepl("HARYANA", target_upper)) return("Haryana")
  if (grepl("HIMACHAL PRADESH", target_upper) || grepl("H[.]P[.]", target_upper)) return("Himachal Pradesh")
  if (grepl("JAMMU", target_upper) || grepl("KASHMIR", target_upper)) return("Jammu & Kashmir")
  if (grepl("JHARKHAND", target_upper)) return("Jharkhand")
  if (grepl("KARNATAKA", target_upper)) return("Karnataka")
  if (grepl("KERALA", target_upper)) return("Kerala")
  if (grepl("MADHYA PRADESH", target_upper) || grepl("M[.]P[.]", target_upper)) return("Madhya Pradesh")
  if (grepl("MAHARASHTRA", target_upper)) return("Maharashtra")
  if (grepl("MANIPUR", target_upper)) return("Manipur")
  if (grepl("MEGHALAYA", target_upper)) return("Meghalaya")
  if (grepl("MIZORAM", target_upper)) return("Mizoram")
  if (grepl("NAGALAND", target_upper)) return("Nagaland")
  if (grepl("ODISHA|ORISSA", target_upper)) return("Odisha")
  if (grepl("PUNJAB", target_upper)) return("Punjab")
  if (grepl("RAJASTHAN", target_upper)) return("Rajasthan")
  if (grepl("SIKKIM", target_upper)) return("Sikkim")
  if (grepl("TAMIL NADU|TAMILNADU", target_upper)) return("Tamil Nadu")
  if (grepl("TELANGANA", target_upper)) return("Telangana")
  if (grepl("TRIPURA", target_upper)) return("Tripura")
  if (grepl("UTTAR PRADESH|U[.]P[.]", target_upper)) return("Uttar Pradesh")
  if (grepl("UTTARAKHAND|UTTARANCHAL", target_upper)) return("Uttarakhand")
  if (grepl("WEST BENGAL", target_upper)) return("West Bengal")
  if (grepl("DELHI", target_upper)) return("Delhi")
  if (grepl("PUDUCHERRY|PONDICHERRY", target_upper)) return("Puducherry")
  if (grepl("CHANDIGARH", target_upper)) return("Chandigarh")
  if (grepl("DAMAN|DIU", target_upper)) return("Daman & Diu")
  if (grepl("DADRA|NAGAR HAVELI", target_upper)) return("Dadra & Nagar Haveli")
  
  # Return title case if unmapped
  return(str_to_title(st))
}

df_kag$state_clean <- mapply(standardize_state, df_kag$state, df_kag$location, USE.NAMES = FALSE)
df_kag$state <- df_kag$state_clean
df_kag$state_clean <- NULL

cat(sprintf("      Standardized states. Unique recognized states in Kaggle: %d\n", 
            n_distinct(df_kag$state, na.rm = TRUE)))

# Save cleaned Kaggle dataset
kag_clean_path <- file.path(PROC_DIR, "kaggle_water_quality_clean.csv")
write.csv(df_kag, kag_clean_path, row.names = FALSE)
cat(sprintf("[A.7] Saved Cleaned Kaggle Dataset: %s (%d rows x %d cols)\n\n", 
            basename(kag_clean_path), nrow(df_kag), ncol(df_kag)))

# ------------------------------------------------------------------------------
# 3. CLEANING OFFICIAL CPCB / NWDP MASTER DATASET
# ------------------------------------------------------------------------------
cat("------------------------------------------------------------------\n")
cat("PART B: Cleaning Official CPCB / NWDP Master Dataset\n")
cat("------------------------------------------------------------------\n")

cpcb_master_path <- file.path(PROC_DIR, "nwdp_cpcb_master_water_quality.csv")
df_cpcb <- read_csv(cpcb_master_path, show_col_types = FALSE, progress = FALSE)

n_raw_cpcb <- nrow(df_cpcb)
cat(sprintf("[B.1] Loaded CPCB Master Observations: %s rows x %d cols\n", 
            format(n_raw_cpcb, big.mark = ","), ncol(df_cpcb)))

# Step 1: Standardize State Names in CPCB
cat("[B.2] Standardizing State & UT names across CPCB records...\n")
df_cpcb <- df_cpcb %>% 
  mutate(
    state = case_when(
      state %in% c("Jammu And Kashmir", "Jammu & Kashmir") ~ "Jammu & Kashmir",
      state %in% c("Andaman And Nicobar", "Andaman And Nicobar Islands") ~ "Andaman & Nicobar Islands",
      state %in% c("Daman And Diu", "Daman & Diu") ~ "Daman & Diu",
      state %in% c("Dadra And Nagar Haveli", "Dadra & Nagar Haveli") ~ "Dadra & Nagar Haveli",
      state %in% c("Orissa", "Odisha") ~ "Odisha",
      TRUE ~ state
    )
  )

# Step 2: Validate Date and Temporal Classification
cat("[B.3] Validating dates and seasonal classification...\n")
# Seasons mapping:
# Pre-Monsoon (Summer): March - May (3, 4, 5)
# Monsoon: June - September (6, 7, 8, 9)
# Post-Monsoon (Autumn): October - November (10, 11)
# Winter: December - February (12, 1, 2)
df_cpcb <- df_cpcb %>% 
  mutate(
    month = as.integer(month),
    season = case_when(
      month %in% c(3, 4, 5)  ~ "Pre-Monsoon",
      month %in% c(6, 7, 8, 9) ~ "Monsoon",
      month %in% c(10, 11)   ~ "Post-Monsoon",
      month %in% c(12, 1, 2) ~ "Winter",
      TRUE ~ season
    )
  )

# Step 3: Range Validation & Scientific Anomaly Filtering
cat("[B.4] Validating core physicochemical parameter ranges...\n")

# pH range [0, 14]
bad_ph_cpcb <- sum(!is.na(df_cpcb$ph) & (df_cpcb$ph < 0 | df_cpcb$ph > 14))
cat(sprintf("      Invalid CPCB pH values (>14 or <0): %d (Max observed: %.2f)\n", 
            bad_ph_cpcb, max(df_cpcb$ph, na.rm = TRUE)))
df_cpcb$ph[!is.na(df_cpcb$ph) & (df_cpcb$ph < 0 | df_cpcb$ph > 14)] <- NA

# DO range [0, 25 mg/L]
bad_do_cpcb <- sum(!is.na(df_cpcb$dissolved_oxygen_mg_l) & (df_cpcb$dissolved_oxygen_mg_l < 0 | df_cpcb$dissolved_oxygen_mg_l > 25))
cat(sprintf("      Invalid CPCB DO values (>25 mg/L): %d (Max observed: %.2f mg/L)\n", 
            bad_do_cpcb, max(df_cpcb$dissolved_oxygen_mg_l, na.rm = TRUE)))
df_cpcb$dissolved_oxygen_mg_l[!is.na(df_cpcb$dissolved_oxygen_mg_l) & (df_cpcb$dissolved_oxygen_mg_l < 0 | df_cpcb$dissolved_oxygen_mg_l > 25)] <- NA

# Zero evaluation:
# DO == 0 mg/L can be a genuine anaerobic condition (severe septic pollution). We preserve it!
# EC <= 0 is physically impossible in natural water bodies:
bad_ec_cpcb <- sum(!is.na(df_cpcb$electrical_conductivity_us_cm) & df_cpcb$electrical_conductivity_us_cm <= 0)
cat(sprintf("      Zero/Negative Electrical Conductivity observations: %d\n", bad_ec_cpcb))
df_cpcb$electrical_conductivity_us_cm[!is.na(df_cpcb$electrical_conductivity_us_cm) & df_cpcb$electrical_conductivity_us_cm <= 0] <- NA

# BOD check: negative values impossible
bad_bod_cpcb <- sum(!is.na(df_cpcb$bod_mg_l) & df_cpcb$bod_mg_l < 0)
cat(sprintf("      Negative BOD observations: %d\n", bad_bod_cpcb))
df_cpcb$bod_mg_l[!is.na(df_cpcb$bod_mg_l) & df_cpcb$bod_mg_l < 0] <- NA

# Save cleaned CPCB Master dataset
write_csv(df_cpcb, cpcb_master_path)
cat(sprintf("[B.5] Cleaned CPCB Master Dataset successfully verified & updated: %s\n\n", 
            basename(cpcb_master_path)))

# ------------------------------------------------------------------------------
# 4. DATA CLEANING AUDIT SUMMARY TABLE
# ------------------------------------------------------------------------------
cat("------------------------------------------------------------------\n")
cat("STEP 4: Data Cleaning Impact Audit Table\n")
cat("------------------------------------------------------------------\n")

cleaning_summary <- data.frame(
  Dataset = c(
    "Kaggle", "Kaggle", "Kaggle", "Kaggle",
    "CPCB Master", "CPCB Master", "CPCB Master", "CPCB Master"
  ),
  Cleaning_Step = c(
    "Full Duplicate Removal",
    "OCR Header Repair ('nitrate_nitrite_n_mg_l')",
    "Catastrophic pH Outlier Conversion (pH > 14 to NA)",
    "State Name Normalization & Recovery",
    "State / UT Name Normalization",
    "Seasonal Classification Assignment",
    "Physically Impossible pH Outlier Conversion (pH > 14)",
    "Physically Impossible DO Outlier Conversion (DO > 25 mg/L)"
  ),
  Records_Affected = c(
    n_dups_kag,
    nrow(df_kag),
    n_bad_ph_kag,
    sum(!is.na(df_kag$state)),
    sum(df_cpcb$state %in% c("Jammu & Kashmir", "Odisha", "Andaman & Nicobar Islands")),
    nrow(df_cpcb),
    bad_ph_cpcb,
    bad_do_cpcb
  ),
  Scientific_Justification = c(
    "Remove redundant duplicate records",
    "Fix PDF/OCR text extraction artifacts",
    "Aqueous pH scale restricted to 0-14",
    "Resolve misaligned station/river descriptions in state field",
    "Standardize Union Territory and State spelling variants",
    "Enable seasonal monsoon dynamic comparisons",
    "Remove non-physical pH readings (>14.0) likely due to decimal shift",
    "Surface water oxygen saturation upper physical limit under normal temperature"
  ),
  stringsAsFactors = FALSE
)

print(cleaning_summary)

# Save cleaning summary table to reports
write.csv(cleaning_summary, file.path(BASE_DIR, "reports", "data_cleaning_audit_summary.csv"), row.names = FALSE)
cat(sprintf("\nAudit summary table saved to: reports/data_cleaning_audit_summary.csv\n"))

cat("\n==================================================================\n")
cat("   DATA CLEANING PIPELINE COMPLETED SUCCESSFULLY\n")
cat("==================================================================\n")

