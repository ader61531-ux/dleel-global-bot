
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

SERVICES = {
    "followers": "📈 نمو المتابعين الحقيقيين",
    "ads": "📢 الحملات الإعلانية والترويج",
    "design": "🎨 التصميم وصناعة المحتوى",
    "management": "📱 إدارة حسابات التواصل",
    "web": "💻 المواقع والمتاجر الإلكترونية",
    "bots": "🤖 إنشاء بوتات تيليغرام",
    "other": "🌍 خدمات رقمية أخرى"
}

PLATFORMS = {
    "telegram": "Telegram",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "tiktok": "TikTok",
    "youtube": "YouTube",
    "whatsapp": "WhatsApp",
    "other": "منصة أخرى"
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    keyboard = [
        [InlineKeyboardButton("العربية 🇸🇦", callback_data="lang_ar")],
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")]
    ]

    await update.message.reply_text(
        "🌍 أهلاً بك في DLEEL GLOBAL\n\n"
        "منصتك العالمية للتسويق والخدمات الرقمية.\n\n"
        "Welcome to DLEEL GLOBAL\n"
        "Choose your language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    data = q.data
    lang = context.user_data.get("lang", "ar")

    if data.startswith("lang_"):
        lang = data[-2:]
        context.user_data["lang"] = lang

        if lang == "ar":
            text = "اختر الخدمة التي تريدها:"
            rows = [
                [InlineKeyboardButton(v, callback_data="service_" + k)]
                for k, v in SERVICES.items()
            ]
        else:
            names = {
                "followers": "📈 Real Audience Growth",
                "ads": "📢 Advertising Campaigns",
                "design": "🎨 Design & Content",
                "management": "📱 Social Media Management",
                "web": "💻 Websites & Online Stores",
                "bots": "🤖 Telegram Bot Development",
                "other": "🌍 Other Digital Services"
            }
            text = "Choose the service you need:"
            rows = [
                [InlineKeyboardButton(v, callback_data="service_" + k)]
                for k, v in names.items()
            ]

        await q.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(rows)
        )

    elif data.startswith("service_"):
        key = data.replace("service_", "", 1)
        if key not in SERVICES:
            return

        context.user_data["service"] = SERVICES[key]

        if lang == "ar":
            text = "اختر المنصة المطلوبة:"
            names = PLATFORMS
        else:
            text = "Choose your platform:"
            names = {
                "telegram": "Telegram",
                "instagram": "Instagram",
                "facebook": "Facebook",
                "tiktok": "TikTok",
                "youtube": "YouTube",
                "whatsapp": "WhatsApp",
                "other": "Other"
            }

        rows = [
            [InlineKeyboardButton(v, callback_data="platform_" + k)]
            for k, v in names.items()
        ]

        await q.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(rows)
        )

    elif data.startswith("platform_"):
        key = data.replace("platform_", "", 1)

        if key not in PLATFORMS:
            return

        context.user_data["platform"] = PLATFORMS[key]
        context.user_data["waiting"] = True

        text = (
            "📝 اكتب تفاصيل طلبك الآن:\n\n"
            "1- رابط الحساب أو الموقع.\n"
            "2- الخدمة المطلوبة.\n"
            "3- العدد أو الميزانية إن وجدت.\n\n"
            "⚠️ لا ترسل كلمة المرور أو رموز التحقق."
            if lang == "ar" else
            "📝 Describe your request:\n\n"
            "1- Account or website link.\n"
            "2- Required service.\n"
            "3- Quantity or budget if available.\n\n"
            "Never send passwords or verification codes."
        )

        await q.edit_message_text(text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "تم إلغاء الطلب. للبدء من جديد أرسل /start"
    )


async def receive_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get("waiting"):
        return

    user = update.effective_user
    request = update.message.text or ""

    if not request.strip() or len(request) > 3500:
        await update.message.reply_text(
            "يرجى إرسال تفاصيل نصية لا تتجاوز 3500 حرف."
        )
        return

    service = context.user_data.get("service", "غير محدد")
    platform = context.user_data.get("platform", "غير محددة")

    username = f"@{user.username}" if user.username else "لا يوجد"

    admin_text = (
        "📩 طلب جديد - DLEEL GLOBAL\n\n"
        f"الخدمة: {service}\n"
        f"المنصة: {platform}\n"
        f"الاسم: {user.full_name}\n"
        f"المستخدم: {username}\n"
        f"رقم المستخدم: {user.id}\n\n"
        f"تفاصيل الطلب:\n{request}"
    )

    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text=admin_text
            )
        except Exception:
            await update.message.reply_text(
                "تعذر إرسال الطلب للإدارة حالياً. حاول لاحقاً."
            )
            return

    context.user_data["waiting"] = False

    lang = context.user_data.get("lang", "ar")

    message = (
        "✅ تم استلام طلبك بنجاح!\n\n"
        "سيقوم فريق DLEEL GLOBAL بمراجعة طلبك والتواصل معك.\n"
        "شكراً لثقتك بنا 🤝"
        if lang == "ar" else
        "✅ Your request has been received!\n\n"
        "Our team will review your request and contact you.\n"
        "Thank you for choosing DLEEL GLOBAL!"
    )

    await update.message.reply_text(message)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_request
        )
    )

    print("DLEEL GLOBAL is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
