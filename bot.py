import os
import telebot
from telebot import types
from supabase import create_client, Client

# --- البيانات الثابتة (تعبئة آلية كما طلبت) ---
TOKEN = "7544026369:AAGD5VfH0mE_G6i9F6F5F6F5F6F5F6" # التوكن الخاص بك
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # مفتاح سوبابيس
ADMIN_ID = 6091303835 # ايدي الإدارة الخاص بك

# --- بيانات الدفع الخاصة بك ---
USDT_WALLET = "0xbe3a3F17f1574EE9483eab41B9EE2022Ec316149"
SYRIATEL_CASH = "92274277 - 26092765 - 64288797 - 15260106"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📥 إيداع", "📤 سحب", "👤 محفظتي", "👥 فريقي", "🛠 الدعم الفني")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Prestige_User"
    
    user_data = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user_data.data:
        referrer_id = None
        if len(message.text.split()) > 1:
            referrer_id = message.text.split()[1]
            
        supabase.table("users").insert({
            "id": user_id,
            "username": username,
            "balance": 0,
            "referred_by": referrer_id,
            "role": "user",
            "active_refs": 0,
            "commission_rate": 5 
        }).execute()
        
    bot.send_message(user_id, "👑 أهلاً بك في Prestige Trading Bot\nالسيستم الأقوى لإدارة التداول والعمولات الآلية.", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📥 إيداع")
def deposit(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("USDT (BEP20)", callback_data="pay_usdt"))
    markup.add(types.InlineKeyboardButton("سيريتل كاش", callback_data="pay_syriatel"))
    bot.send_message(message.chat.id, "اختر وسيلة الإيداع المفضلة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def payment_details(call):
    if call.data == "pay_usdt":
        msg = f"حول لعنوان USDT BEP20:\n\n`{USDT_WALLET}`"
    else:
        msg = f"حول لأحد أرقام سيريتل كاش:\n\n`{SYRIATEL_CASH}`\n\n(يتم إضافة عمولة 5% على إيداع سيريتل)"
    
    bot.send_message(call.message.chat.id, f"{msg}\n\n⚠️ أرسل صورة التحويل الآن لتوثيق العملية.", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"approve_{message.from_user.id}"),
               types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{message.from_user.id}"))
    
    bot.send_message(ADMIN_ID, f"📩 طلب إيداع من: @{message.from_user.username}\nID: {message.from_user.id}", reply_markup=markup)
    bot.reply_to(message, "✅ تم استلام الصورة، بانتظار تأكيد الإدارة.")

@bot.callback_query_handler(func=lambda call: call.data.startswith(('approve_', 'reject_')))
def admin_action(call):
    user_id = int(call.data.split('_')[1])
    if "approve" in call.data:
        user_info = supabase.table("users").select("*").eq("id", user_id).execute().data[0]
        referrer_id = user_info.get('referred_by')
        
        if referrer_id:
            ref_data = supabase.table("users").select("*").eq("id", referrer_id).execute().data[0]
            new_refs = ref_data['active_refs'] + 1
            new_rate = 15 if new_refs >= 20 else 10 if ref_data['role'] == 'agent' else 5
            
            supabase.table("users").update({"active_refs": new_refs, "commission_rate": new_rate}).eq("id", referrer_id).execute()

        bot.send_message(user_id, "🎉 تم تأكيد إيداعك بنجاح!")
    else:
        bot.send_message(user_id, "❌ تم رفض طلبك، تواصل مع الدعم.")
    bot.answer_callback_query(call.id)

bot.polling(none_stop=True)
