import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

def make_serializable(val):
    # Handle both numpy and plain python nan/inf
    if pd.isna(val) or val in [float('inf'), float('-inf'), np.inf, -np.inf]:
        return None
    if isinstance(val, (np.generic,)):
        return val.item()
    return val


def parse_peers_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    # Extract header names
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    # There may be a S.No. column; skip or keep as needed

    # Extract rows
    peers = []
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue  # probably header or footer
        # The Name is a link
        name_link = tds[1].find("a")
        name = name_link.get_text(strip=True) if name_link else tds[1].get_text(strip=True)
        url = name_link['href'] if name_link else None

        peer_data = {
            "sno": tds[0].get_text(strip=True),
            "name": name,
            "url": url,
            "cmp": tds[2].get_text(strip=True),
            "pe": tds[3].get_text(strip=True),
            "market_cap": tds[4].get_text(strip=True),
            "div_yld": tds[5].get_text(strip=True),
            "np_qtr": tds[6].get_text(strip=True),
            "qtr_profit_var": tds[7].get_text(strip=True),
            "sales_qtr": tds[8].get_text(strip=True),
            "qtr_sales_var": tds[9].get_text(strip=True),
            "roce": tds[10].get_text(strip=True),
        }
        peers.append(peer_data)
    return peers

def make_json_serializable(record):
    """Convert all np.nan, inf, -inf to None for JSON serialization."""
    for k, v in record.items():
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            record[k] = None
    return record


def clean_json(obj):
    if isinstance(obj, dict):
        return {str(k): clean_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json(x) for x in obj]
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif hasattr(obj, "isoformat"):  # handle Timestamp to string
        return str(obj)
    return obj