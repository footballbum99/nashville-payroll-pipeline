

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import re
import streamlit as st
import pandas as pd
import numpy as np
import requests
import altair as alt
import csv
import glob
import os
import time

def get_shadow_root(driver, element):
    return driver.execute_script("return arguments[0].shadowRoot", element)

def run_selenium_extraction():
    download_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(download_dir, exist_ok=True)

    # Clean old files
    for f in os.listdir(download_dir):
        if f.endswith(".csv") or f.endswith(".part"):
            try:
                os.remove(os.path.join(download_dir, f))
            except:
                pass

    options = webdriver.FirefoxOptions()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "text/csv,application/csv,text/plain")
    options.set_preference("browser.download.manager.showWhenStarting", False)

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 20)

    csv_clicked = False

    try:
        driver.get("https://datanashvillegov-nashville.hub.arcgis.com/datasets/e413edb1a0854c5ab58102b001249e24_0/explore")

        print("Polling DOM for nested Shadow roots...")

        download_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-default"))
        )
        download_btn.click()

        # Try for up to ~30 seconds
        for _ in range(60):
            try:
                hub_list = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "arcgis-hub-download-list"))
                )

                for _ in range(30):
                    try:
                        list_shadow = hub_list.shadow_root
                        items = list_shadow.find_elements(By.CSS_SELECTOR, "arcgis-hub-download-list-item")

                        for item in items:
                            item_shadow = item.shadow_root
                            title_el = item_shadow.find_element(By.CSS_SELECTOR, ".download-option-card-title")

                            if "CSV" in title_el.text:
                                calcite_btn = item_shadow.find_element(By.CSS_SELECTOR, "calcite-button")
                                calcite_shadow = calcite_btn.shadow_root
                                native_button = calcite_shadow.find_element(By.CSS_SELECTOR, "button")

                                driver.execute_script("arguments[0].click();", native_button)
                                print("🎯 CSV download initiated successfully.")
                                csv_clicked = True
                                break

                        if csv_clicked:
                            break

                    except Exception:
                        time.sleep(0.5)

                if csv_clicked:
                    break

            except Exception:
                time.sleep(0.5)

        if not csv_clicked:
            raise RuntimeError("Failed to locate or click the CSV option within time limit.")

        # -------------------------
        # WAIT FOR DOWNLOAD
        # -------------------------
        print("Waiting for the 32MB file download to complete (Max 20 seconds)...")
        timeout = 300
        start_time = time.time()

        while time.time() - start_time < timeout:
            files = [f for f in os.listdir(download_dir) if not f.startswith(".")]

            # Still downloading?
            if any(f.endswith(".part") for f in files):
                time.sleep(2)
                continue

            # Completed CSV?
            csv_files = [f for f in files if f.endswith(".csv")]
            if csv_files:
                target_file = os.path.join(download_dir, csv_files[0])
                initial_size = os.path.getsize(target_file)
                time.sleep(2)

                if initial_size == os.path.getsize(target_file) and initial_size > 0:
                    print(f"🎉 Pipeline Extract Complete: {csv_files[0]} ({initial_size / (1024*1024):.2f} MB)")
                    return target_file

            time.sleep(1)

        raise TimeoutError("Download phase timed out.")

    finally:
        driver.quit()

def clean_currency(s):
    def fix_value(x):
        x = str(x).strip()
        # Remove currency symbols and commas
        x = re.sub(r"[^\d\.\-Ee]", "", x)

        if re.match(r"^-?\d*\.\d+-\d+$", x):
            x = re.sub(r"(-?\d*\.\d+)-(\d+)$", r"\1E-\2", x)

        if x in ("", "-", ".", "NaN"):
            return 0.0

        try:
            return float(x)
        except:
            return 0.0

    return s.apply(fix_value)

