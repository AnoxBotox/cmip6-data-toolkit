# 🌍 CMIP6 Data Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.20+-red.svg)](https://streamlit.io/)
[![xarray](https://img.shields.io/badge/xarray-climate--ready-green.svg)](https://xarray.dev/)

An interactive, high-performance **CMIP6 Climate Data Platform** for federated Earth System Grid Federation (ESGF) discovery, automated NetCDF batch downloading, multi-file chunk merging, and spatial-temporal subsetting.

Developed by **Avishek Acharya**  
*Institute of Engineering, Purwanchal Campus, Dharan, Nepal*

---

## 🌟 Key Features

- 🔍 **Federated ESGF Search with Multi-Node Fallback**: Queries Solr indexes across DKRZ, CEDA, and LLNL nodes with automated retry and local fallback logic.
- 🎯 **Curated Models & Variables**: Select from 60+ curated CMIP6 models and essential surface & pressure-level variables (`pr`, `tas`, `tasmax`, `tasmin`, `hurs`, `sfcWind`, `zg`, `ta`, etc.).
- 📅 **Independent Past & Future Year Range Trimming**: Configure historical (1850–2014) and future SSP scenarios (SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5) independently.
- 🗺️ **Spatial Bounding Box & Calendar Month Subsetting**: Filter geographically by bounding box (with antimeridian wrap-around support) and specific calendar months.
- 📦 **Automated Chunk Merging & Subsetting**: Automatically concatenates chronologically ordered raw `.nc` chunk files into continuous datasets per run, deduplicating boundaries and outputting ready-to-analyze NetCDF files.
- 🔬 **Interactive NetCDF Inspector**: Examine NetCDF header attributes, dimensions, coordinates, variables, and metadata natively in the web browser.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/avishek-acharya/cmip6-data-toolkit.git
cd cmip6-data-toolkit
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```

---

## 📁 Repository Structure

```
cmip6-data-toolkit/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions automated build & lint workflow
├── .streamlit/
│   └── config.toml            # Streamlit theme & server configuration
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Python build metadata
├── .gitignore                 # Standard git ignore rules (ignores data & .nc files)
├── LICENSE                    # MIT License (Avishek Acharya)
└── README.md                  # Project documentation
```

---

## 🛠️ Technology Stack

- **UI Framework**: [Streamlit](https://streamlit.io/)
- **Data Engine**: [xarray](https://xarray.dev/) & [netCDF4](https://unidata.github.io/netcdf4-python/)
- **Array Math**: [NumPy](https://numpy.org/) & [Pandas](https://pandas.pydata.org/)
- **Networking**: [Requests](https://requests.readthedocs.io/) (Solr ESGF API)

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.

Developed by **Avishek Acharya**  
Institute of Engineering, Purwanchal Campus, Dharan, Nepal.
