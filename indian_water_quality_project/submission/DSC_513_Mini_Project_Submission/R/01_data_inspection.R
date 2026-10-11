# ==============================================================================
# Script: 01_data_inspection.R
# Project: Geographic and Seasonal Analysis of Surface Water Quality in India
# Course: DSC 513 - Introduction to Data Science (M.Tech Mini Project)
# Description: Comprehensive dataset inspection and schema profiling script for
#              official CPCB/NWDP surface water quality datasets (315 CSV files)
#              and Kaggle historical water quality data.
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
  stop("Could not locate data/raw/nwdp_cpcb directory. Please verify working directory.")
}

BASE_DIR <- find_base_dir()
cat("=== DSC 513: SURFACE WATER QUALITY DATASET INSPECTION ===\n")
cat(sprintf("Working Root Directory: %s\n\n", BASE_DIR))

RAW_DIR     <- file.path(BASE_DIR, "data", "raw")
PHYS_DIR    <- file.path(RAW_DIR, "nwdp_cpcb", "physical")
CHEM_DIR    <- file.path(RAW_DIR, "nwdp_cpcb", "chemical")
BIO_DIR     <- file.path(RAW_DIR, "nwdp_cpcb", "biological")
KAGGLE_FILE <- file.path(RAW_DIR, "kaggle", "water_dataX.csv")
PROC_DIR    <- file.path(BASE_DIR, "data", "processed")

# ------------------------------------------------------------------------------
# 2. AUDIT OF DOWNLOADED CPCB / NWDP RAW CSV FILES
# ------------------------------------------------------------------------------
cat("------------------------------------------------------------------\n")
cat("STEP 1: File Inventory & Schema Consistency Check\n")
cat("------------------------------------------------------------------\n")

phys_files <- list.files(PHYS_DIR, pattern = "[.]csv$", full.names = TRUE)
chem_files <- list.files(CHEM_DIR, pattern = "[.]csv$", full.names = TRUE)
bio_files  <- list.files(BIO_DIR,  pattern = "[.]csv$", full.names = TRUE)

cat(sprintf("Found %d Physical parameter CSV files in: %s\n", length(phys_files), PHYS_DIR))
cat(sprintf("Found %d Chemical parameter CSV files in: %s\n", length(chem_files), CHEM_DIR))
cat(sprintf("Found %d Biological parameter CSV files in: %s\n", length(bio_files), BIO_DIR))
cat(sprintf("Total CPCB raw files: %d\n\n", length(phys_files) + length(chem_files) + length(bio_files)))

# Function to inspect headers across files
audit_headers <- function(files, category_name) {
  hdrs <- sapply(files, function(f) {
    con <- file(f, "r")
    h <- readLines(con, n = 1, warn = FALSE)
    close(con)
    h
  })
  u_hdrs <- unique(hdrs)
  cat(sprintf("[%s Parameters] Total Files: %d | Unique Schemas: %d\n", category_name, length(files), length(u_hdrs)))
  for (i in seq_along(u_hdrs)) {
    cols <- strsplit(u_hdrs[i], ",")[[1]]
    count_matching <- sum(hdrs == u_hdrs[i])
    cat(sprintf("  Schema %d (%d files, %d columns):\n    %s\n", 
                i, count_matching, length(cols), 
                paste(head(cols, 8), collapse = ", ")))
    if (length(cols) > 8) cat(sprintf("    ... and %d more columns\n", length(cols) - 8))
  }
  
  # Check for misclassified files
  if (category_name == "Chemical" && length(u_hdrs) > 1) {
    misclassified <- names(hdrs)[hdrs == u_hdrs[which.min(table(hdrs))]]
    cat(sprintf("  * NOTE: Misclassified biological file identified in chemical folder: %s\n", 
                basename(misclassified)))
  }
  cat("\n")
}

audit_headers(phys_files, "Physical")
audit_headers(chem_files, "Chemical")
audit_headers(bio_files,  "Biological")

# Count raw observations across all files without loading all data into memory
count_total_records <- function(files) {
  total <- 0
  for (f in files) {
    lines <- length(readLines(f, warn = FALSE))
    if (lines > 1) total <- total + (lines - 1)
  }
  total
}

cat("Calculating total raw observations (line count verification)...\n")
n_phys <- count_total_records(phys_files)
n_chem <- count_total_records(chem_files)
n_bio  <- count_total_records(bio_files)

cat(sprintf("  Physical Raw Observations:   %s\n", format(n_phys, big.mark = ",")))
cat(sprintf("  Chemical Raw Observations:   %s\n", format(n_chem, big.mark = ",")))
cat(sprintf("  Biological Raw Observations: %s\n", format(n_bio,  big.mark = ",")))
cat(sprintf("  Total CPCB Observations:     %s\n\n", format(n_phys + n_chem + n_bio, big.mark = ",")))

# ------------------------------------------------------------------------------
# 3. KAGGLE HISTORICAL DATASET INSPECTION
# ------------------------------------------------------------------------------
cat("------------------------------------------------------------------\n")
cat("STEP 2: Historical Kaggle Dataset Inspection\n")
cat("------------------------------------------------------------------\n")

if (!file.exists(KAGGLE_FILE)) {
  stop(sprintf("Kaggle dataset not found at: %s", KAGGLE_FILE))
}

cat(sprintf("Reading Kaggle file: %s\n", basename(KAGGLE_FILE)))
# Reading with latin1 encoding due to micro symbol in conductivity column
df_kaggle_raw <- read.csv(KAGGLE_FILE, stringsAsFactors = FALSE, 
                          fileEncoding = "latin1", check.names = FALSE)

