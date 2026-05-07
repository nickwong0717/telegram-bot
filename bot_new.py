import os
import logging
from datetime import datetime, timedelta

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

BAD_WORDS = [
    "http://",
    "https://",
    "t.me/",
    "whatsapp",
    "free money",
    "bonus link",
]

WELCOME = {
    "zh": {
        "text": """🎉 欢迎 {name}！

🔥 新手最快上手：
1️⃣ 点击注册
2️⃣ 登录开始
3️⃣ 联系客服领取奖励 🎁

💡 推荐使用 USDT 进行充值与提现：
✔️ 速度更快
✔️ 更稳定
✔️ 隐私性更高
✔️ 支持多货币

👉 适合马来西亚与东南亚用户

👇 请选择：""",
        "register": "🔥 立即注册",
        "cs": "🧑‍💻 联系客服",
        "group": "📢 玩家群",
        "website": "🌐 官方入口",
        "rules": "📌 群规则",
    },
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
✔️ Sokong multi-currency

👉 Sesuai untuk pemain Malaysia & Asia Tenggara

👇 Pilih sekarang:""",
        "register": "🔥 Daftar Sekarang",
        "cs": "🧑‍💻 Hubungi CS",
        "group": "📢 Group Pemain",
        "website": "🌐 Laman Utama",
        "rules": "📌 Peraturan Group",
    },
    "id": {
        "text": """🎉 Selamat datang {name}!

🔥 Mulai sekarang:
1️⃣ Klik Daftar
2️⃣ Login & mulai main
3️⃣ Hubungi CS untuk bonus 🎁

💡 Rekomendasi:
Gunakan USDT untuk deposit & withdraw

✔️ Lebih cepat
✔️ Lebih stabil
✔️ Privasi lebih aman
✔️ Support multi-currency

👉 Cocok untuk pemain Indonesia & Asia

👇 Pilih di bawah:""",
        "register": "🔥 Daftar Sekarang",
        "cs": "🧑‍💻 Hubungi CS",
        "group": "📢 Grup Pemain",
        "website": "🌐 Website Utama",
        "rules": "📌 Peraturan Grup",
    },
    "en": {
        "text": """🎉 Welcome {name}!

🔥 Quick start:
1️⃣ Click Register
2️⃣ Login & play
3️⃣ Contact CS for bonus 🎁

💡 Recommendation:
Use USDT for deposit & withdrawal

✔️ Faster transactions
✔️ More stable
✔️ Better privacy
✔️ Multi-currency supported

👉 Ideal for Malaysia & Southeast Asia users

👇 Choose below:""",
        "register": "🔥 Register Now",
        "cs": "🧑‍💻 Contact Support",
        "group": "📢 Player Group",
        "website": "🌐 Main Website",
        "rules": "📌 Group Rules",
    },
}


def language_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh"),
            InlineKeyboardButton("🇲🇾 Malay", callback_data="lang_ms"),
        ],
        [
            InlineKeyboardButton("🇮🇩 Indonesia", callback_data="lang_id"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ],
    ])


def main_keyboard(lang="ms"):
    t = WELCOME.get(lang, WELCOME["ms"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["register"], url=REGISTER_LINK)],
        [
            InlineKeyboardButton(t["cs"], url=CS_LINK),
            InlineKeyboardButton(t["group"], url=GROUP_LINK),
        ],
        [InlineKeyboardButton(t["website"], url=WEBSITE_LINK)],
        [InlineKeyboardButton(t["rules"], callback_data=f"rules_{lang}")],
    ])


def get_user_lang(user_id):
    return user_lang.get(user_id, "ms")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "请选择语言 / Sila pilih bahasa / Please choose language:",
        reply_markup=language_keyboard()
    )


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for user in update.message.new_chat_members:
        name = user.first_name or "friend"
        user_lang[user.id] = "ms"

        try:
            until = datetime.now() + timedelta(seconds=30)
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until,
            )
        except Exception as e:
            logging.warning(f"Restrict failed: {e}")

        await update.message.reply_text(
            f"🎉 Selamat datang {name}!\n\n请选择语言 / Sila pilih bahasa / Please choose language:",
            reply_markup=language_keyboard()
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("lang_"):
        lang = data.replace("lang_", "")
        user_id = query.from_user.id
        user_lang[user_id] = lang

        name = query.from_user.first_name or "friend"
        text = WELCOME[lang]["text"].format(name=name)

        await query.edit_message_text(
            text=text,
            reply_markup=main_keyboard(lang)
        )

    elif data.startswith("rules_"):
        lang = data.replace("rules_", "")

        rules_text = {
            "zh": "📌 群规则：\n\n1. 禁止广告\n2. 禁止私信骚扰群友\n3. 禁止刷屏\n4. 有问题请联系客服",
            "ms": "📌 Peraturan Group:\n\n1. Dilarang spam iklan\n2. Jangan ganggu ahli lain\n3. Jangan flood mesej\n4. Ada masalah sila hubungi CS",
            "id": "📌 Peraturan Grup:\n\n1. Dilarang spam iklan\n2. Jangan ganggu member lain\n3. Jangan kirim pesan berlebihan\n4. Hubungi CS jika perlu",
            "en": "📌 Group Rules:\n\n1. No spam ads\n2. Do not disturb members\n3. No message flooding\n4. Contact support if needed",
        }

        await query.message.reply_text(rules_text.get(lang, rules_text["ms"]))


async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    user = update.effective_user

    if any(bad in text for bad in BAD_WORDS):
        try:
            await update.message.delete()
            await update.message.chat.ban_member(user.id)
        except Exception as e:
            logging.warning(f"Anti spam failed: {e}")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Bot is running.\n\n"
        "Welcome Bot: ✅\n"
        "Multi-language: ✅\n"
        "Anti-spam: ✅\n"
        "USDT welcome text: ✅"
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
