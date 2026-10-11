# ==============================================================================
# Script: 03_exploratory_analysis.R
# Project: Geographic and Seasonal Analysis of Surface Water Quality in India
# Course: DSC 513 - Introduction to Data Science (M.Tech Mini Project)
# Description: Exploratory data analysis, statistical summaries, hypothesis testing,
#              and high-resolution visualization generation for water quality data.
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
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  library(readr)
})

# ------------------------------------------------------------------------------
# 1. PATH RESOLUTION & SETUP
# ------------------------------------------------------------------------------
find_base_dir <- function() {
  candidates <- c(".", "indian_water_quality_project", "..")
  for (cand in candidates) {
    if (dir.exists(file.path(cand, "data", "processed"))) {
      return(normalizePath(cand))
    }
  }
  stop("Could not locate data/processed directory.")
}

BASE_DIR <- find_base_dir()
cat("=== DSC 513: EXPLORATORY DATA ANALYSIS & VISUALIZATION PIPELINE ===\n")
cat(sprintf("Working Root Directory: %s\n\n", BASE_DIR))

PROC_DIR <- file.path(BASE_DIR, "data", "processed")
FIG_DIR  <- file.path(BASE_DIR, "figures")
dir.create(FIG_DIR, showWarnings = FALSE, recursive = TRUE)

# Set unified publication ggplot2 theme
theme_set(
  theme_minimal(base_size = 11) +
    theme(
      plot.title = element_text(face = "bold", size = 13, hjust = 0),
      plot.subtitle = element_text(color = "#444444", size = 9.5),
      axis.title = element_text(face = "bold", size = 10),
      legend.position = "bottom",
      panel.grid.minor = element_blank(),
      strip.text = element_text(face = "bold")
    )
)

# ------------------------------------------------------------------------------
# 2. LOAD CLEANED DATASETS
# ------------------------------------------------------------------------------
cat("[1/6] Loading Cleaned Datasets...\n")
cpcb_master_path <- file.path(PROC_DIR, "nwdp_cpcb_master_water_quality.csv")
kag_clean_path   <- file.path(PROC_DIR, "kaggle_water_quality_clean.csv")

df_cpcb <- read_csv(cpcb_master_path, show_col_types = FALSE, progress = FALSE)
df_kag  <- read.csv(kag_clean_path, stringsAsFactors = FALSE)

cat(sprintf("  Loaded CPCB Master: %s rows x %d cols\n", format(nrow(df_cpcb), big.mark = ","), ncol(df_cpcb)))
cat(sprintf("  Loaded Kaggle Data: %d rows x %d cols\n\n", nrow(df_kag), ncol(df_kag)))

# ------------------------------------------------------------------------------
# 3. STATISTICAL SUMMARIES OF CORE PARAMETERS
# ------------------------------------------------------------------------------
cat("[2/6] Calculating Parametric & Non-Parametric Statistics...\n")

core_params <- c("dissolved_oxygen_mg_l", "bod_mg_l", "ph", "electrical_conductivity_us_cm")

cat("\n--- CPCB Summary Statistics (2018–2021) ---\n")
for (p in core_params) {
  vals <- na.omit(df_cpcb[[p]])
  cat(sprintf("  %-30s | N: %6d | Mean: %6.2f | SD: %7.2f | Median: %6.2f | IQR: %6.2f | Min: %6.2f | Max: %8.2f\n",
              p, length(vals), mean(vals), sd(vals), median(vals), IQR(vals), min(vals), max(vals)))
}

cat("\n--- Kaggle Summary Statistics (2003–2014) ---\n")
kag_params <- c("dissolved_oxygen_mg_l", "bod_mg_l", "ph", "conductivity_umhos_cm")
for (p in kag_params) {
  vals <- na.omit(df_kag[[p]])
  cat(sprintf("  %-30s | N: %6d | Mean: %6.2f | SD: %7.2f | Median: %6.2f | IQR: %6.2f | Min: %6.2f | Max: %8.2f\n",
              p, length(vals), mean(vals), sd(vals), median(vals), IQR(vals), min(vals), max(vals)))
}

