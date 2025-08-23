#!/usr/bin/env python3
# Kansas City Industry Landscape Builder (Extended)
# ------------------------------------------------
# Pulls:
#   1) ABS Company Summary (abscs) — firms, employment, payroll, receipts
#   2) ABS Characteristics of Businesses (abscb) — innovation, remote work, franchise, family-owned, etc.
#   3) ABS Characteristics of Business Owners (abscbo) — sex, race, ethnicity, veteran, age, education, etc.
#   4) ABS Module: Business Characteristics (absmcb) — rotating topical content (e.g., COVID, tech)
#   5) CBP (cbp) — establishments, employment, payroll (most current annual)
#
# Geography: CBSA/MSA (default 28140 = Kansas City, MO-KS)
# Output: CSV + Excel; Excel has a "combined" sheet (abscs+cbp) and separate raw sheets for all pulls.
#
# Notes:
# - We aggregate to 2-digit NAICS (including combined 31-33, 44-45, 48-49) to avoid NAICS2017 vs NAICS2022 crosswalk.
# - For ABSCB, ABSCBO, ABSMCB we default to ownership totals (SEX/ETH/RACE/VET totals) to keep metro-level counts usable.
# - Headers are renamed to human-friendly titles before saving.
import argparse
import sys
import time
from typing import List, Dict, Any, Optional

import requests
import pandas as pd

# -----------------------------
# Config
# -----------------------------
ABS_YEAR_PATH = "2022"       # ABS dataset path (ref year 2022, published 2023)
CBP_YEAR = "2023"            # CBP latest year (annual)
DEFAULT_CBSA = "28140"       # Kansas City, MO-KS

ABS_CS_BASE  = f"https://api.census.gov/data/{ABS_YEAR_PATH}/abscs"
ABS_CB_BASE  = f"https://api.census.gov/data/{ABS_YEAR_PATH}/abscb"
ABS_CBO_BASE = f"https://api.census.gov/data/{ABS_YEAR_PATH}/abscbo"
ABS_MCB_BASE = f"https://api.census.gov/data/{ABS_YEAR_PATH}/absmcb"
CBP_BASE     = f"https://api.census.gov/data/{CBP_YEAR}/cbp"

# 2-digit NAICS sectors to query (strings). '31-33' is a combined manufacturing sector in ABS.
NAICS_2DIGIT = [
    "00", "11", "21", "22", "23", "31-33", "42", "44-45", "48-49", "51",
    "52", "53", "54", "55", "56", "61", "62", "71", "72", "81"
]

# -----------------------------
# Helpers
# -----------------------------
def _retry_get(url: str, params: Dict[str, Any], tries: int = 5, backoff: float = 0.8):
    last_exc = None
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=60)
            if r.status_code == 200:
                return r
            else:
                last_exc = RuntimeError(f"Status {r.status_code}: {r.text[:200]}")
        except Exception as e:
            last_exc = e
        time.sleep(backoff * (2 ** i))
    raise last_exc if last_exc else RuntimeError("Unknown error during GET")

def _to_numeric(df: pd.DataFrame, cols: List[str]) -> None:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

