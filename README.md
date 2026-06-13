---
# Binance Futures Testnet Trading Bot

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Binance](https://img.shields.io/badge/Binance-Futures_Testnet-F0B90B?style=for-the-badge&logo=binance&logoColor=black)
![Typer](https://img.shields.io/badge/CLI-Typer-009688?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A clean Python CLI tool for placing LIMIT and MARKET futures orders on the Binance Testnet. Built with a modular architecture, structured logging, and environment-based credential management. Safe: testnet only — no real funds at risk.

---

## What It Does

Places LIMIT and MARKET orders on `testnet.binancefuture.com` via Binance REST API. Every order is signed with HMAC-SHA256, logged to `logs/`, and printed to the terminal with a clean summary. Designed for learning API integration, order mechanics, and data engineering with live(ish) market data.

---

## Architecture

```
cli.py (Typer CLI entry point)
   │
   ├── bot/validators.py    → Input validation (symbol, side, quantity, price)
   ├── bot/client.py        → Binance API client (auth, signing, requests)
   ├── bot/orders.py        → Order placement logic (MARKET / LIMIT)
   └── bot/logging_config.py → Structured logger setup
         │
         ▼
   logs/market_order.log
   logs/limit_order.log
```

---

## Quickstart

```bash
# Clone and setup
git clone https://github.com/Abhinay6699/trading_bot.git
cd trading_bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env → add your Binance Testnet API key and secret
# Get keys at: https://testnet.binancefuture.com
```

---

## Usage

**MARKET Buy — Buy 0.01 BTC at current price:**
```bash
python3 cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
```
```
✅  Order placed successfully
─────────────────────────────────────
orderId     : 13036508623
status      : NEW
executedQty : 0.0000
avgPrice    : 0.00
```

**LIMIT Buy — Buy 0.01 BTC at $65,000:**
```bash
python3 cli.py --symbol BTCUSDT --side BUY --type LIMIT --qty 0.01 --price 65000
```

**LIMIT Sell — Sell 0.01 BTC at $80,000 (take profit):**
```bash
python3 cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.01 --price 80000
```

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── client.py          # Binance API client (auth, signing, HTTP)
│   ├── orders.py          # Order placement (MARKET / LIMIT)
│   ├── validators.py      # Input validation
│   ├── logging_config.py  # Structured logging setup
│   └── __init__.py
├── logs/
│   ├── market_order.log
│   └── limit_order.log
├── cli.py                 # Typer CLI entry point
├── .env.example           # Credential template
├── requirements.txt
└── README.md
```

---

## Design Notes

- **Testnet only**: Hardcoded to `testnet.binancefuture.com` — no accidental real-money orders
- **HMAC-SHA256 signing**: All requests are properly signed per Binance API spec
- **System clock sync**: API signatures require accurate system time — bot assumes this
- **Manual invocation**: No background daemon loop — each order is a deliberate CLI call
- **Structured logs**: All orders logged with timestamp, symbol, side, type, quantity, price, and order ID

---

## What I Learned Building This

Financial data is not clean. Market data has gaps, timestamps drift, and exchanges have downtime. Working with a live-feed API — even testnet — teaches data engineering discipline that no Kaggle dataset does: error handling is not optional, latency matters, and every request can fail.

---

## Tech Stack

- **Language**: Python 3.9+
- **CLI**: Typer
- **API Client**: requests + HMAC-SHA256 signing
- **Config**: python-dotenv
- **Logging**: Python logging module (file + console handlers)
---