# ------------------------------------------------------------------------------
# 4. HYPOTHESIS TESTING (MONSOON DYNAMICS & STATE DIFFERENCES)
# ------------------------------------------------------------------------------
cat("\n[3/6] Running Inferential Statistical Hypothesis Tests...\n")

# Test 1: Wilcoxon Rank-Sum Test for Seasonal Dilution (Pre-Monsoon vs Monsoon DO)
season_test_data <- df_cpcb %>% 
  filter(season %in% c("Pre-Monsoon", "Monsoon"), !is.na(dissolved_oxygen_mg_l))

wt_res <- wilcox.test(dissolved_oxygen_mg_l ~ season, data = season_test_data)
cat("\n  [Test 1] Wilcoxon Rank-Sum Test: Dissolved Oxygen (Pre-Monsoon vs Monsoon):\n")
cat(sprintf("    W = %.0f, p-value = %.3e (Statistically Significant at alpha=0.01: %s)\n",
            wt_res$statistic, wt_res$p.value, ifelse(wt_res$p.value < 0.01, "YES", "NO")))
cat(sprintf("    Pre-Monsoon Median DO: %.2f mg/L | Monsoon Median DO: %.2f mg/L\n",
            median(season_test_data$dissolved_oxygen_mg_l[season_test_data$season == "Pre-Monsoon"]),
            median(season_test_data$dissolved_oxygen_mg_l[season_test_data$season == "Monsoon"])))

# Test 2: Kruskal-Wallis Test for State Differences in BOD
top_states <- df_cpcb %>% 
  count(state, sort = TRUE) %>% 
  filter(!is.na(state)) %>% 
  slice_head(n = 6) %>% 
  pull(state)

state_bod_data <- df_cpcb %>% 
  filter(state %in% top_states, !is.na(bod_mg_l))

kw_res <- kruskal.test(bod_mg_l ~ state, data = state_bod_data)
cat("\n  [Test 2] Kruskal-Wallis Test: BOD Differences Across Top 6 States:\n")
cat(sprintf("    Chi-squared = %.2f, df = %d, p-value = %.3e (Significant: %s)\n",
            kw_res$statistic, kw_res$parameter, kw_res$p.value, ifelse(kw_res$p.value < 0.01, "YES", "NO")))

# ------------------------------------------------------------------------------
# 5. GENERATING PUBLICATION-QUALITY FIGURES (ggplot2)
# ------------------------------------------------------------------------------
cat("\n[4/6] Generating Publication Visualizations...\n")

# Plot 1: Missingness Overview
calc_missing <- function(df, dname) {
  data.frame(
    dataset = dname,
    variable = colnames(df),
    na_pct = round(colMeans(is.na(df)) * 100, 2),
    stringsAsFactors = FALSE
  )
}
m_kag  <- calc_missing(df_kag, "Kaggle (2003-2014)") %>% 
  filter(variable %in% c("ph", "dissolved_oxygen_mg_l", "bod_mg_l", "conductivity_umhos_cm", "temperature_c", "fecal_coliform_mpn_100ml"))
m_cpcb <- calc_missing(df_cpcb, "CPCB (2018-2021)") %>% 
  filter(variable %in% c("ph", "dissolved_oxygen_mg_l", "bod_mg_l", "electrical_conductivity_us_cm", "turbidity_ntu", "fecal_coliform_mpn_100ml")) %>% 
  mutate(variable = ifelse(variable == "electrical_conductivity_us_cm", "conductivity_umhos_cm", variable))

p1_df <- bind_rows(m_cpcb, m_kag)

p1 <- ggplot(p1_df, aes(x = reorder(variable, na_pct), y = na_pct, fill = dataset)) +
  geom_col(position = position_dodge(width = 0.8), width = 0.7) +
  coord_flip() +
  scale_fill_manual(values = c("CPCB (2018-2021)" = "#2b5c8f", "Kaggle (2003-2014)" = "#d95f02")) +
  labs(
    title = "Figure 1: Missingness Rate by Water Quality Parameter",
    subtitle = "Empirical comparison of observation completeness across monitoring programs",
    x = "Parameter", y = "Missing Percentage (%)", fill = "Data Source"
  )
