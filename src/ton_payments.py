import logging
import os
from typing import Optional

import aiohttp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

try:
    from pytonlib.utils.address import prepare_address
except Exception:  # pragma: no cover - optional dependency handling
    prepare_address = None

TON_WALLET = os.getenv("TON_WALLET", "")
TON_EXPLORER_API = "https://tonapi.io/v2/blockchain/accounts/{wallet}/transactions?limit=20"

MONTHLY_TON = 5
PER_GEN_TON = 0.5
NANO = 1_000_000_000  # 1 TON in nano


def _normalized_wallet() -> str:
    if not TON_WALLET:
        return ""
    if prepare_address:
        try:
            return prepare_address(TON_WALLET)
        except Exception as exc:  # pragma: no cover - best effort normalization
            logging.warning("Wallet normalization failed: %s", exc)
    return TON_WALLET


WALLET_B64 = _normalized_wallet()


def payment_keyboard() -> InlineKeyboardMarkup:
    monthly_url = f"https://tonhub.com/transfer/{WALLET_B64}?amount={int(MONTHLY_TON * NANO)}&text=KittyKodakAI%20Pro"
    per_gen_url = f"https://tonhub.com/transfer/{WALLET_B64}?amount={int(PER_GEN_TON * NANO)}&text=KittyKodakAI%20One%20Gen"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Buy Pro 5 TON / month", url=monthly_url),
                InlineKeyboardButton(text="Pay 0.5 TON / gen", url=per_gen_url),
            ],
            [
                InlineKeyboardButton(text="I paid 5 TON (Pro)", callback_data="check_monthly"),
                InlineKeyboardButton(text="I paid 0.5 TON (1 gen)", callback_data="check_one"),
            ],
        ]
    )


async def _fetch_transactions(wallet: str) -> Optional[list]:
    if not wallet:
        return None
    url = TON_EXPLORER_API.format(wallet=wallet)
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logging.error("TON API error %s: %s", resp.status, await resp.text())
                    return None
                data = await resp.json()
                return data.get("transactions", [])
    except Exception as exc:  # pragma: no cover - network best effort
        logging.exception("TON explorer call failed: %s", exc)
        return None


async def verify_payment(min_ton: float) -> bool:
    """Check recent inbound transactions for the expected amount."""
    if not WALLET_B64:
        return False
    txs = await _fetch_transactions(WALLET_B64)
    if not txs:
        return False
    required = int(min_ton * NANO)
    for tx in txs:
        in_msg = tx.get("in_msg") or {}
        try:
            value = int(in_msg.get("value", 0))
        except (TypeError, ValueError):
            continue
        destination = in_msg.get("destination", "")
        normalized_dest = destination
        if prepare_address and destination:
            try:
                normalized_dest = prepare_address(destination)
            except Exception:  # pragma: no cover
                normalized_dest = destination
        is_incoming = normalized_dest and normalized_dest.lower() == WALLET_B64.lower()
        if is_incoming and value >= required:
            return True
    return False