# -----------------------------
# ABS: Company Summary (abscs)
# -----------------------------
def fetch_abs_company_summary(cbsa: str, naics_codes: List[str], api_key: Optional[str]) -> pd.DataFrame:
    rows = []
    for code in naics_codes:
        params = {
            "get": ",".join([
                "GEO_ID", "NAME", "NAICS2022", "NAICS2022_LABEL",
                "FIRMPDEMP", "EMP", "PAYANN", "RCPPDEMP"
            ]),
            "for": f"metropolitan statistical area/micropolitan statistical area:{cbsa}",
            "NAICS2022": code,
            "SEX": "001", "ETH_GROUP": "001", "RACE_GROUP": "00", "VET_GROUP": "001",
        }
        if api_key:
            params["key"] = api_key
        r = _retry_get(ABS_CS_BASE, params)
        data = r.json()
        header, values = data[0], data[1:]
        for v in values:
            rows.append(dict(zip(header, v)))
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    _to_numeric(df, ["FIRMPDEMP", "EMP", "PAYANN", "RCPPDEMP"])
    df["dataset"] = f"ABS_{ABS_YEAR_PATH}_CS"
    df["year_ref"] = 2022
    df["naics_2"] = df["NAICS2022"].str.extract(r"^(\d{2}|31-33|44-45|48-49|00)$")[0]
    df = df.rename(columns={
        "NAICS2022": "NAICS",
        "NAICS2022_LABEL": "NAICS_LABEL"
    })
    # Friendly headers (company summary)
    df = df.rename(columns={
        "NAME": "Geography",
        "GEO_ID": "Geo_ID",
        "FIRMPDEMP": "Employer_Firms_ABS",
        "EMP": "Employment_ABS",
        "PAYANN": "Annual_Payroll_ABS",
        "RCPPDEMP": "Receipts_ABS",
        "NAICS": "NAICS_Code",
        "NAICS_LABEL": "Industry_Sector",
        "naics_2": "NAICS_2digit",
        "dataset": "Dataset",
        "year_ref": "Year"
    })
    return df

# -----------------------------
# ABS: Characteristics of Businesses (abscb)
# -----------------------------
def fetch_abs_business_characteristics(cbsa: str, api_key: Optional[str]) -> pd.DataFrame:
    params = {
        "get": ",".join([
            "GEO_ID", "NAME", "NAICS2022", "NAICS2022_LABEL",
            "QDESC", "QDESC_LABEL", "BUSCHAR", "BUSCHAR_LABEL",
            "FIRMPDEMP", "EMP", "PAYANN"
        ]),
        "for": f"metropolitan statistical area/micropolitan statistical area:{cbsa}",
        "SEX": "001", "ETH_GROUP": "001", "RACE_GROUP": "00", "VET_GROUP": "001",
    }
    if api_key:
        params["key"] = api_key
    r = _retry_get(ABS_CB_BASE, params)
    data = r.json()
    header, values = data[0], data[1:]
    df = pd.DataFrame([dict(zip(header, v)) for v in values])
    if df.empty:
        return df
    _to_numeric(df, ["FIRMPDEMP", "EMP", "PAYANN"])
    df["dataset"] = f"ABS_{ABS_YEAR_PATH}_CB"
    df["year_ref"] = 2022
    df["naics_2"] = df["NAICS2022"].str.extract(r"^(\d{2}|31-33|44-45|48-49|00)$")[0]
    df = df.rename(columns={
        "NAICS2022": "NAICS_Code",
        "NAICS2022_LABEL": "Industry_Sector",
        "NAME": "Geography",
        "GEO_ID": "Geo_ID",
        "QDESC": "Question_Code",
        "QDESC_LABEL": "Question",
        "BUSCHAR": "Business_Characteristic_Code",
        "BUSCHAR_LABEL": "Business_Characteristic",
        "FIRMPDEMP": "Employer_Firms_ABS",
        "EMP": "Employment_ABS",
        "PAYANN": "Annual_Payroll_ABS",
        "naics_2": "NAICS_2digit",
        "dataset": "Dataset",
        "year_ref": "Year"
    })
    return df

