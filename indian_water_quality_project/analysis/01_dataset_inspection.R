# ==============================================================================
# Script: 01_dataset_inspection.R
# Project: Geographic and Temporal Analysis of Surface Water Quality in India
# Course: DSC 513 - Introduction to Data Science (M.Tech Project)
# Description: Reproducible R script to load, inspect, profile, and visualize
#              the official NWDP/CPCB and Kaggle water quality datasets.
# Packages: base R, ggplot2, dplyr, tidyr
# ==============================================================================

# Suppress package startup messages
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tidyr)
})

# Define Project Paths
BASE_DIR      <- "f:/M.Tech @ IIIT Kottayam/DSC 513 Introduction to Data Science/Project/indian_water_quality_project"
DATA_RAW_KAG  <- file.path(BASE_DIR, "data/raw/kaggle/water_dataX.csv")
DATA_PROC_DIR <- file.path(BASE_DIR, "data/processed")
FIG_DIR       <- file.path(BASE_DIR, "figures")

dir.create(FIG_DIR, showWarnings = FALSE, recursive = TRUE)

cat("\n====================================================================\n")
cat("   DSC 513: SURFACE WATER QUALITY IN INDIA - DATASET INSPECTION\n")
cat("====================================================================\n\n")

# ------------------------------------------------------------------------------
# 1. LOAD DATASETS
# ------------------------------------------------------------------------------
cat(">>> [1/7] Loading Processed & Raw Datasets...\n")

# Load Cleaned Kaggle Dataset
df_kaggle <- read.csv(file.path(DATA_PROC_DIR, "kaggle_water_quality_clean.csv"), 
                      stringsAsFactors = FALSE)
cat(sprintf("  [+] Kaggle Cleaned Dataset Loaded: %d rows x %d cols\n", 
            nrow(df_kaggle), ncol(df_kaggle)))

# Load Cleaned CPCB Master Harmonized Dataset
df_cpcb_master <- read.csv(file.path(DATA_PROC_DIR, "nwdp_cpcb_master_water_quality.csv"), 
                            stringsAsFactors = FALSE)
cat(sprintf("  [+] CPCB Master Dataset Loaded: %d rows x %d cols\n", 
            nrow(df_cpcb_master), ncol(df_cpcb_master)))

# ------------------------------------------------------------------------------
# 2. DATASET DIMENSIONS, STRUCTURE & DATA TYPES
# ------------------------------------------------------------------------------
cat("\n>>> [2/7] Inspecting Structure & Variable Types...\n")

cat("\n--- Kaggle Dataset Schema ---\n")
print(str(df_kaggle))

cat("\n--- CPCB Master Dataset Schema ---\n")
print(str(df_cpcb_master))

# ------------------------------------------------------------------------------
# 3. MISSING VALUE AUDIT & RANKING
# ------------------------------------------------------------------------------
cat("\n>>> [3/7] Calculating Empirical Missingness Rates...\n")

calc_missingness <- function(df, dataset_name) {
  data.frame(
    dataset   = dataset_name,
    variable  = colnames(df),
    total_obs = nrow(df),
    valid_obs = colSums(!is.na(df)),
    na_count  = colSums(is.na(df)),
    na_pct    = round(colMeans(is.na(df)) * 100, 2),
    stringsAsFactors = FALSE
  ) %>% arrange(desc(na_pct))
}

miss_kaggle <- calc_missingness(df_kaggle, "Kaggle (2003-2014)")
miss_cpcb   <- calc_missingness(df_cpcb_master, "CPCB (2018-2021)")

cat("\nTop Missing Variables in Kaggle:\n")
print(head(miss_kaggle, 10))

cat("\nTop Missing Variables in CPCB Master:\n")
print(head(miss_cpcb, 10))

# ------------------------------------------------------------------------------
# 4. SUMMARY STATISTICS FOR CORE PARAMETERS
# ------------------------------------------------------------------------------
cat("\n>>> [4/7] Computing Core Numerical Parameter Summary Statistics...\n")

core_params <- c("ph", "dissolved_oxygen_mg_l", "bod_mg_l", "fecal_coliform_mpn_100ml")

cat("\n--- CPCB Master Summary Statistics (2018-2021) ---\n")
for (p in core_params) {
  if (p %in% colnames(df_cpcb_master)) {
    vals <- na.omit(df_cpcb_master[[p]])
    cat(sprintf("  Param: %-25s | N: %-6d | Mean: %-6.2f | SD: %-6.2f | Median: %-6.2f | IQR: %-6.2f | Min: %-6.2f | Max: %-6.2f\n",
                p, length(vals), mean(vals), sd(vals), median(vals), IQR(vals), min(vals), max(vals)))
  }
}

