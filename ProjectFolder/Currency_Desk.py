import tkinter as tk
from tkinter import ttk, messagebox
import threading, json, os
from datetime import datetime
import requests

API_URL = "https://open.er-api.com/v6/latest/{base}"
CACHE_FILE = "rates_cache.json"
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

BG       = "#0f1220"
PANEL    = "#151a2f"
TEXT     = "#e6e6e6"
MUTED    = "#a3adc2"
ACCENT   = "#7c3aed"
ACCENT_H = "#a78bfa"


class CurrencyDesk(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Currency Desk")
        self.geometry("700x580")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Set up dark theme for UI
        style = ttk.Style(self)
        if "darkly" not in style.theme_names():
            style.theme_create(
                "darkly",
                parent="clam",
                settings={
                    "TFrame": {"configure": {"background": BG, "borderwidth": 0}},
                    "Card.TFrame": {"configure": {"background": PANEL, "borderwidth": 0}},
                    "TLabel": {"configure": {"background": PANEL, "foreground": TEXT, "font": ("Segoe UI", 11)}},
                    "Header.TLabel": {"configure": {"background": PANEL, "foreground": TEXT, "font": ("Segoe UI Semibold", 18)}},
                    "Sub.TLabel": {"configure": {"background": PANEL, "foreground": MUTED, "font": ("Segoe UI", 10)}},
                    "TButton": {
                        "configure": {"background": "#1f2547", "foreground": TEXT, "borderwidth": 0,
                                      "padding": (10, 6), "focuscolor": "", "relief": "flat"},
                        "map": {"background": [("active", "#242b56"), ("disabled", "#252a44")],
                                "foreground": [("disabled", "#6b7280")]}
                    },
                    "Accent.TButton": {
                        "configure": {"background": ACCENT, "foreground": "white", "padding": (12, 6)},
                        "map": {"background": [("active", ACCENT_H)]},
                    },
                },
            )
        style.theme_use("darkly")

        # App state variables
        self.session = requests.Session()
        self.base = "USD"
        self.rates = {}
        self.last_updated_txt = "—"
        self.online = False

        self.amount_var = tk.StringVar(value="500")
        self.from_var   = tk.StringVar(value="USD")
        self.to_var     = tk.StringVar(value="ILS")

        # Layout root
        root = ttk.Frame(self, padding=16, style="TFrame")
        root.pack(fill="both", expand=True)

        # Header card
        head = ttk.Frame(root, style="Card.TFrame")
        head.pack(fill="x")
        pad = ttk.Frame(head, style="Card.TFrame")
        pad.pack(padx=16, pady=16, fill="x")

        ttk.Label(pad, text="Currency Desk", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(pad, text="Development by Etesh Barck", style="Sub.TLabel").grid(row=0, column=1, sticky="e")

        self.status_lbl = ttk.Label(pad, text="Status: starting…", style="Sub.TLabel")
        self.status_lbl.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # Controls card
        ctr = ttk.Frame(root, style="Card.TFrame")
        ctr.pack(fill="x", pady=(12, 8))
        cp = ttk.Frame(ctr, style="Card.TFrame")
        cp.pack(padx=16, pady=16, fill="x")

        ttk.Label(cp, text="From", style="TLabel").grid(row=0, column=0, sticky="w")
        self.from_cb = ttk.Combobox(cp, state="readonly", textvariable=self.from_var, width=14,
                                    values=[c for c, _ in CURS])
        self.from_cb.grid(row=1, column=0, sticky="w")
        self.from_cb.current(0)

        ttk.Label(cp, text="To", style="TLabel").grid(row=0, column=1, sticky="w", padx=(16, 0))
        self.to_cb = ttk.Combobox(cp, state="readonly", textvariable=self.to_var, width=14,
                                  values=[c for c, _ in CURS])
        self.to_cb.grid(row=1, column=1, sticky="w", padx=(16, 0))
        self.to_cb.current(6)

        ttk.Label(cp, text="Amount", style="TLabel").grid(row=0, column=2, sticky="w", padx=(16, 0))
        amt_entry = ttk.Entry(cp, textvariable=self.amount_var, width=16)
        amt_entry.grid(row=1, column=2, sticky="w", padx=(16, 0))

        convert_btn = ttk.Button(cp, text="Convert", style="Accent.TButton", command=self.convert_once)
        convert_btn.grid(row=1, column=3, padx=(16, 0))

        refresh_btn = ttk.Button(cp, text="Refresh Rates", command=self.fetch_async)
        refresh_btn.grid(row=1, column=4, padx=(12, 0))

        self.result_lbl = ttk.Label(cp, text="Result: —", style="TLabel")
        self.result_lbl.grid(row=2, column=0, columnspan=5, sticky="w", pady=(10, 0))

        for i in range(5):
            cp.columnconfigure(i, weight=1)

        # Table card
        tbl = ttk.Frame(root, style="Card.TFrame")
        tbl.pack(fill="both", expand=True)
        tp = ttk.Frame(tbl, style="Card.TFrame")
        tp.pack(padx=16, pady=16, fill="both", expand=True)

        self.table_title = ttk.Label(tp, text="From → All (Amount applied)", style="TLabel")
        self.table_title.pack(anchor="w", pady=(0, 6))

        tree_wrap = ttk.Frame(tp, style="Card.TFrame")
        tree_wrap.pack(fill="both", expand=True)

        xscroll = ttk.Scrollbar(tree_wrap, orient="horizontal")
        yscroll = ttk.Scrollbar(tree_wrap, orient="vertical")

        self.tree = ttk.Treeview(
            tree_wrap,
            columns=("code", "name", "per_one", "amount_total"),
            show="headings",
            height=12,
            xscrollcommand=xscroll.set,
            yscrollcommand=yscroll.set,
        )

        yscroll.config(command=self.tree.yview)
        xscroll.config(command=self.tree.xview)

        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("code", text="Code")
        self.tree.heading("name", text="Name")
        self.tree.heading("per_one", text="1 From → To")
        self.tree.heading("amount_total", text="Amount From → To")

        self.tree.column("code", width=70, anchor="center", stretch=False)
        self.tree.column("name", width=260, anchor="w", stretch=True)
        self.tree.column("per_one", width=140, anchor="e", stretch=False)
        self.tree.column("amount_total", width=170, anchor="e", stretch=False)

        self.fetch_async()


    def _only_date(self, s: str) -> str:
        # Extract only the date part from a datetime string
        try:
            dt = datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z")
            return dt.strftime("%a, %d %b %Y")
        except Exception:
            parts = s.split()
            return " ".join(parts[:4]) if len(parts) >= 4 else s

    def fetch_async(self):
        # Start background fetch and schedule next fetch
        self._set_status("Fetching rates…")
        threading.Thread(target=self._fetch_rates_with_cache, daemon=True).start()

    def _fetch_rates_with_cache(self):
        online = False
        base = "USD"
        rates = {}
        updated_txt = "—"
        try:
            resp = self.session.get(API_URL.format(base=base), timeout=6)
            resp.raise_for_status()
            data = resp.json()
            all_rates = data.get("rates", {})
            # Keep only supported currencies and always 1.0 for base
            rates = {code: float(all_rates.get(code, 0.0)) for code, _ in CURS}
            rates[base] = 1.0
            updated_txt = self._only_date(data.get("time_last_update_utc", "").strip())
            # Save cache to file
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"base": base, "rates": rates, "updated": updated_txt}, f)
            online = True
        except Exception:
            # Try loading from cache if online fetch fails
            if os.path.exists(CACHE_FILE):
                try:
                    with open(CACHE_FILE, "r", encoding="utf-8") as f:
                        cached = json.load(f)
                    base = cached.get("base", "USD")
                    rates = cached.get("rates", {})
                    updated_txt = self._only_date(cached.get("updated", "cached"))
                except Exception:
                    rates = {}
            else:
                rates = {}

        # Apply rates on UI thread
        self.after(0, lambda: self._apply_rates(base, rates, updated_txt, online))

    def _apply_rates(self, base: str, rates: dict, updated_txt: str, online: bool):
        self.base = base
        self.rates = rates
        self.last_updated_txt = updated_txt
        self.online = online

        if not self.rates:
            self._set_status("Status: error (no rates)")
        else:
            net = "online" if self.online else "offline (cache)"
            self._set_status(f"Status: {net} · Last update: {self.last_updated_txt}")

        self.refresh_table()
        self.after(AUTO_REFRESH_MS, self.fetch_async)

    def _to_float(self, s: str, default: float = 1.0) -> float:
        # Convert string to float, fallback to default
        try:
            return max(float(s.strip().replace(",", ".")), 0.0)
        except Exception:
            return default

    def _rate(self, code: str) -> float | None:
        # Return how many units of 'code' per 1 USD
        r = self.rates.get(code)
        if not r or r <= 0:
            return None
        return r

    def convert_amount(self, amount: float, from_code: str, to_code: str) -> float | None:
        # Convert amount from one currency to another using USD as base
        if from_code == to_code:
            return amount
        rf = self._rate(from_code)
        rt = self._rate(to_code)
        if rf is None or rt is None:
            return None
        return amount * (rt / rf)

    def convert_once(self):
        # Convert once and update result label
        amount = self._to_float(self.amount_var.get(), 1.0)
        f = self.from_var.get()
        t = self.to_var.get()
        val = self.convert_amount(amount, f, t)
        if val is None:
            messagebox.showerror("Error", "Rates not ready yet.")
            return
        self.result_lbl.config(text=f"Result: {amount:,.3f} {f} → {val:,.3f} {t}")
        self.refresh_table()

    def refresh_table(self):
        # Refresh the table with conversion results
        f = self.from_var.get()
        self.table_title.config(text=f"{f} → All (Amount applied)")

        for row in self.tree.get_children():
            self.tree.delete(row)

        amount = self._to_float(self.amount_var.get(), 1.0)
        for code, name in CURS:
            if code == f:
                per_one = 1.0
                total = amount
            else:
                conv1 = self.convert_amount(1.0, f, code)
                convA = None if conv1 is None else conv1 * amount
                per_one = conv1 if conv1 is not None else "—"
                total = convA if convA is not None else "—"

            per_one_str = f"{per_one:,.3f}" if isinstance(per_one, (int, float)) else "—"
            total_str   = f"{total:,.3f}"   if isinstance(total,   (int, float)) else "—"

            self.tree.insert("", "end", values=(code, name, per_one_str, total_str))

    def _set_status(self, txt: str):
        self.status_lbl.config(text=txt)


if __name__ == "__main__":
    CurrencyDesk().mainloop()
