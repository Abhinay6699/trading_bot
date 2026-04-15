"""
bot/client.py — BinanceClient wrapping the Binance Futures Testnet REST API.

Uses httpx for HTTP transport so there is no dependency on the heavyweight
python-binance SDK, giving us full control over request signing and logging.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import urllib.parse
from typing import Any

import httpx

from bot.logging_config import get_logger

logger = get_logger(__name__)

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 5_000  # milliseconds


class BinanceClientError(RuntimeError):
    """Raised when the Binance API returns a non-2xx response or an error body."""

    def __init__(self, status_code: int, code: int, msg: str) -> None:
        self.status_code = status_code
        self.code = code
        self.msg = msg
        super().__init__(f"Binance API error [{code}]: {msg} (HTTP {status_code})")


class BinanceClient:
    """
    Thin, authenticated HTTP client for the Binance USDS-M Futures Testnet.

    Parameters
    ----------
    api_key:    Testnet API key
    api_secret: Testnet API secret
    base_url:   Override the default testnet URL (useful for testing)
    timeout:    httpx request timeout in seconds
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = TESTNET_BASE_URL,
        timeout: float = 10.0,
    ) -> None:
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must be non-empty strings.")
        self._api_key = api_key
        self._api_secret = api_secret.encode()
        self._base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={
                "X-MBX-APIKEY": api_key,
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "TradingBot/1.0",
            },
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict[str, Any]) -> dict[str, Any]:
        """Append a HMAC-SHA256 signature to *params* (mutates in-place).

        Timestamp and recvWindow are injected first so they are included in
        the signature payload.  The signature is always the LAST key so that
        Binance can verify the canonical query string.
        """
        params["timestamp"] = int(time.time() * 1_000)
        params["recvWindow"] = RECV_WINDOW
        query = urllib.parse.urlencode(params)
        signature = hmac.new(
            self._api_secret,
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _raise_for_binance_error(self, response: httpx.Response) -> None:
        """Parse the response and raise BinanceClientError if it contains an error."""
        try:
            body: dict[str, Any] = response.json()
        except Exception:
            response.raise_for_status()
            return

        if response.is_error or (isinstance(body, dict) and "code" in body and body["code"] != 200):
            code = body.get("code", -1)
            msg = body.get("msg", response.text)
            raise BinanceClientError(response.status_code, int(code), str(msg))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def new_order(self, **params: Any) -> dict[str, Any]:
        """
        POST /fapi/v1/order — Place a new Futures order.

        All valid Binance order parameters may be passed as keyword arguments.
        Returns the parsed JSON response dict on success.
        """
        signed = self._sign(dict(params))
        endpoint = "/fapi/v1/order"

        logger.info("API REQUEST  POST %s  params=%r", endpoint, self._redact(signed))

        response = self._http.post(endpoint, data=signed)

        logger.info(
            "API RESPONSE POST %s  status=%d  body=%s",
            endpoint,
            response.status_code,
            response.text,
        )

        self._raise_for_binance_error(response)
        return response.json()

    def get_exchange_info(self) -> dict[str, Any]:
        """
        GET /fapi/v1/exchangeInfo — Retrieve exchange metadata (symbols, filters …).
        No authentication required.
        """
        endpoint = "/fapi/v1/exchangeInfo"
        logger.info("API REQUEST  GET %s", endpoint)
        response = self._http.get(endpoint)
        logger.info(
            "API RESPONSE GET %s  status=%d",
            endpoint,
            response.status_code,
        )
        self._raise_for_binance_error(response)
        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._http.close()

    def __enter__(self) -> "BinanceClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _redact(params: dict[str, Any]) -> dict[str, Any]:
        """Return a copy of *params* with the signature field masked."""
        safe = dict(params)
        if "signature" in safe:
            safe["signature"] = "***"
        return safe