# -----------------------------
# ABS: Characteristics of Business Owners (abscbo)
# -----------------------------
def fetch_abs_owner_characteristics(cbsa: str, api_key: Optional[str]) -> pd.DataFrame:
    params = {
        "get": ",".join([
            "GEO_ID", "NAME", "NAICS2022", "NAICS2022_LABEL",
            "OWNER_SEX", "OWNER_ETH", "OWNER_RACE", "OWNER_VET",
            "QDESC", "QDESC_LABEL", "OWNCHAR", "OWNCHAR_LABEL",
            "OWNPDEMP"
        ]),
        "for": f"metropolitan statistical area/micropolitan statistical area:{cbsa}",
        # When using OWNER_* selectors, do not pass SEX/ETH/RACE/VET totals; the owner fields carry the breakdown
    }
    if api_key:
        params["key"] = api_key
    r = _retry_get(ABS_CBO_BASE, params)
    data = r.json()
    header, values = data[0], data[1:]
    df = pd.DataFrame([dict(zip(header, v)) for v in values])
    if df.empty:
        return df
    _to_numeric(df, ["OWNPDEMP"])
    df["dataset"] = f"ABS_{ABS_YEAR_PATH}_CBO"
    df["year_ref"] = 2022
    df["naics_2"] = df["NAICS2022"].str.extract(r"^(\d{2}|31-33|44-45|48-49|00)$")[0]
    df = df.rename(columns={
        "NAICS2022": "NAICS_Code",
        "NAICS2022_LABEL": "Industry_Sector",
        "NAME": "Geography",
        "GEO_ID": "Geo_ID",
        "QDESC": "Question_Code",
        "QDESC_LABEL": "Question",
        "OWNCHAR": "Owner_Characteristic_Code",
        "OWNCHAR_LABEL": "Owner_Characteristic",
        "OWNPDEMP": "Owner_Employer_Firms_ABS",
        "OWNER_SEX": "Owner_Sex_Code",
        "OWNER_ETH": "Owner_Ethnicity_Code",
        "OWNER_RACE": "Owner_Race_Code",
        "OWNER_VET": "Owner_Veteran_Code",
        "naics_2": "NAICS_2digit",
        "dataset": "Dataset",
        "year_ref": "Year"
    })
    return df

# -----------------------------
# ABS: Module Business Characteristics (absmcb)
# -----------------------------
def fetch_abs_module(cbsa: str, api_key: Optional[str]) -> pd.DataFrame:
    params = {
        "get": ",".join([
            "GEO_ID", "NAME", "NAICS2022", "NAICS2022_LABEL",
            "QDESC", "QDESC_LABEL", "BUSCHAR", "BUSCHAR_LABEL",
            "FIRMPDEMP", "EMP", "PAYANN"
        ]),
        "for": f"metropolitan statistical area/micropolitan statistical area:{cbsa}",
        "SEX": "001", "ETH_GROUP": "001", "RACE_GROUP": "00", "VET_GROUP": "001",
    }
    if api_key:
        params["key"] = api_key
    r = _retry_get(ABS_MCB_BASE, params)
    data = r.json()
    header, values = data[0], data[1:]
    df = pd.DataFrame([dict(zip(header, v)) for v in values])
    if df.empty:
        return df
    _to_numeric(df, ["FIRMPDEMP", "EMP", "PAYANN"])
    df["dataset"] = f"ABS_{ABS_YEAR_PATH}_MCB"
    df["year_ref"] = 2022
    df["naics_2"] = df["NAICS2022"].str.extract(r"^(\d{2}|31-33|44-45|48-49|00)$")[0]
    df = df.rename(columns={
        "NAICS2022": "NAICS_Code",
        "NAICS2022_LABEL": "Industry_Sector",
        "NAME": "Geography",
        "GEO_ID": "Geo_ID",
        "QDESC": "Question_Code",
        "QDESC_LABEL": "Question",
        "BUSCHAR": "Business_Characteristic_Code",
        "BUSCHAR_LABEL": "Business_Characteristic",
        "FIRMPDEMP": "Employer_Firms_ABS",
        "EMP": "Employment_ABS",
        "PAYANN": "Annual_Payroll_ABS",
        "naics_2": "NAICS_2digit",
        "dataset": "Dataset",
        "year_ref": "Year"
    })
    return df

