import os
import logging
import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

REGISTER_LINK = "https://cm8gold.com/r/cm8jess"
GROUP_LINK = "https://t.me/cm8asiaplayer"
CS_LINK = "https://t.me/jessi_cm8"
WEBSITE_LINK = "https://cm8gaming.com"

logging.basicConfig(level=logging.INFO)

user_lang = {}
verified_users = set()

WELCOME = {
    "ms": {
        "text": """🎉 Selamat datang {name}!

🔥 Cara paling cepat mula:
1️⃣ Klik Daftar Sekarang
2️⃣ Login & mula bermain
3️⃣ Hubungi CS untuk bonus 🎁

💡 Cadangan:
Gunakan USDT untuk deposit & pengeluaran

✔️ Lebih pantas
✔️ Lebih stabil
✔️ Privasi lebih terjaga

👇 Pilih sekarang:""",
        "register": "🔥 Daftar Sekarang",
        "cs": "🧑‍💻 Hubungi CS",
        "group": "📢 Group Pemain",
        "website": "🌐 Laman Utama",
    }
}


def language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇲🇾 Malay", callback_data="lang_ms")]
    ])


def verify_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Verify", callback_data=f"verify_{user_id}")]
    ])


def main_keyboard(lang="ms"):
    t = WELCOME["ms"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["register"], url=REGISTER_LINK)],
        [
            InlineKeyboardButton(t["cs"], url=CS_LINK),
            InlineKeyboardButton(t["group"], url=GROUP_LINK),
        ],
        [InlineKeyboardButton(t["website"], url=WEBSITE_LINK)],
    ])


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        name = user.first_name or "friend"
        user_lang[user.id] = "ms"

        try:
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
        except:
            pass

        await update.message.reply_text(
            f"🎉 Selamat datang {name}!\n\nKlik VERIFY dahulu untuk buka chat.",
            reply_markup=verify_keyboard(user.id)
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("verify_"):
        user_id = int(data.replace("verify_", ""))

        if query.from_user.id != user_id:
            await query.answer("Not for you", show_alert=True)
            return

        verified_users.add(user_id)

        try:
            await context.bot.restrict_chat_member(
                chat_id=query.message.chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=True),
            )
        except:
            pass

        name = query.from_user.first_name or "friend"

        await query.edit_message_text(
            f"✅ Verified!\n\nWelcome {name}"
        )

        await query.message.reply_text(
            WELCOME["ms"]["text"].format(name=name),
            reply_markup=main_keyboard()
        )


async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text.lower()

    # 🚨 只限制未 verify 用户
    if user.id in verified_users:
        return

    # 🚨 检测 link
    if "http://" in text or "https://" in text or "t.me/" in text:
        try:
            await update.message.delete()
            await update.message.chat.ban_member(user.id)
            return
        except:
            pass

    # 🚨 检测 domain（重点）
    domain_pattern = r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"

    if re.search(domain_pattern, text):
        try:
            await update.message.delete()
            await update.message.chat.ban_member(user.id)
            return
        except:
            pass

    # 🚨 关键词
    spam_words = ["bonus", "free", "赚钱", "投资", "airdrop"]

    if any(word in text for word in spam_words):
        try:
            await update.message.delete()
        except:
            pass


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
