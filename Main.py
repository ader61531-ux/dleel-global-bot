
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

CATEGORIES = {
    "trade": "🛒 البيع والشراء",
    "property": "🏠 العقارات والأراضي",
    "services": "🔧 المهن والخدمات",
    "companies": "🏢 الشركات والمحلات",
    "network": "🤝 العلاقات والتواصل",
    "other": "🌍 وساطة عامة"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("العربية 🇸🇦", callback_data="lang_ar")],
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")]
    ]
    await update.message.reply_text(
        "مرحباً بك في DLEEL Global 🌍\n"
        "منصة الوساطة والخدمات العالمية.\n\n"
        "Choose your language / اختر لغتك:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data.startswith("lang_"):
        context.user_data["lang"] = data[-2:]
        lang = data[-2:]
        if lang == "ar":
            text = "اختر القسم الذي تبحث عنه:"
            rows = [
                [InlineKeyboardButton(v, callback_data="cat_" + k)]
                for k, v in CATEGORIES.items()
            ]
        else:
            text = "Choose the service you need:"
            names = {
                "trade": "🛒 Trade & Shopping",
                "property": "🏠 Real Estate",
                "services": "🔧 Services & Jobs",
                "companies": "🏢 Companies & Shops",
                "network": "🤝 Business Networking",
                "other": "🌍 General Mediation"
            }
            rows = [
                [InlineKeyboardButton(v, callback_data="cat_" + k)]
                for k, v in names.items()
            ]
        await q.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(rows)
        )

    elif data.startswith("cat_"):
        key = data[4:]
        context.user_data["category"] = CATEGORIES[key]
        context.user_data["waiting"] = True
        lang = context.user_data.get("lang", "ar")
        text = (
            "اكتب تفاصيل طلبك، وسنتواصل معك."
            if lang == "ar" else
            "Please describe what you need. We will contact you."
        )
        await q.edit_message_text(text)

async def receive_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting"):
        return

    user = update.effective_user
    category = context.user_data.get("category", "غير محدد")
    request = update.message.text
    username = f"@{user.username}" if user.username else "لا يوجد"

    admin_text = (
        "📩 طلب وساطة جديد - DLEEL Global\n\n"
        f"القسم: {category}\n"
        f"الاسم: {user.full_name}\n"
        f"المستخدم: {username}\n"
        f"رقم المستخدم: {user.id}\n"
        f"الطلب:\n{request}"
    )

    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID), text=admin_text
            )
        except Exception:
            pass

    context.user_data["waiting"] = False
    await update.message.reply_text(
        "شكراً لك! تم استلام طلبك وسنراجع تفاصيله ونتواصل معك. 🤝"
    )
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, receive_request
    ))
    print("DLEEL Global Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