# -----------------------------
# CBP (cbp)
# -----------------------------
def fetch_cbp(cbsa: str, naics_codes: List[str], api_key: Optional[str]) -> pd.DataFrame:
    rows = []
    for code in naics_codes:
        params = {
            "get": ",".join([
                "NAME", "NAICS2017", "NAICS2017_LABEL",
                "ESTAB", "EMP", "PAYQTR1", "PAYANN"
            ]),
            "for": f"metropolitan statistical area/micropolitan statistical area:{cbsa}",
            "NAICS2017": code,
            "LFO": "001",
        }
        if api_key:
            params["key"] = api_key
        r = _retry_get(CBP_BASE, params)
        data = r.json()
        header, values = data[0], data[1:]
        for v in values:
            rows.append(dict(zip(header, v)))
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    _to_numeric(df, ["ESTAB", "EMP", "PAYQTR1", "PAYANN"])
    df["dataset"] = f"CBP_{CBP_YEAR}"
    df["year_ref"] = int(CBP_YEAR)
    df["naics_2"] = df["NAICS2017"].str.extract(r"^(\d{2}|31-33|44-45|48-49|00)$")[0]
    df = df.rename(columns={
        "NAICS2017": "NAICS_Code",
        "NAICS2017_LABEL": "Industry_Sector",
        "NAME": "Geography",
        "ESTAB": "Establishments_CBP",
        "EMP": "Employment_CBP",
        "PAYQTR1": "Q1_Payroll_CBP",
        "PAYANN": "Annual_Payroll_CBP",
        "naics_2": "NAICS_2digit",
        "dataset": "Dataset",
        "year_ref": "Year"
    })
    return df

# -----------------------------
# Merge for the core "industry landscape" view (ABSCs + CBP)
# -----------------------------
def build_combined(abs_cs: pd.DataFrame, cbp: pd.DataFrame) -> pd.DataFrame:
    # Keep one row per geography x NAICS_2digit for each dataset
    cs_keep = [
        "Geography", "Geo_ID", "NAICS_Code", "Industry_Sector", "NAICS_2digit",
        "Employer_Firms_ABS", "Employment_ABS", "Annual_Payroll_ABS", "Receipts_ABS",
        "Dataset", "Year"
    ]
    cbp_keep = [
        "Geography", "NAICS_Code", "Industry_Sector", "NAICS_2digit",
        "Establishments_CBP", "Employment_CBP", "Q1_Payroll_CBP", "Annual_Payroll_CBP",
        "Dataset", "Year"
    ]
    cs_sub = abs_cs[cs_keep].drop_duplicates(subset=["Geo_ID", "NAICS_2digit"])
    cbp_sub = cbp[cbp_keep].drop_duplicates(subset=["Geography", "NAICS_2digit"])

    merged = pd.merge(
        cs_sub, cbp_sub,
        how="outer",
        on=["Geography", "NAICS_2digit", "NAICS_Code", "Industry_Sector"],
        suffixes=("_ABS", "_CBP")
    )

    # Rename dataset/year to clear labels
    merged = merged.rename(columns={
        "Dataset_ABS": "Dataset_ABS_CS",
        "Dataset_CBP": "Dataset_CBP",
        "Year_ABS": "Year_ABS_CS",
        "Year_CBP": "Year_CBP"
    })
    # If those columns don't exist due to merge logic, create explicit indicators
    merged["Dataset_ABS_CS"] = f"ABS_{ABS_YEAR_PATH}_CS"
    merged["Dataset_CBP"] = f"CBP_{CBP_YEAR}"
    merged["Year_ABS_CS"] = 2022
    merged["Year_CBP"] = int(CBP_YEAR)

    # Column order
    cols = [
        "Geography", "NAICS_2digit", "NAICS_Code", "Industry_Sector",
        "Employer_Firms_ABS", "Employment_ABS", "Annual_Payroll_ABS", "Receipts_ABS",
        "Establishments_CBP", "Employment_CBP", "Q1_Payroll_CBP", "Annual_Payroll_CBP",
        "Geo_ID", "Dataset_ABS_CS", "Year_ABS_CS", "Dataset_CBP", "Year_CBP"
    ]
    for c in cols:
        if c not in merged.columns:
            merged[c] = pd.NA
    merged = merged[cols]

    # Sort by NAICS_2digit
    def naics_sort_key(v: str):
        import pandas as _pd
        if _pd.isna(v):
            return (999, 2)
        if v in ("31-33", "44-45", "48-49"):
            try:
                return (int(v.split("-")[0]), 1)
            except Exception:
                return (999, 2)
        try:
            return (int(v), 0)
        except Exception:
            return (999, 2)

    merged = merged.sort_values(by=["NAICS_2digit"], key=lambda s: s.map(naics_sort_key))
    return merged

