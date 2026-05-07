import os
import logging
import re
from datetime import timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
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
GROUP_LINK = "https://t.me/+mlw8J3VjSghlMDU9"
CS_LINK = "https://t.me/jessi_cm8"
WEBSITE_LINK = "https://cm8app.net/"

logging.basicConfig(level=logging.INFO)

user_lang = {}
verified_users = set()
spam_warnings = {}
banned_users = {}

WHITELIST_DOMAINS = set([
    "cm8gold.com",
    "cm8app.net",
    "t.me/jessi_cm8",
    "t.me/+mlw8J3VjSghlMDU9",
])

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

👇 请选择：""",
        "register": "🔥 立即注册",
        "cs": "🧑‍💻 联系客服",
        "group": "📢 CM8 Channel",
        "website": "⬇️ 下载 APP",
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

👇 Pilih sekarang:""",
        "register": "🔥 Daftar Sekarang",
        "cs": "🧑‍💻 Hubungi CS",
        "group": "📢 CM8 Channel",
        "website": "⬇️ Muat Turun App",
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
✔️ Privasi lebih aman
✔️ Support multi-currency

👇 Pilih di bawah:""",
        "register": "🔥 Daftar Sekarang",
        "cs": "🧑‍💻 Hubungi CS",
        "group": "📢 CM8 Channel",
        "website": "⬇️ Download Aplikasi",
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
✔️ Better privacy
✔️ Multi-currency supported

👇 Choose below:""",
        "register": "🔥 Register Now",
        "cs": "🧑‍💻 Contact Support",
        "group": "📢 CM8 Channel",
        "website": "⬇️ Download App",
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


def verify_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Verify / 解锁发言", callback_data=f"verify_{user_id}")]
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
    ])


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False


def is_whitelisted(text: str):
    return any(domain.lower() in text.lower() for domain in WHITELIST_DOMAINS)


def has_domain_or_link(text: str):
    domain_pattern = r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"
    return (
        "http://" in text
        or "https://" in text
        or "t.me/" in text
        or re.search(domain_pattern, text)
    )


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
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
        except Exception as e:
            logging.warning(f"Restrict failed: {e}")

        await update.message.reply_text(
            f"🎉 Welcome {name}!\n\n"
            "Please click Verify to unlock chat.\n"
            "请先点击 Verify 解锁发言。\n"
            "Sila klik Verify dahulu untuk buka chat.",
            reply_markup=verify_keyboard(user.id)
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("verify_"):
        target_user_id = int(data.replace("verify_", ""))

        if query.from_user.id != target_user_id:
            await query.answer("This verify button is not for you.", show_alert=True)
            return

        verified_users.add(target_user_id)

        try:
            await context.bot.restrict_chat_member(
                chat_id=query.message.chat_id,
                user_id=target_user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_audios=True,
                    can_send_documents=True,
                    can_send_photos=True,
                    can_send_videos=True,
                    can_send_video_notes=True,
                    can_send_voice_notes=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_invite_users=True,
                ),
            )

            await query.edit_message_text(
                "✅ Verification successful!\n\n"
                "你已经解锁，可以发言了。\n"
                "Anda sudah boleh mula chat."
            )

            await query.message.reply_text(
                "请选择语言 / Sila pilih bahasa / Please choose language:",
                reply_markup=language_keyboard()
            )

        except Exception as e:
            logging.warning(f"Verify failed: {e}")
            await query.answer("Verify failed. Please contact admin.", show_alert=True)

        return

    if data.startswith("lang_"):
        lang = data.replace("lang_", "")
        user_lang[query.from_user.id] = lang

        name = query.from_user.first_name or "friend"
        await query.edit_message_text(
            text=WELCOME[lang]["text"].format(name=name),
            reply_markup=main_keyboard(lang)
        )


