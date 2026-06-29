import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from flask import Flask, request

BOT_TOKEN = "8934195042:AAFgnJ5x4FlZ73mS1CYRQ6DDIDJHn9va47k"
CHANNEL_USERNAME = "@eFWarriors"
WEBHOOK_URL = "https://efwarriors2.onrender.com"
WEBAPP_URL = "https://yusupbaevzamanbek2-create.github.io/eFWarriors2/"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

user_lang = {}

TEXTS = {
    "uz": {
        "choose_lang": "Tilni tanlang:",
        "subscribe": "⚽ *eF Warriors — World Cup 2026*\n\nO'yindan foydalanish uchun avval kanalga obuna bo'ling 👇",
        "check_btn": "✅ Obunani tekshirish",
        "not_subscribed": "❌ Siz hali obuna bo'lmagansiz!",
        "subscribed": "✅ Obuna tasdiqlandi!",
        "open_app": "🎮 O'yinga kirish uchun quyidagi tugmani bosing:",
        "open_btn": "🎮 eF Warriors ga kirish",
    },
    "ru": {
        "choose_lang": "Выберите язык:",
        "subscribe": "⚽ *eF Warriors — World Cup 2026*\n\nПодпишитесь на канал, чтобы использовать бота 👇",
        "check_btn": "✅ Проверить подписку",
        "not_subscribed": "❌ Вы ещё не подписаны!",
        "subscribed": "✅ Подписка подтверждена!",
        "open_app": "🎮 Нажмите кнопку ниже, чтобы войти в игру:",
        "open_btn": "🎮 Войти в eF Warriors",
    },
    "en": {
        "choose_lang": "Choose language:",
        "subscribe": "⚽ *eF Warriors — World Cup 2026*\n\nPlease subscribe to the channel to use the bot 👇",
        "check_btn": "✅ Check subscription",
        "not_subscribed": "❌ You are not subscribed yet!",
        "subscribed": "✅ Subscription confirmed!",
        "open_app": "🎮 Press the button below to enter the game:",
        "open_btn": "🎮 Open eF Warriors",
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

def webapp_keyboard(lang):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        TEXTS[lang]["open_btn"],
        web_app=WebAppInfo(url=WEBAPP_URL)
    ))
    return kb

# QADAM 1: /start → til tanlash
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🌐 *Tilni tanlang / Выберите язык / Choose language:*",
        parse_mode="Markdown",
        reply_markup=lang_keyboard()
    )

# QADAM 2: Til tanlangandan keyin → obuna tekshirish
@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def set_language(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang
    bot.answer_callback_query(call.id)

    if is_subscribed(call.from_user.id):
        # Allaqachon obuna → Web App tugmasi
        bot.send_message(
            call.message.chat.id,
            TEXTS[lang]["open_app"],
            reply_markup=webapp_keyboard(lang)
        )
    else:
        # Obuna emas → obuna sahifasi
        bot.send_message(
            call.message.chat.id,
            TEXTS[lang]["subscribe"],
            parse_mode="Markdown",
            reply_markup=subscribe_keyboard(lang)
        )

# QADAM 3: Obunani tekshirish → Web App tugmasi
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_subscription(call):
    uid = call.from_user.id
    lang = user_lang.get(uid, "uz")

    if is_subscribed(uid):
        bot.answer_callback_query(call.id, TEXTS[lang]["subscribed"])
        bot.send_message(
            call.message.chat.id,
            TEXTS[lang]["open_app"],
            reply_markup=webapp_keyboard(lang)
        )
    else:
        bot.answer_callback_query(call.id, TEXTS[lang]["not_subscribed"], show_alert=True)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

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
    
