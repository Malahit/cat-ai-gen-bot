import logging
import os
from typing import Optional

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from ai_generator import generate_cat_image
from database import Database, FREE_LIMIT
from ton_payments import MONTHLY_TON, PER_GEN_TON, payment_keyboard, verify_payment

router = Router()

PERPLEXITY_KEY = os.getenv("PERPLEXITY_KEY", "")


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🐱 Generate Cat"), KeyboardButton(text="💎 Go Pro")],
            [KeyboardButton(text="📊 My Stats"), KeyboardButton(text="❓ Help")],
        ],
        resize_keyboard=True,
        persistent=True,
    )


def after_photo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Generate Again", callback_data="gen_again"),
                InlineKeyboardButton(text="💎 Upgrade", callback_data="show_pay"),
            ]
        ]
    )


async def _send_cat_photo(message: types.Message, image_bytes: Optional[bytes]) -> None:
    if not image_bytes:
        await message.answer("Generation failed. Please try again in a moment.")
        return
    photo = BufferedInputFile(file=image_bytes, filename="kitty.png")
    await message.answer_photo(
        photo=photo,
        caption="Like it? Generate another or upgrade to Pro 👇",
        reply_markup=after_photo_keyboard(),
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "Welcome to KittyKodakAI! 🐱\n\n"
        "Generate cute AI cat images in seconds.\n"
        f"Free: {FREE_LIMIT} generations/day.\n\n"
        "Try it: tap <b>🐱 Generate Cat</b> or send /cat astronaut",
        reply_markup=main_keyboard(),
    )


@router.message(lambda m: m.text == "🐱 Generate Cat")
async def btn_generate(message: types.Message) -> None:
    await message.answer(
        "Send me a prompt like:\n"
        "/cat astronaut\n"
        "/cat ninja in the rain\n"
        "/cat sleeping on a cloud"
    )


@router.message(lambda m: m.text == "💎 Go Pro")
async def btn_pro(message: types.Message) -> None:
    await message.answer(
        f"Upgrade to Pro via TON.\n"
        f"Pro subscription: {MONTHLY_TON} TON / month.\n"
        f"Single generation: {PER_GEN_TON} TON.",
        reply_markup=payment_keyboard(),
    )


@router.message(lambda m: m.text == "📊 My Stats")
async def btn_stats(message: types.Message, db: Database) -> None:
    used, pro_until, credits = await db.get_stats(message.from_user.id)
    await message.answer(
        f"📊 Your stats:\n\n"
        f"Used today: {used}/{FREE_LIMIT}\n"
        f"Pro until: {pro_until}\n"
        f"Paid credits: {credits}"
    )


@router.message(lambda m: m.text == "❓ Help")
async def btn_help(message: types.Message) -> None:
    await message.answer(
        "🐱 <b>How to use KittyKodakAI:</b>\n\n"
        "1. Tap <b>🐱 Generate Cat</b> and send a prompt\n"
        "2. Or type directly: /cat your prompt\n"
        "3. Free users get 3 generations/day\n"
        "4. Upgrade via <b>💎 Go Pro</b> for unlimited access\n\n"
        "<b>Examples:</b>\n"
        "• /cat samurai at sunset\n"
        "• /cat pirate with a treasure map\n"
        "• /cat astronaut on the moon"
    )


@router.message(Command("cat"))
async def cmd_cat(message: types.Message, command: CommandObject, db: Database) -> None:
    prompt = (command.args or "").strip()
    if not prompt:
        await message.answer("Send like: /cat astronaut cat sipping coffee.")
        return
    if not PERPLEXITY_KEY:
        await message.answer("Generator is temporarily unavailable. Please try again later.")
        return
    can_generate = await db.can_generate(message.from_user.id)
    if not can_generate:
        await message.answer(
            "Free limit reached for today 😿\n\nUpgrade to Pro:",
            reply_markup=payment_keyboard(),
        )
        return
    is_pro = await db.has_pro(message.from_user.id)
    await message.chat.do("upload_photo")
    image_bytes = await generate_cat_image(PERPLEXITY_KEY, prompt)
    await db.add_generation(message.from_user.id, is_pro=is_pro)
    await _send_cat_photo(message, image_bytes)


@router.message(Command("pay"))
async def cmd_pay(message: types.Message) -> None:
    await message.answer(
        f"Upgrade to Pro via TON Connect.\n"
        f"Pro subscription: {MONTHLY_TON} TON / month.\n"
        f"Single generation: {PER_GEN_TON} TON.",
        reply_markup=payment_keyboard(),
    )


@router.callback_query(lambda c: c.data == "gen_again")
async def cb_gen_again(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Send me your next prompt:\n/cat your idea here"
    )


@router.callback_query(lambda c: c.data == "show_pay")
async def cb_show_pay(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        f"Upgrade to Pro via TON Connect.\n"
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
        await callback.message.answer("🎉 Pro activated for 30 days! Enjoy unlimited cats.")
    else:
        await db.add_paid_credit(callback.from_user.id, credits=1)
        await callback.message.answer("✅ One-time generation unlocked! Use /cat now.")


@router.message(Command(commands=["stats", "my_stats"]))
async def cmd_stats(message: types.Message, db: Database) -> None:
    used, pro_until, credits = await db.get_stats(message.from_user.id)
    await message.answer(
        f"📊 Your stats:\n\n"
        f"Used today: {used}/{FREE_LIMIT}\n"
        f"Pro until: {pro_until}\n"
        f"Paid credits: {credits}"
    )
