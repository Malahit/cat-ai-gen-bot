import logging
import os
from typing import Optional

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, CallbackQuery

from .ai_generator import generate_cat_image
from .database import Database, FREE_LIMIT
from .ton_payments import MONTHLY_TON, PER_GEN_TON, payment_keyboard, verify_payment

router = Router()

PERPLEXITY_KEY = os.getenv("PERPLEXITY_KEY", "")


async def _send_cat_photo(message: types.Message, image_bytes: Optional[bytes]) -> None:
    if not image_bytes:
        await message.answer("Generation failed. Please /retry or try again later.")
        return
    photo = BufferedInputFile(file=image_bytes, filename="kitty.png")
    await message.answer_photo(
        photo=photo,
        caption="Pro tip: /pay to unlock unlimited kitty magic.",
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "Welcome to KittyKodakAI! Generate cute cat images with AI.\n"
        f"Free: {FREE_LIMIT}/day. Try /cat astronaut → cat astronaut!\n"
        "Ready to upgrade? /pay for Pro."
    )


@router.message(Command("cat"))
async def cmd_cat(message: types.Message, command: CommandObject, db: Database) -> None:
    prompt = (command.args or "").strip()
    if not prompt:
        await message.answer("Send like: /cat astronaut cat sipping coffee.")
        return
    if not PERPLEXITY_KEY:
        await message.answer("Perplexity key missing. Please set PERPLEXITY_KEY.")
        return
    can_generate = await db.can_generate(message.from_user.id)
    if not can_generate:
        await message.answer("Free limit reached. Upgrade to Pro: /pay")
        return
    is_pro = await db.has_pro(message.from_user.id)
    await message.chat.do("upload_photo")
    image_bytes = await generate_cat_image(PERPLEXITY_KEY, prompt)
    await db.add_generation(message.from_user.id, is_pro=is_pro)
    await _send_cat_photo(message, image_bytes)


@router.message(Command("pay"))
async def cmd_pay(message: types.Message) -> None:
    await message.answer(
        "Upgrade to Pro via TON Connect.\n"
        f"Pro subscription: {MONTHLY_TON} TON / month.\n"
        f"Single generation: {PER_GEN_TON} TON.",
        reply_markup=payment_keyboard(),
    )


@router.callback_query(lambda c: c.data in {"check_monthly", "check_one"})
async def cb_check_payment(callback: CallbackQuery, db: Database) -> None:
    await callback.answer("Checking TON payment...")
    required = MONTHLY_TON if callback.data == "check_monthly" else PER_GEN_TON
    ok = await verify_payment(required)
    if not ok:
        await callback.message.answer("Payment not found yet. Try again in 30s or contact support.")
        return
    if callback.data == "check_monthly":
        await db.extend_pro(callback.from_user.id, days=30)
        await callback.message.answer("Pro activated for 30 days! Enjoy unlimited cats.")
    else:
        await db.add_paid_credit(callback.from_user.id, credits=1)
        await callback.message.answer("One-time generation unlocked! Use /cat now.")


@router.message(Command(commands=["stats", "my_stats"]))
async def cmd_stats(message: types.Message, db: Database) -> None:
    used, pro_until, credits = await db.get_stats(message.from_user.id)
    await message.answer(
        f"Used: {used}/{FREE_LIMIT} free today.\n"
        f"Pro until: {pro_until}\n"
        f"Paid credits available: {credits}"
    )