ggsave(file.path(FIG_DIR, "01_missingness_overview.png"), p1, width = 8, height = 4.8, dpi = 300)
cat("  [+] Saved 01_missingness_overview.png\n")

# Plot 2: CPCB Geographic Station Map
p2 <- ggplot(
  df_cpcb %>% distinct(station, latitude, longitude, state) %>% filter(!is.na(latitude), !is.na(longitude)),
  aes(x = longitude, y = latitude)
) +
  geom_point(alpha = 0.35, size = 1.3, color = "#1b7837") +
  coord_fixed(ratio = 1.1) +
  labs(
    title = "Figure 2: Official CPCB Surface Water Quality Monitoring Network",
    subtitle = "Spatial distribution of 4,017 georeferenced stations across Indian river basins (EPSG:4326)",
    x = "Longitude (°E)", y = "Latitude (°N)"
  )
ggsave(file.path(FIG_DIR, "02_cpcb_geographic_stations_map.png"), p2, width = 7.5, height = 7.5, dpi = 300)
cat("  [+] Saved 02_cpcb_geographic_stations_map.png\n")

# Plot 3: Distribution Density of DO and pH
p3_do <- ggplot(df_cpcb %>% filter(!is.na(dissolved_oxygen_mg_l)), aes(x = dissolved_oxygen_mg_l)) +
  geom_histogram(aes(y = after_stat(density)), bins = 35, fill = "#3182bd", color = "white", alpha = 0.7) +
  geom_density(color = "#08519c", linewidth = 0.9) +
  geom_vline(xintercept = 4.0, linetype = "dashed", color = "red", linewidth = 0.8) +
  annotate("text", x = 4.3, y = 0.20, label = "CPCB Class C Minimum (4.0 mg/L)", color = "red", hjust = 0, size = 3.2) +
  labs(
    title = "Figure 3: Empirical Density Distribution of Dissolved Oxygen",
    subtitle = "Official CPCB Surface Water Monitoring Network (2018–2021)",
    x = "Dissolved Oxygen (mg/L)", y = "Density"
  ) +
  xlim(0, 15)
ggsave(file.path(FIG_DIR, "03_water_quality_distributions.png"), p3_do, width = 8, height = 4.8, dpi = 300)
cat("  [+] Saved 03_water_quality_distributions.png\n")

# Plot 4: State-wise Dissolved Oxygen Boxplot
p4_data <- df_cpcb %>% 
  filter(state %in% top_states, !is.na(dissolved_oxygen_mg_l))

p4 <- ggplot(p4_data, aes(x = reorder(state, dissolved_oxygen_mg_l, FUN = median), y = dissolved_oxygen_mg_l, fill = state)) +
  geom_boxplot(outlier.alpha = 0.15, show.legend = FALSE, width = 0.6) +
  geom_hline(yintercept = 4.0, linetype = "dashed", color = "red", linewidth = 0.8) +
  coord_flip() +
  scale_fill_brewer(palette = "Set2") +
  labs(
    title = "Figure 4: Dissolved Oxygen (DO) Distribution Across Major States",
    subtitle = "Dashed red reference line indicates CPCB Class C minimum standard (4.0 mg/L)",
    x = "State", y = "Dissolved Oxygen (mg/L)"
  ) +
  ylim(0, 14)
ggsave(file.path(FIG_DIR, "04_state_dissolved_oxygen_boxplot.png"), p4, width = 8, height = 5, dpi = 300)
cat("  [+] Saved 04_state_dissolved_oxygen_boxplot.png\n")

# Plot 5: Seasonal BOD Variation
p5_data <- df_cpcb %>% 
  filter(!is.na(season), !is.na(bod_mg_l), bod_mg_l <= 30)

p5 <- ggplot(
  p5_data, 
  aes(x = factor(season, levels = c("Pre-Monsoon", "Monsoon", "Post-Monsoon", "Winter")), 
      y = bod_mg_l, fill = season)
) +
  geom_boxplot(outlier.alpha = 0.15, show.legend = FALSE, width = 0.55) +
  geom_hline(yintercept = 3.0, linetype = "dashed", color = "red", linewidth = 0.8) +
  annotate("text", x = 1.0, y = 4.0, label = "CPCB Class C Limit (3.0 mg/L)", color = "red", hjust = 0, size = 3.2) +
  scale_fill_brewer(palette = "Blues") +
  labs(
    title = "Figure 5: Seasonal Variation in Biochemical Oxygen Demand (BOD)",
    subtitle = "Examining monsoon river dilution and post-monsoon organic concentration",
    x = "Season", y = "BOD (mg/L)"
  )