async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text.lower()

    if await is_admin(update, context, user.id):
        return

    if is_whitelisted(text):
        return

    spam_words = [
        "airdrop",
        "free money",
        "bonus link",
        "投资",
        "赚钱",
        "广告",
        "加微信",
        "加我",
    ]

    is_spam = has_domain_or_link(text) or any(word in text for word in spam_words)

    if not is_spam:
        return

    spam_warnings[user.id] = spam_warnings.get(user.id, 0) + 1

    try:
        await update.message.delete()
    except Exception as e:
        logging.warning(f"Delete failed: {e}")

    if spam_warnings[user.id] == 1:
        try:
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=update.message.date + timedelta(minutes=10),
            )

            await update.message.reply_text(
                f"⚠️ {user.first_name}, links or spam words are not allowed.\n"
                "You have been muted for 10 minutes.\n\n"
                "第一次警告：广告/链接不允许，已禁言10分钟。"
            )
        except Exception as e:
            logging.warning(f"Mute failed: {e}")

        return

    if spam_warnings[user.id] >= 2:
        try:
            await update.message.chat.ban_member(user.id)

            banned_users[user.id] = {
                "name": user.first_name or "Unknown",
                "username": user.username or "-",
                "id": user.id,
                "reason": text[:80],
            }

            logging.info(f"BANNED USER => ID:{user.id} USERNAME:@{user.username}")

            await update.message.reply_text(
                f"🚫 User banned for repeated spam: {user.first_name}"
            )
        except Exception as e:
            logging.warning(f"Ban failed: {e}")


async def banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("Only admin can use this command.")
        return

    if not banned_users:
        await update.message.reply_text("✅ Banlist is empty.")
        return

    lines = ["🚫 Banned Users:\n"]
    for user_id, info in banned_users.items():
        lines.append(
            f"ID: {user_id}\n"
            f"Name: {info['name']}\n"
            f"Username: @{info['username']}\n"
            f"Reason: {info['reason']}\n"
        )

    await update.message.reply_text("\n".join(lines[:30]))


async def whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("Only admin can use this command.")
        return

    text = "✅ Whitelist Domains:\n\n" + "\n".join(sorted(WHITELIST_DOMAINS))
    await update.message.reply_text(text)


async def whitelist_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("Only admin can use this command.")
        return

    if not context.args:
        await update.message.reply_text("Use: /whitelist_add domain.com")
        return

    domain = context.args[0].lower().replace("https://", "").replace("http://", "").strip("/")
    WHITELIST_DOMAINS.add(domain)

    await update.message.reply_text(f"✅ Added to whitelist: {domain}")


async def whitelist_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("Only admin can use this command.")
        return

    if not context.args:
        await update.message.reply_text("Use: /whitelist_remove domain.com")
        return

    domain = context.args[0].lower().replace("https://", "").replace("http://", "").strip("/")
    WHITELIST_DOMAINS.discard(domain)

    await update.message.reply_text(f"✅ Removed from whitelist: {domain}")


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("Only admin can use this command.")
        return

    if not context.args:
        await update.message.reply_text("Use: /unban user_id")
        return

    try:
        user_id = int(context.args[0])

        await context.bot.unban_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            only_if_banned=True,
        )

        spam_warnings.pop(user_id, None)
        verified_users.discard(user_id)
        banned_users.pop(user_id, None)

        await update.message.reply_text(f"✅ Unbanned user: {user_id}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Bot Status\n\n"
        "Welcome: ✅\n"
        "Verify Unlock: ✅\n"
        "Anti-spam: ✅\n"
        "First spam: delete + 10 min mute ✅\n"
        "Second spam: ban ✅\n"
        "Banlist: ✅\n"
        "Whitelist: ✅\n\n"
        f"Verified users: {len(verified_users)}\n"
        f"Warnings: {len(spam_warnings)}\n"
        f"Banned recorded: {len(banned_users)}\n"
        f"Whitelist domains: {len(WHITELIST_DOMAINS)}"
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("banlist", banlist))
    app.add_handler(CommandHandler("whitelist", whitelist))
    app.add_handler(CommandHandler("whitelist_add", whitelist_add))
    app.add_handler(CommandHandler("whitelist_remove", whitelist_remove))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