cat("\n--- Kaggle Summary Statistics (2003-2014) ---\n")
for (p in core_params) {
  if (p %in% colnames(df_kaggle)) {
    vals <- na.omit(df_kaggle[[p]])
    cat(sprintf("  Param: %-25s | N: %-6d | Mean: %-6.2f | SD: %-6.2f | Median: %-6.2f | IQR: %-6.2f | Min: %-6.2f | Max: %-6.2f\n",
                p, length(vals), mean(vals), sd(vals), median(vals), IQR(vals), min(vals), max(vals)))
  }
}

# ------------------------------------------------------------------------------
# 5. GEOGRAPHIC & TEMPORAL COVERAGE AUDIT
# ------------------------------------------------------------------------------
cat("\n>>> [5/7] Assessing Spatial & Temporal Granularity...\n")

cat(sprintf("  [CPCB] Unique States:   %d\n", length(unique(na.omit(df_cpcb_master$state)))))
cat(sprintf("  [CPCB] Unique Districts:%d\n", length(unique(na.omit(df_cpcb_master$district)))))
cat(sprintf("  [CPCB] Unique Stations: %d\n", length(unique(na.omit(df_cpcb_master$station)))))
cat(sprintf("  [CPCB] Coordinate Valid: %.2f%%\n", 
            mean(!is.na(df_cpcb_master$latitude) & !is.na(df_cpcb_master$longitude)) * 100))
cat(sprintf("  [CPCB] Observation Years: %s\n", 
            paste(sort(unique(na.omit(df_cpcb_master$year))), collapse = ", ")))

cat(sprintf("\n  [Kaggle] Unique States:   %d\n", length(unique(na.omit(df_kaggle$state)))))
cat(sprintf("  [Kaggle] Unique Stations: %d\n", length(unique(na.omit(df_kaggle$station_code)))))
cat(sprintf("  [Kaggle] Coordinate Valid: 0.00%% (Absent)\n"))
cat(sprintf("  [Kaggle] Observation Years: %s\n", 
            paste(sort(unique(na.omit(df_kaggle$year))), collapse = ", ")))

# ------------------------------------------------------------------------------
# 6. STATISTICAL HYPOTHESIS TESTING DEMONSTRATION
# ------------------------------------------------------------------------------
cat("\n>>> [6/7] Running Preliminary Statistical Hypothesis Tests (base R)...\n")

# A. Seasonal Wilcoxon Rank-Sum Test: Pre-Monsoon vs Monsoon DO in CPCB
df_season_test <- df_cpcb_master %>% 
  filter(season %in% c("Pre-Monsoon", "Monsoon"), !is.na(dissolved_oxygen_mg_l))

if (nrow(df_season_test) > 50) {
  wt_res <- wilcox.test(dissolved_oxygen_mg_l ~ season, data = df_season_test)
  cat("\n  [Test 1] Wilcoxon Rank-Sum Test: DO Difference (Pre-Monsoon vs Monsoon):\n")
  cat(sprintf("    W = %.0f, p-value = %.3e (Statistically Significant: %s)\n",
              wt_res$statistic, wt_res$p.value, ifelse(wt_res$p.value < 0.05, "YES", "NO")))
}

# B. ANOVA Test: BOD across Top 5 Indian States
top_states <- df_cpcb_master %>% 
  group_by(state) %>% 
  summarise(n = sum(!is.na(bod_mg_l))) %>% 
  arrange(desc(n)) %>% 
  slice_head(n = 5) %>% 
  pull(state)

df_state_test <- df_cpcb_master %>% 
  filter(state %in% top_states, !is.na(bod_mg_l), bod_mg_l < 50)

if (nrow(df_state_test) > 100) {
  aov_res <- aov(bod_mg_l ~ state, data = df_state_test)
  cat("\n  [Test 2] One-Way ANOVA: BOD Differences Across Top 5 States:\n")
  print(summary(aov_res))
}

# ------------------------------------------------------------------------------
# 7. GENERATING EXPLORATORY & DIAGNOSTIC VISUALIZATIONS
# ------------------------------------------------------------------------------
cat("\n>>> [7/7] Generating and Saving Diagnostic Figures (ggplot2)...\n")

theme_set(theme_minimal(base_size = 12) +
          theme(plot.title = element_text(face = "bold", size = 14, hjust = 0),
                plot.subtitle = element_text(color = "#555555", size = 10),
                axis.title = element_text(face = "bold"),
                panel.grid.minor = element_blank()))