ggsave(file.path(FIG_DIR, "05_seasonal_bod_variation.png"), p5, width = 8, height = 4.8, dpi = 300)
cat("  [+] Saved 05_seasonal_bod_variation.png\n")

# Plot 6: Correlation Matrix Heatmap
cor_vars <- c("ph", "dissolved_oxygen_mg_l", "bod_mg_l", "electrical_conductivity_us_cm", "turbidity_ntu")
cor_data <- df_cpcb %>% select(all_of(cor_vars)) %>% drop_na()

cm <- cor(cor_data, method = "spearman")
cm_df <- as.data.frame(as.table(cm))
colnames(cm_df) <- c("Var1", "Var2", "Correlation")

var_labels <- c(
  "ph" = "pH",
  "dissolved_oxygen_mg_l" = "DO",
  "bod_mg_l" = "BOD",
  "electrical_conductivity_us_cm" = "Conductivity",
  "turbidity_ntu" = "Turbidity"
)
cm_df$Var1 <- recode(cm_df$Var1, !!!var_labels)
cm_df$Var2 <- recode(cm_df$Var2, !!!var_labels)

p6 <- ggplot(cm_df, aes(x = Var1, y = Var2, fill = Correlation)) +
  geom_tile(color = "white", linewidth = 0.8) +
  geom_text(aes(label = sprintf("%.2f", Correlation)), color = "black", size = 3.6, fontface = "bold") +
  scale_fill_gradient2(low = "#b2182b", mid = "#f7f7f7", high = "#2166ac", midpoint = 0, limit = c(-1, 1)) +
  labs(
    title = "Figure 6: Spearman Rank Correlation Matrix of Water Quality Indicators",
    subtitle = "Evaluated on complete pairwise CPCB monitoring observations (2018–2021)",
    x = "", y = "", fill = "Spearman r"
  )
ggsave(file.path(FIG_DIR, "06_correlation_matrix.png"), p6, width = 6.5, height = 5.5, dpi = 300)
cat("  [+] Saved 06_correlation_matrix.png\n")

# Plot 7: Decadal Shift Comparison (Kaggle Historical vs CPCB Modern)
k_comp <- df_kag %>% 
  filter(!is.na(state), !is.na(dissolved_oxygen_mg_l)) %>% 
  group_by(state) %>% 
  summarise(median_do = median(dissolved_oxygen_mg_l), n = n()) %>% 
  filter(n >= 15) %>% 
  mutate(era = "Historical (2003-2014)")

c_comp <- df_cpcb %>% 
  filter(!is.na(state), !is.na(dissolved_oxygen_mg_l)) %>% 
  group_by(state) %>% 
  summarise(median_do = median(dissolved_oxygen_mg_l), n = n()) %>% 
  filter(state %in% k_comp$state) %>% 
  mutate(era = "Modern CPCB (2018-2021)")

comp_df <- bind_rows(k_comp, c_comp)

p7 <- ggplot(comp_df, aes(x = reorder(state, median_do), y = median_do, fill = era)) +
  geom_col(position = position_dodge(width = 0.8), width = 0.7) +
  coord_flip() +
  scale_fill_manual(values = c("Historical (2003-2014)" = "#e66101", "Modern CPCB (2018-2021)" = "#5e3c99")) +
  labs(
    title = "Figure 7: Decadal Comparison of State Median Dissolved Oxygen",
    subtitle = "Historical Kaggle baseline (2003–2014) vs Modern official CPCB monitoring (2018–2021)",
    x = "State", y = "Median Dissolved Oxygen (mg/L)", fill = "Monitoring Epoch"
  )
ggsave(file.path(FIG_DIR, "07_decadal_historical_comparison.png"), p7, width = 8.5, height = 5.5, dpi = 300)
cat("  [+] Saved 07_decadal_historical_comparison.png\n")

