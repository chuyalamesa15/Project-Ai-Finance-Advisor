import customtkinter as ctk
import json
import os
import hashlib
import datetime
import threading
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from google import genai
from database import Database


# ── Theme ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_primary":    "#0A0E1A",
    "bg_secondary":  "#111827",
    "bg_card":       "#1C2333",
    "bg_card2":      "#141B2D",
    "accent_blue":   "#3B82F6",
    "accent_cyan":   "#06B6D4",
    "accent_green":  "#10B981",
    "accent_red":    "#EF4444",
    "accent_orange": "#F59E0B",
    "accent_purple": "#8B5CF6",
    "text_primary":  "#F1F5F9",
    "text_secondary":"#94A3B8",
    "text_muted":    "#475569",
    "border":        "#1E2D45",
    "hover":         "#253352",
}

FONT_TITLE  = ("Trebuchet MS", 28, "bold")
FONT_HEAD   = ("Trebuchet MS", 18, "bold")
FONT_SUB    = ("Trebuchet MS", 14, "bold")
FONT_BODY   = ("Trebuchet MS", 13)
FONT_SMALL  = ("Trebuchet MS", 11)
FONT_MONO   = ("Courier New",  12)


# ── Helpers ────────────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def fmt_currency(val: float) -> str:
    return f"Rp {val:,.0f}".replace(",", ".")


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
class LoginPage(ctk.CTkFrame):
    def __init__(self, master, on_login, on_register):
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self.on_login = on_login
        self.on_register = on_register
        self._build()

    def _build(self):
        # gradient bg effect via canvas-less method — just nested frames
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                            corner_radius=24, width=460)
        card.grid(row=0, column=0, padx=40, pady=40, sticky="")
        card.grid_propagate(False)
        card.configure(width=460, height=600)

        # Logo area
        logo_frame = ctk.CTkFrame(card, fg_color="transparent")
        logo_frame.pack(pady=(50, 10))

        icon_lbl = ctk.CTkLabel(logo_frame, text="💎",
                                font=("Trebuchet MS", 52))
        icon_lbl.pack()

        title = ctk.CTkLabel(logo_frame, text="FinanceAI",
                             font=FONT_TITLE, text_color=COLORS["accent_blue"])
        title.pack()
        sub = ctk.CTkLabel(logo_frame, text="AI-Powered Financial Advisor",
                           font=FONT_SMALL, text_color=COLORS["text_secondary"])
        sub.pack()

        # Divider
        div = ctk.CTkFrame(card, height=1, fg_color=COLORS["border"])
        div.pack(fill="x", padx=40, pady=20)

        # Form
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(padx=40, fill="x")

        ctk.CTkLabel(form, text="Username", font=FONT_SUB,
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.user_entry = ctk.CTkEntry(form, height=46, font=FONT_BODY,
                                       placeholder_text="Masukkan username",
                                       fg_color=COLORS["bg_primary"],
                                       border_color=COLORS["border"],
                                       text_color=COLORS["text_primary"])
        self.user_entry.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(form, text="Password", font=FONT_SUB,
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.pass_entry = ctk.CTkEntry(form, height=46, font=FONT_BODY,
                                       placeholder_text="Masukkan password",
                                       show="●",
                                       fg_color=COLORS["bg_primary"],
                                       border_color=COLORS["border"],
                                       text_color=COLORS["text_primary"])
        self.pass_entry.pack(fill="x", pady=(0, 24))
        self.pass_entry.bind("<Return>", lambda e: self._do_login())

        self.err_lbl = ctk.CTkLabel(form, text="", font=FONT_SMALL,
                                    text_color=COLORS["accent_red"])
        self.err_lbl.pack()

        btn_login = ctk.CTkButton(form, text="MASUK", height=50, font=FONT_SUB,
                                  fg_color=COLORS["accent_blue"],
                                  hover_color="#2563EB",
                                  corner_radius=12,
                                  command=self._do_login)
        btn_login.pack(fill="x", pady=(8, 12))

        btn_reg = ctk.CTkButton(form, text="Belum punya akun? Daftar",
                                height=46, font=FONT_BODY,
                                fg_color="transparent",
                                border_width=1,
                                border_color=COLORS["accent_blue"],
                                text_color=COLORS["accent_blue"],
                                hover_color=COLORS["hover"],
                                corner_radius=12,
                                command=self.on_register)
        btn_reg.pack(fill="x")

    def _do_login(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()
        if not u or not p:
            self.err_lbl.configure(text="⚠ Username dan password wajib diisi")
            return
        self.on_login(u, p, self.err_lbl)


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTER PAGE
# ══════════════════════════════════════════════════════════════════════════════
class RegisterPage(ctk.CTkFrame):
    def __init__(self, master, on_register, on_back):
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self.on_register = on_register
        self.on_back = on_back
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=24)
        card.grid(row=0, column=0, padx=40, pady=30, sticky="")
        card.configure(width=520, height=700)
        card.grid_propagate(False)

        # Header
        ctk.CTkLabel(card, text="💎", font=("Trebuchet MS", 44)).pack(pady=(40, 4))
        ctk.CTkLabel(card, text="Buat Akun Baru", font=FONT_TITLE,
                     text_color=COLORS["accent_cyan"]).pack()
        ctk.CTkLabel(card, text="Bergabung dengan FinanceAI",
                     font=FONT_SMALL, text_color=COLORS["text_secondary"]).pack(pady=(2, 16))

        div = ctk.CTkFrame(card, height=1, fg_color=COLORS["border"])
        div.pack(fill="x", padx=40, pady=(0, 16))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(padx=40, fill="x")

        def field(label, ph, show=False):
            ctk.CTkLabel(form, text=label, font=FONT_SUB,
                         text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
            e = ctk.CTkEntry(form, height=44, font=FONT_BODY,
                             placeholder_text=ph, show="●" if show else "",
                             fg_color=COLORS["bg_primary"],
                             border_color=COLORS["border"],
                             text_color=COLORS["text_primary"])
            e.pack(fill="x", pady=(0, 12))
            return e

        self.name_e  = field("Nama Lengkap", "Nama lengkap Anda")
        self.user_e  = field("Username",     "Buat username unik")
        self.pass_e  = field("Password",     "Minimal 6 karakter", show=True)
        self.cpass_e = field("Konfirmasi Password", "Ulangi password", show=True)

        # Account type selector
        ctk.CTkLabel(form, text="Jenis Akun", font=FONT_SUB,
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 6))
        self.acc_type = ctk.StringVar(value="pribadi")
        type_frame = ctk.CTkFrame(form, fg_color=COLORS["bg_primary"],
                                  corner_radius=10)
        type_frame.pack(fill="x", pady=(0, 16))

        for val, label, icon in [("pribadi", "Akun Pribadi", "👤"),
                                  ("badan_usaha", "Badan Usaha", "🏢")]:
            rb = ctk.CTkRadioButton(type_frame, text=f" {icon}  {label}",
                                    variable=self.acc_type, value=val,
                                    font=FONT_BODY,
                                    text_color=COLORS["text_primary"],
                                    fg_color=COLORS["accent_blue"])
            rb.pack(side="left", padx=20, pady=12)

        self.err_lbl = ctk.CTkLabel(form, text="", font=FONT_SMALL,
                                    text_color=COLORS["accent_red"])
        self.err_lbl.pack()

        ctk.CTkButton(form, text="DAFTAR SEKARANG", height=50, font=FONT_SUB,
                      fg_color=COLORS["accent_cyan"], hover_color="#0891B2",
                      corner_radius=12, command=self._do_register).pack(fill="x", pady=(8, 8))

        ctk.CTkButton(form, text="← Kembali ke Login", height=40, font=FONT_BODY,
                      fg_color="transparent", text_color=COLORS["text_secondary"],
                      hover_color=COLORS["hover"], corner_radius=12,
                      command=self.on_back).pack(fill="x")

    def _do_register(self):
        n  = self.name_e.get().strip()
        u  = self.user_e.get().strip()
        p  = self.pass_e.get().strip()
        cp = self.cpass_e.get().strip()
        at = self.acc_type.get()

        if not all([n, u, p, cp]):
            self.err_lbl.configure(text="⚠ Semua kolom wajib diisi"); return
        if len(p) < 6:
            self.err_lbl.configure(text="⚠ Password minimal 6 karakter"); return
        if p != cp:
            self.err_lbl.configure(text="⚠ Password tidak cocok"); return
        self.on_register(n, u, p, at, self.err_lbl)


# ══════════════════════════════════════════════════════════════════════════════
#  TRANSACTION DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class TransactionDialog(ctk.CTkToplevel):
    PRIBADI_CATEGORIES = {
        "Pemasukan": ["Gaji", "Freelance", "Investasi", "Hadiah", "Lainnya"],
        "Pengeluaran": ["Makanan & Minuman", "Transportasi", "Kesehatan",
                        "Hiburan", "Belanja", "Tagihan", "Pendidikan", "Lainnya"],
    }
    BADAN_CATEGORIES = {
        "Pemasukan": ["Penjualan", "Jasa", "Investasi", "Pinjaman", "Lainnya"],
        "Pengeluaran": ["Gaji Karyawan", "Operasional", "Bahan Baku",
                        "Marketing", "Sewa", "Pajak", "Utilitas", "Lainnya"],
    }

    def __init__(self, master, acc_type, on_save):
        super().__init__(master)
        self.on_save = on_save
        self.cats = (self.PRIBADI_CATEGORIES if acc_type == "pribadi"
                     else self.BADAN_CATEGORIES)
        self.title("Tambah Transaksi")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_card"])
        self.grab_set()
        self._build()

    def _build(self):
        pad = {"padx": 32, "pady": 8}

        ctk.CTkLabel(self, text="➕  Tambah Transaksi",
                     font=FONT_HEAD, text_color=COLORS["accent_blue"]).pack(pady=(28, 4))
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=32, pady=8)

        # Type
        ctk.CTkLabel(self, text="Jenis Transaksi", font=FONT_SUB,
                     text_color=COLORS["text_secondary"]).pack(anchor="w", **pad)
        self.t_type = ctk.StringVar(value="Pemasukan")
        tf = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=10)
        tf.pack(fill="x", padx=32, pady=(0, 8))
        for v, c in [("Pemasukan", COLORS["accent_green"]),
                     ("Pengeluaran", COLORS["accent_red"])]:
            ctk.CTkRadioButton(tf, text=v, variable=self.t_type, value=v,
                               font=FONT_BODY, text_color=COLORS["text_primary"],
                               fg_color=c, command=self._update_cats
                               ).pack(side="left", padx=24, pady=10)

        # Category
        ctk.CTkLabel(self, text="Kategori", font=FONT_SUB,
                     text_color=COLORS["text_secondary"]).pack(anchor="w", **pad)
        self.cat_var = ctk.StringVar(value=self.cats["Pemasukan"][0])
        self.cat_menu = ctk.CTkOptionMenu(self, variable=self.cat_var,
                                          values=self.cats["Pemasukan"],
                                          font=FONT_BODY, height=44,
                                          fg_color=COLORS["bg_primary"],
                                          button_color=COLORS["accent_blue"],
                                          dropdown_fg_color=COLORS["bg_card"])
        self.cat_menu.pack(fill="x", padx=32, pady=(0, 8))

        # Amount
        ctk.CTkLabel(self, text="Jumlah (Rp)", font=FONT_SUB,
                     text_color=COLORS["text_secondary"]).pack(anchor="w", **pad)
        self.amount_e = ctk.CTkEntry(self, height=46, font=FONT_BODY,
                                     placeholder_text="Contoh: 500000",
                                     fg_color=COLORS["bg_primary"],
                                     border_color=COLORS["border"],
                                     text_color=COLORS["text_primary"])
        self.amount_e.pack(fill="x", padx=32, pady=(0, 8))

        # Description
        ctk.CTkLabel(self, text="Deskripsi", font=FONT_SUB,
                     text_color=COLORS["text_secondary"]).pack(anchor="w", **pad)
        self.desc_e = ctk.CTkEntry(self, height=46, font=FONT_BODY,
                                   placeholder_text="Catatan singkat transaksi",
                                   fg_color=COLORS["bg_primary"],
                                   border_color=COLORS["border"],
                                   text_color=COLORS["text_primary"])
        self.desc_e.pack(fill="x", padx=32, pady=(0, 16))

        self.err_lbl = ctk.CTkLabel(self, text="", font=FONT_SMALL,
                                    text_color=COLORS["accent_red"])
        self.err_lbl.pack()

        ctk.CTkButton(self, text="SIMPAN TRANSAKSI", height=50, font=FONT_SUB,
                      fg_color=COLORS["accent_green"], hover_color="#059669",
                      corner_radius=12, command=self._save).pack(fill="x", padx=32, pady=(4, 20))

    def _update_cats(self):
        t = self.t_type.get()
        vals = self.cats[t]
        self.cat_menu.configure(values=vals)
        self.cat_var.set(vals[0])

    def _save(self):
        try:
            amt = float(self.amount_e.get().replace(",", "").replace(".", ""))
            if amt <= 0: raise ValueError
        except ValueError:
            self.err_lbl.configure(text="⚠ Jumlah harus berupa angka positif")
            return
        desc = self.desc_e.get().strip() or "-"
        self.on_save({
            "type": self.t_type.get(),
            "category": self.cat_var.get(),
            "amount": amt,
            "description": desc,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
class Dashboard(ctk.CTkFrame):
    def __init__(self, master, user_data: dict, db: Database, on_logout):
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self.user = user_data
        self.db   = db
        self.on_logout = on_logout
        self.ai_model  = None
        self.ai_client = None
        self.chat_hist = []
        self.transactions = []
        self._setup_ai()
        self._load_transactions()
        self._build()

    # ── AI Setup ──────────────────────────────────────────────────────────────
    def _setup_ai(self):
        api_key = self.db.get_api_key(self.user["username"])
        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                self.ai_client = client
                self.ai_model  = client   # simpan client, dipakai di _send_ai
            except Exception:
                self.ai_client = None
                self.ai_model  = None



    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Sidebar ──
        self.sidebar = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"],
                                    width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self._build_sidebar()

        # ── Main Content ──
        self.content = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_primary"],
                                              scrollbar_button_color=COLORS["border"])
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)

        self._show_overview()

    def _build_sidebar(self):
        sb = self.sidebar

        # Logo
        logo_f = ctk.CTkFrame(sb, fg_color=COLORS["bg_card"], height=100)
        logo_f.pack(fill="x")
        ctk.CTkLabel(logo_f, text="💎 FinanceAI",
                     font=("Trebuchet MS", 17, "bold"),
                     text_color=COLORS["accent_blue"]).pack(pady=20)

        # User info
        acc_label = "👤 Pribadi" if self.user["acc_type"] == "pribadi" else "🏢 Badan Usaha"
        acc_color = COLORS["accent_cyan"] if self.user["acc_type"] == "pribadi" else COLORS["accent_orange"]

        ctk.CTkFrame(sb, height=1, fg_color=COLORS["border"]).pack(fill="x")
        ui_f = ctk.CTkFrame(sb, fg_color="transparent")
        ui_f.pack(fill="x", padx=16, pady=16)
        ctk.CTkLabel(ui_f, text=f"Halo, {self.user['name'].split()[0]}!",
                     font=FONT_SUB, text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(ui_f, text=acc_label, font=FONT_SMALL,
                     text_color=acc_color).pack(anchor="w")
        ctk.CTkFrame(sb, height=1, fg_color=COLORS["border"]).pack(fill="x")

        # Nav buttons
        nav_items = [
            ("📊  Overview",        "overview"),
            ("💳  Transaksi",       "transactions"),
            ("📈  Diagram",         "chart"),
            ("🤖  AI Advisor",      "ai"),
            ("⚙️  Pengaturan",      "settings"),
        ]
        self.nav_btns = {}
        for label, key in nav_items:
            btn = ctk.CTkButton(sb, text=label, anchor="w",
                                height=46, font=FONT_BODY,
                                fg_color="transparent",
                                text_color=COLORS["text_secondary"],
                                hover_color=COLORS["hover"],
                                corner_radius=10,
                                command=lambda k=key: self._nav(k))
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_btns[key] = btn

        # Logout
        ctk.CTkFrame(sb, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(20, 0))
        ctk.CTkButton(sb, text="🚪  Keluar", anchor="w",
                      height=46, font=FONT_BODY,
                      fg_color="transparent",
                      text_color=COLORS["accent_red"],
                      hover_color=COLORS["hover"],
                      corner_radius=10,
                      command=self.on_logout).pack(fill="x", padx=12, pady=8)

    def _nav(self, key):
        for k, b in self.nav_btns.items():
            b.configure(fg_color=COLORS["accent_blue"] if k == key else "transparent",
                        text_color=COLORS["text_primary"] if k == key else COLORS["text_secondary"])
        for w in self.content.winfo_children():
            w.destroy()
        {"overview": self._show_overview,
         "transactions": self._show_transactions,
         "chart": self._show_chart,
         "ai": self._show_ai,
         "settings": self._show_settings}[key]()

    # ── Load Data ─────────────────────────────────────────────────────────────
    def _load_transactions(self):
        self.transactions = self.db.get_transactions(self.user["username"])

    def _totals(self):
        inc = sum(t["amount"] for t in self.transactions if t["type"] == "Pemasukan")
        exp = sum(t["amount"] for t in self.transactions if t["type"] == "Pengeluaran")
        return inc, exp, inc - exp

    # ── OVERVIEW ──────────────────────────────────────────────────────────────
    def _show_overview(self):
        c = self.content
        inc, exp, net = self._totals()
        is_biz = self.user["acc_type"] == "badan_usaha"

        # Page title
        title_f = ctk.CTkFrame(c, fg_color="transparent")
        title_f.pack(fill="x", padx=24, pady=(24, 0))
        ctk.CTkLabel(title_f, text="📊 Dashboard Overview",
                     font=FONT_HEAD, text_color=COLORS["text_primary"]).pack(side="left")
        date_s = datetime.datetime.now().strftime("%d %B %Y")
        ctk.CTkLabel(title_f, text=date_s, font=FONT_SMALL,
                     text_color=COLORS["text_muted"]).pack(side="right")

        # KPI Cards
        kpi_f = ctk.CTkFrame(c, fg_color="transparent")
        kpi_f.pack(fill="x", padx=24, pady=16)
        kpi_f.columnconfigure((0, 1, 2), weight=1)

        label1 = "Total Pendapatan" if not is_biz else "Total Omzet"
        label2 = "Total Pengeluaran" if not is_biz else "Total Biaya Operasional"
        label3 = "Saldo Bersih" if not is_biz else "Laba Bersih"

        cards = [
            (label1, fmt_currency(inc), "📈", COLORS["accent_green"], 0),
            (label2, fmt_currency(exp), "📉", COLORS["accent_red"],   1),
            (label3, fmt_currency(net), "💰", COLORS["accent_blue"],  2),
        ]
        for label, val, ico, color, col in cards:
            frame = ctk.CTkFrame(kpi_f, fg_color=COLORS["bg_card"],
                                 corner_radius=16)
            frame.grid(row=0, column=col, padx=6, pady=6, sticky="ew")
            ctk.CTkLabel(frame, text=ico, font=("Trebuchet MS", 32)).pack(pady=(20, 4))
            ctk.CTkLabel(frame, text=label, font=FONT_SMALL,
                         text_color=COLORS["text_secondary"]).pack()
            ctk.CTkLabel(frame, text=val, font=("Trebuchet MS", 17, "bold"),
                         text_color=color).pack(pady=(4, 20))

        # ── Mini Chart ────────────────────────────────────────────────────────
        self._render_mini_chart(c)

        # ── Recent Transactions ───────────────────────────────────────────────
        rec_f = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=16)
        rec_f.pack(fill="x", padx=24, pady=(8, 24))
        hdr = ctk.CTkFrame(rec_f, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(hdr, text="Transaksi Terakhir",
                     font=FONT_SUB, text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkButton(hdr, text="+ Tambah", height=32, font=FONT_SMALL,
                      fg_color=COLORS["accent_blue"], corner_radius=8,
                      command=self._add_transaction).pack(side="right")

        recent = self.transactions[-8:][::-1]
        if not recent:
            ctk.CTkLabel(rec_f, text="Belum ada transaksi. Tambahkan yang pertama!",
                         font=FONT_BODY, text_color=COLORS["text_muted"]).pack(pady=24)
        else:
            for t in recent:
                self._render_tx_row(rec_f, t)
        ctk.CTkFrame(rec_f, height=1, fg_color="transparent").pack(pady=8)

    def _render_mini_chart(self, parent):
        if not self.transactions:
            return
        chart_card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=16)
        chart_card.pack(fill="x", padx=24, pady=(0, 8))
        ctk.CTkLabel(chart_card, text="Tren 6 Bulan Terakhir",
                     font=FONT_SUB, text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(16, 4))

        months = {}
        for t in self.transactions:
            m = t["date"][:7]
            if m not in months:
                months[m] = {"Pemasukan": 0, "Pengeluaran": 0}
            months[m][t["type"]] += t["amount"]

        keys = sorted(months.keys())[-6:]
        inc_v = [months[k]["Pemasukan"] / 1e6 for k in keys]
        exp_v = [months[k]["Pengeluaran"] / 1e6 for k in keys]
        labels = [k[5:] + "/" + k[2:4] for k in keys]

        fig = Figure(figsize=(8, 2.6), facecolor=COLORS["bg_card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["bg_card"])
        x = range(len(keys))
        ax.bar([i - 0.2 for i in x], inc_v, 0.38, color=COLORS["accent_green"], alpha=0.85, label="Pemasukan")
        ax.bar([i + 0.2 for i in x], exp_v, 0.38, color=COLORS["accent_red"],   alpha=0.85, label="Pengeluaran")
        ax.set_xticks(list(x)); ax.set_xticklabels(labels, color=COLORS["text_secondary"], fontsize=9)
        ax.tick_params(colors=COLORS["text_muted"])
        ax.spines[:].set_color(COLORS["border"])
        ax.set_ylabel("Juta (Rp)", color=COLORS["text_secondary"], fontsize=9)
        ax.legend(facecolor=COLORS["bg_card2"], edgecolor=COLORS["border"],
                  labelcolor=COLORS["text_primary"], fontsize=9)
        fig.tight_layout(pad=1.2)

        canvas = FigureCanvasTkAgg(fig, chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=16, pady=(0, 16))

    def _render_tx_row(self, parent, t):
        row = ctk.CTkFrame(parent, fg_color=COLORS["bg_card2"], corner_radius=10)
        row.pack(fill="x", padx=16, pady=3)
        row.columnconfigure(1, weight=1)

        color = COLORS["accent_green"] if t["type"] == "Pemasukan" else COLORS["accent_red"]
        sign  = "+" if t["type"] == "Pemasukan" else "-"

        icon_bg = ctk.CTkFrame(row, fg_color=color, width=36, height=36, corner_radius=8)
        icon_bg.grid(row=0, column=0, padx=(12, 10), pady=10)
        icon_bg.grid_propagate(False)
        ctk.CTkLabel(icon_bg, text="↑" if t["type"] == "Pemasukan" else "↓",
                     font=("Trebuchet MS", 16, "bold"),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(info, text=t["category"], font=FONT_BODY,
                     text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(info, text=f"{t['description']}  •  {t['date']}",
                     font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(anchor="w")

        ctk.CTkLabel(row, text=f"{sign}{fmt_currency(t['amount'])}",
                     font=("Trebuchet MS", 14, "bold"),
                     text_color=color).grid(row=0, column=2, padx=16)

    # ── TRANSACTIONS ──────────────────────────────────────────────────────────
    def _show_transactions(self):
        c = self.content
        is_biz = self.user["acc_type"] == "badan_usaha"

        hdr = ctk.CTkFrame(c, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 0))
        title_txt = "💳 Transaksi Bisnis" if is_biz else "💳 Transaksi Pribadi"
        ctk.CTkLabel(hdr, text=title_txt, font=FONT_HEAD,
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkButton(hdr, text="+ Tambah Transaksi", height=40, font=FONT_BODY,
                      fg_color=COLORS["accent_blue"], corner_radius=10,
                      command=self._add_transaction).pack(side="right")

        # Filter bar
        filter_f = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=12)
        filter_f.pack(fill="x", padx=24, pady=12)
        self.filter_var = ctk.StringVar(value="Semua")
        for opt in ["Semua", "Pemasukan", "Pengeluaran"]:
            clr = {"Semua": COLORS["accent_blue"],
                   "Pemasukan": COLORS["accent_green"],
                   "Pengeluaran": COLORS["accent_red"]}[opt]
            ctk.CTkRadioButton(filter_f, text=opt, variable=self.filter_var,
                               value=opt, font=FONT_BODY,
                               text_color=COLORS["text_primary"],
                               fg_color=clr,
                               command=lambda: self._show_transactions()
                               ).pack(side="left", padx=20, pady=10)

        # Table header
        th = ctk.CTkFrame(c, fg_color=COLORS["bg_card2"], corner_radius=10)
        th.pack(fill="x", padx=24, pady=(4, 0))
        for col, w, txt in [(0, 120, "TANGGAL"), (1, 160, "KATEGORI"),
                             (2, 200, "DESKRIPSI"), (3, 120, "JUMLAH"), (4, 80, "JENIS")]:
            th.columnconfigure(col, weight=1)
            ctk.CTkLabel(th, text=txt, font=FONT_SMALL,
                         text_color=COLORS["text_muted"]).grid(row=0, column=col, padx=12, pady=8, sticky="w")

        filt = self.filter_var.get()
        shown = [t for t in self.transactions
                 if filt == "Semua" or t["type"] == filt][::-1]

        if not shown:
            ctk.CTkLabel(c, text="Tidak ada transaksi yang cocok.",
                         font=FONT_BODY, text_color=COLORS["text_muted"]).pack(pady=24)
            return

        for t in shown:
            row = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=8)
            row.pack(fill="x", padx=24, pady=2)
            for col in range(5): row.columnconfigure(col, weight=1)
            color = COLORS["accent_green"] if t["type"] == "Pemasukan" else COLORS["accent_red"]
            sign  = "+" if t["type"] == "Pemasukan" else "-"
            data  = [t["date"], t["category"], t["description"],
                     f"{sign}{fmt_currency(t['amount'])}", t["type"]]
            cols  = [COLORS["text_muted"], COLORS["text_primary"],
                     COLORS["text_secondary"], color, color]
            for idx, (val, clr) in enumerate(zip(data, cols)):
                ctk.CTkLabel(row, text=val, font=FONT_SMALL,
                             text_color=clr).grid(row=0, column=idx,
                                                   padx=12, pady=10, sticky="w")

    # ── CHART ─────────────────────────────────────────────────────────────────
    def _show_chart(self):
        c = self.content
        inc, exp, net = self._totals()
        is_biz = self.user["acc_type"] == "badan_usaha"

        ctk.CTkLabel(c, text="📈 Analisis Diagram Keuangan",
                     font=FONT_HEAD, text_color=COLORS["text_primary"]).pack(anchor="w", padx=24, pady=(24, 16))

        if not self.transactions:
            ctk.CTkLabel(c, text="Belum ada data transaksi untuk ditampilkan.",
                         font=FONT_BODY, text_color=COLORS["text_muted"]).pack(pady=40)
            return

        # ── Row 1: pie charts ──
        row1 = ctk.CTkFrame(c, fg_color="transparent")
        row1.pack(fill="x", padx=24, pady=(0, 16))
        row1.columnconfigure((0, 1), weight=1)

        for col, ttype, title_txt in [
            (0, "Pengeluaran", "Komposisi Pengeluaran"),
            (1, "Pemasukan",  "Komposisi Pemasukan"),
        ]:
            card = ctk.CTkFrame(row1, fg_color=COLORS["bg_card"], corner_radius=16)
            card.grid(row=0, column=col, padx=6, sticky="nsew")
            ctk.CTkLabel(card, text=title_txt, font=FONT_SUB,
                         text_color=COLORS["text_primary"]).pack(pady=(16, 4))

            cat_data = {}
            for t in self.transactions:
                if t["type"] == ttype:
                    cat_data[t["category"]] = cat_data.get(t["category"], 0) + t["amount"]

            if not cat_data:
                ctk.CTkLabel(card, text="Tidak ada data",
                             font=FONT_SMALL, text_color=COLORS["text_muted"]).pack(pady=30)
                continue

            palette = [COLORS["accent_blue"], COLORS["accent_cyan"], COLORS["accent_green"],
                       COLORS["accent_orange"], COLORS["accent_purple"],
                       "#EC4899", "#F97316", "#84CC16"]

            fig = Figure(figsize=(4, 3.2), facecolor=COLORS["bg_card"])
            ax  = fig.add_subplot(111)
            ax.set_facecolor(COLORS["bg_card"])
            wedges, texts, autotexts = ax.pie(
                cat_data.values(), labels=cat_data.keys(),
                colors=palette[:len(cat_data)],
                autopct="%1.1f%%", startangle=140,
                wedgeprops={"edgecolor": COLORS["bg_card"], "linewidth": 2},
                textprops={"color": COLORS["text_secondary"], "fontsize": 8},
            )
            for at in autotexts:
                at.set_color(COLORS["text_primary"]); at.set_fontsize(8)
            fig.tight_layout(pad=1)
            canvas = FigureCanvasTkAgg(fig, card)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", padx=12, pady=(0, 16))

        # ── Row 2: monthly bar ──
        card2 = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=16)
        card2.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(card2, text="Perbandingan Bulanan: Pemasukan vs Pengeluaran",
                     font=FONT_SUB, text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(16, 4))

        months = {}
        for t in self.transactions:
            m = t["date"][:7]
            if m not in months: months[m] = {"Pemasukan": 0, "Pengeluaran": 0}
            months[m][t["type"]] += t["amount"]

        keys   = sorted(months.keys())
        inc_v  = [months[k]["Pemasukan"] / 1e6 for k in keys]
        exp_v  = [months[k]["Pengeluaran"] / 1e6 for k in keys]
        labels = [k[5:] + "/" + k[2:4] for k in keys]

        fig2 = Figure(figsize=(9, 3.2), facecolor=COLORS["bg_card"])
        ax2  = fig2.add_subplot(111)
        ax2.set_facecolor(COLORS["bg_card"])
        x = list(range(len(keys)))
        ax2.bar([i - 0.22 for i in x], inc_v, 0.42, color=COLORS["accent_green"], alpha=0.88, label="Pemasukan")
        ax2.bar([i + 0.22 for i in x], exp_v, 0.42, color=COLORS["accent_red"],   alpha=0.88, label="Pengeluaran")
        ax2.set_xticks(x); ax2.set_xticklabels(labels, color=COLORS["text_secondary"], fontsize=9)
        ax2.tick_params(colors=COLORS["text_muted"])
        ax2.spines[:].set_color(COLORS["border"])
        ax2.set_ylabel("Juta (Rp)", color=COLORS["text_secondary"])
        ax2.legend(facecolor=COLORS["bg_card2"], edgecolor=COLORS["border"],
                   labelcolor=COLORS["text_primary"], fontsize=10)
        fig2.tight_layout(pad=1.2)

        canvas2 = FigureCanvasTkAgg(fig2, card2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="x", padx=16, pady=(0, 16))

        # ── Row 3: cumulative net ──
        card3 = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=16)
        card3.pack(fill="x", padx=24, pady=(0, 24))
        label3 = "Pertumbuhan Aset Bersih" if not is_biz else "Tren Laba Kumulatif"
        ctk.CTkLabel(card3, text=label3, font=FONT_SUB,
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(16, 4))

        net_v = [(iv - ev) for iv, ev in zip(inc_v, exp_v)]
        cum   = []
        s = 0
        for v in net_v:
            s += v; cum.append(s)

        fig3 = Figure(figsize=(9, 2.8), facecolor=COLORS["bg_card"])
        ax3  = fig3.add_subplot(111)
        ax3.set_facecolor(COLORS["bg_card"])
        clr_line = COLORS["accent_cyan"]
        ax3.plot(x, cum, color=clr_line, linewidth=2.5, marker="o", markersize=5)
        ax3.fill_between(x, cum, alpha=0.15, color=clr_line)
        ax3.set_xticks(x); ax3.set_xticklabels(labels, color=COLORS["text_secondary"], fontsize=9)
        ax3.tick_params(colors=COLORS["text_muted"])
        ax3.spines[:].set_color(COLORS["border"])
        ax3.set_ylabel("Juta (Rp)", color=COLORS["text_secondary"])
        ax3.axhline(0, color=COLORS["text_muted"], linewidth=0.8, linestyle="--")
        fig3.tight_layout(pad=1.2)
        canvas3 = FigureCanvasTkAgg(fig3, card3)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="x", padx=16, pady=(0, 16))

    # ── AI ADVISOR ────────────────────────────────────────────────────────────
    def _show_ai(self):
        c = self.content
        ctk.CTkLabel(c, text="🤖 AI Financial Advisor",
                     font=FONT_HEAD, text_color=COLORS["text_primary"]).pack(anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(c, text="Tanyakan apa saja tentang keuangan Anda kepada AI!",
                     font=FONT_SMALL, text_color=COLORS["text_secondary"]).pack(anchor="w", padx=24, pady=(0, 12))

        if not self.ai_model:
            warn = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=12)
            warn.pack(fill="x", padx=24, pady=8)
            ctk.CTkLabel(warn, text="⚠️  API Key Gemini belum dikonfigurasi.",
                         font=FONT_BODY, text_color=COLORS["accent_orange"]).pack(pady=(16, 4))
            ctk.CTkLabel(warn, text="Masuk ke menu Pengaturan untuk menambahkan API Key.",
                         font=FONT_SMALL, text_color=COLORS["text_secondary"]).pack(pady=(0, 16))
            ctk.CTkButton(warn, text="⚙️ Ke Pengaturan", height=40, font=FONT_BODY,
                          fg_color=COLORS["accent_orange"], hover_color="#D97706",
                          corner_radius=10, command=lambda: self._nav("settings")).pack(pady=(0, 16))
            return

        # Chat area
        self.chat_box = ctk.CTkScrollableFrame(c, fg_color=COLORS["bg_card"],
                                               corner_radius=16, height=380)
        self.chat_box.pack(fill="x", padx=24, pady=(0, 8))
        self.chat_box.columnconfigure(0, weight=1)

        # Quick prompts
        qp_f = ctk.CTkFrame(c, fg_color="transparent")
        qp_f.pack(fill="x", padx=24, pady=(0, 8))
        is_biz = self.user["acc_type"] == "badan_usaha"
        quick = (["Analisa keuangan bisnis saya", "Tips efisiensi biaya operasional",
                  "Strategi meningkatkan profit", "Cara manajemen arus kas"]
                 if is_biz else
                 ["Analisa keuangan saya bulan ini", "Tips hemat pengeluaran",
                  "Cara investasi yang aman", "Bagaimana meningkatkan tabungan?"])
        for q in quick:
            ctk.CTkButton(qp_f, text=q, height=32, font=FONT_SMALL,
                          fg_color=COLORS["bg_card2"], text_color=COLORS["accent_cyan"],
                          hover_color=COLORS["hover"], corner_radius=20,
                          command=lambda q=q: self._send_ai(q)).pack(side="left", padx=4, pady=4)

        # Input
        inp_f = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=12)
        inp_f.pack(fill="x", padx=24, pady=(0, 24))
        self.ai_input = ctk.CTkEntry(inp_f, height=48, font=FONT_BODY,
                                     placeholder_text="Tulis pertanyaan keuangan Anda...",
                                     fg_color=COLORS["bg_primary"],
                                     border_color=COLORS["border"],
                                     text_color=COLORS["text_primary"])
        self.ai_input.pack(side="left", fill="x", expand=True, padx=12, pady=12)
        self.ai_input.bind("<Return>", lambda e: self._send_ai())
        ctk.CTkButton(inp_f, text="Kirim ➤", height=40, font=FONT_BODY,
                      fg_color=COLORS["accent_blue"], hover_color="#2563EB",
                      corner_radius=10, command=self._send_ai).pack(side="right", padx=12)

        # Show existing chat
        for role, msg in self.chat_hist:
            self._render_chat_bubble(role, msg)

    def _send_ai(self, preset=None):
        if not self.ai_client: return
        msg = preset or self.ai_input.get().strip()
        if not msg: return
        if hasattr(self, "ai_input"): self.ai_input.delete(0, "end")

        self.chat_hist.append(("user", msg))
        self._render_chat_bubble("user", msg)

        inc, exp, net = self._totals()
        is_biz = self.user["acc_type"] == "badan_usaha"
        ctx = (f"Anda adalah AI Financial Advisor profesional untuk {'badan usaha' if is_biz else 'keuangan pribadi'}. "
               f"Data keuangan user: Pemasukan Rp {inc:,.0f}, Pengeluaran Rp {exp:,.0f}, "
               f"Saldo Bersih Rp {net:,.0f}. "
               f"Berikan jawaban dalam Bahasa Indonesia yang jelas, praktis, dan mudah dipahami. "
               f"Jawab pertanyaan: {msg}")

        thinking = ctk.CTkLabel(self.chat_box,
                                text="🤖 AI sedang berpikir...",
                                font=FONT_SMALL, text_color=COLORS["text_muted"],
                                wraplength=500)
        thinking.grid(sticky="w", padx=12, pady=4)

        def worker():
            try:
                resp = self.ai_client.models.generate_content(
                    model="models/gemini-2.5-flash",
                    contents=ctx
                )
                answer = resp.text
            except Exception as e:
                answer = f"⚠️ Error: {e}"
            self.after(0, lambda: (thinking.destroy(),
                                   self.chat_hist.append(("ai", answer)),
                                   self._render_chat_bubble("ai", answer)))


        threading.Thread(target=worker, daemon=True).start()

    def _render_chat_bubble(self, role, msg):
        if not hasattr(self, "chat_box"): return
        is_user = role == "user"
        bubble = ctk.CTkFrame(self.chat_box,
                              fg_color=COLORS["accent_blue"] if is_user else COLORS["bg_card2"],
                              corner_radius=14)
        bubble.grid(sticky="e" if is_user else "w", padx=12, pady=4,
                    ipadx=6, ipady=6)
        prefix = "Anda: " if is_user else "🤖 AI: "
        ctk.CTkLabel(bubble, text=prefix + msg, wraplength=480, justify="left",
                     font=FONT_BODY, text_color=COLORS["text_primary"]).pack(padx=12, pady=8)

    # ── SETTINGS ──────────────────────────────────────────────────────────────
    def _show_settings(self):
        c = self.content
        ctk.CTkLabel(c, text="⚙️ Pengaturan",
                     font=FONT_HEAD, text_color=COLORS["text_primary"]).pack(anchor="w", padx=24, pady=(24, 16))

        # API Key section
        card = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=16)
        card.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(card, text="🔑  Konfigurasi Gemini API Key",
                     font=FONT_SUB, text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(card, text="Dapatkan API Key gratis di: https://aistudio.google.com",
                     font=FONT_SMALL, text_color=COLORS["accent_cyan"]).pack(anchor="w", padx=20, pady=(0, 12))

        current = self.db.get_api_key(self.user["username"]) or ""
        masked  = ("●" * (len(current) - 4) + current[-4:]) if len(current) > 4 else current

        ef = ctk.CTkFrame(card, fg_color="transparent")
        ef.pack(fill="x", padx=20, pady=(0, 16))
        self.api_entry = ctk.CTkEntry(ef, height=46, font=FONT_MONO,
                                      placeholder_text="Masukkan Gemini API Key baru...",
                                      fg_color=COLORS["bg_primary"],
                                      border_color=COLORS["border"],
                                      text_color=COLORS["text_primary"])
        if masked: self.api_entry.insert(0, masked)
        self.api_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.api_status = ctk.CTkLabel(ef, text="", font=FONT_SMALL)
        self.api_status.pack(side="left")

        ctk.CTkButton(card, text="Simpan API Key", height=44, font=FONT_BODY,
                      fg_color=COLORS["accent_green"], hover_color="#059669",
                      corner_radius=10, command=self._save_api).pack(padx=20, pady=(0, 20), anchor="w")

        # Profile info
        p_card = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=16)
        p_card.pack(fill="x", padx=24, pady=(0, 24))
        ctk.CTkLabel(p_card, text="👤  Informasi Akun",
                     font=FONT_SUB, text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(20, 12))

        at = "Akun Pribadi 👤" if self.user["acc_type"] == "pribadi" else "Badan Usaha 🏢"
        for label, val in [("Nama", self.user["name"]),
                            ("Username", self.user["username"]),
                            ("Jenis Akun", at)]:
            row = ctk.CTkFrame(p_card, fg_color=COLORS["bg_card2"], corner_radius=8)
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text=label, font=FONT_SMALL,
                         text_color=COLORS["text_muted"], width=120).pack(side="left", padx=12, pady=10)
            ctk.CTkLabel(row, text=val, font=FONT_BODY,
                         text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkFrame(p_card, height=1, fg_color="transparent").pack(pady=8)

    def _save_api(self):
        key = self.api_entry.get().strip()
        if not key or "●" in key:
            self.api_status.configure(text="⚠ Masukkan API key baru", text_color=COLORS["accent_orange"])
            return
        try:
            client = genai.Client(api_key=key)
            self.db.save_api_key(self.user["username"], key)
            self.ai_client = client
            self.ai_model  = client
            self.api_status.configure(text="✓ Tersimpan!", text_color=COLORS["accent_green"])
        except Exception as e:
            err_str = str(e)
            err_msg = err_str[:80] + ("..." if len(err_str) > 80 else "")
            self.api_status.configure(text=f"✗ {err_msg}", text_color=COLORS["accent_red"])
    # ── Add Transaction ────────────────────────────────────────────────────────
    def _add_transaction(self):
        def on_save(tx):
            self.db.add_transaction(self.user["username"], tx)
            self._load_transactions()
            self._nav("overview")
        TransactionDialog(self, self.user["acc_type"], on_save)


# ══════════════════════════════════════════════════════════════════════════════
#  APP ROOT
# ══════════════════════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FinanceAI — AI-Powered Financial Advisor")
        self.geometry("1200x780")
        self.minsize(1000, 680)
        self.configure(fg_color=COLORS["bg_primary"])

        self.db = Database()
        self._current_page = None
        self._show_login()

    def _clear(self):
        if self._current_page:
            self._current_page.destroy()

    def _show_login(self):
        self._clear()
        page = LoginPage(self, self._do_login, self._show_register)
        page.pack(fill="both", expand=True)
        self._current_page = page

    def _show_register(self):
        self._clear()
        page = RegisterPage(self, self._do_register, self._show_login)
        page.pack(fill="both", expand=True)
        self._current_page = page

    def _show_dashboard(self, user):
        self._clear()
        page = Dashboard(self, user, self.db, self._show_login)
        page.pack(fill="both", expand=True)
        page._nav("overview")
        self._current_page = page

    def _do_login(self, username, password, err_lbl):
        user = self.db.get_user(username)
        if not user or user["password"] != hash_password(password):
            err_lbl.configure(text="⚠ Username atau password salah")
            return
        self._show_dashboard(user)

    def _do_register(self, name, username, password, acc_type, err_lbl):
        if self.db.get_user(username):
            err_lbl.configure(text="⚠ Username sudah digunakan"); return
        self.db.create_user(name, username, hash_password(password), acc_type)
        user = self.db.get_user(username)
        self._show_dashboard(user)


if __name__ == "__main__":
    app = App()
    app.mainloop()