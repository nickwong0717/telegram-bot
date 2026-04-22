import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== 环境变量 =====
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

REGISTER_LINK = "https://cm8gold.com/r/cm8jess"

# ===== 语言内容 =====
LANG = {
    "en": {
        "welcome": "Welcome 👋\n\nChoose an option:",
        "guide": "Guide:\n\n👉 Start here:\n" + REGISTER_LINK,
        "faq": "FAQ:\n\nType 'start' to continue",
        "start_btn": "Start Now",
        "guide_btn": "Guide",
        "faq_btn": "FAQ",
        "lang_btn": "Language",
    },
    "zh": {
        "welcome": "欢迎 👋\n\n请选择：",
        "guide": "新手指南：\n\n👉 开始请用：\n" + REGISTER_LINK,
        "faq": "常见问题：\n\n输入 开始 继续",
        "start_btn": "立即开始",
        "guide_btn": "新手指南",
        "faq_btn": "常见问题",
        "lang_btn": "语言",
    },
    "id": {
        "welcome": "Selamat datang 👋\n\nSilakan pilih:",
        "guide": "Panduan:\n\n👉 Mulai di sini:\n" + REGISTER_LINK,
        "faq": "FAQ:\n\nKetik mulai",
        "start_btn": "Mulai",
        "guide_btn": "Panduan",
        "faq_btn": "FAQ",
        "lang_btn": "Bahasa",
    }
}

# ===== 按钮 =====
def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("English", callback_data="set_en")],
        [InlineKeyboardButton("中文", callback_data="set_zh")],
        [InlineKeyboardButton("Bahasa Indonesia", callback_data="set_id")],
    ])

def menu(lang):
    t = LANG[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["guide_btn"], callback_data="guide")],
        [InlineKeyboardButton(t["faq_btn"], callback_data="faq")],
        [InlineKeyboardButton(t["start_btn"], url=REGISTER_LINK)],
        [InlineKeyboardButton(t["lang_btn"], callback_data="change_lang")],
    ])

# ===== start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User triggered /start")
    await update.message.reply_text(
        "Choose Language / 请选择语言",
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
    t = LANG[lang]

    if query.data == "guide":
        await query.edit_message_text(t["guide"], reply_markup=menu(lang))
    elif query.data == "faq":
        await query.edit_message_text(t["faq"], reply_markup=menu(lang))
    elif query.data == "change_lang":
        await query.edit_message_text(
            "Choose Language / 请选择语言",
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