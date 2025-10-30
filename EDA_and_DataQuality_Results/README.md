# EDA_and_DataQuality_Results

This directory serves as the centralized repository of all automated data quality reports, exploratory data analysis (EDA) visuals, and summary statistics for QueryTube datasets.

## Contents
- **data_quality_and_eda_report_Masterdataset_1.txt** 📑
  - Comprehensive text report detailing missing values, duplicates, statistical summaries, and key insights for the main YouTube video metadata.

- **dqc_missing_values.png** 🟨
  - Visualization of missing value distribution across main dataset columns to facilitate audit and cleaning.

- **eda_correlation_matrix.png** 🔗
  - Heatmap of feature correlation, useful for identifying relationships among numerical variables (views, likes, etc.).

- **eda_log_distributions.png** & **eda_numerical_distributions.png** 📉
  - Plot the (log-scale and raw) distributions of main statistical features: useful to assess skew and distributional properties.

- **eda_publishing_trend.png** 📈
  - Time series plot of video publishing activity; reveals seasonality or other temporal patterns in the dataset.

- **eda_top_categories.png** & **eda_top_channels.png** 🏆
  - Ranking visuals displaying the most frequent video categories and most prolific channels in the dataset.

- **Dataset_2/**
  - Subdirectory containing analysis, plots, and reports for the transcript dataset (distinct from core video metadata), including:
  - **enhanced_quality_summary.csv**: Quantitative quality metrics and category breakdowns for transcripts.
  - **enhanced_transcript_analysis_dashboard.png**: Multi-plot dashboard charting transcript content length, quality classifications, and additional transcript analytics.

These artifacts assist with ongoing data health monitoring, project reporting, and support reproducibility for research or development workflows.
