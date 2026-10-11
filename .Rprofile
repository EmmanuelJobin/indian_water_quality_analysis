# Automatically add local project library and pandoc / TinyTeX paths
local({
  proj_lib <- file.path(getwd(), "r_libs")
  if (dir.exists(proj_lib) && !(proj_lib %in% .libPaths())) {
    .libPaths(c(proj_lib, .libPaths()))
  }
  proj_lib_parent <- file.path(getwd(), "indian_water_quality_project", "r_libs")
  if (dir.exists(proj_lib_parent) && !(proj_lib_parent %in% .libPaths())) {
    .libPaths(c(proj_lib_parent, .libPaths()))
  }
  
  # Ensure pandoc from RStudio is found if not on system PATH
  if (Sys.which("pandoc") == "") {
    rstudio_pandoc_paths <- c(
      "/Applications/RStudio.app/Contents/Resources/app/quarto/bin/tools/aarch64",
      "/Applications/RStudio.app/Contents/Resources/app/quarto/bin/tools/x86_64",
      "/Applications/RStudio.app/Contents/Resources/app/resources/pandoc"
    )
    for (p in rstudio_pandoc_paths) {
      if (file.exists(file.path(p, "pandoc"))) {
        Sys.setenv(RSTUDIO_PANDOC = p)
        if (requireNamespace("rmarkdown", quietly = TRUE)) {
          rmarkdown::find_pandoc(dir = p)
        }
        break
      }
    }
  }

  # Ensure TinyTeX pdflatex is found if installed
  tinytex_bin <- path.expand("~/Library/TinyTeX/bin/universal-darwin")
  if (dir.exists(tinytex_bin) && !grepl(tinytex_bin, Sys.getenv("PATH"))) {
    Sys.setenv(PATH = paste(tinytex_bin, Sys.getenv("PATH"), sep = ":"))
  }
})
