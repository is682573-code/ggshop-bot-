import asyncpg
import logging
from datetime import datetime
from config import DATABASE_URL

logger = logging.getLogger(__name__)
_pool: asyncpg.Pool = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                tg_id       BIGINT PRIMARY KEY,
                username    TEXT,
                lang        TEXT DEFAULT 'ru',
                created_at  TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS purchases (
                id              SERIAL PRIMARY KEY,
                tg_id           BIGINT NOT NULL,
                roblox_user     TEXT NOT NULL,
                plan            TEXT NOT NULL,
                days            TEXT NOT NULL,
                price           INTEGER NOT NULL,
                payment_label   TEXT UNIQUE,
                status          TEXT DEFAULT 'pending',
                created_at      TIMESTAMP DEFAULT NOW(),
                paid_at         TIMESTAMP
            );
        """)
    logger.info("✅ Database initialized")


# ─── Users ────────────────────────────────────────────────────

async def upsert_user(tg_id: int, username: str = None, lang: str = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT lang FROM users WHERE tg_id=$1", tg_id)
        if existing:
            if lang:
                await conn.execute("UPDATE users SET username=$1, lang=$2 WHERE tg_id=$3",
                                   username, lang, tg_id)
            else:
                await conn.execute("UPDATE users SET username=$1 WHERE tg_id=$2",
                                   username, tg_id)
        else:
            await conn.execute(
                "INSERT INTO users (tg_id, username, lang) VALUES ($1,$2,$3)",
                tg_id, username, lang or "ru"
            )


async def get_user_lang(tg_id: int) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT lang FROM users WHERE tg_id=$1", tg_id)
        return row["lang"] if row else "ru"


# ─── Purchases ────────────────────────────────────────────────

async def create_purchase(tg_id: int, roblox_user: str, plan: str,
                           days: str, price: int, label: str) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO purchases (tg_id, roblox_user, plan, days, price, payment_label)
               VALUES ($1,$2,$3,$4,$5,$6) RETURNING id""",
            tg_id, roblox_user, plan, days, price, label
        )
        return row["id"]


async def get_purchase_by_label(label: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM purchases WHERE payment_label=$1", label
        )


async def mark_paid(label: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE purchases SET status='paid', paid_at=NOW() WHERE payment_label=$1",
            label
        )


# ─── Stats ────────────────────────────────────────────────────

async def get_stats() -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        total_users   = await conn.fetchval("SELECT COUNT(*) FROM users")
        total_sales   = await conn.fetchval("SELECT COUNT(*) FROM purchases WHERE status='paid'")
        total_revenue = await conn.fetchval("SELECT COALESCE(SUM(price),0) FROM purchases WHERE status='paid'")
        today_sales   = await conn.fetchval(
            "SELECT COUNT(*) FROM purchases WHERE status='paid' AND paid_at::date=CURRENT_DATE"
        )
        return {
            "users": total_users,
            "sales": total_sales,
            "revenue": total_revenue,
            "today": today_sales,
        }
