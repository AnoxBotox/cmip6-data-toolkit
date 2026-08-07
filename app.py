import os
import re
import json
from datetime import date, datetime
from urllib.parse import urlparse
from collections import defaultdict

import requests
import streamlit as st

try:
    import numpy as np
    import xarray as xr
    XARRAY_AVAILABLE = True
except Exception:
    XARRAY_AVAILABLE = False


# ============================================================
# CMIP6 DATA TOOLKIT
# ============================================================

st.set_page_config(
    page_title="CMIP6 Data Toolkit | Developed by Avishek Acharya",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS Styling & Professional Theme
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hero Header */
    .hero-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }

    .hero-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    }

    .developer-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 14px;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 10px 0;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        margin: 0;
        max-width: 900px;
        line-height: 1.5;
    }

    /* Metric Styling */
    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }

    /* Primary Action Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39) !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.55) !important;
    }

    /* Footer styling */
    .footer-container {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
        margin-top: 3.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        color: #64748b;
        font-size: 0.92rem;
    }

    .footer-highlight {
        color: #38bdf8;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

APP_NAME = "🌍 CMIP6 Data Toolkit"
PROJECT = "CMIP6"
DEVELOPER = "Avishek Acharya"
INSTITUTION = "Institute of Engineering, Purwanchal Campus, Dharan, Nepal"

DOWNLOAD_DIR = r"D:\cmip6_raw\CMIP6_Data"
SUBSET_DIR = os.path.join(DOWNLOAD_DIR, "subset")

ESGF_ENDPOINTS = [
    "https://esgf-data.dkrz.de/esg-search/search",
    "https://esgf.ceda.ac.uk/esg-search/search",
    "https://esgf-node.llnl.gov/esg-search/search",
]


# ============================================================
# MODEL LIST (curated CMIP6 source_id values)
# ============================================================

CMIP6_MODELS = [
    "ACCESS-CM2",
    "ACCESS-ESM1-5",
    "AWI-CM-1-1-MR",
    "AWI-ESM-1-1-LR",
    "BCC-CSM2-MR",
    "BCC-ESM1",
    "CAMS-CSM1-0",
    "CanESM5",
    "CanESM5-CanOE",
    "CESM2",
    "CESM2-FV2",
    "CESM2-WACCM",
    "CESM2-WACCM-FV2",
    "CIESM",
    "CMCC-CM2-HR4",
    "CMCC-CM2-SR5",
    "CMCC-ESM2",
    "CNRM-CM6-1",
    "CNRM-CM6-1-HR",
    "CNRM-ESM2-1",
    "E3SM-1-0",
    "E3SM-1-1",
    "E3SM-1-1-ECA",
    "EC-Earth3",
    "EC-Earth3-AerChem",
    "EC-Earth3-CC",
    "EC-Earth3-Veg",
    "EC-Earth3-Veg-LR",
    "FGOALS-f3-L",
    "FGOALS-g3",
    "FIO-ESM-2-0",
    "GFDL-ESM4",
    "GISS-E2-1-G",
    "GISS-E2-1-H",
    "HadGEM3-GC31-LL",
    "HadGEM3-GC31-MM",
    "IITM-ESM",
    "INM-CM4-8",
    "INM-CM5-0",
    "IPSL-CM5A2-INCA",
    "IPSL-CM6A-LR",
    "KACE-1-0-G",
    "KIOST-ESM",
    "MCM-UA-1-0",
    "MIROC6",
    "MIROC-ES2H",
    "MIROC-ES2L",
    "MPI-ESM-1-2-HAM",
    "MPI-ESM1-2-HR",
    "MPI-ESM1-2-LR",
    "MRI-ESM2-0",
    "NESM3",
    "NorCPM1",
    "NorESM2-LM",
    "NorESM2-MM",
    "SAM0-UNICON",
    "TaiESM1",
    "UKESM1-0-LL",
]


# ============================================================
# VARIABLE LIST (curated, no facet dumping)
# ============================================================

VARIABLES = {
    "pr": "Precipitation",
    "tas": "Near-surface air temperature",
    "tasmax": "Daily maximum near-surface air temperature",
    "tasmin": "Daily minimum near-surface air temperature",
    "hurs": "Near-surface relative humidity",
    "huss": "Near-surface specific humidity",
    "sfcWind": "Near-surface wind speed",
    "uas": "Eastward near-surface wind",
    "vas": "Northward near-surface wind",
    "ps": "Surface air pressure",
    "psl": "Sea level pressure",
    "hfls": "Surface upward latent heat flux",
    "hfss": "Surface upward sensible heat flux",
    "rsds": "Surface downwelling shortwave radiation",
    "rlds": "Surface downwelling longwave radiation",
    "rsus": "Surface upwelling shortwave radiation",
    "rlus": "Surface upwelling longwave radiation",
    "clt": "Total cloud cover percentage",
    "evspsbl": "Evaporation including sublimation and transpiration",
    "mrro": "Total runoff",
    "snw": "Surface snow amount",
    "snd": "Snow depth",
    "sftlf": "Percentage of grid cell occupied by land",
    "siconc": "Sea-ice area percentage",
    "sithick": "Sea ice thickness",
    "tos": "Sea surface temperature",
}

# Variables that are defined on pressure levels (rather than surface only).
# Used only to decide whether to show the "Level" hint as relevant.
PRESSURE_LEVEL_VARIABLES = {
    "zg",
    "ta",
    "ua",
    "va",
    "hus",
    "wap",
}


EXPERIMENTS = {
    "historical": "Historical",
    "ssp119": "SSP1-1.9",
    "ssp126": "SSP1-2.6",
    "ssp434": "SSP4-3.4",
    "ssp534-over": "SSP5-3.4OS",
    "ssp245": "SSP2-4.5",
    "ssp460": "SSP4-6.0",
    "ssp370": "SSP3-7.0",
    "ssp585": "SSP5-8.5",
}


FREQUENCIES = {
    "day": "Daily",
    "mon": "Monthly",
    "fx": "Fixed (no temporal resolution)",
}


PRESSURE_LEVEL_OPTIONS = [
    "1 hPa", "5 hPa", "10 hPa", "20 hPa", "30 hPa", "50 hPa",
    "70 hPa", "100 hPa", "150 hPa", "200 hPa", "250 hPa",
    "300 hPa", "400 hPa", "500 hPa", "600 hPa", "700 hPa",
    "850 hPa", "925 hPa", "1000 hPa",
]

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

MONTH_NUMBER = {name: i + 1 for i, name in enumerate(MONTH_NAMES)}


HIST_YEAR_GROUPS = ["1850-1899", "1900-1949", "1950-1999", "2000-2014"]
SCEN_YEAR_GROUPS = ["2015-2049", "2050-2099", "2100-2100"]

HIST_MIN_YEAR, HIST_MAX_YEAR = 1850, 2014
SCEN_MIN_YEAR, SCEN_MAX_YEAR = 2015, 2100


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "search_results": [],
    "file_results_raw": [],
    "last_file_search": None,
    "selected_month_list": list(MONTH_NAMES),
    "downloaded_records": [],
    "subset_records": [],
}

