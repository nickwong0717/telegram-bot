import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== 环境变量 =====
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

# ===== 链接 =====
REGISTER_LINK = "https://cm8gold.com/r/cm8jess"
GROUP_LINK = "https://t.me/cm8asiaplayer"
CS_LINK = "https://t.me/jessi_cm8"

# ===== 语言内容 =====
LANG = {
    "en": {
        "choose_lang": "Choose Language",
        "welcome": "Welcome 👋\n\nChoose an option:",
        "bonus_btn": "🎁 BONUS",
        "group_btn": "👥 Player Group",
        "cs_btn": "👩‍💼 Live Support 8am-1am GMT+8",
        "lang_btn": "🌐 Language",
    },
    "zh": {
        "choose_lang": "请选择语言",
        "welcome": "欢迎 👋\n\n请选择：",
        "bonus_btn": "🎁 BONUS",
        "group_btn": "👥 玩家群",
        "cs_btn": "👩‍💼 真人客服 8am-1am GMT+8",
        "lang_btn": "🌐 语言",
    },
    "id": {
        "choose_lang": "Pilih Bahasa",
        "welcome": "Selamat datang 👋\n\nSilakan pilih:",
        "bonus_btn": "🎁 BONUS",
        "group_btn": "👥 Grup Pemain",
        "cs_btn": "👩‍💼 Customer Service 8am-1am GMT+8",
        "lang_btn": "🌐 Bahasa",
    }
}

# ===== 语言按钮 =====
def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("English", callback_data="set_en")],
        [InlineKeyboardButton("中文", callback_data="set_zh")],
        [InlineKeyboardButton("Bahasa Indonesia", callback_data="set_id")],
    ])

# ===== 主菜单 =====
def menu(lang):
    t = LANG[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["bonus_btn"], url=REGISTER_LINK)],
        [InlineKeyboardButton(t["group_btn"], url=GROUP_LINK)],
        [InlineKeyboardButton(t["cs_btn"], url=CS_LINK)],
        [InlineKeyboardButton(t["lang_btn"], callback_data="change_lang")],
    ])

# ===== start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User triggered /start")
    await update.message.reply_text(
        "Choose Language / 请选择语言 / Pilih Bahasa",
        reply_markup=lang_keyboard()
    )

# ===== 按钮处理 =====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("set_"):
        lang = query.data.split("_")[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(
            LANG[lang]["welcome"],
            reply_markup=menu(lang)
        )
        return

    lang = context.user_data.get("lang", "en")

    if query.data == "change_lang":
        await query.edit_message_text(
            "Choose Language / 请选择语言 / Pilih Bahasa",
            reply_markup=lang_keyboard()
        )

# ===== main =====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == "__main__":
    main()
