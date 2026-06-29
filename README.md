# README — Metro Nashville Payroll Data Pipeline & Dashboard

This project delivers an end-to-end data solution for extracting, transforming, and visualizing the Metro Nashville Government employee payroll records. It couples a Selenium-driven web pipeline—engineered to bypass dynamic, nested Shadow DOM architectures on ArcGIS Hub—with an interactive Streamlit analytics dashboard for multi-level exploratory data analysis.

---

**Target Production Dataset:** `Metro_Government.csv`  
This resource features standardized currency fields, recalculated totals, chronological workforce sequencing, and forward/backward-filled historical metadata.

## 🚀 Key Features

### Data Engineering Pipeline
* **Shadow DOM Traversal:** Automated web scraping through hierarchical structures (`arcgis-hub-download-list` ➔ `calcite-button`) using headless-capable Selenium Firefox configurations.
* **Download Polling Protection:** Monitors system file locks and transient partial file downloads (`.part`) to ensure seamless data-packet integrity.
* **Corrupted Currency Normalization:** Heavy regex string sanitation converting broken notation types (e.g., `-3.45-13` ➔ `-3.45E-13`) into clean floating-point types.
* **Historical Imputation:** Groups records by unique employee names over time to fill institutional history gaps using forward/backward (`ffill`/`bfill`) logic.

### Streamlit Analytics Client
* **Dual Temporal Engines:** Toggle dynamically between localized `Single Year` timelines and comprehensive `Compare Years` ranges via selection pills.
* **Stateful Drill-Down Routing:** Traverses multi-level layout stacks from high-level branch overviews down to specific employee histories using `st.session_state` persistence.
* **Enriched Statistical Grids:** Embeds custom HTML markdown blocks isolating collective city headcount metrics, average benchmarks, and multi-variable ledger accounts.

## 📂 Project Structure
```text
├── scraper.py                # Main data engineering ETL pipeline engine script
├── csv                       # Auto-cleaned
├── app.py                    # Streamlit dashboard interface and visualization views
└── README.md                 # System project documentation
```

## 🧰 Requirements & Installation

### Environment Setup
Verify your system runs Python 3.9+ along with an active production instance of Mozilla Firefox.

```bash
pip install selenium pandas numpy scikit-learn streamlit altair requests
```

### WebDriver Dependency
The extraction tier uses **GeckoDriver** to orchestrate browser automated tasks. Add the driver's binary executable path directly to your target host system's `PATH` variables.

## ⚙️ Workflow Execution Architecture

### Phase 1: Browser Ingestion Engine (`scraper.py ➔ run_selenium_extraction`)
1. Purges residual historical components and partial data tracking logs found in `/data`.
2. Configures a detached Firefox driver optimization matrix preventing interactive popup loops.
3. Coordinates precise web interactions using active polling via `WebDriverWait` selectors.
4. Triggers background browser streaming routines, routing downloads straight to disk blocks.

### Phase 2: Structural Ledger Normalization (`scraper.py ➔ process_csv`)
1. **Sanitization:** Clears non-numeric currency flags and enforces unified float structures.
2. **Re-Aggregation:** Programmatically recalculates `Total Pay` across 7 separate localized payment fields to prevent analytical drift.
3. **Prefix Evaluation:** Decodes administrative business tags to apply clean department labels.
4. **Timeline Balancing:** Orders rows by index fields to safely execute historical sequence imputation.

### Phase 3: Dashboard Interface Display (`app.py`)
1. Scans the local filesystem to load the highest-priority processed CSV dataset.
2. Intercepts structural string definitions to run a secondary, fail-safe instance of currency regex normalization.
3. Allocates UI frames to handle tab partitions (Summary, Branch Drilling, Overtime Outliers, Charts, and Data Tables).

---

## 🧪 Running the Software

### 1. Execute the ETL Pipeline

#### Option A: Full End-to-End Extraction Sequence
Run the full sequence to automate browser-based extraction and data normalization:
```python
# Execute within an orchestration script or interactive terminal
file_path = run_selenium_extraction()
process_csv()
```

#### Option B: Independent Dataset Processing
Skip the live browser connection by manually copying a pre-downloaded source CSV file into and running the transformation script directly:
```python
process_csv()
```

