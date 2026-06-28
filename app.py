
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import csv
import glob
import re
import os 

=df = pd.read_csv(glob.glob("Project/*.csv")[0])

df_raw = df.copy()

st.set_page_config(
    page_title="Nashville Metro Salary Data",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.extremelycoolapp.com/help",
        "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "This is a simple Streamlit app to display the Nashville Metro Salary Data. The app allows users to explore salary data for employees in the Nashville Metro Government. The raw data is sourced from the Nashville Metro Government's public records (https://datanashvillegov-nashville.hub.arcgis.com/datasets/e413edb1a0854c5ab58102b001249e24_0/explore).",
    },
)

st.title("Nashville Metro Salary Data")
st.text("This is a simple Streamlit app to display the Nashville Metro Salary Data")


def clean_currency(s):
    def fix_value(x):
        x = str(x).strip()
        # Remove currency symbols and commas
        x = re.sub(r"[^\d\.\-Ee]", "", x)

        # Fix malformed scientific notation like "-3.45-13" → "-3.45E-13"
        if re.match(r"^-?\d*\.\d+-\d+$", x):
            x = re.sub(r"(-?\d*\.\d+)-(\d+)$", r"\1E-\2", x)

        if x in ("", "-", ".", "NaN"):
            return 0.0

        try:
            return float(x)
        except:
            return 0.0

    return s.apply(fix_value)

def money(x):
    return f"${x:,.2f}"

# -------------------------------------------------------
# 1. CLEAN & PREPARE DATA (DO THIS BEFORE ANY FILTERING)
# -------------------------------------------------------

pay_cols = [
    "Regular Pay",
    "Overtime Pay",
    "Supplemental Pay",
    "Longevity",
    "Bonuses",
    "Payouts",
    "Other Pay",
]

# 1. Clean data and fix types efficiently
for col in pay_cols:
    if col in df.columns:
        df[col] = clean_currency(df[col]).fillna(0.0)

df["Fiscal Year"] = df["Fiscal Year"].astype(int)
df = df.drop(columns=["OBJECTID"], errors="ignore")

# 2. Derive structural pay columns
df["Total Pay"] = df[pay_cols].sum(axis=1)
df["Extra Pay"] = df["Total Pay"] - df["Regular Pay"] - df["Overtime Pay"]

YEARS = sorted(df["Fiscal Year"].unique(), reverse=True)
default_year = YEARS[0] if YEARS else None

# 3. Sidebar/Control Panel Navigation
mode = st.radio("Data Selector", ["Single Year", "Compare Years"])

if mode == "Single Year":
    selected_year = st.pills(
        "Select Fiscal Year",
        YEARS,
        default=default_year,
        selection_mode="single",
    )
    df_year = df[df["Fiscal Year"] == selected_year].copy()
    year_label = f"FY {selected_year}"
else:
    selected_years = st.pills(
        "Years to compare",
        YEARS,
        default=YEARS,
        selection_mode="multi",
    )
    df_year = df[df["Fiscal Year"].isin(selected_years)].copy()
    if len(selected_years) == 1:
        year_label = f"FY {selected_years[0]}"
    elif selected_years:
        year_label = f"FY {min(selected_years)}–{max(selected_years)}"
    else:
        year_label = "No Years Selected"

# 4. Define Column Display Formats for Tables
currency_format = {col: "${:,.2f}" for col in pay_cols + ["Extra Pay", "Total Pay"]}

ordered_cols = [
    "Employee Name",
    "Job Class",
    "Branch",
    "Description",
    "Regular Pay",
    "Overtime Pay",
    "Supplemental Pay",
    "Longevity",
    "Bonuses",
    "Payouts",
    "Other Pay",
    "Total Pay",
    "Fiscal Year"
]

# 5. Application Tabs Setup
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Summary & Breakdown",
    "Branch Breakdown",
    "Job Type Class Breakdown",
    "Highest Paid Metro Employees",
    "Most Overtime Pay",
    "Most Extra Pay",
    "Charts",
     "Data"
])

