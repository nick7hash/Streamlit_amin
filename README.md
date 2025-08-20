# BluePeak Sales Dashboard

## Project Overview
This project is a Streamlit-based sales dashboard that analyzes and visualizes sales data for strategic insights. The data is ingested from Bigquery to Local SQLite database, and processed using Python libraries including Pandas, Plotly, and Statsmodels.

The main objectives of this dashboard are:
- Identify key sales trends across regions and products
- Highlight top-performing pincodes and product variants
- Provide actionable insights for data-driven decision making
## Dashboard Url - https://bluepeak.streamlit.app/

## Project Structure
- streamlit => Streamlit configuration files
- assets/ => css file and colorscheme markdown file
- amin.db => SQLite database with processed data
- analysis.ipynb => Jupyter notebook for data exploration
- collections.csv => Product Category data for mapping
- dashboard.py => Main Streamlit dashboard script
- ingestion.py => Data ingestion script
- log.log => Logging information
- pincode_with_lat-long.csv => Pincode dataset with coordinates
- requirements.txt => Python dependencies

## Features
- Interactive dashboard using Streamlit
- Visualizations created with Plotly
- Summary and conclusion sections highlighting key insights
- Supports date range selection and filtering

## Tools Used
- Streamlit
- Pandas
- Plotly
- Sqlite
- GCP

## Conclusion
This dashboard provides a comprehensive view of sales performance, highlighting high-performing regions, key products, and revenue trends. It supports data-driven decision-making and strategic planning for improving sales performance.