### 2. Boot the Streamlit Dashboard UI
Launch your local web interface instance using the execution loop:
```bash
streamlit run app.py
```
*This command runs a local server process, automatically opening the dashboard in your default browser at `http://localhost:8501`.*

---

## 📊 Dataset Schema Definition

The underlying production dataset `Metro_Government.csv` structures information across these explicit parameters:

| Attribute Name | Type | Analytical Context & Rule Inversion |
| :--- | :--- | :--- |
| **Employee Name** | String | Core identifying name string used for relational lookups |
| **Branch** | String | Human-readable parent division identity mapped via organizational codes |
| **Description** | String | Mapped operational subunit or granular structural section identifier |
| **Regular Pay** | Float | Base foundational hourly or salaried compensation metrics |
| **Overtime Pay** | Float | Tracked extra structural shifts or service hour compensation |
| **Supplemental Pay**| Float | Specialized allowances, active tracking stipends, or location additions |
| **Longevity** | Float | Financial recognition metrics tracking employee career milestones |
| **Bonuses** | Float | Merit awards or discretionary lump-sum payments |
| **Payouts** | Float | Accrued benefits, severance buckets, or offboard settlements |
| **Other Pay** | Float | Residual miscellaneous tracking fields |
| **Total Pay** | Float | Programmatic summary field aggregating all distinct payment channels |
| **Fiscal Year** | Integer | Annual reporting cycle calendar tag (sorted chronologically) |

---

## Dashboard Preview

<!-- <img width="1732" height="816" alt="image" src="https://github.com/user-attachments/assets/178aac9e-ff32-46b8-89bd-cbd021393772" /> -->
---
<img width="1677" height="717" alt="image" src="https://github.com/user-attachments/assets/6ee4f59a-9b44-472f-9397-e9cab2510fc9" />

"<img width="1690" height="596" alt="image" src="https://github.com/user-attachments/assets/1b2bc6b8-b13c-481a-a577-7bd7b0a28402" />

<img width="1164" height="596" alt="image" src="https://github.com/user-attachments/assets/87ce64cc-df10-4e6d-b098-774081b77102" />

---

## 💻 Technical Design: Stateful App Drill-Downs

The Streamlit UI application utilizes state tracking rules to manage internal nested layout changes across individual organizational layers without losing current context:

```text
Level 0: City-Wide Branch Summary Matrix
   │
   └──➔ Level 1: Filtered Departmental Roster (Stores 'selected_branch_drill')
             │
             └──➔ Level 2: Historical Employee Record View (Stores 'selected_employee_drill')
```
*Triggering an interface "Back" event flushes the corresponding operational key variables from `st.session_state` and executes an `st.rerun()` window frame cycle.*

---

## 🐞 Diagnostics & Troubleshooting

### Web Scraper Fails to Collect Target CSV
* **Root Cause:** Dynamic elements on the ArcGIS platform might take longer to load than the defined polling limit.
* **Resolution:** Increase the duration threshold on the `WebDriverWait(driver, 20)` wrapper function inside your code module. Ensure no older, orphan background browser processes remain active in your task list.

### Application Crashes with an `IndexError` on Launch
* **Root Cause:** The system cannot detect a valid `.csv` data table along the local desktop asset file paths.
* **Resolution:** Confirm that the output files exist inside the designated data storage fold or rewrite the file paths inside `app.py` to target your preferred relative repository directories.

### Unmapped Core Prefix Strings
* **Root Cause:** Transitioning across fiscal intervals sometimes introduces new departmental shorthand codes into the public data files.
* **Resolution:** Review the tracking table rows exported into `unknown_df` and append the missing short-code definitions straight to your `prefix_map` dictionary layout.

---

## 📈 Future Infrastructure Roadmap
* [ ] Implement localized caching optimization layers using `@st.cache_data` to decouple filesystem reads from frame re-renders.
* [ ] Replace standard print outputs with automated python `logging` infrastructure handling severe error diagnostics.
* [ ] Wrap extraction environments within a discrete **Dockerfile** configuration to eliminate GeckoDriver dependency drift.
