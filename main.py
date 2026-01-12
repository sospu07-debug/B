import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatMemberStatus

# ================== الإعدادات ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL = "@YUXU_21"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# ================== الأزرار ==================
MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["🤖 تشغيل الذكاء الاصطناعي"],
        ["🔧 حسابات المطور"]
    ],
    resize_keyboard=True
)

# ================== المتغيرات ==================
user_history = {}
ai_enabled = {}

# ================== تحقق الاشتراك ==================
async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_subscribed(context.bot, user_id):
        await update.message.reply_text(
            "🚫 لازم تشترك بالقناة أولاً:\n"
            f"https://t.me/{CHANNEL.replace('@','')}"
        )
        return

    ai_enabled[user_id] = False

    await update.message.reply_text(
        "👋 أهلاً في البوت\nاختار من الأزرار 👇",
        reply_markup=MAIN_MENU
    )

# ================== الدردشة ==================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if not await is_subscribed(context.bot, user_id):
        await update.message.reply_text(
            "🚫 لازم تشترك بالقناة أولاً:\n"
            f"https://t.me/{CHANNEL.replace('@','')}"
        )
        return

    if text == "🔧 حسابات المطور":
        await update.message.reply_text(
            "👨‍💻 حسابات المطور:\n"
            "📌 Telegram: @rrz3u\n"
            "📌 Channel: https://t.me/YUXU_21\n"
            "📌 Instagram: rrz3u",
            reply_markup=MAIN_MENU
        )
        return

    if text == "🤖 تشغيل الذكاء الاصطناعي":
        ai_enabled[user_id] = True
        user_history[user_id] = [
            {
                "role": "system",
                "content": (
                    "أنت مساعد ذكاء اصطناعي ذكي المستوى، "
                    "تفهم السؤال قبل الإجابة وتقدم ردود دقيقة "
                    "وبأسلوب عربي بشري طبيعي."
                )
            }
        ]
        await update.message.reply_text(
            "🤖 تم تشغيل الذكاء الاصطناعي\nاسأل الآن 👇",
            reply_markup=MAIN_MENU
        )
        return

    if not ai_enabled.get(user_id):
        await update.message.reply_text(
            "⚠️ اضغط (🤖 تشغيل الذكاء الاصطناعي) أولاً",
            reply_markup=MAIN_MENU
        )
        return

    user_history[user_id].append({"role": "user", "content": text})
    user_history[user_id] = user_history[user_id][-25:]

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": user_history[user_id],
        "temperature": 0.85,
        "max_tokens": 800
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=data, timeout=30)
        answer = r.json()["choices"][0]["message"]["content"]
    except:
        await update.message.reply_text("❌ صار خطأ، حاول مرة ثانية.")
        return

    user_history[user_id].append({"role": "assistant", "content": answer})
    await update.message.reply_text(answer)

# ================== تشغيل البوت ==================
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()

if __name__ == "__main__":
    main()
