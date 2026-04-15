# 🏆 Pro-Sports Performance Engine

A dark-themed, interactive sports analytics dashboard built with Streamlit and Plotly. Drop in any sports CSV and get instant visualizations — no configuration needed.

---

## Features

- Auto-detects CSV files in the project folder and identifies the sport type (NBA, FIFA, or General)
- KPI cards showing row count, attributes, unique athletes, and missing data
- Distribution tab with a gradient histogram and KDE density curve overlay
- Correlation tab with a color-encoded scatter plot and automatic trendline
- Raw data inspection table
- Fully dark, glass-morphism UI theme

---

## Requirements

- Python 3.9 or higher
- Dependencies listed in `requirements.txt`

---

## Installation

**1. Clone or download the project**

```bash
git clone <your-repo-url>
cd pro-sports-engine
```

**2. Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Usage

**1. Add your data**

Place one or more `.csv` files in the same folder as `sports_dashboard.py`. The app auto-detects them on startup.

**2. Run the app**

```bash
streamlit run sports_dashboard.py
```

**3. Open in browser**

Streamlit will print a local URL (usually `http://localhost:8501`). Open it in any browser.

---

## Supported Dataset Formats

The app auto-detects sport type based on column names:

| Sport | Detection Logic |
|-------|----------------|
| NBA | Columns contain `pts`, `ppg`, or `nba` |
| FIFA | Columns contain `overall`, `club`, or `fifa` |
| General Sports | Any other CSV with numeric columns |

Any CSV with at least one numeric column will work. A column named `name` or `player` is used for hover labels in charts.

---

## Project Structure

```
pro-sports-engine/
├── sports_dashboard.py   # Main app
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── *.csv                 # Your data files (add here)
```

---

## Notes

- `scipy` is required for the KDE density curve on the histogram. If unavailable, the histogram still renders without the overlay.
- The app caches loaded CSV data using `@st.cache_data`. If you add new files, use **Rerun** in the Streamlit menu or press `R` to reload.
- Tested on Python 3.9, 3.10, and 3.11.