# -----------------------------------------
# TAB 1 — Summary + Breakdown
# -----------------------------------------

with tab1:
    def big_metric(col_obj, label, value):
        col_obj.markdown(
            f"""
            <div style='text-align:center;'>
                <div style='font-size:18px; font-weight:600; color:#555;'>{label}</div>
                <div style='font-size:26px; font-weight:700; color:#2E86C1; margin-top:4px;'>
                    {value}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("Summary")
    
    if not df_year.empty:
        c1, c2, c3, c4 = st.columns(4)
        big_metric(c1, "Total Employees", f"{len(df_year):,}")
        big_metric(c2, "Total Payroll", f"${df_year['Total Pay'].sum():,.2f}")
        big_metric(c3, "Average Pay", f"${df_year['Total Pay'].mean():,.2f}")
        big_metric(c4, "Median Pay", f"${df_year['Total Pay'].median():,.2f}")

        st.markdown("---")

        c5, c6, c7, c8 = st.columns(4)
        big_metric(c5, "Regular Pay", f"${df_year['Regular Pay'].sum():,.2f}")
        big_metric(c6, "Overtime Pay", f"${df_year['Overtime Pay'].sum():,.2f}")
        big_metric(c7, "Supplemental Pay", f"${df_year['Supplemental Pay'].sum():,.2f}")
        big_metric(c8, "Longevity", f"${df_year['Longevity'].sum():,.2f}")
        
        st.markdown("---")

        c9, c10, c11 = st.columns(3)
        big_metric(c9, "Bonuses", f"${df_year['Bonuses'].sum():,.2f}")
        big_metric(c10, "Payouts", f"${df_year['Payouts'].sum():,.2f}")
        big_metric(c11, "Other Pay", f"${df_year['Other Pay'].sum():,.2f}")
    else:
        st.warning("No data available for the selected parameters.")

# -----------------------------------------
# TAB 2 — Pay by Branch
# -----------------------------------------

with tab2:
    # 1. Initialize independent session state keys for multilevel drill-down
    if "selected_branch_drill" not in st.session_state:
        st.session_state.selected_branch_drill = None
    if "selected_employee_drill" not in st.session_state:
        st.session_state.selected_employee_drill = None

    # ---- LEVEL 2: INDIVIDUAL EMPLOYEE DETAIL VIEW PAGE ----
    if st.session_state.selected_branch_drill and st.session_state.selected_employee_drill:
        emp_name = st.session_state.selected_employee_drill
        
        if st.button("⬅️ Back to Employee Roster", key="btn_back_to_roster"):
            st.session_state.selected_employee_drill = None
            st.rerun()

        st.markdown("---")

        # Filter active dataset strictly to this specific Employee Name
        df_emp_details = df_year[df_year["Employee Name"] == emp_name].copy()

        for col in currency_format:
            df_emp_details[col] = df_emp_details[col].apply(lambda x: f"${x:,.2f}")

        st.subheader(f"Historical Records for {emp_name}") 
        st.caption("💡 Select Compare Years, to view their pay history.")
        st.dataframe(
            df_emp_details.drop(columns=["Branch", "Extra Pay"]).reset_index(drop=True),
        )

    # ---- LEVEL 1: BRANCH DETAIL VIEW PAGE (EMPLOYEE ROSTER) ----
    elif st.session_state.selected_branch_drill:
        branch_name = st.session_state.selected_branch_drill

        # Back button
        if st.button("⬅️ Back to Branch Summary", key="btn_back_branch"):
            st.session_state.selected_branch_drill = None
            st.rerun()

        st.markdown("---")

        # Filter active dataset strictly to this specific Branch
        df_branch_details = df_year[df_year["Branch"] == branch_name].copy()

        # -------------------------------
        # 1. Job Class Filter
        # -------------------------------
        unique_jobs = sorted(df_branch_details["Job Class"].dropna().unique())
        job_options = ["All Job Classes"] + unique_jobs

        selected_jobs = st.selectbox(
            "Select Job Class to Filter",
            options=job_options,
            index=0
        )

        # Apply job filter
        df_filtered_job = df_branch_details.copy()
        if selected_jobs != "All Job Classes":
            df_filtered_job = df_filtered_job[df_filtered_job["Job Class"] == selected_jobs]


        st.subheader(f"Employee Roster for {branch_name}")

        # Dynamic high-level performance cards for the branch
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Active Staff", f"{len(df_filtered_job):,}")
        m2.metric("Average Employee Pay", f"${df_filtered_job['Total Pay'].mean():,.2f}")
        m3.metric("Total Spend", f"${df_filtered_job['Total Pay'].sum():,.2f}")
        m4.metric("OT Spend", f"${df_filtered_job['Overtime Pay'].sum():,.2f}")
        m5.metric("Extra Pay Spend", f"${df_filtered_job['Extra Pay'].sum():,.2f}")

        st.markdown("---")

        # -------------------------------
        # 2. Employee Roster Table
        # -------------------------------
        st.caption("💡 Click on the box to the left of the table to drill down into a single employee.")
        
        for col in currency_format:
            df_filtered_job[col] = df_filtered_job[col].apply(lambda x: f"${x:,.2f}")

        # Drop columns not needed in roster view
        df_display = df_filtered_job.drop(
            columns=["Branch", "Extra Pay", "Fiscal Year"],
            errors="ignore"
        ).reset_index(drop=True)

        event_emp = st.dataframe(
            df_display,
            on_select="rerun",
            selection_mode="single-row",
        )
            
        # Monitor employee row selection clicks
        selected_emp_rows = event_emp.get("selection", {}).get("rows", [])
        if selected_emp_rows:
            emp_row_idx = selected_emp_rows[0]
            
            # 1. Properly drop columns and reset the index to match the UI row sequence
            df_branch_reset = df_branch_details.drop(columns=["Branch", "Extra Pay", "Fiscal Year"]).reset_index(drop=True)
            
            # 2. Extract the correct employee name using the visual row index
            chosen_emp = df_branch_reset.iloc[emp_row_idx]["Employee Name"]
            
            # 3. Commit to session state and update UI
            st.session_state.selected_employee_drill = chosen_emp
            st.rerun()

    # ---- DEFAULT: MAIN BRANCH SUMMARY VIEW ----
    else:
        st.subheader(f"{year_label} Pay by Branch")
        st.caption("💡 Click on the box to the left of the table to drill down.")
        st.markdown("---")

      # Process clean numeric aggregates
        top_units = (
            df_year.groupby("Branch")["Total Pay"]
            .agg(emp_count="count", total_payroll="sum", average_pay="mean", median_pay="median")
            .sort_values("total_payroll", ascending=False)
            .reset_index()
        )

        # 1. Base dictionary configuration with your text and headcount fields
        config_dict = {
            "Branch": st.column_config.TextColumn("Branch"),
            "emp_count": st.column_config.NumberColumn("Headcount", format="%d")
        }

        # 2. Target financial metrics and explicitly assign them a clean dollar formatting ruleset
        currency_format = ["total_payroll", "average_pay", "median_pay"]

        for col in currency_format:
            top_units[col] = top_units[col].apply(lambda x: f"${x:,.2f}")

        currency_format1 = ["emp_count"]

        for col in currency_format1:
            top_units[col] = top_units[col].apply(lambda x: f"{x:,.2f}")

        # 3. Render the interactive selection table
        event_branch = st.dataframe(
            top_units,
            on_select="rerun",
            selection_mode="single-row",
            column_config=config_dict,
            use_container_width=True,
            hide_index=True
        )


        # Monitor branch row selection clicks
        selected_branch_rows = event_branch.get("selection", {}).get("rows", [])
        if selected_branch_rows:
            row_idx = selected_branch_rows[0]
            chosen_branch = top_units.iloc[row_idx]["Branch"]
            
            st.session_state.selected_branch_drill = chosen_branch
            st.rerun()

# -----------------------------------------
# TAB 3 — Pay by Job Type/Class
# -----------------------------------------

with tab3:
    # 1. Initialize session state key if it doesn't exist
    if "selected_job_class" not in st.session_state:
        st.session_state.selected_job_class = None

    # ---- DRILL DOWN: DETAIL VIEW PAGE ----
    if st.session_state.selected_job_class:
        job_cls = st.session_state.selected_job_class
        
        if st.button("⬅️ Back to Job Class Summary"):
            st.session_state.selected_job_class = None
            st.rerun()

        st.title(f"Detailed Analysis: {job_cls}")
        st.markdown("---")

        # Filter active dataset strictly to this specific Job Class
        df_class = df_year[df_year["Job Class"] == job_cls].copy()

        # Dynamic high-level performance cards
        m1, m2, m3, m4 , m5 = st.columns(5)
        m1.metric("Total Active Staff", f"{len(df_class):,}")
        m2.metric("Average Class Pay", f"${df_class['Total Pay'].mean():,.2f}")
        m3.metric("Total Spend", f"${df_class['Total Pay'].sum():,.2f}")
        m4.metric("OT Spend", f"${df_class['Overtime Pay'].sum():,.2f}")
        m5.metric("Extra Pay Spend", f"${df_class['Extra Pay'].sum():,.2f}")

        st.dataframe(
            df_class[ordered_cols].reset_index(drop=True),
             column_config={col: st.column_config.NumberColumn(format="$%,.2f") for col in currency_format}
        )

    # ---- DEFAULT: MAIN SUMMARY VIEW ----
    else:
        st.subheader(f"{year_label} Pay by Job Class")
        st.caption("💡 Click on the box to the left of the table to drill down.")
        st.markdown("---")
        
        # Branch drop-down filter
        c_branch, = st.columns(1)
        with c_branch:
            unique_branches = sorted(df_year["Branch"].dropna().unique())
            branch_options = ["All Branches"] + unique_branches
            
            selected_branch = st.selectbox(
                "Select Branch to Filter",
                options=branch_options,
                index=0
            )

        # Apply branch constraint to base dataset
        df_filtered_branch = df_year.copy()
        if selected_branch != "All Branches":
            df_filtered_branch = df_filtered_branch[
                df_filtered_branch["Branch"] == selected_branch
            ]

        # Process clean numeric aggregates (No disruptive manual string conversions)
        job_class_summary = (
            df_filtered_branch.groupby("Job Class")["Total Pay"]
            .agg(emp_count="count", total_payroll="sum", average_pay="mean")
            .sort_values("total_payroll", ascending=False)
            .reset_index()
        )
        
             # Display selection table utilizing native column configurations
        event = st.dataframe(
            job_class_summary,
            on_select="rerun",
            selection_mode="single-row", 
            column_config={
            "Job Class": st.column_config.TextColumn("Job Class"),
            "emp_count": st.column_config.NumberColumn("Employee Count", format="%,d"),    
            "total_payroll": st.column_config.NumberColumn("Total Payroll", format="$%,.2f"), 
            "average_pay": st.column_config.NumberColumn("Average Pay", format="$%,.2f"),   
        }

    )
        
        # Monitor row selection clicks
        selected_rows = event.get("selection", {}).get("rows", [])
        if selected_rows:
            row_index = selected_rows[0]
            chosen_class = job_class_summary.iloc[row_index]["Job Class"]
            
            # Update application state and reload page into Detail View
            st.session_state.selected_job_class = chosen_class
            st.rerun()

# -----------------------------------------
# TAB 4 — Top Earners
# -----------------------------------------

with tab4:  
    st.markdown(f"### Metro employees earning over $120K Total Pay for {year_label}")
    st.markdown("---")

    # 1. Added .copy() to fix warning risks
    top20 = df_filtered_branch[df_filtered_branch["Total Pay"] >= 120000].sort_values("Total Pay", ascending=False).copy()

    ordered_cols1 = [
        "Employee Name", "Job Class", "Branch", "Description",
        "Regular Pay", "Overtime Pay", "Supplemental Pay", "Longevity",
        "Bonuses", "Payouts", "Other Pay", "Extra Pay", "Total Pay", "Fiscal Year"
    ]

    # Formatting string conversion safely
    for col in pay_cols + ["Extra Pay", "Total Pay"]:
        if col in top20.columns:
            top20[col] = top20[col].apply(lambda x: f"${x:,.2f}")

    # --- TABLE ---
    top20 = top20[ordered_cols1]
    top20 = top20.reset_index(drop=True)

    st.dataframe(top20, use_container_width=True)

    # --- CHART DATA ---
    # 2. Fixed Data Scope Mismatch: Changed df_year to df_filtered_branch
    chart_df = df_filtered_branch.copy()
    chart_df["Total Pay"] = chart_df["Total Pay"].astype(float)

    st.markdown("---")

    # 3. Aggregated Y-axis values and added high-quality currency tooltips
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("Branch:N", sort="-y", title="Branch"),
            y=alt.Y("sum(Total Pay):Q", title="Total Pay Sum ($)"),
            tooltip=["Branch", alt.Tooltip("sum(Total Pay):Q", format="$,.2f")]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)

# -----------------------------------------
# TAB 5 — Most Overtime Pay
# -----------------------------------------

with tab5:
    st.markdown(f"### Employees earning over $30K Overtime Pay for {year_label}")
    st.markdown("---")

    # 1. Added .copy() to prevent SettingWithCopyWarning
    top_ot = df_year[df_year["Overtime Pay"] >= 30000].sort_values("Overtime Pay", ascending=False).copy()

    # 2. Fixed KeyError: Ensure "Overtime Pay" is in the formatting list instead of "Extra Pay"
    for col in pay_cols + ["Overtime Pay", "Total Pay"]:
        if col in top_ot.columns:
            # 1. Clean up string characters if any exist, then convert to numeric floats
            top_ot[col] = pd.to_numeric(
                top_ot[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False), 
                errors='coerce'
            ).fillna(0)
            
            # 2. Safely apply currency formatting now that every value is guaranteed to be a float
            top_ot[col] = top_ot[col].apply(lambda x: f"${x:,.2f}")

    top_ot = top_ot[ordered_cols]
    top_ot = top_ot.reset_index(drop=True)

    st.dataframe(top_ot, use_container_width=True)

    # --- CHART DATA ---
    chart_df = df_year.copy()
    chart_df["Overtime Pay"] = chart_df["Overtime Pay"].astype(float)

    st.markdown("---")

    # 3. Added sum() aggregation and professional currency tooltip formatting
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("Branch:N", sort="-y", title="Branch"),
            y=alt.Y("sum(Overtime Pay):Q", title="Total Overtime Pay ($)"),
            tooltip=["Branch", alt.Tooltip("sum(Overtime Pay):Q", format="$,.2f")]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)


# -----------------------------------------
# TAB 6 — Most Extra Pay
# -----------------------------------------
with tab6:
    st.markdown(f"### Employees earning over $30K in Extra Pay for {year_label}")
    st.caption("Extra Pay = Supplemental Pay + Longevity + Bonuses + Payouts + Other Pay")  
    st.markdown("---")

    # Use copy() to prevent modifying the original DataFrame accidentally
    top_extra = df_year[df_year["Extra Pay"] >= 30000].sort_values("Extra Pay", ascending=False).copy()

    for col in pay_cols + ["Extra Pay", "Total Pay"]:
        top_extra[col] = top_extra[col].apply(lambda x: f"${x:,.2f}")

    top_extra = top_extra[ordered_cols]
    top_extra = top_extra.reset_index(drop=True)

    st.dataframe(top_extra, use_container_width=True)

    st.markdown("---")

    # --- CHART DATA ---
    # Explicitly copy and safely convert column to float
    chart_df = df_year.copy()
    chart_df["Extra Pay"] = chart_df["Extra Pay"].astype(float)

    # Added sum() aggregation to accurately stack or group data by Branch
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("Branch:N", sort="-y", title="Branch"),
            y=alt.Y("sum(Extra Pay):Q", title="Total Extra Pay ($)"),
            tooltip=["Branch", alt.Tooltip("sum(Extra Pay):Q", format="$,.2f")]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)


with tab7:
    st.subheader("Charts")

    # Calculate key metrics safely using numeric values
    total_payroll = df_year["Total Pay"].sum()
    total_employees = len(df_year)
    avg_overtime = df_year["Overtime Pay"].mean()

    # Display in Streamlit columns
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Department Payroll", value=f"${total_payroll:,.0f}")
    col2.metric(label="Headcount", value=f"{total_employees:,}")
    col3.metric(label="Average Overtime Per Employee", value=f"${avg_overtime:,.2f}")

    # --- PRE-FLIGHT CHECK: Ensure fields are numeric before running analytics ---
    numeric_cols = ["Regular Pay", "Extra Pay", "Overtime Pay", "Total Pay"]
    for col in numeric_cols:
        if col in df_filtered_branch.columns:
            df_year[col] = pd.to_numeric(
                df_year[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False),
                errors='coerce'
            ).fillna(0)
        if col in df_year.columns:
            df_year[col] = pd.to_numeric(
                df_year[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False),
                errors='coerce'
            ).fillna(0)

    # 3. --- AGGREGATIONS ---
    branch_summary = df_year.groupby("Branch")[["Regular Pay", "Extra Pay", "Overtime Pay"]].sum().reset_index()
    branch_summary["OT Percentage"] = (branch_summary["Overtime Pay"] / (branch_summary["Regular Pay"] + branch_summary["Overtime Pay"])) * 100
    branch_summary["Extra Percentage"] = (branch_summary["Extra Pay"] / (branch_summary["Regular Pay"] + branch_summary["Extra Pay"])) * 100

    # --- SCATTER PLOT ---
    chart_scatter = (
        alt.Chart(df_year)
        .mark_circle(size=60)
        .encode(
            x=alt.X("Regular Pay:Q", title="Base Regular Pay ($)"),
            y=alt.Y("Extra Pay:Q", title="Extra / Overtime Pay ($)"),
            color="Branch:N",
            tooltip=["Employee Name", "Job Class", "Regular Pay", "Extra Pay"]
        )
        .properties(height=400, title="Base Salary vs. Supplemental Earnings")
    )
    st.altair_chart(chart_scatter, use_container_width=True)

    # --- BAR CHART ---
    top_15_ratio_branches = branch_summary.sort_values("OT Percentage", ascending=False).head(15)
    chart_ratio = (
        alt.Chart(top_15_ratio_branches)
        .mark_bar()
        .encode(
            x=alt.X("Branch:N", sort="-y", title="Branch"),
            y=alt.Y("OT Percentage:Q", title="% of Payroll Spent on Overtime"),
            tooltip=["Branch", alt.Tooltip("OT Percentage:Q", format=".1f")]
        )
        .properties(height=400, title="Top 15 Branches Dependent on Overtime")
    )
    st.altair_chart(chart_ratio, use_container_width=True)

       # --- BAR CHART ---
    top_15_ratio_branches = branch_summary.sort_values("Extra Percentage", ascending=False).head(15)
    chart_ratio = (
        alt.Chart(top_15_ratio_branches)
        .mark_bar()
        .encode(
            x=alt.X("Branch:N", sort="-y", title="Branch"),
            y=alt.Y("Extra Percentage:Q", title="% of Payroll Spent on Extra Pay"),
            tooltip=["Branch", alt.Tooltip("Extra Percentage:Q", format=".1f")]
        )
        .properties(height=400, title="Top 15 Branches Dependent on Extra Pay")
    )
    st.altair_chart(chart_ratio, use_container_width=True)