# Plot 1: Missingness Comparison
p1_data <- bind_rows(
  miss_kaggle %>% filter(variable %in% c("ph", "dissolved_oxygen_mg_l", "bod_mg_l", "conductivity_umhos_cm", "fecal_coliform_mpn_100ml", "temperature_c")),
  miss_cpcb %>% filter(variable %in% c("ph", "dissolved_oxygen_mg_l", "bod_mg_l", "electrical_conductivity_us_cm", "fecal_coliform_mpn_100ml", "turbidity_ntu"))
)

p1 <- ggplot(p1_data, aes(x = reorder(variable, na_pct), y = na_pct, fill = dataset)) +
  geom_col(position = position_dodge(width = 0.8), width = 0.7) +
  coord_flip() +
  scale_fill_manual(values = c("CPCB (2018-2021)" = "#2b5c8f", "Kaggle (2003-2014)" = "#d95f02")) +
  labs(title = "Missingness Rate by Water Quality Parameter",
       subtitle = "Empirical comparison of valid observation completeness",
       x = "Parameter", y = "Missing Percentage (%)", fill = "Dataset")
ggsave(file.path(FIG_DIR, "01_missingness_overview.png"), plot = p1, width = 9, height = 5, dpi = 300)
cat("  [+] Saved figures/01_missingness_overview.png\n")

# Plot 2: Geographic Station Distribution Map (CPCB)
p2 <- ggplot(df_cpcb_master %>% distinct(station, latitude, longitude, state) %>% filter(!is.na(latitude), !is.na(longitude)),
             aes(x = longitude, y = latitude)) +
  geom_point(alpha = 0.4, size = 1.2, color = "#1b7837") +
  labs(title = "Official CPCB Surface Water Monitoring Stations in India",
       subtitle = "Spatial distribution of 4,000+ georeferenced monitoring stations (WGS84)",
       x = "Longitude (°E)", y = "Latitude (°N)") +
  coord_fixed(ratio = 1.1)
ggsave(file.path(FIG_DIR, "02_cpcb_geographic_stations_map.png"), plot = p2, width = 8, height = 8, dpi = 300)
cat("  [+] Saved figures/02_cpcb_geographic_stations_map.png\n")

# Plot 3: Dissolved Oxygen vs BOD Distribution Density
p3 <- ggplot(df_cpcb_master %>% filter(!is.na(dissolved_oxygen_mg_l), dissolved_oxygen_mg_l <= 14), 
             aes(x = dissolved_oxygen_mg_l)) +
  geom_density(fill = "#3182bd", alpha = 0.5, color = "#08519c") +
  geom_vline(xintercept = 4.0, linetype = "dashed", color = "red", linewidth = 0.8) +
  annotate("text", x = 4.2, y = 0.15, label = "CPCB Class C Minimum (4.0 mg/L)", color = "red", hjust = 0, size = 3.5) +
  labs(title = "Distribution of Dissolved Oxygen (DO) in Indian Surface Waters (2018–2021)",
       subtitle = "CPCB Monitoring Network empirical density distribution",
       x = "Dissolved Oxygen (mg/L)", y = "Density")
ggsave(file.path(FIG_DIR, "03_water_quality_distributions.png"), plot = p3, width = 8, height = 5, dpi = 300)
cat("  [+] Saved figures/03_water_quality_distributions.png\n")

# Plot 4: Top States DO Boxplot
p4_data <- df_cpcb_master %>% 
  filter(state %in% top_states, !is.na(dissolved_oxygen_mg_l), dissolved_oxygen_mg_l <= 14)

p4 <- ggplot(p4_data, aes(x = reorder(state, dissolved_oxygen_mg_l, FUN = median), y = dissolved_oxygen_mg_l, fill = state)) +
  geom_boxplot(outlier.alpha = 0.2, show.legend = FALSE) +
  coord_flip() +
  scale_fill_brewer(palette = "Set2") +
  geom_hline(yintercept = 4.0, linetype = "dashed", color = "red") +
  labs(title = "Dissolved Oxygen (DO) Comparison Across Major States",
       subtitle = "Dashed red line indicates CPCB Class C minimum standard (4 mg/L)",
       x = "State", y = "Dissolved Oxygen (mg/L)")
ggsave(file.path(FIG_DIR, "04_state_dissolved_oxygen_boxplot.png"), plot = p4, width = 8, height = 5, dpi = 300)
cat("  [+] Saved figures/04_state_dissolved_oxygen_boxplot.png\n")

