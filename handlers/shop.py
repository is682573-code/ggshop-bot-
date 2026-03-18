import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import PLANS, DAYS_LABEL, ADMIN_ID, ADMIN_USERNAME, SUPPORT_USERNAME_2
from database import get_user_lang, create_purchase, get_purchase_by_label, mark_paid, update_roblox_username
from keyboards import plans_keyboard, periods_keyboard, confirm_keyboard, pay_keyboard, back_keyboard
from locales import t
from payments import generate_label, build_payment_url, add_key_to_server

router = Router()
logger = logging.getLogger(__name__)


class PurchaseState(StatesGroup):
    waiting_roblox_after_pay = State()


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
    price = PLANS[plan][days]
    period = DAYS_LABEL[days][lang]
    plan_name = PLANS[plan]["name"]

    await state.update_data(plan=plan, days=days)

    await call.message.delete()
    await call.message.answer(
        t("order_summary", lang, plan=plan_name, period=period, price=price),
        parse_mode="HTML",
        reply_markup=confirm_keyboard(plan, days, lang)
    )
    await call.answer()


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_and_pay(call: CallbackQuery, state: FSMContext):
    _, plan, days = call.data.split(":")
    lang = await get_user_lang(call.from_user.id)
    price = PLANS[plan][days]
    period = DAYS_LABEL[days][lang]
    plan_name = PLANS[plan]["name"]

    label = generate_label()
    await create_purchase(
        tg_id=call.from_user.id,
        roblox_user="PENDING",
        plan=plan,
        days=days,
        price=price,
        label=label
    )
    await state.update_data(label=label, plan=plan, days=days)

    pay_url = build_payment_url(
        amount=price,
        label=label,
        comment=f"GGshop {plan_name} {period}"
    )

    await call.message.delete()
    await call.message.answer(
        t("pay_instruction", lang, price=price),
        parse_mode="HTML",
        reply_markup=pay_keyboard(pay_url, lang)
    )
    await call.answer()


@router.callback_query(F.data == "check_payment")
async def check_payment(call: CallbackQuery, state: FSMContext):
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

    if purchase["status"] == "paid" and purchase["roblox_user"] != "PENDING":
        await call.answer("✅ Ключ уже выдан!", show_alert=True)
        return

    if purchase["status"] == "paid":
        # Оплата есть — просим username
        await call.message.delete()
        await call.message.answer(
            t("payment_confirmed_enter_roblox", lang),
            parse_mode="HTML"
        )
        await state.set_state(PurchaseState.waiting_roblox_after_pay)
        await call.answer()
        return

    # Оплата ещё не пришла
    await call.answer(t("payment_pending_alert", lang), show_alert=True)


@router.message(PurchaseState.waiting_roblox_after_pay)
async def receive_roblox_after_pay(message: Message, state: FSMContext):
    roblox = message.text.strip()
    lang = await get_user_lang(message.from_user.id)
    data = await state.get_data()
    label = data.get("label")

    if not label:
        await message.answer("❌ Ошибка. Начни заново /start")
        await state.clear()
        return

    purchase = await get_purchase_by_label(label)
    if not purchase or purchase["status"] != "paid":
        await message.answer(t("payment_not_found", lang, support=ADMIN_USERNAME))
        return

    await update_roblox_username(label, roblox)

    plan = purchase["plan"]
    days = purchase["days"]
    period = DAYS_LABEL[days][lang]
    plan_name = PLANS[plan]["name"]

    ok = await add_key_to_server(roblox, days)
    key_status = t("key_added", lang, username=roblox) if ok else t("key_error", lang, username=roblox)

    await message.answer(
        t("payment_success", lang,
          username=roblox,
          plan=plan_name,
          period=period,
          support=ADMIN_USERNAME),
        parse_mode="HTML"
    )

    await message.bot.send_message(
        ADMIN_ID,
        f"💰 <b>Новая оплата!</b>\n\n"
        f"👤 TG: @{message.from_user.username or message.from_user.id}\n"
        f"🎮 Roblox: <code>{roblox}</code>\n"
        f"📦 Тариф: {plan_name}\n"
        f"⏳ Период: {period}\n"
        f"💳 Сумма: {purchase['price']} руб.\n\n"
        f"{key_status}",
        parse_mode="HTML"
    )
    await state.clear()
