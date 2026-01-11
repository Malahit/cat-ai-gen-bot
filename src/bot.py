"""
Telegram bot handlers using aiogram
"""
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F

from ai_gen import generate_cat_image
from ton_pay import create_payment, check_payment_status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command"""
    await message.answer(
        "🐱 Welcome to Cat AI Generator Bot!\n\n"
        "Generate unique AI cat images using Perplexity API.\n\n"
        "Commands:\n"
        "/generate - Create a new cat image\n"
        "/help - Show this message"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command"""
    await message.answer(
        "🐱 Cat AI Generator Bot Help\n\n"
        "This bot generates unique cat images using AI.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/generate - Generate a cat image (requires payment)\n\n"
        "Payment is processed via TON blockchain."
    )


@dp.message(Command("generate"))
async def cmd_generate(message: types.Message):
    """Handle /generate command - initiate payment"""
    user_id = message.from_user.id
    
    # Create payment request
    payment_data = create_payment(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Pay with TON", url=payment_data["payment_url"])],
        [InlineKeyboardButton(text="✅ Check Payment", callback_data=f"check_{payment_data['payment_id']}")]
    ])
    
    await message.answer(
        f"🐱 Generate AI Cat Image\n\n"
        f"Price: {payment_data['amount']} TON\n\n"
        f"Click the button below to pay via TON blockchain:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("check_"))
async def check_payment_callback(callback: types.CallbackQuery):
    """Check payment status"""
    payment_id = callback.data.split("_")[1]
    
    if check_payment_status(payment_id):
        await callback.message.answer("⏳ Generating your cat image...")
        
        try:
            # Generate cat image
            image_url = await generate_cat_image()
            
            await callback.message.answer_photo(
                photo=image_url,
                caption="🐱 Here's your AI-generated cat image!"
            )
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            await callback.message.answer(
                "❌ Error generating image. Please try again later."
            )
    else:
        await callback.answer("⚠️ Payment not confirmed yet. Please wait and try again.", show_alert=True)


async def main():
    """Start the bot"""
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
