import telebot
from telebot import types
from supabase import create_client, Client

# --- البيانات الجديدة والنهائية ---
TOKEN = "8795395476:AAFVU9fXwQF8dwlh8kSnK1Z9GnOY4VEag8Q" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht"
ADMIN_ID = 6091303835 

# بيانات الدفع
USDT_WALLET = "0xbe3a3F17f1574EE9483eab41B9EE2022Ec316149"
SYRIATEL_CASH = "92274277 - 26092765 - 64288797 - 15260106"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "User"
        
        # تسجيل المستخدم في قاعدة البيانات (Supabase)
        supabase.table("users").upsert({
            "id": user_id, 
            "username": username
        }).execute()

        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("📥 إيداع", "📤 سحب", "👤 محفظتي", "👥 فريقي", "🛠 الدعم الفني")
        bot.send_message(user_id, f"👑 أهلاً بك {username} في Prestige Trading\nالسيستم يعمل الآن بنجاح وقاعدة البيانات متصلة.", reply_markup=markup)
    except Exception as e:
        # إذا حدث خطأ في الاتصال بقاعدة البيانات، يستمر البوت في العمل
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("📥 إيداع", "📤 سحب", "👤 محفظتي", "👥 فريقي", "🛠 الدعم الفني")
        bot.send_message(message.chat.id, "👑 أهلاً بك في Prestige Trading\nالبوت جاهز لخدمتك.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📥 إيداع")
def deposit(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("USDT (BEP20)", callback_data="pay_usdt"))
    markup.add(types.InlineKeyboardButton("سيريتل كاش", callback_data="pay_syriatel"))
    bot.send_message(message.chat.id, "اختر وسيلة الإيداع المتاحة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def payment_details(call):
    if call.data == "pay_usdt":
        msg = f"حول لعنوان USDT BEP20:\n\n`{USDT_WALLET}`"
    else:
        msg = f"حول لأحد أرقام سيريتل كاش:\n\n`{SYRIATEL_CASH}`"
    bot.send_message(call.message.chat.id, f"{msg}\n\n⚠️ أرسل صورة التحويل (سكرين شوت) الآن ليتم التأكيد.", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # إرسال صورة التحويل للأدمن فوراً
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.reply_to(message, "✅ تم استلام الصورة، جاري مراجعة العملية من قبل الإدارة.")

# تشغيل البوت بشكل مستمر وتلقائي
bot.infinity_polling()
