"""
cli.py — Typer-based CLI entry point for the Binance Futures Testnet trading bot.

Usage examples:
    python cli.py --symbol BTCUSDT --side BUY  --type MARKET --qty 0.01
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --qty 0.01 --price 70000
"""

from __future__ import annotations

import os
import traceback
from typing import Optional

import typer
from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import configure_logging, get_logger
from bot.orders import place_limit_order, place_market_order

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

# Load .env from the project root (same directory as this script).
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Configure logging before anything else so all subsequent loggers inherit
# the file + console handlers.
configure_logging()
logger = get_logger(__name__)

app = typer.Typer(
    name="trading-bot",
    help="Binance Futures Testnet trading bot — place MARKET or LIMIT orders.",
    add_completion=False,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_credentials() -> tuple[str, str]:
    """
    Load BINANCE_API_KEY and BINANCE_API_SECRET from the environment.

    Raises SystemExit (via typer.echo + raise typer.Exit) if either is absent.
    """
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    missing: list[str] = []
    if not api_key:
        missing.append("BINANCE_API_KEY")
    if not api_secret:
        missing.append("BINANCE_API_SECRET")

    if missing:
        typer.echo(
            f"[ERROR] Missing environment variable(s): {', '.join(missing)}\n"
            "        Set them in your .env file or export them before running.",
            err=True,
        )
        raise typer.Exit(code=1)

    return api_key, api_secret


def _print_order_result(result: dict) -> None:
    """Pretty-print the fields required by the spec."""
    typer.echo("")
    typer.echo("  ✅  Order placed successfully")
    typer.echo("  ─────────────────────────────────────")
    typer.echo(f"  orderId     : {result.get('orderId', 'N/A')}")
    typer.echo(f"  status      : {result.get('status', 'N/A')}")
    typer.echo(f"  executedQty : {result.get('executedQty', 'N/A')}")
    typer.echo(f"  avgPrice    : {result.get('avgPrice', 'N/A')}")
    typer.echo("")


def _handle_error(exc: Exception) -> None:
    """Log the full traceback to file and print a concise message to the terminal."""
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error("Order failed — %s\n%s", exc, tb)

    if isinstance(exc, ValueError):
        typer.echo(f"\n  ❌  Validation error: {exc}\n", err=True)
    elif isinstance(exc, BinanceClientError):
        typer.echo(
            f"\n  ❌  Binance API error [{exc.code}]: {exc.msg}  "
            f"(HTTP {exc.status_code})\n",
            err=True,
        )
    else:
        typer.echo(f"\n  ❌  Unexpected error: {exc}\n", err=True)

    typer.echo(
        "  ℹ️   Full traceback written to trading_bot.log",
        err=True,
    )


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------


@app.command()
def trade(
    symbol: str = typer.Option(
        ...,
        "--symbol",
        help="Trading pair symbol, e.g. BTCUSDT.",
        show_default=False,
    ),
    side: str = typer.Option(
        ...,
        "--side",
        help="Order side: BUY or SELL.",
        show_default=False,
    ),
    order_type: str = typer.Option(
        ...,
        "--type",
        help="Order type: MARKET or LIMIT.",
        show_default=False,
    ),
    qty: float = typer.Option(
        ...,
        "--qty",
        help="Quantity of base asset to trade (e.g. 0.01).",
        show_default=False,
    ),
    price: Optional[float] = typer.Option(
        None,
        "--price",
        help="Limit price (required for LIMIT orders, ignored for MARKET).",
        show_default=False,
    ),
) -> None:
    """
    Place a Futures order on the Binance Testnet.

    \b
    Examples:
      python cli.py --symbol BTCUSDT --side BUY  --type MARKET --qty 0.01
      python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --qty 0.01 --price 70000
    """
    api_key, api_secret = _load_credentials()

    # Normalise type here so the branch below works regardless of casing.
    normalised_type = order_type.strip().upper()

    logger.info(
        "CLI invoked: symbol=%s side=%s type=%s qty=%s price=%s",
        symbol,
        side,
        normalised_type,
        qty,
        price,
    )

    try:
        with BinanceClient(api_key=api_key, api_secret=api_secret) as client:
            if normalised_type == "MARKET":
                result = place_market_order(
                    client=client,
                    symbol=symbol,
                    side=side,
                    qty=qty,
                )
            elif normalised_type == "LIMIT":
                if price is None:
                    raise ValueError(
                        "price is required for LIMIT orders — pass --price <value>."
                    )
                result = place_limit_order(
                    client=client,
                    symbol=symbol,
                    side=side,
                    qty=qty,
                    price=price,
                )
            else:
                raise ValueError(
                    f"order type '{order_type}' is not supported — use MARKET or LIMIT."
                )

        _print_order_result(result)

    except (ValueError, BinanceClientError) as exc:
        _handle_error(exc)
        raise typer.Exit(code=1)
    except Exception as exc:  # noqa: BLE001
        _handle_error(exc)
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app()