# -----------------------------
# Main
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Compile KC industry landscape with extended ABS insights")
    parser.add_argument("--cbsa", default=DEFAULT_CBSA, help="CBSA/MSA code (default 28140 = Kansas City, MO-KS)")
    parser.add_argument("--naics", nargs="*", default=NAICS_2DIGIT, help="2-digit NAICS list to pull")
    parser.add_argument("--api-key", default=None, help="Census API key (optional for repeated/heavier use)")
    parser.add_argument("--out-prefix", default="kc_industry_landscape", help="Output filename prefix")
    args = parser.parse_args()

    print(f"Fetching ABS Company Summary ({ABS_YEAR_PATH}) for CBSA {args.cbsa} ...")
    abs_cs = fetch_abs_company_summary(args.cbsa, args.naics, args.api_key)
    print(f"ABSCs rows: {len(abs_cs)}")

    print(f"Fetching CBP ({CBP_YEAR}) for CBSA {args.cbsa} ...")
    cbp = fetch_cbp(args.cbsa, args.naics, args.api_key)
    print(f"CBP rows: {len(cbp)}")

    print("Fetching ABS: Characteristics of Businesses ...")
    abs_cb = fetch_abs_business_characteristics(args.cbsa, args.api_key)
    print(f"ABSCB rows: {len(abs_cb)}")

    print("Fetching ABS: Characteristics of Business Owners ...")
    abs_cbo = fetch_abs_owner_characteristics(args.cbsa, args.api_key)
    print(f"ABSCBO rows: {len(abs_cbo)}")

    print("Fetching ABS: Module Business Characteristics ...")
    abs_mcb = fetch_abs_module(args.cbsa, args.api_key)
    print(f"ABSMCB rows: {len(abs_mcb)}")

    if abs_cs.empty and cbp.empty and abs_cb.empty and abs_cbo.empty and abs_mcb.empty:
        print("No data returned. Check your internet connection and parameters.", file=sys.stderr)
        sys.exit(2)

    combined = build_combined(abs_cs, cbp)

    out_xlsx = f"{args.out_prefix}.xlsx"
    
    with pd.ExcelWriter(out_xlsx) as xw:
        combined.to_excel(xw, sheet_name="combined_industry_view", index=False)
        if not abs_cs.empty:
            abs_cs.to_excel(xw, sheet_name="abs_company_summary", index=False)
        if not cbp.empty:
            cbp.to_excel(xw, sheet_name="cbp", index=False)
        if not abs_cb.empty:
            abs_cb.to_excel(xw, sheet_name="abs_business_chars", index=False)
        if not abs_cbo.empty:
            abs_cbo.to_excel(xw, sheet_name="abs_owner_chars", index=False)
        if not abs_mcb.empty:
            abs_mcb.to_excel(xw, sheet_name="abs_module_chars", index=False)

    print(f"Saved: {out_xlsx}")
    print("Excel file contains all extended ABS data in organized sheets:")
    print("  • combined_industry_view - Core industry landscape (ABSCs + CBP)")
    print("  • abs_company_summary - ABS Company Summary data")
    print("  • cbp - County Business Patterns data")
    print("  • abs_business_chars - Business characteristics (innovation, remote work, etc.)")
    print("  • abs_owner_chars - Owner demographics (sex, race, ethnicity, veteran status)")
    print("  • abs_module_chars - Specialized business characteristics (COVID, tech adoption)")

if __name__ == "__main__":
    main()
