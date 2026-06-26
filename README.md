# Metro Nashville Government salary: Automated Data Pipeline & Streamlit Dashboard

An end‑to‑end Python data engineering and analytics application that automates salary data collection, cleans and structures complex financial datasets, and delivers an interactive analytics dashboard for exploring employee compensation across branches, job classes, and fiscal years.

This project combines web automation, data engineering, and interactive data visualization into a single, reproducible workflow.

---

## 📌 Project Overview
This application automates the entire lifecycle of public workforce salary data:
* **Automated Extraction:** Downloads salary CSV files from the Nashville Open Data Portal via the ArcGIS Hub website using Selenium.
* **Data Normalization:** Bypasses complex Shadow DOM tree wrappers, cleans raw data, fixes corrupted formatting, and normalizes institutional department names using pandas.
* **Metric Derivation:** Computes specialized tracking fields like *Total Pay* and *Extra Pay* to enforce mathematical integrity.
* **Temporal Comparison:** Empowers users to explore local spending trends by single year or multi‑year comparisons.
* **Hierarchical Drill-Down:** Provides micro-navigation paths from Branch → Job Class → Employee History.
* **Interactive UI:** Serves dynamic insights through a responsive, multi-tab Streamlit dashboard.

---

## 📊 Data Source
* **Origin:** Nashville Open Data Portal via ArcGIS Hub
* **Dataset Name:** Metro Government Employee Earnings

---

## 🛠️ Tech Stack
* **Python 3.8+:** Core engineering logic and orchestration layer for scraping, cleaning, and serving data
* **Selenium & WebDriver:** Headless browser automation backend to handle dynamically rendered web components and event‑driven DOM interactions
* **pandas & NumPy:** Data cleaning, regular expression text manipulation, type fixing, normalization, and aggregation workflows
* **Streamlit:** Multi‑tab dashboard with persistent UI navigation via session_state for a smooth, app‑like user experience
* **Altair:** Declarative charting library used for interactive, reproducible visualizations
* **Requests:** Lightweight HTTP client for external API enrichment and metadata retrieval
* **scikit‑learn:** Feature scaling for scoring, ranking, or downstream ML‑ready transformations
* **Standard Library Utilities:** os, glob, csv, and re for file discovery, directory scanning, pattern matching, and lightweight I/O

---

## ⭐ Key Features

### 🤖 Shadow DOM Traversal & Scraping
The extraction script navigates multi-layered, deep Shadow DOM elements (`arcgis-hub-download-list` and `calcite-button`) to trigger native browser CSV downloads completely headless.

### 🧼 Automated Data Cleaning & Type Fixing
Standardizes all pay columns using regular expression cleaners to handle broken floating-point formatting, trailing minus signs, scientific notation, and currency symbols (`$,`).

### 📈 Derived Financial Metrics
The pipeline recalculates and cross-references financial integrity by validating:
* **Total Pay** = Sum of all independent pay categories (re-summed gross channels)
* **Extra Pay** = Supplemental Pay + Longevity + Bonuses + Payouts + Other Pay

### 📅 Multi‑Year Analysis
Toggle seamlessly between **Single Year View** and **Multi‑Year Comparison View**. The dashboard UI dynamically adjusts all labels, metric callouts, and graphical summaries based on your active selection.

### 🔍 Multi‑Level Drill‑Down Navigation
Hierarchical exploration powered by Streamlit’s native `session_state` preserves user tracking across selections:
```text
Branch ──> Employee Roster ──> Employee History
```

### 🗂️ Rich, Multi‑Tab Dashboard Ecosystem
1. **Summary & Breakdown:** High-level KPIs and salary totals.
2. **Branch Breakdown:** Drill‑down into specific operational branches.
3. **Job Class Breakdown:** Filter by branch and explore granular job types.
4. **Highest Paid Employees:** Instant filtering for Total Pay ≥ \$120K.
5. **Most Overtime:** Highlights personnel with Overtime Pay ≥ \$30K.
6. **Most Extra Pay:** Highlights personnel with Extra Pay ≥ \$30K.
7. **Raw Data Explorer:** Regex name searching paired with active pay-range sliders.

---

## 🏗️ Architecture
```text
Selenium Scraper (ArcGIS Hub)
              ↓ 
        Raw CSV Files 
              ↓ 
 pandas Cleaning & Transformation (Regex / Typings)
              ↓ 
    Derived Metrics Engine (Total Pay & Extra Pay)
              ↓ 
 Streamlit Dashboard UI (7 Tabs + Drill‑Down States)
```

---

## 🛠️ Prerequisites & Installation

### 1. System Requirements
* **Python 3.8** or higher
* **Mozilla Firefox Browser**
* **Geckodriver** (Ensure it is added to your system's `PATH` variable)

### 2. Python Dependencies
Install all pipeline and interface dependencies using `pip`:
```bash
pip install selenium pandas numpy scikit-learn scipy streamlit
```

---

## 📁 Project Structure
```text
.
├── scrape.py               # Selenium scraper & data transformation pipeline
├── app.py                  # Streamlit dashboard application (Main UI) 
├── utils/                  # Helper modules (clean_currency, loaders, etc.) 
├── data/                   # Subdirectory where raw CSV targets are downloaded
├── requirements.txt        # Project dependencies list
└── README.md               # Project documentation
```
> **Note:** The scraper script expects a directory named `Project/` or `data/` to exist in the root execution directory before launching native browser tasks.

---

## 🚀 Execution Workflow

### Step 1: Run the Scraping & Data Engineering Pipeline
Execute the pipeline from your terminal to parse the web portal, extract the assets, run calculations, and clean database schemas:
```bash
python scrape.py
```
*This drops non-essential database tracking columns (`OBJECTID`), handles 7 payment streams, maps institutional acronyms (e.g., `POL`, `ECC`, `NDOT`) to clean department strings, and loads a modeling-ready `cleaned_metro_data.csv` to storage.*

### Step 2: Launch the Analytics Interface
Boot up the local web engine to explore dashboard metrics and employee roster trees:
```bash
streamlit run app.py
```

---

## Dashboard Preview

<img width="1679" height="821" alt="image" src="https://github.com/user-attachments/assets/18fd2a42-5887-4389-be0a-489e95243c31" />
---
<img width="1732" height="816" alt="image" src="https://github.com/user-attachments/assets/178aac9e-ff32-46b8-89bd-cbd021393772" />
---
<img width="1730" height="476" alt="image" src="https://github.com/user-attachments/assets/938ad906-436a-4f42-b13b-82b1519105c4" />

---

## 📋 Final Output Schema
The output layer contains the following critical, structured analytical dimensions:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| **Fiscal Year** | Integer | The target budget/accounting year of the payout. |
| **Business Unit** | String | The exact accounting entity node identifier code. |
| **Regular Pay** | Float | Base salaried or standard hourly compensation. |
| **Total Pay** | Float | Re-summed actual gross pay across all channels. |
| **Extra Pay** | Float | Delta total pay (Total Pay minus Regular Pay). |
| **Prefix** | String | Extracted department acronym (e.g., `MNPD`, `FIR`). |

---

## ▶️ Future Enhancements
Automated scheduling (cron, Task Scheduler)
Database backend (PostgreSQL / SQLite)
Docker containerization
Cloud deployment (Streamlit Cloud, Azure App Service)
API layer for external consumption