for _key, _value in DEFAULT_STATE.items():
    if _key not in st.session_state:
        st.session_state[_key] = list(_value) if isinstance(_value, list) else _value


# ============================================================
# GENERIC HELPERS
# ============================================================

def safe_filename(value):
    value = str(value)
    value = re.sub(r'[<>:"/\\|?*]', "_", value)
    return value


def field(record, name, default=""):
    """ESGF's Solr JSON response returns most facet fields (source_id,
    experiment_id, variable_id, member_id, grid_label, frequency,
    table_id, datetime_start, datetime_stop, ...) as single-element lists
    rather than plain strings, e.g. {"member_id": ["r1i1p1f1"]}. Reading
    these with plain dict.get() hands back an unhashable list, which
    breaks set()/sorting/dict-key use downstream. This normalizes any such
    field to a plain scalar value."""

    value = record.get(name, default)

    if isinstance(value, list):
        return value[0] if value else default

    return value


def frequency_label(code):
    return FREQUENCIES.get(code, code)


def variable_label(code):
    return VARIABLES.get(code, code)


def experiment_label(code):
    return EXPERIMENTS.get(code, code)


def natural_member_sort_key(member_id):
    match = re.match(r"r(\d+)i(\d+)p(\d+)f(\d+)", str(member_id))
    if match:
        return tuple(int(x) for x in match.groups())
    return (999999, 0, 0, 0)


def expand_year_groups(groups):
    years = set()
    for group in groups:
        if "-" in group:
            start_str, end_str = group.split("-")
            years.update(range(int(start_str), int(end_str) + 1))
        else:
            years.add(int(group))
    return years


def consecutive_ranges(years):
    """Turn a set of years into a sorted list of (start_year, end_year)
    tuples covering consecutive runs, so that e.g. {2015,2016,2020}
    becomes [(2015,2016), (2020,2020)]."""

    if not years:
        return []

    sorted_years = sorted(years)
    ranges = []
    run_start = sorted_years[0]
    run_end = sorted_years[0]

    for year in sorted_years[1:]:
        if year == run_end + 1:
            run_end = year
        else:
            ranges.append((run_start, run_end))
            run_start = year
            run_end = year

    ranges.append((run_start, run_end))
    return ranges


# ============================================================
# ESGF DATE PARSING
# ============================================================

