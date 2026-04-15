"""
bot/orders.py — High-level order placement functions.

Each function:
  1. Delegates to validators.validate_order_params() for pre-flight checks.
  2. Constructs the correct Binance API payload.
  3. Calls BinanceClient.new_order() and returns the raw response dict.

The caller (cli.py) is responsible for pretty-printing results and handling
exceptions.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from bot.client import BinanceClient
from bot.logging_config import get_logger
from bot.validators import validate_order_params

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_decimal(value: Decimal) -> str:
    """
    Render a Decimal as a plain numeric string without trailing zeros or
    scientific notation (e.g. Decimal('0.010') → '0.01').
    """
    return format(value.normalize(), "f")


# ---------------------------------------------------------------------------
# Public order functions
# ---------------------------------------------------------------------------


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    qty: str | float | int,
) -> dict[str, Any]:
    """
    Place a MARKET order on Binance Futures Testnet.

    Parameters
    ----------
    client : BinanceClient
        An authenticated client instance.
    symbol : str
        Trading pair, e.g. 'BTCUSDT'.
    side : str
        'BUY' or 'SELL'.
    qty : str | float | int
        Quantity of the base asset to trade.

    Returns
    -------
    dict
        Raw Binance order-response payload.

    Raises
    ------
    ValueError
        If any parameter fails validation (before any network call).
    BinanceClientError
        If the API returns an error response.
    """
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type="MARKET",
        qty=qty,
        price=None,
    )

    logger.info(
        "Placing MARKET order: symbol=%s side=%s qty=%s",
        params["symbol"],
        params["side"],
        _format_decimal(params["quantity"]),
    )

    response = client.new_order(
        symbol=params["symbol"],
        side=params["side"],
        type="MARKET",
        quantity=_format_decimal(params["quantity"]),
    )

    logger.info(
        "MARKET order accepted: orderId=%s status=%s executedQty=%s avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice"),
    )

    return response


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    qty: str | float | int,
    price: str | float | int,
    time_in_force: str = "GTC",
) -> dict[str, Any]:
    """
    Place a LIMIT order on Binance Futures Testnet.

    Parameters
    ----------
    client : BinanceClient
        An authenticated client instance.
    symbol : str
        Trading pair, e.g. 'BTCUSDT'.
    side : str
        'BUY' or 'SELL'.
    qty : str | float | int
        Quantity of the base asset to trade.
    price : str | float | int
        Limit price for the order.
    time_in_force : str
        'GTC' (Good Till Cancelled, default), 'IOC', or 'FOK'.

    Returns
    -------
    dict
        Raw Binance order-response payload.

    Raises
    ------
    ValueError
        If any parameter fails validation (before any network call).
    BinanceClientError
        If the API returns an error response.
    """
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type="LIMIT",
        qty=qty,
        price=price,
    )

    logger.info(
        "Placing LIMIT order: symbol=%s side=%s qty=%s price=%s tif=%s",
        params["symbol"],
        params["side"],
        _format_decimal(params["quantity"]),
        _format_decimal(params["price"]),
        time_in_force,
    )

    response = client.new_order(
        symbol=params["symbol"],
        side=params["side"],
        type="LIMIT",
        quantity=_format_decimal(params["quantity"]),
        price=_format_decimal(params["price"]),
        timeInForce=time_in_force,
    )

    logger.info(
        "LIMIT order accepted: orderId=%s status=%s executedQty=%s avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice"),
    )

    return response
