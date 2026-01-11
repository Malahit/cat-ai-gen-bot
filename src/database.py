import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple

from redis import asyncio as aioredis


FREE_LIMIT = 3


class Database:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        self._lock = asyncio.Lock()

    async def _get_today(self) -> str:
        return datetime.now(timezone.utc).date().isoformat()

    def _key(self, user_id: int) -> str:
        return f"user:{user_id}"

    async def _load(self, user_id: int) -> Dict:
        raw = await self._client.get(self._key(user_id))
        if not raw:
            return {
                "free_used": 0,
                "paid_credits": 0,
                "pro_until": None,
                "last_reset": await self._get_today(),
            }
        return json.loads(raw)

    async def _save(self, user_id: int, data: Dict) -> None:
        await self._client.set(self._key(user_id), json.dumps(data))

    async def ensure_daily_reset(self, user_id: int) -> Dict:
        data = await self._load(user_id)
        today = await self._get_today()
        if data.get("last_reset") != today:
            data["free_used"] = 0
            data["last_reset"] = today
            await self._save(user_id, data)
        return data

    async def get_stats(self, user_id: int) -> Tuple[int, str, int]:
        data = await self.ensure_daily_reset(user_id)
        pro_until = data.get("pro_until")
        return data.get("free_used", 0), pro_until or "N/A", data.get("paid_credits", 0)

    async def has_pro(self, user_id: int) -> bool:
        data = await self.ensure_daily_reset(user_id)
        pro_until = data.get("pro_until")
        if not pro_until:
            return False
        try:
            until_dt = datetime.fromisoformat(pro_until)
        except ValueError:
            return False
        if until_dt.tzinfo is None:
            until_dt = until_dt.replace(tzinfo=timezone.utc)
        return until_dt > datetime.now(timezone.utc)

    async def can_generate(self, user_id: int) -> bool:
        data = await self.ensure_daily_reset(user_id)
        if await self.has_pro(user_id):
            return True
        if data.get("paid_credits", 0) > 0:
            return True
        return data.get("free_used", 0) < FREE_LIMIT

    async def add_generation(self, user_id: int, is_pro: bool) -> None:
        async with self._lock:
            data = await self.ensure_daily_reset(user_id)
            if not is_pro:
                if data.get("paid_credits", 0) > 0:
                    data["paid_credits"] -= 1
                else:
                    data["free_used"] = data.get("free_used", 0) + 1
            await self._save(user_id, data)

    async def extend_pro(self, user_id: int, days: int) -> None:
        async with self._lock:
            data = await self.ensure_daily_reset(user_id)
            now = datetime.now(timezone.utc)
            current_until = datetime.fromisoformat(data.get("pro_until")) if data.get("pro_until") else now
            new_until = max(now, current_until) + timedelta(days=days)
            data["pro_until"] = new_until.isoformat()
            await self._save(user_id, data)

    async def add_paid_credit(self, user_id: int, credits: int) -> None:
        async with self._lock:
            data = await self.ensure_daily_reset(user_id)
            data["paid_credits"] = data.get("paid_credits", 0) + credits
            await self._save(user_id, data)
