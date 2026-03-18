import asyncpg
import logging
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
