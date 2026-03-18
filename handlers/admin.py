import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from database import get_stats
from keyboards import admin_keyboard
from payments import add_key_to_server, delete_key_from_server

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


class AdminState(StatesGroup):
    waiting_give_username = State()
    waiting_del_username  = State()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return
    await message.answer(
        "🛠 <b>Admin панель</b>\n\nВыбери действие:",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )


@router.callback_query(F.data == "admin:stats")
async def admin_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    stats = await get_stats()
    await call.message.edit_text(
        f"📊 <b>Статистика</b>\n\n"
        f"👥 Пользователей: <b>{stats['users']}</b>\n"
        f"💳 Всего продаж: <b>{stats['sales']}</b>\n"
        f"💰 Общая выручка: <b>{stats['revenue']} руб.</b>\n"
        f"📅 Сегодня продаж: <b>{stats['today']}</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )
    await call.answer()


@router.callback_query(F.data == "admin:givekey")
async def admin_give_key_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    await call.message.answer("🎁 Введи Roblox username для бесплатного ключа:")
    await state.set_state(AdminState.waiting_give_username)
    await call.answer()


@router.message(AdminState.waiting_give_username)
async def admin_give_key_exec(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    username = message.text.strip()
    ok = await add_key_to_server(username, days="999")
    if ok:
        await message.answer(f"✅ Ключ выдан: <code>{username}</code>", parse_mode="HTML")
    else:
        await message.answer(f"⚠️ Ошибка key-сервера. Добавь вручную: <code>{username}</code>",
                             parse_mode="HTML")
    await state.clear()


@router.callback_query(F.data == "admin:delkey")
async def admin_del_key_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    await call.message.answer("🗑 Введи Roblox username для удаления ключа:")
    await state.set_state(AdminState.waiting_del_username)
    await call.answer()


@router.message(AdminState.waiting_del_username)
async def admin_del_key_exec(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    username = message.text.strip()
    ok = await delete_key_from_server(username)
    if ok:
        await message.answer(f"✅ Ключ удалён: <code>{username}</code>", parse_mode="HTML")
    else:
        await message.answer(f"⚠️ Ошибка key-сервера. Удали вручную: <code>{username}</code>",
                             parse_mode="HTML")
    await state.clear()
