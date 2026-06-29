import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

BOT_TOKEN = "8934195042:AAFgnJ5x4FlZ73mS1CYRQ6DDIDJHn9va47k"
CHANNEL_USERNAME = "@FWarriorsbot"
WEBHOOK_URL = "https://your-app-name.onrender.com"  # Render URL

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

user_lang = {}

TEXTS = {
    "uz": {
        "welcome": "Assalomu alaykum! Botga xush kelibsiz 🎉",
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
        "subscribe": "Botdan foydalanish uchun kanalga obuna bo'ling 👇",
        "check_btn": "✅ Obunani tekshirish",
        "not_subscribed": "❌ Siz hali obuna bo'lmagansiz!",
        "lang_set": "Til o'rnatildi: O'zbek 🇺🇿",
    },
    "ru": {
        "welcome": "Привет! Добро пожаловать в бот 🎉",
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
        "subscribe": "Подпишитесь на канал, чтобы использовать бота 👇",
        "check_btn": "✅ Проверить подписку",
        "not_subscribed": "❌ Вы ещё не подписаны!",
        "lang_set": "Язык установлен: Русский 🇷🇺",
    },
    "en": {
        "welcome": "Hello! Welcome to the bot 🎉",
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
        "subscribe": "Please subscribe to the channel to use the bot 👇",
        "check_btn": "✅ Check subscription",
        "not_subscribed": "❌ You are not subscribed yet!",
        "lang_set": "Language set: English 🇬🇧",
    },
}

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def lang_keyboard():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    )
    return kb

def subscribe_keyboard(lang):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 Kanalga o'tish", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}"))
    kb.add(InlineKeyboardButton(TEXTS[lang]["check_btn"], callback_data="check_sub"))
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        TEXTS["uz"]["choose_lang"],
        reply_markup=lang_keyboard()
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def set_language(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang
    bot.answer_callback_query(call.id, TEXTS[lang]["lang_set"])
    
    if is_subscribed(call.from_user.id):
        bot.send_message(call.message.chat.id, TEXTS[lang]["welcome"])
    else:
        bot.send_message(
            call.message.chat.id,
            TEXTS[lang]["subscribe"],
            reply_markup=subscribe_keyboard(lang)
        )

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_subscription(call):
    uid = call.from_user.id
    lang = user_lang.get(uid, "uz")
    
    if is_subscribed(uid):
        bot.answer_callback_query(call.id, "✅")
        bot.send_message(call.message.chat.id, TEXTS[lang]["welcome"])
    else:
        bot.answer_callback_query(call.id, TEXTS[lang]["not_subscribed"], show_alert=True)

# Webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

# Webhook o'rnatish
@app.route("/set_webhook")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    return "Webhook set!", 200

@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
