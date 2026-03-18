import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database import upsert_user, get_user_lang
from keyboards import lang_keyboard, main_menu, back_keyboard
from locales import t

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await upsert_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "🌍 Выбери язык / Choose language:",
        reply_markup=lang_keyboard()
    )


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(call: CallbackQuery, state: FSMContext):
    lang = call.data.split(":")[1]
    await upsert_user(call.from_user.id, call.from_user.username, lang)
    await call.message.delete()
    await call.message.answer(
        t("welcome", lang),
        parse_mode="HTML",
        reply_markup=main_menu(lang)
    )
    await call.answer()


@router.callback_query(F.data == "menu:back")
async def go_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(call.from_user.id)
    await call.message.delete()
    await call.message.answer(
        t("welcome", lang),
        parse_mode="HTML",
        reply_markup=main_menu(lang)
    )
    await call.answer()


@router.callback_query(F.data == "menu:faq")
async def faq_handler(call: CallbackQuery):
    lang = await get_user_lang(call.from_user.id)
    await call.message.delete()
    await call.message.answer(
        t("faq", lang),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang)
    )
    await call.answer()


@router.callback_query(F.data == "menu:support")
async def support_handler(call: CallbackQuery):
    from config import ADMIN_USERNAME, SUPPORT_USERNAME_2
    lang = await get_user_lang(call.from_user.id)
    await call.message.delete()
    await call.message.answer(
        t("support", lang, admin=ADMIN_USERNAME, support2=SUPPORT_USERNAME_2),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang)
    )
    await call.answer()


@router.callback_query(F.data == "menu:channel")
async def channel_handler(call: CallbackQuery):
    from config import CHANNEL_LINK
    lang = await get_user_lang(call.from_user.id)
    await call.message.delete()
    await call.message.answer(
        t("channel", lang, link=CHANNEL_LINK),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang)
    )
    await call.answer()