# Plot 8: Scatter Plot DO vs BOD
p8_data <- df_cpcb %>% 
  filter(!is.na(dissolved_oxygen_mg_l), !is.na(bod_mg_l), bod_mg_l <= 40, dissolved_oxygen_mg_l <= 14)

p8 <- ggplot(p8_data, aes(x = bod_mg_l, y = dissolved_oxygen_mg_l)) +
  geom_point(alpha = 0.12, size = 1.0, color = "#2b5c8f") +
  geom_smooth(method = "gam", formula = y ~ s(x, bs = "cs"), color = "#d95f02", linewidth = 1, se = TRUE) +
  geom_hline(yintercept = 4.0, linetype = "dashed", color = "red") +
  geom_vline(xintercept = 3.0, linetype = "dashed", color = "red") +
  labs(
    title = "Figure 8: Relationship Between Biochemical Oxygen Demand and Dissolved Oxygen",
    subtitle = "Inverse non-linear dynamic showing severe oxygen depletion under high organic load",
    x = "Biochemical Oxygen Demand - BOD (mg/L)", y = "Dissolved Oxygen - DO (mg/L)"
  )
ggsave(file.path(FIG_DIR, "08_do_vs_bod_relationship.png"), p8, width = 8, height = 4.8, dpi = 300)
cat("  [+] Saved 08_do_vs_bod_relationship.png\n")

# Plot 9: Before-and-After Cleaning Diagnostic (Kaggle pH Outlier Removal)
kag_raw_path <- file.path(BASE_DIR, "data", "raw", "kaggle", "water_dataX.csv")
df_kag_raw <- read.csv(kag_raw_path, stringsAsFactors = FALSE, fileEncoding = "latin1", check.names = FALSE)
ph_raw <- suppressWarnings(as.numeric(ifelse(df_kag_raw$PH %in% c("NAN", "NA", ""), NA, df_kag_raw$PH)))

p9_df <- bind_rows(
  data.frame(Stage = "Raw (Uncleaned)", ph = ph_raw),
  data.frame(Stage = "Cleaned (Post Range-Check)", ph = df_kag$ph)
) %>% filter(!is.na(ph))

p9 <- ggplot(p9_df, aes(x = Stage, y = ph, fill = Stage)) +
  geom_boxplot(outlier.size = 1.5, outlier.color = "red", show.legend = FALSE, width = 0.4) +
  scale_y_log10() +
  scale_fill_manual(values = c("Raw (Uncleaned)" = "#e41a1c", "Cleaned (Post Range-Check)" = "#377eb8")) +
  labs(
    title = "Figure 9: Data Cleaning Diagnostic - pH Outlier Removal (Log Scale)",
    subtitle = "Removing OCR scraping artifacts (values up to 67,115) to restore valid chemical range (0–14)",
    x = "Preprocessing Stage", y = "pH Value (log10 scale)"
  )
ggsave(file.path(FIG_DIR, "09_cleaning_before_after_ph.png"), p9, width = 7.5, height = 4.8, dpi = 300)
cat("  [+] Saved 09_cleaning_before_after_ph.png\n")

# Plot 10: Observations by State
p10_data <- df_cpcb %>% 
  count(state, sort = TRUE) %>% 
  filter(!is.na(state)) %>% 
  slice_head(n = 15)

p10 <- ggplot(p10_data, aes(x = reorder(state, n), y = n)) +
  geom_col(fill = "#41b6c4", width = 0.7) +
  coord_flip() +
  labs(
    title = "Figure 10: Monitoring Observation Frequency Across Top 15 States",
    subtitle = "Official CPCB Surface Water Monitoring Programme (2018–2021)",
    x = "State / UT", y = "Number of Monitoring Records"
  )
ggsave(file.path(FIG_DIR, "10_state_observation_counts.png"), p10, width = 8, height = 5, dpi = 300)
cat("  [+] Saved 10_state_observation_counts.png\n")

cat("\n==================================================================\n")
cat("   ALL 10 PUBLICATION FIGURES GENERATED AND SAVED TO figures/\n")
cat("==================================================================\n")
