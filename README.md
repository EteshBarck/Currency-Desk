# Currency Desk
A dark-themed Tkinter desktop app for fast currency conversion across USD, EUR, JPY, CHF, GBP, TRY, ILS, AZN.
Uses open.er-api.com for live rates, auto-refreshes every 60s, and falls back to a local cache when offline.

Features

8 currencies (USD, EUR, JPY, CHF, GBP, TRY, ILS, AZN)

Convert any → any via cross-rates

Auto refresh every 60s (configurable)

Offline cache (graceful fallback)

Dark UI, scrollable table, resizable columns

Clear status: online/offline, last update (date)

Tech

Python 3.10+

Tkinter / ttk

requests

JSON cache

Quick Start
git clone https://github.com/<your-username>/Currency_App.git
cd Currency_App

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install requests

# macOS / Linux
# python3 -m venv venv && source venv/bin/activate
# python -m pip install --upgrade pip && pip install requests


Run:

python Currency_Desk.py

Configuration

In code you can tune:

API_URL = "https://open.er-api.com/v6/latest/{base}"
AUTO_REFRESH_MS = 60_000
CURS = [
    ("USD", "US Dollar"),
    ("EUR", "Euro"),
    ("JPY", "Japanese Yen"),
    ("CHF", "Swiss Franc"),
    ("GBP", "British Pound"),
    ("TRY", "Turkish Lira"),
    ("ILS", "Israeli Shekel"),
    ("AZN", "Azerbaijani Manat"),
]

How It Works

Fetches rates (base=USD) from the API.

Stores only the configured 8 currencies to rates_cache.json.

Conversion uses cross-rate: amount * (rate[to] / rate[from]).

If fetching fails, reads from cache and marks offline.

Packaging (optional)
pip install pyinstaller
pyinstaller --noconsole --onefile --name CurrencyDesk Currency_Desk.py
# output → dist/CurrencyDesk.exe

.gitignore (suggested)
venv/
__pycache__/
build/
dist/
*.egg-info/
rates_cache.json

License

MIT License — see LICENSE
.

Credits

© 2025 Etesh Barck
Built with Python/Tkinter. FX data by open.er-api.com.
