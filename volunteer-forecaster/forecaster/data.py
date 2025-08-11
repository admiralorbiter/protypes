
from __future__ import annotations
import pandas as pd
from typing import Tuple, List

REQUIRED_COLS = ["date","event_type","industry","outreach","commitments","shows"]

def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}. Required: {REQUIRED_COLS}")
    # coerce types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in ["outreach","commitments","shows"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    df["event_type"] = df["event_type"].astype(str)
    df["industry"] = df["industry"].astype(str)
    # filter impossible rows
    df = df[(df["outreach"] >= 0) & (df["commitments"] >= 0) & (df["shows"] >= 0)]
    df = df[df["commitments"] <= df["outreach"]]
    df = df[df["shows"] <= df["commitments"]]
    return df

def summarize_segments(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["event_type","industry"], as_index=False).agg(
        outreach_sum=("outreach","sum"),
        commitments_sum=("commitments","sum"),
        shows_sum=("shows","sum"),
        n_rows=("industry","count"),
        last_date=("date","max")
    )
    # posterior parameters for Beta-Binomial (uniform prior a=b=1)
    g["a_resp"] = 1 + g["commitments_sum"]
    g["b_resp"] = 1 + (g["outreach_sum"] - g["commitments_sum"]).clip(lower=0)
    g["a_show"] = 1 + g["shows_sum"]
    g["b_show"] = 1 + (g["commitments_sum"] - g["shows_sum"]).clip(lower=0)
    # posterior means
    g["mean_resp"] = g["a_resp"] / (g["a_resp"] + g["b_resp"])
    g["mean_show"] = g["a_show"] / (g["a_show"] + g["b_show"])
    g["mean_pipeline"] = g["mean_resp"] * g["mean_show"]
    return g
