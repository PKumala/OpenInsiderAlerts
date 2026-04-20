# 📊 OpenInsider Alerts

> Real-time monitoring and analysis tool for **insider trading transactions** on the US stock market.  
> Tracks capital movements of corporate executives (purchases/sales) and filters high-volume transactions worth watching.

---

## 🔍 What it does

Corporate insiders (CEOs, CFOs, Directors) are required by law to report their stock transactions to the SEC. This tool:

- **Scrapes** the [OpenInsider](http://openinsider.com) database in real time
- **Filters** transactions by volume, transaction type, and company
- **Displays** results in a clean, readable frontend dashboard
- **Monitors** the market continuously with built-in fault tolerance

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, BeautifulSoup4, Requests |
| Frontend | HTML, CSS, JavaScript |
| Infrastructure | Docker, Docker Compose |

---

## 🏗️ Architecture

```
OpenInsiderAlerts/
├── backend/          # Python scraper & data processing logic
├── frontend/         # HTML/JS dashboard
├── docker/           # Docker configuration files
├── Dockerfile
└── docker-compose.yml
```

---

## ✨ Key Features

### 🕷️ Web Scraping
HTML table parser built with **BeautifulSoup4** and **Requests** that extracts data on capital movements by corporate management. Targets transaction type, trade date, company ticker, insider name, role, and transaction value.

### 🧹 Data Engineering
Raw text data cleaning pipeline that converts string values to numeric formats — enabling filtering by transaction volume, percentage ownership change, and trade size. Strips noise and normalizes inconsistent source formatting.

### 🔁 Stability & Fault Tolerance
- **User-Agent header rotation** to avoid request blocking
- **Network error handling** with retry logic for uninterrupted market monitoring
- Graceful degradation — the scraper keeps running even if individual requests fail

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose installed

### Run with Docker

```bash
git clone https://github.com/PKumala/OpenInsiderAlerts.git
cd OpenInsiderAlerts
docker-compose up --build
```

The app will be available at `http://localhost:PORT` *(update with your actual port)*.

### Run locally (without Docker)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

---

## 📌 Use Case

This tool is useful for investors and analysts who want to follow the **"smart money"** — tracking when company insiders make large purchases of their own stock, which is often considered a bullish signal.

Example filters:
- Transactions over $1,000,000
- Purchases only (excluding option exercises)
- Specific companies or sectors

---

## 📄 License

This project is for educational and personal use only. Data sourced from publicly available SEC filings via [openinsider.com](http://openinsider.com).
