"""
bot/validators.py — Input validation for all order parameters.

Every function raises ValueError with a human-readable message on invalid
input so no bad data ever reaches the network layer.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_TYPES = {"MARKET", "LIMIT"}

# Binance symbol names are always uppercase letters + digits, no spaces.
_MAX_SYMBOL_LEN = 20


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalise a Binance Futures symbol (e.g. 'BTCUSDT').

    Returns the upper-cased symbol on success.
    Raises ValueError if the symbol is invalid.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("symbol must be a non-empty string.")

    symbol = symbol.strip().upper()

    if not symbol.isalnum():
        raise ValueError(
            f"symbol '{symbol}' is invalid — must contain only letters and digits "
            "(e.g. 'BTCUSDT')."
        )

    if len(symbol) > _MAX_SYMBOL_LEN:
        raise ValueError(
            f"symbol '{symbol}' is too long (max {_MAX_SYMBOL_LEN} characters)."
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.

    Returns the upper-cased side string ('BUY' or 'SELL').
    Raises ValueError for any other value.
    """
    if not side or not isinstance(side, str):
        raise ValueError("side must be a non-empty string.")

    side = side.strip().upper()

    if side not in VALID_SIDES:
        raise ValueError(
            f"side '{side}' is invalid — must be one of {sorted(VALID_SIDES)}."
        )

    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.

    Returns the upper-cased type string ('MARKET' or 'LIMIT').
    Raises ValueError for any unsupported type.
    """
    if not order_type or not isinstance(order_type, str):
        raise ValueError("order type must be a non-empty string.")

    order_type = order_type.strip().upper()

    if order_type not in VALID_TYPES:
        raise ValueError(
            f"order type '{order_type}' is not supported — must be one of "
            f"{sorted(VALID_TYPES)}."
        )

    return order_type


def validate_quantity(qty: str | float | int) -> Decimal:
    """
    Validate and parse order quantity.

    Returns a Decimal representation of the quantity (positive, non-zero).
    Raises ValueError for non-numeric or non-positive values.
    """
    try:
        quantity = Decimal(str(qty))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(
            f"qty '{qty}' is not a valid number — provide a positive decimal value "
            "(e.g. 0.01)."
        )

    if quantity <= 0:
        raise ValueError(
            f"qty must be a positive non-zero value; received {quantity}."
        )

    return quantity


def validate_price(price: str | float | int | None, order_type: str) -> Optional[Decimal]:
    """
    Validate and parse order price.

    * For LIMIT orders: price must be present, numeric, and positive.
    * For MARKET orders: price must be None or omitted.

    Returns a Decimal on success, or None for MARKET orders.
    Raises ValueError on any violation.
    """
    if order_type == "MARKET":
        if price is not None:
            raise ValueError(
                "price must not be provided for MARKET orders; it is determined "
                "by the market at execution time."
            )
        return None

    # --- LIMIT ---
    if price is None:
        raise ValueError(
            "price is required for LIMIT orders — provide a positive decimal value "
            "(e.g. 29500.50)."
        )

    try:
        parsed = Decimal(str(price))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(
            f"price '{price}' is not a valid number — provide a positive decimal "
            "value (e.g. 29500.50)."
        )

    if parsed <= 0:
        raise ValueError(
            f"price must be a positive non-zero value; received {parsed}."
        )

    return parsed


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    qty: str | float | int,
    price: str | float | int | None = None,
) -> dict:
    """
    Run all validators in the correct order and return a clean params dict.

    This is the single public entry point used by orders.py.

    Returns
    -------
    dict with keys: symbol, side, type, quantity, price (price may be None).
    """
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_type = validate_order_type(order_type)
    clean_qty = validate_quantity(qty)
    clean_price = validate_price(price, clean_type)

    return {
        "symbol": clean_symbol,
        "side": clean_side,
        "type": clean_type,
        "quantity": clean_qty,
        "price": clean_price,
    }