def process_csv():
    
    csv_path = os.path.join(os.getcwd(), "Project/data")

    file = glob.glob(os.path.join(csv_path, "*.csv"))[0]

    df = pd.read_csv(file)
    
    # 1. CLEAN PAY COLUMNS
    pay_cols = [
        "Regular Pay",
        "Overtime Pay",
        "Supplemental Pay",
        "Longevity",
        "Bonuses",
        "Payouts",
        "Other Pay",
    ]

    for col in pay_cols:
        if col in df.columns:  # Safe check to prevent KeyError
                df[col] = clean_currency(df[col])

    # 2. ALIGN BUSINESS UNIT AND DROPS
    df["Fiscal Year"] = df["Fiscal Year"].astype(np.int64)
    df["Business Unit"] = df["Home Business Unit"]
    df = df.drop(columns=["OBJECTID", ], errors="ignore")

    # 3. RECALCULATE TOTALS (Crucial Order Fix)
    df["Total Pay"] = df[pay_cols].sum(axis=1)
    df["Extra Pay"] = df["Total Pay"] - df["Regular Pay"]

    # Extract prefix candidate
    df['Prefix'] = df['Business Unit'].str.split().str[0].str.upper()

    df['Description'] = df['Business Unit'].str.split(n=1).str[1]

    prefix_map = {
        "AGE": "Agriculture & Extension",
        "BBD": "Business & Building Development",
        "BFC": "Business & Finance",
        "ARENA": "Bridgestone Arena",
        "CIR": "Circuit Court Clerk",
        "CEC": "Community Education Admin",
        "COD": "Codes Administration",
        "CHA": "Community Health Assessment",
        "CRB": "Community Review Board",
        "ADM": "County Clerk / Administration",
        "TRU": "County Trustee",
        "CCC": "Criminal Court Clerk",
        "CJP": "Criminal Justice Planning",
        "FIN": "Department of Finance",
        "LAW": "Department of Law",
        "DA": "District Attorney General",
        "EBDA": "East Bank Development Authority",
        "ELE": "Election Commission",
        "ECC": "Emergency Communications Center (911)",
        "GSD": "General Services Department",
        "FAR": "Farmers Market",
        "FIR": "Fire Department",
        "GSR": "General Services Department",
        "GSC": "General Sessions Court",
        "HEA": "Health Department",
        "HEALTH": "Health Equity",
        "HIS": "Historical Commission",
        "HRC": "Human Relations Commission",
        "HR": "Human Resources",
        "ITS": "Information Technology Services",
        "IA": "Internal Audit / Internal Affairs",
        "JIS": "Justice Integration Services",
        "JUV": "Juvenile Court",
        "JCC": "Juvenile Court Clerk",
        "MAY": "Mayor’s Office",
        "NCAC": "Youth Development",
        "MCO": "Medical Examiner / Coroner's Office",
        "ART": "Metro Arts (Arts Commission)",
        "COU": "Metro Council",
        "MCL": "Metro Council Liaison",
        "MNPS": "Metro Nashville Public Schools",
        "MAC": "Metropolitan Action Commission",
        "MUN": "Municipal Auditorium",
        "NDOT": "Nashville Department of Transportation",
        "MTA": "Nashville Metropolitan Transit Authority (WeGo)",
        "LIB": "Nashville Public Library",
        "NWS": "National Weather Service / Water Stormwater",
        "OEM": "Office of Emergency Management",
        "OFS": "Office of Family Safety",
        "OFM": "Office of Fleet Management",
        "OHS": "Office of Homeless Services",
        "PAR": "Parks and Recreation",
        "PLA": "Planning Department",
        "POL": "Police Department (MNPD)",
        "ASR": "Property Assessor",
        "PDF": "Public Defender",
        "SHE": "Sheriff's Office",
        "SOC": "Social Services",
        "SWC": "SWC Administration",

        "SPA": "Sports Facilities",
        "STC": "State Trial Courts",
        "VCIF": "Violent Crime Intervention Fund",
        "W&S": "Water and Sewer Services"
    }

    df['Branch'] = df['Prefix'].map(prefix_map)

    # --- 6. Identify unknown prefixes (but DO NOT remove them) ---
    known_prefixes = set(prefix_map.keys())
    unknown_df = df[~df['Prefix'].isin(known_prefixes)]

    df.drop(columns=["Prefix", "Home Business Unit", "Business Unit", "Extra Pay"], inplace=True)

    first = [ 'Employee Name', 'Branch', 'Description']
    df = df[first + [c for c in df.columns if c not in first]]

    col = 'Fiscal Year'
    df = df[[c for c in df.columns if c != col] + [col]]
    
    # Sort chronologically
    df = df.sort_values(by=['Employee Name', 'Fiscal Year'])

    # Fill missing values within each employee group
    columns_to_fill = ['Branch', 'Description']
    df[columns_to_fill] = df.groupby('Employee Name')[columns_to_fill].ffill().bfill()

    df.to_csv("Project/Metro_Government.csv", index=False)
    
file_path = process_csv()
