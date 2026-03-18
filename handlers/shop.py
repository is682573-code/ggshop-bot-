import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import PLANS, DAYS_LABEL, ADMIN_ID, ADMIN_USERNAME, SUPPORT_USERNAME_2
from database import get_user_lang, create_purchase, get_purchase_by_label, mark_paid
from keyboards import plans_keyboard, periods_keyboard, confirm_keyboard, pay_keyboard, back_keyboard
from locales import t
from payments import generate_label, build_payment_url, add_key_to_server

router = Router()
logger = logging.getLogger(__name__)


class PurchaseState(StatesGroup):
    waiting_roblox = State()


@router.callback_query(F.data == "menu:plans")
async def show_plans(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(call.from_user.id)
    await call.message.delete()
    await call.message.answer(
        t("choose_plan", lang),
        parse_mode="HTML",
        reply_markup=plans_keyboard(lang)
    )
    await call.answer()


@router.callback_query(F.data.startswith("plan:"))
async def show_plan_detail(call: CallbackQuery, state: FSMContext):
    plan = call.data.split(":")[1]
    lang = await get_user_lang(call.from_user.id)
    text_key = f"plan_{plan}"
    await call.message.delete()
    await call.message.answer(
        t(text_key, lang),
        parse_mode="HTML",
        reply_markup=periods_keyboard(plan, lang)
    )
    await call.answer()


@router.callback_query(F.data.startswith("period:"))
async def choose_period(call: CallbackQuery, state: FSMContext):
    _, plan, days = call.data.split(":")
    lang = await get_user_lang(call.from_user.id)
    await state.update_data(plan=plan, days=days)
    await call.message.delete()
    await call.message.answer(
        t("enter_roblox", lang),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang, target=f"plan:{plan}")
    )
    await state.set_state(PurchaseState.waiting_roblox)
    await call.answer()


@router.message(PurchaseState.waiting_roblox)
async def receive_roblox_username(message: Message, state: FSMContext):
    roblox = message.text.strip()
    lang = await get_user_lang(message.from_user.id)
    data = await state.get_data()
    plan = data.get("plan")
    days = data.get("days")
    price = PLANS[plan][days]
    period = DAYS_LABEL[days][lang]
    plan_name = PLANS[plan]["name"]

    await state.update_data(roblox=roblox)

    await message.answer(
        t("roblox_confirm", lang,
          plan=plan_name, period=period, price=price, username=roblox),
        parse_mode="HTML",
        reply_markup=confirm_keyboard(plan, days, lang)
    )


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_purchase(call: CallbackQuery, state: FSMContext):
    _, plan, days = call.data.split(":")
    lang = await get_user_lang(call.from_user.id)
    data = await state.get_data()
    roblox = data.get("roblox", "unknown")
    price = PLANS[plan][days]
    period = DAYS_LABEL[days][lang]
    plan_name = PLANS[plan]["name"]

    label = generate_label()
    await create_purchase(
        tg_id=call.from_user.id,
        roblox_user=roblox,
        plan=plan,
        days=days,
        price=price,
        label=label
    )
    await state.update_data(label=label)

    pay_url = build_payment_url(
        amount=price,
        label=label,
        comment=f"GGshop {plan_name} {period} — {roblox}"
    )

    await call.message.delete()
    await call.message.answer(
        t("pay_instruction", lang, price=price),
        parse_mode="HTML",
        reply_markup=pay_keyboard(pay_url, lang)
    )
    await call.answer()


@router.callback_query(F.data == "check_payment")
async def check_payment_manually(call: CallbackQuery, state: FSMContext):
    """Ручная проверка — на случай если webhook не дошёл."""
    lang = await get_user_lang(call.from_user.id)
    data = await state.get_data()
    label = data.get("label")

    if not label:
        await call.answer("❌ Нет активного платежа.", show_alert=True)
        return

    purchase = await get_purchase_by_label(label)
    if not purchase:
        await call.answer("❌ Платёж не найден.", show_alert=True)
        return

    if purchase["status"] == "paid":
        await _deliver_key(call, purchase, lang)
    else:
        await call.answer("⏳ Оплата ещё не подтверждена. Подожди немного.", show_alert=True)


async def _deliver_key(call: CallbackQuery, purchase, lang: str):
    """Отправляет ключ пользователю и уведомляет админа."""
    from aiogram import Bot
    bot: Bot = call.bot

    roblox = purchase["roblox_user"]
    plan = purchase["plan"]
    days = purchase["days"]
    period = DAYS_LABEL[days][lang]
    plan_name = PLANS[plan]["name"]

    # Добавить на key-сервер
    ok = await add_key_to_server(roblox, days)
    key_status = t("key_added", lang, username=roblox) if ok else t("key_error", lang, username=roblox)

    await call.message.delete()
    await call.message.answer(
        t("payment_success", lang,
          username=roblox,
          plan=plan_name,
          period=period,
          support=ADMIN_USERNAME),
        parse_mode="HTML"
    )

    # Уведомление администратору
    await bot.send_message(
        ADMIN_ID,
        f"💰 <b>Новая оплата!</b>\n\n"
        f"👤 TG: @{call.from_user.username or call.from_user.id}\n"
        f"🎮 Roblox: <code>{roblox}</code>\n"
        f"📦 Тариф: {plan_name}\n"
        f"⏳ Период: {period}\n"
        f"💳 Сумма: {purchase['price']} руб.\n\n"
        f"{key_status}",
        parse_mode="HTML"
    )
