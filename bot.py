import telebot
from telebot import types
from supabase import create_client, Client

# --- الإعدادات النهائية (التوكنات الجديدة) ---
TOKEN = "8795395476:AAFVU9fXwQF8dwlh8kSnK1Z9GnOY4VEag8Q" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht"
ADMIN_ID = 6091303835 

# بيانات الدفع
USDT_WALLET = "0xbe3a3F17f1574EE9483eab41B9EE2022Ec316149"
SYRIATEL_CASH = "92274277 - 26092765 - 64288797 - 15260106"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# دالة لتوليد القائمة الرئيسية (Inline)
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📥 إيداع", callback_data="deposit"),
        types.InlineKeyboardButton("📤 سحب", callback_data="withdraw"),
        types.InlineKeyboardButton("👤 محفظتي", callback_data="wallet"),
        types.InlineKeyboardButton("👥 فريقي", callback_data="team"),
        types.InlineKeyboardButton("🛠 الدعم الفني", callback_data="support")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "عزيزي المشترك"
    
    # تسجيل في السوبا
    try:
        supabase.table("users").upsert({"id": user_id, "username": username}).execute()
    except: pass

    welcome_msg = (
        f"✨ **مرحباً بك في عالم Prestige Trading** ✨\n\n"
        f"عزيزي {username}، أنت الآن متصل بأقوى نظام تداول آلي.\n"
        f"استخدم الأزرار أدناه لإدارة استثماراتك."
    )
    bot.send_message(user_id, welcome_msg, reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "main_menu":
        bot.edit_message_text("اختر من القائمة الرئيسية:", chat_id, message_id, reply_markup=main_menu())

    elif call.data == "deposit":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("USDT (BEP20)", callback_data="pay_usdt"))
        markup.add(types.InlineKeyboardButton("سيريتل كاش", callback_data="pay_syriatel"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
        bot.edit_message_text("💎 **قسم الإيداع**\n\nاختر وسيلة الدفع المناسبة لك:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("pay_"):
        method = "USDT BEP20" if "usdt" in call.data else "سيريتل كاش"
        address = USDT_WALLET if "usdt" in call.data else SYRIATEL_CASH
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="deposit"))
        
        pay_msg = f"✅ **تم اختيار {method}**\n\nيرجى التحويل إلى:\n`{address}`\n\nبعد التحويل، أرسل سكرين شوت (صورة) للعملية هنا."
        bot.edit_message_text(pay_msg, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ["withdraw", "wallet", "team", "support"]:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
        bot.edit_message_text("🚧 هذا القسم قيد التجهيز وسيتم تفعيله خلال ساعات.", chat_id, message_id, reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # إرسال للأدمن
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(ADMIN_ID, f"🔔 **إشعار إيداع جديد!**\nمن المستخدم: @{message.from_user.username}\nID: `{message.from_user.id}`", parse_mode="Markdown")
    bot.reply_to(message, "✅ **تم استلام الصورة**\nجاري تدقيق العملية من قبل الإدارة وسوف يتم شحن رصيدك فوراً.")

bot.infinity_polling()