# Plot 5: Seasonal BOD Dynamics
p5_data <- df_cpcb_master %>% 
  filter(!is.na(season), !is.na(bod_mg_l), bod_mg_l < 25)

p5 <- ggplot(p5_data, aes(x = factor(season, levels = c("Pre-Monsoon", "Monsoon", "Post-Monsoon", "Winter")), 
                          y = bod_mg_l, fill = season)) +
  geom_boxplot(outlier.alpha = 0.15, show.legend = FALSE) +
  scale_fill_brewer(palette = "Blues") +
  geom_hline(yintercept = 3.0, linetype = "dashed", color = "red") +
  annotate("text", x = 1, y = 3.5, label = "CPCB Class C Limit (3 mg/L)", color = "red", hjust = 0, size = 3.2) +
  labs(title = "Seasonal Variation in Biochemical Oxygen Demand (BOD)",
       subtitle = "Evaluating monsoon dilution effects on organic pollution",
       x = "Season", y = "BOD (mg/L)")
ggsave(file.path(FIG_DIR, "05_seasonal_bod_variation.png"), plot = p5, width = 8, height = 5, dpi = 300)
cat("  [+] Saved figures/05_seasonal_bod_variation.png\n")

# Plot 6: Correlation Matrix Heatmap (base R + ggplot)
cor_vars <- c("ph", "dissolved_oxygen_mg_l", "bod_mg_l", "electrical_conductivity_us_cm", "turbidity_ntu")
cor_data <- df_cpcb_master %>% select(all_of(cor_vars)) %>% drop_na()
if (nrow(cor_data) > 100) {
  cm <- cor(cor_data, method = "spearman")
  cm_df <- as.data.frame(as.table(cm))
  colnames(cm_df) <- c("Var1", "Var2", "Correlation")
  
  p6 <- ggplot(cm_df, aes(x = Var1, y = Var2, fill = Correlation)) +
    geom_tile(color = "white") +
    geom_text(aes(label = sprintf("%.2f", Correlation)), color = "black", size = 3.5) +
    scale_fill_gradient2(low = "#b2182b", mid = "#f7f7f7", high = "#2166ac", midpoint = 0, limit = c(-1, 1)) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
    labs(title = "Spearman Correlation Matrix of Water Quality Indicators",
         subtitle = "CPCB Surface Water Monitoring Network",
         x = "", y = "")
  ggsave(file.path(FIG_DIR, "06_correlation_matrix.png"), plot = p6, width = 7, height = 6, dpi = 300)
  cat("  [+] Saved figures/06_correlation_matrix.png\n")
}

# Plot 7: Decadal Comparison of State Median DO (Historical vs Modern)
k_state_do <- df_kaggle %>% 
  filter(!is.na(state), !is.na(dissolved_oxygen_mg_l)) %>% 
  group_by(state) %>% 
  summarise(median_do = median(dissolved_oxygen_mg_l), n = n()) %>% 
  filter(n >= 15) %>% 
  mutate(era = "Historical (2003-2014)")

c_state_do <- df_cpcb_master %>% 
  filter(!is.na(state), !is.na(dissolved_oxygen_mg_l)) %>% 
  group_by(state) %>% 
  summarise(median_do = median(dissolved_oxygen_mg_l), n = n()) %>% 
  filter(state %in% k_state_do$state) %>% 
  mutate(era = "Modern CPCB (2018-2021)")

comp_df <- bind_rows(k_state_do, c_state_do)
if (nrow(comp_df) > 0) {
  p7 <- ggplot(comp_df, aes(x = reorder(state, median_do), y = median_do, fill = era)) +
    geom_col(position = position_dodge(width = 0.8), width = 0.7) +
    coord_flip() +
    scale_fill_manual(values = c("Historical (2003-2014)" = "#e66101", "Modern CPCB (2018-2021)" = "#5e3c99")) +
    labs(title = "Decadal Shift in State Median Dissolved Oxygen (DO)",
       subtitle = "Comparing historical baseline (2003–2014) with modern CPCB monitoring (2018–2021)",
       x = "State", y = "Median Dissolved Oxygen (mg/L)", fill = "Monitoring Period")
  ggsave(file.path(FIG_DIR, "07_decadal_historical_comparison.png"), plot = p7, width = 9, height = 6, dpi = 300)
  cat("  [+] Saved figures/07_decadal_historical_comparison.png\n")
}

cat("\n====================================================================\n")
cat("   ALL 7 DIAGNOSTIC FIGURES GENERATED AND SAVED TO figures/\n")
cat("====================================================================\n")