def parse_esgf_datetime(value):
    if not value:
        return None

    text = str(value).strip()

    if text.endswith("Z"):
        text = text[:-1]

    text = text.replace("T", " ")

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y-%m",
        "%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass

    match = re.search(r"(\d{4})-?(\d{2})-?(\d{2})", text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass

    match = re.search(r"(\d{4})", text)
    if match:
        try:
            return date(int(match.group(1)), 1, 1)
        except ValueError:
            pass

    return None


def parse_filename_period(filename):
    """Fallback: derive (start_date, end_date) from a CMIP6 filename such as
    tasmax_day_INM-CM5-0_historical_r1i1p1f1_gr1_19500101-19991231.nc"""

    dates = re.findall(r"(\d{6,8})", filename)

    if len(dates) < 2:
        return None, None

    def to_date(token, is_end):
        token = token.strip()
        if len(token) == 8:
            try:
                return datetime.strptime(token, "%Y%m%d").date()
            except ValueError:
                return None
        if len(token) == 6:
            year = int(token[0:4])
            month = int(token[4:6])
            if is_end:
                if month == 12:
                    return date(year, 12, 31)
                next_month = date(year, month + 1, 1)
                return date(year, next_month.month - 1, 28) if month != 12 else date(year, 12, 31)
            return date(year, month, 1)
        return None

    start = to_date(dates[-2], is_end=False)
    end = to_date(dates[-1], is_end=True)
    return start, end


def get_file_period(record):
    """Return (start_date, end_date) for a File record, using the ESGF
    datetime_start / datetime_stop facets first and falling back to the
    filename encoding when those facets are missing or unparsable."""

    start = parse_esgf_datetime(field(record, "datetime_start", None))
    end = parse_esgf_datetime(field(record, "datetime_stop", None))

    if start is not None and end is not None:
        return start, end

    filename = extract_filename(record)
    fallback_start, fallback_end = parse_filename_period(filename)

    return (start or fallback_start), (end or fallback_end)


# ============================================================
# FILE / URL HELPERS
# ============================================================

def extract_filename(record):
    title = field(record, "title", None)

    if title:
        return os.path.basename(str(title))

    for item in get_url_list(record):
        url = item.split("|")[0]
        name = os.path.basename(urlparse(url).path)
        if name:
            return name

    return ""


def get_url_list(record):
    urls = record.get("url", [])

    if isinstance(urls, str):
        urls = [urls]

    return [x for x in urls if isinstance(x, str)]


def get_http_url(record):
    for item in get_url_list(record):
        lower = item.lower()
        if "httpserver" in lower or "application/netcdf" in lower or "application/x-netcdf" in lower:
            return item.split("|")[0]

    # Some nodes only tag the mime type as generic "http"
    for item in get_url_list(record):
        parts = item.split("|")
        if len(parts) >= 2 and "http" in parts[1].lower():
            return parts[0]

    return None


def get_opendap_url(record):
    for item in get_url_list(record):
        lower = item.lower()
        if "opendap" in lower:
            url = item.split("|")[0]
            if url.endswith(".html"):
                url = url[: -len(".html")]
            return url

    return None


# ============================================================
# ESGF SEARCH
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def esgf_search(params):
    """Query ESGF search nodes for a given params dict."""

    last_error = None
    last_empty_response = None

    for endpoint in ESGF_ENDPOINTS:
        try:
            response = requests.get(endpoint, params=params, timeout=90)

            if response.status_code != 200:
                last_error = f"{endpoint}: HTTP {response.status_code}"
                continue

            data = response.json()
            docs = data.get("response", {}).get("docs", [])

            if docs:
                return data

            last_empty_response = data

        except Exception as exc:
            last_error = f"{endpoint}: {type(exc).__name__}: {exc}"

    if last_empty_response is not None:
        return last_empty_response

    raise RuntimeError(last_error or "All ESGF nodes failed.")


def esgf_search_with_fallback(base_params):
    """Try a federated (distrib=true) search first. If every endpoint
    comes back empty, retry once more with distrib=false."""

    data = esgf_search(dict(base_params, distrib="true"))
    docs = data.get("response", {}).get("docs", [])

    if docs:
        return docs

    data = esgf_search(dict(base_params, distrib="false"))
    return data.get("response", {}).get("docs", [])


@st.cache_data(ttl=900, show_spinner=False)
def search_datasets(models, experiments, variables, frequency):
    params = {
        "project": PROJECT,
        "type": "Dataset",
        "latest": "true",
        "replica": "false",
        "frequency": frequency,
        "limit": 1000,
        "format": "application/solr+json",
    }

    if models:
        params["source_id"] = ",".join(models)

    if experiments:
        params["experiment_id"] = ",".join(experiments)

    if variables:
        params["variable_id"] = ",".join(variables)

    return esgf_search_with_fallback(params)


@st.cache_data(ttl=900, show_spinner=False)
def search_files(model, experiment, variable, frequency):
    params = {
        "project": PROJECT,
        "type": "File",
        "latest": "true",
        "replica": "false",
        "source_id": model,
        "experiment_id": experiment,
        "variable_id": variable,
        "frequency": frequency,
        "limit": 3000,
        "format": "application/solr+json",
    }

    return esgf_search_with_fallback(params)


@st.cache_data(ttl=900, show_spinner=False)
def check_available_frequencies(model, experiment, variable):
    """Diagnostic helper: find out which frequencies exist for combo."""

    params = {
        "project": PROJECT,
        "type": "Dataset",
        "latest": "true",
        "replica": "false",
        "source_id": model,
        "experiment_id": experiment,
        "variable_id": variable,
        "limit": 50,
        "format": "application/solr+json",
    }

    docs = esgf_search_with_fallback(params)

    return sorted(set(field(d, "frequency") for d in docs if field(d, "frequency")))


# ============================================================
# FILE FILTERING / MINIMAL COVERAGE LOGIC
# ============================================================

def file_overlaps_period(file_start, file_end, period_start, period_end):
    if file_start is None or file_end is None:
        return False

    return file_start <= period_end and file_end >= period_start


def dedupe_records(records):
    """Remove duplicate copies of the same physical file."""

    seen = {}

    for record in records:
        start, end = get_file_period(record)
        key = (
            field(record, "member_id"),
            field(record, "grid_label"),
            start,
            end,
        )
        if key not in seen:
            seen[key] = record

    return list(seen.values())


def files_matching_periods(records, year_ranges):
    """Return records overlapping requested year ranges."""

    if not year_ranges:
        return []

    matched = []

    for record in records:
        file_start, file_end = get_file_period(record)

        for start_year, end_year in year_ranges:
            period_start = date(start_year, 1, 1)
            period_end = date(end_year, 12, 31)

            if file_overlaps_period(file_start, file_end, period_start, period_end):
                matched.append(record)
                break

    return dedupe_records(matched)


# ============================================================
# DOWNLOAD
# ============================================================

def download_file(record, destination):
    url = get_http_url(record)

    if not url:
        opendap_url = get_opendap_url(record)
        if opendap_url:
            return False, (
                "No direct HTTP NetCDF URL found. An OpenDAP URL is "
                "available instead: " + opendap_url
            )
        return False, "No HTTP or OpenDAP URL found for this file."

    filename = extract_filename(record) or "cmip6_file.nc"
    filename = safe_filename(filename)

    os.makedirs(destination, exist_ok=True)
    output_path = os.path.join(destination, filename)

    if os.path.exists(output_path):
        return True, output_path

    try:
        with requests.get(url, stream=True, timeout=180) as response:
            response.raise_for_status()

            with open(output_path, "wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)

        return True, output_path

    except Exception as exc:
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass
        return False, str(exc)


# ============================================================
# POST-DOWNLOAD SPATIAL / TEMPORAL SUBSETTING
# ============================================================

def find_coord_name(dataset, candidates):
    lower_map = {name.lower(): name for name in dataset.coords}

    for candidate in candidates:
        if candidate in lower_map:
            return lower_map[candidate]

    return None


def apply_subset_to_dataset(
    dataset,
    apply_spatial,
    north,
    south,
    west,
    east,
    start_date,
    end_date,
    month_numbers,
):
    """Apply geographic box, date range and month filter to an xarray Dataset."""

    lat_name = find_coord_name(dataset, ["lat", "latitude"])
    lon_name = find_coord_name(dataset, ["lon", "longitude"])
    time_name = find_coord_name(dataset, ["time"])

    if apply_spatial and lat_name and lon_name:
        west_sel, east_sel = west, east

        lon_values = dataset[lon_name].values
        lon_is_0_360 = lon_values.min() >= 0 and lon_values.max() > 180

        if lon_is_0_360:
            west_sel = west_sel % 360
            east_sel = east_sel % 360

        lat_values = dataset[lat_name].values
        lat_ascending = lat_values[0] <= lat_values[-1]

        if lat_ascending:
            lat_slice = slice(south, north)
        else:
            lat_slice = slice(north, south)

        if west_sel <= east_sel:
            lon_slice = slice(west_sel, east_sel)
            dataset = dataset.sel(**{lat_name: lat_slice, lon_name: lon_slice})
        else:
            first_part = dataset.sel(**{lon_name: slice(west_sel, 360)})
            second_part = dataset.sel(**{lon_name: slice(0, east_sel)})
            dataset = xr.concat([first_part, second_part], dim=lon_name)
            dataset = dataset.sel(**{lat_name: lat_slice})

    if time_name and (start_date is not None) and (end_date is not None):
        dataset = dataset.sel(**{time_name: slice(str(start_date), str(end_date))})

    if time_name and month_numbers and len(month_numbers) < 12:
        month_index = dataset[time_name].dt.month
        dataset = dataset.sel(**{time_name: month_index.isin(list(month_numbers))})

    return dataset


def subset_netcdf_file(
    input_path,
    output_path,
    apply_spatial,
    north,
    south,
    west,
    east,
    start_date,
    end_date,
    month_numbers,
):
    """Open a single NetCDF file, subset it, and save the result."""

    if not XARRAY_AVAILABLE:
        raise RuntimeError(
            "xarray is not installed. Install it with: pip install xarray netCDF4"
        )

    dataset = xr.open_dataset(input_path)

    try:
        dataset = apply_subset_to_dataset(
            dataset, apply_spatial, north, south, west, east,
            start_date, end_date, month_numbers,
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        dataset.to_netcdf(output_path)

    finally:
        dataset.close()


def merge_and_subset_files(
    input_paths,
    output_path,
    apply_spatial,
    north,
    south,
    west,
    east,
    start_date,
    end_date,
    month_numbers,
):
    """Open one or more NetCDF chunk files, concatenate, subset, and save."""

    if not XARRAY_AVAILABLE:
        raise RuntimeError(
            "xarray is not installed. Install it with: pip install xarray netCDF4"
        )

    datasets = [xr.open_dataset(path) for path in input_paths]

    try:
        if len(datasets) > 1:
            time_name = find_coord_name(datasets[0], ["time"])

            if time_name:
                merged = xr.concat(datasets, dim=time_name)
                merged = merged.sortby(time_name)

                _, unique_index = np.unique(
                    merged[time_name].values, return_index=True
                )
                merged = merged.isel(**{time_name: sorted(unique_index)})
            else:
                merged = xr.merge(datasets)
        else:
            merged = datasets[0]

        merged = apply_subset_to_dataset(
            merged, apply_spatial, north, south, west, east,
            start_date, end_date, month_numbers,
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        merged.to_netcdf(output_path)

    finally:
        for dataset in datasets:
            dataset.close()


# ============================================================
# SIDEBAR NAVIGATION & APP METADATA
# ============================================================

with st.sidebar:
    st.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.5); padding: 0.95rem 1rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 1.2rem;">
            <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Developer & Affiliation</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-top: 3px;">{DEVELOPER}</div>
            <div style="font-size: 0.76rem; color: #38bdf8; margin-top: 3px; line-height: 1.35;">{INSTITUTION}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.header("⚙️ System Status")
    st.markdown(f"**Download Path:**\n`{DOWNLOAD_DIR}`")
    st.markdown(f"**Subset Path:**\n`{SUBSET_DIR}`")

    st.divider()

    st.markdown(
        f"**Engine Capabilities:**\n"
        f"- `xarray`: {'✅ Ready' if XARRAY_AVAILABLE else '❌ Missing'}\n"
        f"- `requests`: ✅ Ready\n"
        f"- `netCDF4`: ✅ Ready\n"
    )

    if st.button("🧹 Clear ESGF Search Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("Search cache cleared!")

    st.divider()
    st.caption(f"CMIP6 Data Toolkit v2.5\n{DEVELOPER}\n{INSTITUTION}")


# ============================================================
# HERO HEADER
# ============================================================

st.markdown(
    f"""
    <div class="hero-header">
        <h1 class="hero-title">{APP_NAME}</h1>
        <p class="hero-subtitle">
            Next-Generation Federated ESGF Discovery, Automated NetCDF Batch Downloader & High-Performance Spatial-Temporal Subsetting Engine.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 1. TEMPORAL RESOLUTION
# ============================================================

st.header("1. Temporal resolution")

frequency_options = list(FREQUENCIES.keys())

selected_frequency = st.selectbox(
    "Temporal resolution",
    options=frequency_options,
    index=frequency_options.index("day"),
    format_func=frequency_label,
)


# ============================================================
# 2. EXPERIMENT
# ============================================================

st.header("2. Experiment")

selected_experiments = st.multiselect(
    "Experiment",
    options=list(EXPERIMENTS.keys()),
    format_func=experiment_label,
    default=[],
)

has_historical = "historical" in selected_experiments
scenario_experiments = [x for x in selected_experiments if x != "historical"]
has_scenario = bool(scenario_experiments)


# ============================================================
# 3. VARIABLE
# ============================================================

st.header("3. Variable")

selected_variables = st.multiselect(
    "Variable",
    options=list(VARIABLES.keys()),
    format_func=variable_label,
    default=[],
)

st.caption(f"{len(VARIABLES)} curated CMIP6 variables available in this toolkit.")


# ============================================================
# 4. LEVEL
# ============================================================

st.header("4. Level")

any_pressure_level_variable = any(
    v in PRESSURE_LEVEL_VARIABLES for v in selected_variables
)

selected_levels = st.multiselect(
    "Pressure level",
    options=PRESSURE_LEVEL_OPTIONS,
    default=[],
    disabled=not any_pressure_level_variable and bool(selected_variables),
)

if selected_variables and not any_pressure_level_variable:
    st.caption("Leave empty for surface variables such as pr, tas, tasmax and tasmin.")
else:
    st.caption(
        "Choose the pressure level(s) relevant to the selected pressure-level variable(s)."
    )


# ============================================================
# 5. MODEL
# ============================================================

st.header("5. Model")

selected_models = st.multiselect(
    "Model",
    options=CMIP6_MODELS,
    default=[],
)

st.caption(f"{len(CMIP6_MODELS)} CMIP6 models available in this toolkit.")


# ============================================================
# 6. YEAR (historical and scenario handled independently)
# ============================================================

st.header("6. Year")

if has_historical:
    st.subheader("Historical period")

    hist_mode = st.radio(
        "Historical year selection",
        ["Year groups", "Custom range", "Individual years"],
        horizontal=True,
        key="hist_year_mode",
    )

    if hist_mode == "Year groups":
        selected_hist_groups = st.multiselect(
            "Historical year groups",
            options=HIST_YEAR_GROUPS,
            default=[],
        )
        hist_years = expand_year_groups(selected_hist_groups)

    elif hist_mode == "Custom range":
        hist_range = st.select_slider(
            "Historical years",
            options=list(range(HIST_MIN_YEAR, HIST_MAX_YEAR + 1)),
            value=(1985, 2014),
        )
        hist_years = set(range(hist_range[0], hist_range[1] + 1))

    else:
        hist_individual = st.multiselect(
            "Individual historical years",
            options=list(range(HIST_MIN_YEAR, HIST_MAX_YEAR + 1)),
            default=[],
        )
        hist_years = set(hist_individual)

    if not hist_years:
        hist_years = set(range(1985, 2015))
        st.caption("No historical years chosen yet — defaulting to 1985-2014.")

else:
    hist_years = set()
    st.caption("Select Historical above to configure historical years.")


if has_scenario:
    st.subheader("Future / SSP period")

    scen_mode = st.radio(
        "SSP year selection",
        ["Year groups", "Custom range", "Individual years"],
        horizontal=True,
        key="scen_year_mode",
    )

    if scen_mode == "Year groups":
        selected_scen_groups = st.multiselect(
            "Future / SSP year groups",
            options=SCEN_YEAR_GROUPS,
            default=[],
        )
        scenario_years = expand_year_groups(selected_scen_groups)

    elif scen_mode == "Custom range":
        scen_range = st.select_slider(
            "SSP years",
            options=list(range(SCEN_MIN_YEAR, SCEN_MAX_YEAR + 1)),
            value=(2015, 2100),
        )
        scenario_years = set(range(scen_range[0], scen_range[1] + 1))

    else:
        scen_individual = st.multiselect(
            "Individual future / SSP years",
            options=list(range(SCEN_MIN_YEAR, SCEN_MAX_YEAR + 1)),
            default=[],
        )
        scenario_years = set(scen_individual)

    if not scenario_years:
        scenario_years = set(range(2015, 2101))
        st.caption("No SSP years chosen yet — defaulting to 2015-2100.")

else:
    scenario_years = set()
    st.caption("Select an SSP experiment above to configure future years.")


hist_year_ranges = consecutive_ranges(hist_years)
scenario_year_ranges = consecutive_ranges(scenario_years)


def year_ranges_for_experiment(experiment_id):
    if experiment_id == "historical":
        return hist_year_ranges
    return scenario_year_ranges


def overall_period_for_experiment(experiment_id):
    """Single (start_date, end_date) span for an experiment, used for the
    post-download subsetting step. Returns (None, None) if no years have
    been chosen for that experiment type."""

    if experiment_id == "historical":
        if hist_years:
            return date(min(hist_years), 1, 1), date(max(hist_years), 12, 31)
        return None, None

    if scenario_years:
        return date(min(scenario_years), 1, 1), date(max(scenario_years), 12, 31)

    return None, None


# ============================================================
# 7. MONTH
# ============================================================

st.header("7. Month")

month_button_col1, month_button_col2, _ = st.columns([1, 1, 4])

with month_button_col1:
    if st.button("Select all months"):
        st.session_state.selected_month_list = list(MONTH_NAMES)

with month_button_col2:
    if st.button("Clear all months"):
        st.session_state.selected_month_list = []

selected_months = st.multiselect(
    "Month",
    options=MONTH_NAMES,
    default=st.session_state.selected_month_list,
    key="selected_month_list",
)

selected_month_numbers = sorted(MONTH_NUMBER[m] for m in selected_months)


# ============================================================
# 8. GEOGRAPHICAL AREA
# ============================================================

st.header("8. Geographical area")

region_mode = st.radio(
    "Geographic extent",
    ["Whole available region", "Sub-region"],
    horizontal=True,
)

apply_spatial_subset = region_mode == "Sub-region"

if apply_spatial_subset:
    north_col, south_col, west_col, east_col = st.columns(4)

    with north_col:
        north = st.number_input("North", min_value=-90.0, max_value=90.0, value=30.5, step=0.1)

    with south_col:
        south = st.number_input("South", min_value=-90.0, max_value=90.0, value=25.0, step=0.1)

    with west_col:
        west = st.number_input("West", min_value=-180.0, max_value=180.0, value=80.0, step=0.1)

    with east_col:
        east = st.number_input("East", min_value=-180.0, max_value=180.0, value=89.5, step=0.1)

else:
    north, south, west, east = 90.0, -90.0, -180.0, 180.0
    st.caption("The whole model domain will be kept — no spatial subset will be applied.")


# ============================================================
# VALIDATION
# ============================================================

selection_errors = []

if not selected_models:
    selection_errors.append("Select at least one model.")

if not selected_experiments:
    selection_errors.append("Select at least one experiment.")

if not selected_variables:
    selection_errors.append("Select at least one variable.")

if apply_spatial_subset and north <= south:
    selection_errors.append("North must be greater than South.")

if apply_spatial_subset and east <= west:
    selection_errors.append("East must be greater than West.")


# ============================================================
# 9. SELECTION SUMMARY
# ============================================================

st.header("9. Selection summary")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Models", len(selected_models))

with c2:
    st.metric("Experiments", len(selected_experiments))

with c3:
    st.metric("Variables", len(selected_variables))

with c4:
    st.metric("Frequency", frequency_label(selected_frequency))

if hist_years:
    st.write(f"**Historical years:** {min(hist_years)} → {max(hist_years)}")

if scenario_years:
    st.write(f"**Future/SSP years:** {min(scenario_years)} → {max(scenario_years)}")

if selected_months:
    st.write("**Months:** " + ", ".join(selected_months))

if apply_spatial_subset:
    st.write(f"**Spatial box:** Lat {south} → {north}, Lon {west} → {east}")
else:
    st.write("**Spatial box:** whole available region (no subset)")

for error in selection_errors:
    st.warning(error)


# ============================================================
# 10. DOWNLOAD FILES
# ============================================================

st.header("10. Download files")

st.markdown(
    "This step searches ESGF for **every combination** of the models, "
    "experiments and variables you selected above, filters the results "
    "down to files that actually overlap your chosen years, and shows "
    "them all in **one combined list** with the exact filename of each "
    "`.nc` file — so you can check you're getting the right data and "
    "select as many files as you want to download in a single batch."
)

MAX_COMBOS_WITHOUT_WARNING = 40

if selected_models and selected_experiments and selected_variables:

    all_combos = [
        (model, experiment, variable)
        for model in selected_models
        for experiment in selected_experiments
        for variable in selected_variables
    ]

    st.caption(
        f"This will search {len(all_combos)} model × experiment × variable "
        f"combination(s)."
    )

    if len(all_combos) > MAX_COMBOS_WITHOUT_WARNING:
        st.warning(
            f"You have selected {len(all_combos)} combinations. Searching "
            "all of them can take a while and may hit ESGF rate limits. "
            "Consider narrowing your model/experiment/variable selection "
            "if the search below is slow or fails."
        )

    if st.button(
        "📂 Find matching files for all selections above",
        type="primary",
        use_container_width=True,
    ):
        raw_files = []
        combo_errors = []
        combo_empty = []

        progress = st.progress(0)
        status = st.empty()

        for position, (model, experiment, variable) in enumerate(all_combos, start=1):
            status.write(
                f"Searching {position}/{len(all_combos)}: "
                f"{model} | {experiment_label(experiment)} | {variable_label(variable)}"
            )

            try:
                combo_files = search_files(model, experiment, variable, selected_frequency)

                if combo_files:
                    raw_files.extend(combo_files)
                else:
                    combo_empty.append((model, experiment, variable))

            except Exception as exc:
                combo_errors.append((model, experiment, variable, str(exc)))

            progress.progress(position / len(all_combos))

        status.write("Search complete.")

        st.session_state.file_results_raw = raw_files
        st.session_state.last_file_search = {
            "combos": all_combos,
            "frequency": selected_frequency,
        }

        if combo_empty:
            with st.expander(f"{len(combo_empty)} combination(s) returned no files"):
                st.caption(
                    "Not every CMIP6 model ran every experiment for every "
                    "variable at every temporal resolution — a combination "
                    "can legitimately be missing. Click below to check "
                    "whether each one exists at a different frequency."
                )

                for model, experiment, variable in combo_empty:
                    st.write(f"- {model} | {experiment} | {variable}")

                if st.button("🔍 Check available frequencies for these combinations"):
                    for model, experiment, variable in combo_empty:
                        try:
                            frequencies = check_available_frequencies(
                                model, experiment, variable
                            )
                        except Exception as exc:
                            st.write(
                                f"- {model} | {experiment} | {variable}: "
                                f"check failed ({exc})"
                            )
                            continue

                        if frequencies:
                            available_text = ", ".join(
                                frequency_label(f) for f in frequencies
                            )
                            st.write(
                                f"- {model} | {experiment} | {variable}: "
                                f"published at **{available_text}**, but not "
                                f"at {frequency_label(selected_frequency)}. "
                                "Try a different temporal resolution in step 1."
                            )
                        else:
                            st.write(
                                f"- {model} | {experiment} | {variable}: "
                                "not published on ESGF at any frequency for "
                                "this experiment/variable combination."
                            )

        if combo_errors:
            with st.expander(f"{len(combo_errors)} combination(s) failed to search"):
                for model, experiment, variable, error in combo_errors:
                    st.write(f"- {model} | {experiment} | {variable}: {error}")

    raw_files = st.session_state.file_results_raw

    if raw_files:

        # --------------------------------------------------------
        # ENSEMBLE MEMBER HANDLING
        # --------------------------------------------------------

        available_members = sorted(
            set(field(r, "member_id") for r in raw_files if field(r, "member_id")),
            key=natural_member_sort_key,
        )

        member_mode = st.radio(
            "Ensemble member selection",
            [
                "First available member per combination (recommended)",
                "Choose specific member(s)",
                "All available members",
            ],
            index=0,
        )

        chosen_members = []

        if member_mode == "Choose specific member(s)" and available_members:
            chosen_members = st.multiselect(
                "Ensemble member(s)",
                options=available_members,
                default=[available_members[0]],
            )

        # --------------------------------------------------------
        # APPLY MEMBER FILTER
        # --------------------------------------------------------

        if member_mode == "All available members":
            member_filtered = raw_files

        elif member_mode == "Choose specific member(s)":
            member_filtered = [
                r for r in raw_files
                if (not chosen_members) or (field(r, "member_id") in chosen_members)
            ]

        else:
            first_member_by_combo = {}

            for record in raw_files:
                key = (
                    field(record, "source_id"),
                    field(record, "experiment_id"),
                    field(record, "variable_id"),
                )
                member = field(record, "member_id")

                if member and (
                    key not in first_member_by_combo
                    or natural_member_sort_key(member)
                    < natural_member_sort_key(first_member_by_combo[key])
                ):
                    first_member_by_combo[key] = member

            member_filtered = [
                r for r in raw_files
                if field(r, "member_id")
                == first_member_by_combo.get(
                    (
                        field(r, "source_id"),
                        field(r, "experiment_id"),
                        field(r, "variable_id"),
                    ),
                    field(r, "member_id"),
                )
            ]

        # --------------------------------------------------------
        # APPLY YEAR FILTER (per record's own experiment)
        # --------------------------------------------------------

        matched_by_experiment = []

        for record in member_filtered:
            record_experiment = field(record, "experiment_id")
            ranges = year_ranges_for_experiment(record_experiment)

            if not ranges:
                continue

            for start_year, end_year in ranges:
                period_start = date(start_year, 1, 1)
                period_end = date(end_year, 12, 31)
                file_start, file_end = get_file_period(record)

                if file_overlaps_period(file_start, file_end, period_start, period_end):
                    matched_by_experiment.append(record)
                    break

        def dedupe_key(record):
            start, end = get_file_period(record)
            return (
                field(record, "source_id"),
                field(record, "experiment_id"),
                field(record, "variable_id"),
                field(record, "member_id"),
                field(record, "grid_label"),
                start,
                end,
            )

        deduped = {}
        for record in matched_by_experiment:
            key = dedupe_key(record)
            if key not in deduped:
                deduped[key] = record

        matching_files = list(deduped.values())

        # --------------------------------------------------------
        # RESULTS TABLE
        # --------------------------------------------------------

        if matching_files:
            st.success(
                f"{len(matching_files):,} file(s) match your selections — "
                f"out of {len(raw_files):,} file records found on ESGF "
                f"across all combinations."
            )

            table_rows = []
            file_labels = []

            for record in matching_files:
                filename = extract_filename(record)
                start, end = get_file_period(record)

                table_rows.append(
                    {
                        "Model": field(record, "source_id"),
                        "Experiment": experiment_label(field(record, "experiment_id")),
                        "Variable": variable_label(field(record, "variable_id")),
                        "Member": field(record, "member_id"),
                        "Grid": field(record, "grid_label"),
                        "Period": f"{start} → {end}" if start and end else "unknown",
                        "File name": filename,
                    }
                )
                file_labels.append(filename)

            st.dataframe(table_rows, use_container_width=True, hide_index=True)

            select_all_files = st.checkbox("Select all matching files", value=True)

            if select_all_files:
                selected_file_indices = list(range(len(matching_files)))
            else:
                selected_file_indices = st.multiselect(
                    "Select files to download (file name shown)",
                    options=list(range(len(matching_files))),
                    default=[],
                    format_func=lambda i: file_labels[i],
                )

            st.caption(
                "Only files whose real time coverage overlaps your selected "
                "years are listed above. Different ensemble members (e.g. "
                "r1i1p1f1, r2i1p1f1) are different scientific realizations, "
                "not duplicate copies of the same data."
            )

            if selected_file_indices:
                selected_records = [matching_files[i] for i in selected_file_indices]

                # Group selected files by ensemble series (Model, Experiment, Variable, Member, Grid)
                selected_series_groups = defaultdict(list)
                for rec in selected_records:
                    s_key = (
                        field(rec, "source_id"),
                        field(rec, "experiment_id"),
                        field(rec, "variable_id"),
                        field(rec, "member_id"),
                        field(rec, "grid_label"),
                    )
                    selected_series_groups[s_key].append(rec)

                st.write(
                    f"**{len(selected_records)} raw `.nc` chunk file(s)** selected, "
                    f"belonging to **{len(selected_series_groups)} ensemble run series** "
                    f"(will auto-merge into {len(selected_series_groups)} single file(s) in step 11)."
                )

                with st.expander("📋 Selection Summary by Parameter Series"):
                    series_rows = []
                    for (model, exp, var, member, grid), group_recs in selected_series_groups.items():
                        series_rows.append({
                            "Model": model,
                            "Experiment": experiment_label(exp),
                            "Variable": variable_label(var),
                            "Member": member,
                            "Grid": grid,
                            "Raw Chunk Files": f"{len(group_recs)} file(s)",
                            "Merging Note": "Will auto-merge into 1 continuous dataset in step 11",
                        })
                    st.dataframe(series_rows, use_container_width=True, hide_index=True)

                    show_all_raw_files = st.checkbox("Show exact raw `.nc` filenames")
                    if show_all_raw_files:
                        for record in selected_records:
                            st.write(f"- `{extract_filename(record)}`")

                if st.button(
                    "⬇️ Download all selected NetCDF files",
                    type="primary",
                    use_container_width=True,
                ):
                    dl_progress = st.progress(0)
                    dl_status = st.empty()

                    success_count = 0
                    failure_count = 0
                    downloaded_records = []

                    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

                    total = len(selected_records)

                    for position, record in enumerate(selected_records, start=1):
                        filename = extract_filename(record)
                        dl_status.write(f"Downloading {position}/{total}: `{filename}`")

                        ok, result = download_file(record, DOWNLOAD_DIR)

                        if ok:
                            success_count += 1
                            downloaded_records.append({"path": result, "record": record})
                        else:
                            failure_count += 1
                            st.error(f"{filename}: {result}")

                        dl_progress.progress(position / total)

                    dl_status.write("Download complete.")

                    st.session_state.downloaded_records = downloaded_records

                    st.success(
                        f"Download finished: {success_count} successful, "
                        f"{failure_count} failed."
                    )
                    st.info(f"Files are saved in:\n`{DOWNLOAD_DIR}`")

        elif st.session_state.last_file_search is not None:
            st.warning(
                "No ESGF file overlaps the selected member(s) and year(s) "
                "for any of the searched combinations. The dataset(s) may "
                "exist, but the available file chunks may not overlap the "
                "requested period, or the chosen member(s) may not be "
                "available."
            )

    elif st.session_state.last_file_search is not None:
        st.warning("No file records were returned by ESGF for these combinations.")

else:
    st.info("Select at least one model, experiment and variable to enable file discovery.")


# ============================================================
# 11. MERGE CHUNKS & APPLY SPATIAL / TEMPORAL SUBSETTING
# ============================================================

st.header("11. Merge Chunks & Apply Spatial/Temporal Subsetting")

st.markdown(
    "After raw NetCDF chunk files are downloaded, use this step to "
    "**stitch continuous time chunks together** into a single dataset per "
    "run, apply your chosen **spatial bounding box**, filter by **months**, "
    "and export trimmed `.nc` files to your subset directory."
)

# Inspect existing files in DOWNLOAD_DIR if downloaded_records is empty
existing_downloaded_files = []
if os.path.exists(DOWNLOAD_DIR):
    for f in os.listdir(DOWNLOAD_DIR):
        if f.endswith(".nc") and os.path.isfile(os.path.join(DOWNLOAD_DIR, f)):
            existing_downloaded_files.append(os.path.join(DOWNLOAD_DIR, f))

has_downloaded_data = bool(st.session_state.downloaded_records or existing_downloaded_files)

if not has_downloaded_data:
    st.info(
        "No downloaded files found in memory or disk. "
        "Complete step 11 above to download files first, or place `.nc` files in `D:\\cmip6_raw\\CMIP6_Data`."
    )
else:
    # Build file mapping grouped by (source_id, experiment_id, variable_id, member_id, grid_label)
    groups = defaultdict(list)

    if st.session_state.downloaded_records:
        for item in st.session_state.downloaded_records:
            rec = item["record"]
            path = item["path"]
            if os.path.exists(path):
                key = (
                    field(rec, "source_id", "UnknownModel"),
                    field(rec, "experiment_id", "UnknownExp"),
                    field(rec, "variable_id", "UnknownVar"),
                    field(rec, "member_id", "UnknownMember"),
                    field(rec, "grid_label", "UnknownGrid"),
                )
                groups[key].append(path)
    else:
        # Infer group from existing filename patterns
        for path in existing_downloaded_files:
            filename = os.path.basename(path)
            parts = filename.replace(".nc", "").split("_")
            if len(parts) >= 6:
                var, freq, model, exp, member, grid = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                key = (model, exp, var, member, grid)
                groups[key].append(path)
            else:
                groups[("Local", "Custom", "Data", "r1i1p1f1", "gn")].append(path)

    st.write(f"Found **{len(groups)} distinct ensemble run series** ready for merging and subsetting:")

    group_table = []
    for (model, exp, var, member, grid), paths in groups.items():
        group_table.append({
            "Model": model,
            "Experiment": experiment_label(exp),
            "Variable": variable_label(var),
            "Member": member,
            "Grid": grid,
            "Chunk Files Count": len(paths),
        })

    st.dataframe(group_table, use_container_width=True, hide_index=True)

    if not XARRAY_AVAILABLE:
        st.error("`xarray` and `netCDF4` are required for merging and subsetting NetCDF files. Please install them via pip.")
    else:
        if st.button("🧩 Merge Chunks & Apply Subsetting", type="primary", use_container_width=True):
            subset_progress = st.progress(0)
            subset_status = st.empty()

            subset_results = []
            total_groups = len(groups)
            os.makedirs(SUBSET_DIR, exist_ok=True)

            for idx, ((model, exp, var, member, grid), input_paths) in enumerate(groups.items(), start=1):
                subset_status.write(f"Processing group {idx}/{total_groups}: `{var}` | `{model}` | `{exp}` | `{member}`")

                # Determine overall target period for this experiment
                period_start, period_end = overall_period_for_experiment(exp)

                out_filename = safe_filename(
                    f"{var}_{selected_frequency}_{model}_{exp}_{member}_{grid}_subset.nc"
                )
                output_path = os.path.join(SUBSET_DIR, out_filename)

                try:
                    # Sort chunk files chronologically
                    input_paths.sort()

                    merge_and_subset_files(
                        input_paths=input_paths,
                        output_path=output_path,
                        apply_spatial=apply_spatial_subset,
                        north=north,
                        south=south,
                        west=west,
                        east=east,
                        start_date=period_start,
                        end_date=period_end,
                        month_numbers=selected_month_numbers,
                    )

                    subset_results.append({
                        "Model": model,
                        "Experiment": exp,
                        "Variable": var,
                        "Member": member,
                        "Grid": grid,
                        "Output Path": output_path,
                        "Size (MB)": round(os.path.getsize(output_path) / (1024 * 1024), 2),
                    })

                except Exception as exc:
                    st.error(f"Failed processing group `{var}_{model}_{exp}`: {exc}")

                subset_progress.progress(idx / total_groups)

            subset_status.write("Subsetting complete!")
            st.session_state.subset_records = subset_results

            if subset_results:
                st.success(f"Successfully subsetted and saved {len(subset_results)} processed NetCDF file(s)!")
                st.info(f"Subsetted files are stored in:\n`{SUBSET_DIR}`")
                st.dataframe(subset_results, use_container_width=True, hide_index=True)


# ============================================================
# 12. INTERACTIVE NETCDF INSPECTOR & DATA PREVIEW
# ============================================================

st.header("12. Interactive NetCDF Data Inspector")

st.markdown(
    "Select any downloaded raw NetCDF file or subsetted output file to "
    "inspect header attributes, dimensions, coordinates, and view quick summary statistics."
)

all_nc_files = []
if os.path.exists(DOWNLOAD_DIR):
    for root, _, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            if file.endswith(".nc"):
                all_nc_files.append(os.path.join(root, file))

if not all_nc_files:
    st.info("No NetCDF files available locally for inspection.")
else:
    selected_file_path = st.selectbox(
        "Select NetCDF file to inspect",
        options=all_nc_files,
        format_func=lambda p: os.path.relpath(p, DOWNLOAD_DIR)
    )

    if selected_file_path and XARRAY_AVAILABLE:
        if st.button("🔍 Inspect NetCDF File"):
            try:
                with xr.open_dataset(selected_file_path) as ds:
                    st.subheader("Dataset Overview")
                    col_ds1, col_ds2, col_ds3 = st.columns(3)

                    with col_ds1:
                        st.metric("File Size (MB)", round(os.path.getsize(selected_file_path) / (1024 * 1024), 2))

                    with col_ds2:
                        st.metric("Data Variables", len(ds.data_vars))

                    with col_ds3:
                        st.metric("Dimensions", ", ".join(f"{k}: {v}" for k, v in ds.dims.items()))

                    st.markdown("**Coordinates:**")
                    st.json({k: str(v.dtype) for k, v in ds.coords.items()})

                    st.markdown("**Data Variables & Units:**")
                    var_info = []
                    for v_name, v_var in ds.data_vars.items():
                        var_info.append({
                            "Variable": v_name,
                            "Long Name": v_var.attrs.get("long_name", "N/A"),
                            "Standard Name": v_var.attrs.get("standard_name", "N/A"),
                            "Units": v_var.attrs.get("units", "N/A"),
                            "Shape": str(v_var.shape),
                        })
                    st.dataframe(var_info, use_container_width=True, hide_index=True)

                    with st.expander("View Global Attributes"):
                        st.json({k: str(v) for k, v in ds.attrs.items()})

            except Exception as exc:
                st.error(f"Could not open file: {exc}")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <div class="footer-container">
        <div>🌍 <b>CMIP6 Data Toolkit</b> • Climate Intelligence Platform</div>
        <div style="margin-top: 6px; font-size: 0.84rem;">Developed by <span class="footer-highlight">{DEVELOPER}</span> • <span style="color: #94a3b8;">{INSTITUTION}</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)
