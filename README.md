# 💎 AI Finance Advisor — Manajemen Keuangan Cerdas Berbasis AI

Aplikasi manajemen keuangan personal & bisnis modern berbasis web dengan integrasi AI Gemini untuk konsultasi keuangan cerdas.

**🌟 Versi Web Terbaru - Modern UI dengan Tailwind CSS & Chart.js**

---

## 🎯 Fitur Unggulan

| Fitur | Deskripsi |
|---|---|
| 🔐 **Autentikasi Aman** | Login/Register dengan JWT & password hashing |
| 👤 / 🏢 **Dual Account** | Akun pribadi atau badan usaha dengan kategori berbeda |
| 📊 **Dashboard Interaktif** | Visualisasi real-time dengan Chart.js |
| 💳 **Manajemen Transaksi** | CRUD transaksi dengan filter & sorting |
| 📈 **Analitik Lengkap** | Laporan bulanan, tren, breakdown kategori |
| 🤖 **AI Advisor** | Chat dengan Gemini AI untuk saran keuangan |
| 🎨 **UI Modern** | Dark theme gradient dengan Tailwind CSS |
| 📱 **Responsive Design** | Mobile-friendly interface |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Modern web browser
- Gemini API Key (gratis)

### Setup (5 menit)

```bash
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Initialize database
python init_db.py

# 3. Jalankan aplikasi
python app.py

# 4. Buka browser
# http://localhost:5000
```

**Demo Account:**
- Email: `demo@example.com`
- Password: `demo123`

Dokumentasi lengkap: [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## 🏗 Tech Stack

```
Backend        Frontend         Database       AI
├─ Flask       ├─ HTML5         ├─ SQLite      └─ Google
├─ SQLAlchemy  ├─ Tailwind CSS  └─ SQLAlchemy     Gemini
└─ JWT         └─ Chart.js                         API
```

---

## 📋 Kategori Transaksi

### Akun Pribadi 👤
**Pemasukan:** Gaji, Freelance, Investasi, Hadiah, Lainnya
**Pengeluaran:** Makanan, Transportasi, Kesehatan, Hiburan, Belanja, Tagihan, Pendidikan, Lainnya

### Badan Usaha 🏢
**Pemasukan:** Penjualan, Jasa, Investasi, Pinjaman, Lainnya
**Pengeluaran:** Gaji Karyawan, Operasional, Bahan Baku, Marketing, Sewa, Pajak, Utilitas, Lainnya

---

## 📁 Struktur Project

```
AI Advisor/
├── app.py                   # Flask + API endpoints
├── init_db.py              # Database initialization
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── SETUP_GUIDE.md        # Installation guide
│
├── templates/            # HTML pages
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── transactions.html
│   ├── advisor.html
│   └── settings.html
│
└── static/              # Assets
    ├── css/style.css
    └── js/
        ├── app.js
        └── api.js
```

---

## 🔑 Setup Gemini API Key

1. Kunjungi: https://aistudio.google.com
2. Klik **Get API Key** → **Create API key**
3. Copy API key
4. Login aplikasi → **Pengaturan** → Paste key → **Simpan**

---

## 🎨 Design Features

✨ **Modern Aesthetic**
- Dark theme dengan gradient purple-pink
- Backdrop blur effects
- Smooth animations & transitions
- Responsive grid layout

📊 **Data Visualization**
- Doughnut chart (Income vs Expense)
- Line chart (12-month trend)
- Category breakdown
- KPI cards dengan icons

🔤 **Typography**
- Headers: Bold & readable (24px-48px)
- Body: Medium (16px)
- Labels: Clear & contrasted (14px)

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Daftar user baru
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Info user current

### Transactions
- `GET /api/transactions` - List transaksi
- `POST /api/transactions` - Tambah transaksi
- `PUT /api/transactions/<id>` - Update transaksi
- `DELETE /api/transactions/<id>` - Hapus transaksi

### Metrics
- `GET /api/metrics/summary` - Ringkasan keuangan
- `GET /api/metrics/category-breakdown` - Breakdown kategori
- `GET /api/metrics/monthly-trend` - Tren 12 bulan

### AI Advisor
- `POST /api/advisor/advice` - Dapatkan saran keuangan

---

## 🔒 Security

✅ Password hashing dengan werkzeug
✅ JWT authentication
✅ SQLAlchemy ORM (SQL injection prevention)
✅ CORS protection
✅ API key encryption

---

## 📚 Dokumentasi

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Installation & running guide
- **[README-WEB.md](README-WEB.md)** - Web app documentation
- **app.py** - API documentation & comments

---

## 🐛 Troubleshooting

```bash
# Python not found
→ Pastikan Python installed & added to PATH

# Port 5000 in use
→ Gunakan port lain atau close aplikasi lain

# Database error
→ Delete finance_advisor.db & run init_db.py lagi

# Module not found
→ pip install -r requirements.txt --force-reinstall
```

---

## 🚀 Deployment

Production checklist:
- [ ] Change JWT_SECRET_KEY
- [ ] Use PostgreSQL database
- [ ] Enable HTTPS
- [ ] Set FLASK_ENV=production
- [ ] Disable DEBUG mode
- [ ] Configure proper CORS origins
- [ ] Setup rate limiting

---

## 📝 Development Notes

### File-file Penting
- `app.py` - Main Flask app dengan semua API endpoints
- `init_db.py` - Database setup dengan demo data
- `templates/*.html` - UI pages (Tailwind CSS)
- `static/js/app.js` - Frontend logic

### Environment Variables
```bash
FLASK_ENV=development
DEBUG=True
JWT_SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-api-key
```

---

## 🤝 Kontribusi

Kontribusi welcome! Silakan:
1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Open Pull Request

---

## 📄 License

MIT License - Bebas digunakan untuk keperluan komersial & non-komersial.

---

**Dikembangkan dengan ❤️ untuk membantu Anda mengelola keuangan dengan cerdas menggunakan AI.**

**Versi:** 2.0 (Web-based)
**Updated:** Juni 2026
