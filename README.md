# Binance Futures Testnet Trading Bot
A Python CLI trading bot designed to securely place LIMIT and MARKET orders on the Binance Futures Testnet.

## Prerequisites
- Python 3.9+
- Activated Binance Demo Trading Futures API keys

## Setup steps
1. Clone the repository: `git clone https://github.com/Abhinay6699/trading_bot.git && cd trading_bot`
2. Create and activate virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
3. Install project dependencies: `pip install -r requirements.txt`
4. Set up environment variables by copying the template: `cp .env.example .env` and populating `.env` with your active Testnet keys.

## How to run
Below are three usage examples using the Typer CLI:

**1. Place a MARKET Buy Order (Buy 0.01 BTC at market price)**
```bash
python3 cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
```
*Expected Output:*
```text
  ✅  Order placed successfully
  ─────────────────────────────────────
  orderId     : 13036508623
  status      : NEW
  executedQty : 0.0000
  avgPrice    : 0.00
```

**2. Place a LIMIT Buy Order (Buy 0.01 BTC at $65,000)**
```bash
python3 cli.py --symbol BTCUSDT --side BUY --type LIMIT --qty 0.01 --price 65000
```
*Expected Output:*
```text
  ✅  Order placed successfully
  ─────────────────────────────────────
  orderId     : 13036511315
  status      : NEW
  executedQty : 0.0000
  avgPrice    : 0.00
```

**3. Place a LIMIT Sell Order (Take profit at $80,000)**
```bash
python3 cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.01 --price 80000
```
*Expected Output:*
```text
  ✅  Order placed successfully
  ─────────────────────────────────────
  orderId     : 13036512240
  status      : NEW
  executedQty : 0.0000
  avgPrice    : 0.00
```

## Project structure
```text
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py
│   ├── logging_config.py
│   ├── orders.py
│   └── validators.py
├── logs/
│   ├── limit_order.log
│   └── market_order.log
├── .env.example
├── .gitignore
├── cli.py
├── README.md
└── requirements.txt
```

## Assumptions made during development
- The target environment utilizes Testnet for mock execution (`testnet.binancefuture.com` / `demo.binance.com`) to prevent accidental liquidations. 
- API signature logic assumes accurate system clock synchronization.
- Users invoke the bot manually per command; there is no infinite background execution daemon loop built-in by default.
