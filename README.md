# Currency Desk — 8-way Converter (Dark)

A dark-themed Tkinter desktop app for fast currency conversion across **USD, EUR, JPY, CHF, GBP, TRY, ILS, AZN**.  
Uses **open.er-api.com** for live rates, auto-refreshes every 60s, and falls back to a local cache when offline.

---

## ✨ Features
- 8 currencies: USD, EUR, JPY, CHF, GBP, TRY, ILS, AZN  
- Convert **any → any** via cross-rates (base-independent)  
- Auto refresh every **60 seconds** (configurable)  
- **Offline cache** (graceful fallback)  
- Dark UI with scrollable table & resizable columns  
- Clear status: **online/offline**, last update (date only)

---

## 🧱 Tech
- Python **3.10+**
- Tkinter / ttk
- `requests`
- JSON cache

---

## 🚀 Install & Run

> Requires **Python 3.10+**. Tkinter ships with Python; only `requests` is installed from PyPI.

```bash
# 1) Get the sources
git clone https://github.com/<your-username>/Currency-Desk.git
cd Currency-Desk

# 2) (Recommended) create and activate a virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

# 3) Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4) Run the app
python ProjectFolder/Currency_Desk.py
Notes

If PowerShell blocks activation on Windows, run once as Administrator:

powershell
Copy code
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
To exit the virtual environment: deactivate.

⚙️ Configuration
Open the Python file and adjust these constants if needed:

python
Copy code
API_URL = "https://open.er-api.com/v6/latest/{base}"  # source API
AUTO_REFRESH_MS = 60_000                               # auto-refresh period (ms)
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
🧪 How It Works
Fetches rates (base=USD) from the API.

Stores only the configured 8 currencies to rates_cache.json.

Conversion uses cross-rate:

css
Copy code
amount * (rate[to] / rate[from])
If fetching fails, reads from cache and shows offline in the status bar.

📦 Packaging (optional)
Create a standalone executable with PyInstaller:

bash
Copy code
pip install pyinstaller
pyinstaller --noconsole --onefile --name CurrencyDesk ProjectFolder/Currency_Desk.py
# output → dist/CurrencyDesk.exe
You can safely ignore/remove build/ and __pycache__/.

🧹 .gitignore (suggested)
pgsql
Copy code
venv/
__pycache__/
build/
dist/
*.egg-info/
rates_cache.json
❓ Troubleshooting
“No module named requests” → pip install requests in the activated venv.

Permission error on venv activate (Windows) → run Set-ExecutionPolicy -Scope CurrentUser RemoteSigned once.

API unreachable → app runs from cached rates (shown as offline).

📜 License
MIT License — see LICENSE.

👤 Credits
© 2025 Etesh Barck
Built with Python/Tkinter. FX data by open.er-api.com.

markdown
Copy code

If your main file isn’t under `ProjectFolder/Currency_Desk.py`, just tweak that path in the **Run** and **PyInstaller** commands.
::contentReference[oaicite:0]{index=0}
