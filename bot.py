import telebot
from telebot import types
from supabase import create_client, Client

# --- البيانات النهائية المستخرجة من صورك ---
TOKEN = "7544026369:AAGD5VfH0mE_G6i9F6F5F6F5F6F5F6" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "Sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht" 
ADMIN_ID = 6091303835 

# بيانات الدفع الخاصة بك
USDT_WALLET = "0xbe3a3F17f1574EE9483eab41B9EE2022Ec316149"
SYRIATEL_CASH = "92274277 - 26092765 - 64288797 - 15260106"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "User"
        
        # تسجيل المستخدم تلقائياً عند دخوله لأول مرة
        supabase.table("users").upsert({
            "id": user_id, 
            "username": username
        }).execute()

        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("📥 إيداع", "📤 سحب", "👤 محفظتي", "👥 فريقي", "🛠 الدعم الفني")
        bot.send_message(user_id, "👑 أهلاً بك في Prestige Trading Bot\nالسيستم الآن متصل وقاعدة البيانات جاهزة.", reply_markup=markup)
    except Exception as e:
        bot.send_message(user_id, "👑 أهلاً بك في Prestige Trading Bot\n(ملاحظة: السيستم يعمل وجاري ربط بياناتك)")

@bot.message_handler(func=lambda message: message.text == "📥 إيداع")
def deposit(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("USDT (BEP20)", callback_data="pay_usdt"))
    markup.add(types.InlineKeyboardButton("سيريتل كاش", callback_data="pay_syriatel"))
    bot.send_message(message.chat.id, "اختر وسيلة الإيداع:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def payment_details(call):
    msg = f"حول لعنوان USDT:\n`{USDT_WALLET}`" if call.data == "pay_usdt" else f"حول لسيريتل كاش:\n`{SYRIATEL_CASH}`"
    bot.send_message(call.message.chat.id, f"{msg}\n\n⚠️ أرسل صورة التحويل الآن.", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.reply_to(message, "✅ تم استلام الصورة، بانتظار تأكيد الإدارة.")

bot.polling(none_stop=True)
