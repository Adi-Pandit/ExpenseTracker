import json
import os
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


DEFAULT_RATE_API_URL = "https://open.er-api.com/v6/latest/{base}"
_STALE_RATE_CACHE = {}


def normalize_currency_code(currency_code):
    if not currency_code:
        raise ValueError("Currency code is required.")

    normalized = currency_code.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError("Currency code must be a 3-letter ISO code.")
    return normalized


@lru_cache(maxsize=64)
def fetch_exchange_rates(base_currency):
    base_currency = normalize_currency_code(base_currency)
    api_url = os.getenv("EXCHANGE_RATE_API_URL", DEFAULT_RATE_API_URL).format(
        base=base_currency
    )

    with urlopen(api_url, timeout=10) as response:
        payload = json.load(response)

    rates = payload.get("rates")
    if not isinstance(rates, dict):
        raise ValueError("Exchange rate provider returned an invalid response.")
    _STALE_RATE_CACHE[base_currency] = rates
    return rates


def get_exchange_rate(from_currency, to_currency):
    from_currency = normalize_currency_code(from_currency)
    to_currency = normalize_currency_code(to_currency)
    if from_currency == to_currency:
        return 1.0

    try:
        rates = fetch_exchange_rates(from_currency)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        rates = _STALE_RATE_CACHE.get(from_currency)
        if rates is None:
            raise ValueError(
                "Unable to fetch exchange rates right now. Please try again later."
            ) from exc

    rate = rates.get(to_currency)
    if rate is None:
        raise ValueError(f"Unsupported currency conversion: {from_currency} to {to_currency}.")
    return float(rate)


def convert_amount(amount, from_currency, to_currency):
    rate = get_exchange_rate(from_currency, to_currency)
    converted_amount = round(float(amount) * rate, 2)
    return rate, converted_amount