cat(sprintf("Kaggle Raw Dimensions: %d rows x %d columns\n\n", nrow(df_kaggle_raw), ncol(df_kaggle_raw)))
cat("Kaggle Column Names and Detected Data Types:\n")
kag_types <- sapply(df_kaggle_raw, class)
for (nm in names(kag_types)) {
  sample_val <- df_kaggle_raw[[nm]][1]
  cat(sprintf("  %-35s : %-10s (Sample: '%s')\n", nm, kag_types[nm], as.character(sample_val)))
}

cat("\nFirst 3 Records in Kaggle:\n")
print(head(df_kaggle_raw[, c(1:6, 12)], 3))

cat("\nLast 3 Records in Kaggle:\n")
print(tail(df_kaggle_raw[, c(1:6, 12)], 3))

# Kaggle missing values audit
cat("\nKaggle Missing Values and Missingness Markers:\n")
kag_missing <- data.frame(
  Column = colnames(df_kaggle_raw),
  NA_Count = sapply(df_kaggle_raw, function(x) sum(is.na(x) | x == "" | x == "NAN" | x == "NA")),
  stringsAsFactors = FALSE
)
kag_missing$Missing_Pct <- round(kag_missing$NA_Count / nrow(df_kaggle_raw) * 100, 2)
print(kag_missing)

# Kaggle duplicate check
kag_dup_count <- sum(duplicated(df_kaggle_raw))
cat(sprintf("\nKaggle Full-Row Duplicate Records: %d\n", kag_dup_count))

# Temporal and Geographic Coverage in Kaggle
cat(sprintf("Kaggle Temporal Span: %d to %d\n", 
            min(as.numeric(df_kaggle_raw$year), na.rm = TRUE),
            max(as.numeric(df_kaggle_raw$year), na.rm = TRUE)))
cat(sprintf("Kaggle Distinct Raw STATE entries: %d\n", length(unique(df_kaggle_raw$STATE))))

# ------------------------------------------------------------------------------
# 4. MASTER PROCESSED CPCB DATASET AUDIT
# ------------------------------------------------------------------------------
cat("\n------------------------------------------------------------------\n")
cat("STEP 3: Processed CPCB Master Harmonized Dataset Audit\n")
cat("------------------------------------------------------------------\n")

cpcb_master_path <- file.path(PROC_DIR, "nwdp_cpcb_master_water_quality.csv")
if (file.exists(cpcb_master_path)) {
  cat(sprintf("Reading Master Processed File: %s\n", basename(cpcb_master_path)))
  df_cpcb_master <- read_csv(cpcb_master_path, show_col_types = FALSE, progress = FALSE)
  
  cat(sprintf("Master Dataset Dimensions: %s rows x %d columns\n\n", 
              format(nrow(df_cpcb_master), big.mark = ","), ncol(df_cpcb_master)))
  
  cat("Variable Types Classification:\n")
  numeric_vars <- names(df_cpcb_master)[sapply(df_cpcb_master, is.numeric)]
  char_vars    <- names(df_cpcb_master)[sapply(df_cpcb_master, is.character)]
  
  cat(sprintf("  Numeric Variables (%d): %s\n", length(numeric_vars), paste(numeric_vars, collapse = ", ")))
  cat(sprintf("  Character / Categorical (%d): %s\n\n", length(char_vars), paste(char_vars, collapse = ", ")))
  
  cat("CPCB Geographic & Temporal Coverage:\n")
  cat(sprintf("  States / UTs Covered:    %d\n", n_distinct(df_cpcb_master$state, na.rm = TRUE)))
  cat(sprintf("  Districts Covered:       %d\n", n_distinct(df_cpcb_master$district, na.rm = TRUE)))
  cat(sprintf("  Monitoring Stations:     %d\n", n_distinct(df_cpcb_master$station, na.rm = TRUE)))
  cat(sprintf("  Valid Coordinates:       %.2f%% (EPSG:4326 WGS84)\n", 
              mean(!is.na(df_cpcb_master$latitude) & !is.na(df_cpcb_master$longitude)) * 100))
  cat(sprintf("  Observation Years:       %s\n", paste(sort(unique(na.omit(df_cpcb_master$year))), collapse = ", ")))
  
  # Summary Statistics of Primary Parameters
  cat("\nSummary Statistics of Core Water Quality Parameters:\n")
  core_vars <- c("dissolved_oxygen_mg_l", "bod_mg_l", "ph", "electrical_conductivity_us_cm")
  sum_stats <- df_cpcb_master %>% 
    summarise(across(all_of(core_vars), list(
      N_Valid = ~sum(!is.na(.)),
      Mean    = ~mean(., na.rm = TRUE),
      SD      = ~sd(., na.rm = TRUE),
      Median  = ~median(., na.rm = TRUE),
      IQR     = ~IQR(., na.rm = TRUE),
      Min     = ~min(., na.rm = TRUE),
      Max     = ~max(., na.rm = TRUE)
    ), .names = "{.col}__{.fn}")) %>% 
    pivot_longer(everything(), names_to = c("Parameter", "Metric"), names_sep = "__") %>% 
    pivot_wider(names_from = Metric, values_from = value)
  
  print(as.data.frame(sum_stats))
} else {
  cat("Master processed CPCB file not yet created. Run 02_data_cleaning.R next.\n")
}

cat("\n==================================================================\n")
cat("   DATASET INSPECTION COMPLETED SUCCESSFULLY\n")
cat("==================================================================\n")
