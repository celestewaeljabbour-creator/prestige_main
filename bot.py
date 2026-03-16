import telebot
from telebot import types
from supabase import create_client, Client

# --- الإعدادات (نفس بياناتك الشغالة) ---
TOKEN = "8795395476:AAFVU9fXwQF8dwlh8kSnK1Z9GnOY4VEag8Q" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht"
ADMIN_ID = 6091303835  # معرفك الخاص كأدمن

# بيانات الدفع
USDT_WALLET = "0xbe3a3F17f1574EE9483eab41B9EE2022Ec316149"
SYRIATEL_CASH = "92274277 - 26092765 - 64288797 - 15260106"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- الدوال المساعدة للأزرار ---

def main_menu(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # أزرار المستخدم العادي
    btn_dep = types.InlineKeyboardButton("📥 إيداع", callback_data="deposit")
    btn_wit = types.InlineKeyboardButton("📤 سحب", callback_data="withdraw")
    btn_wal = types.InlineKeyboardButton("👤 محفظتي", callback_data="wallet")
    btn_tea = types.InlineKeyboardButton("👥 فريقي", callback_data="team")
    btn_sup = types.InlineKeyboardButton("🛠 الدعم الفني", callback_data="support")
    
    markup.add(btn_dep, btn_wit, btn_wal, btn_tea)
    markup.add(btn_sup)
    
    # إذا كان المستخدم هو الأدمن، تظهر له لوحة تحكم إضافية
    if user_id == ADMIN_ID:
        btn_adm = types.InlineKeyboardButton("👑 لوحة التحكم (أدمن)", callback_data="admin_panel")
        markup.add(btn_adm)
        
    return markup

# --- معالجة الأوامر ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "عزيزي"
    
    # حذف الكيبورد القديم (مهم جداً مشان ما تضل الأزرار تحت)
    remove_markup = types.ReplyKeyboardRemove()
    
    # تسجيل/تحديث المستخدم بالسوبا
    try:
        supabase.table("users").upsert({"id": user_id, "username": username}).execute()
    except: pass

    welcome_text = (
        f"🏆 **مرحباً بك في Prestige Trading**\n\n"
        f"أهلاً بك يا {username}.. النظام متصل الآن بأحدث تقنيات التداول.\n"
        f"استخدم القائمة أدناه للتحكم بحسابك."
    )
    
    # نرسل الرسالة ونحذف الكيبورد السفلي ونعرض الـ Inline
    bot.send_message(user_id, "تم تحديث النظام..", reply_markup=remove_markup)
    bot.send_message(user_id, welcome_text, reply_markup=main_menu(user_id), parse_mode="Markdown")

# --- معالجة الضغط على الأزرار ---

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    user_id = call.from_user.id

    if call.data == "main_menu":
        bot.edit_message_text("القائمة الرئيسية:", chat_id, msg_id, reply_markup=main_menu(user_id))

    elif call.data == "deposit":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("USDT (BEP20)", callback_data="pay_usdt"))
        markup.add(types.InlineKeyboardButton("سيريتل كاش", callback_data="pay_syriatel"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
        bot.edit_message_text("💰 **قسم الإيداع**\n\nاختر وسيلة الدفع التي تناسبك:", chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("pay_"):
        method = "USDT (BEP20)" if "usdt" in call.data else "سيريتل كاش"
        addr = USDT_WALLET if "usdt" in call.data else SYRIATEL_CASH
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="deposit"))
        
        text = f"✅ **خيار الدفع: {method}**\n\nيرجى التحويل إلى:\n`{addr}`\n\n⚠️ بعد التحويل، أرسل (صورة/سكرين) للعملية هنا."
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "wallet":
        # جلب البيانات من سوبا (كمثال)
        try:
            res = supabase.table("users").select("balance").eq("id", user_id).execute()
            bal = res.data[0]['balance'] if res.data else 0.0
        except: bal = 0.0
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
        text = f"👤 **محفظتك الشخصية**\n\n💰 الرصيد الحالي: {bal}$\n📥 إجمالي الإيداع: 0.0$\n📤 إجمالي السحب: 0.0$"
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "team":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
        text = "👥 **نظام الفريق والعمولات**\n\nرابط الإحالة الخاص بك:\n`https://t.me/Prestige_Trading_Bot?start={user_id}`\n\nعدد فريقك: 0"
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "support":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
        text = "🛠 **الدعم الفني**\n\nإذا واجهت أي مشكلة، اكتبها الآن في رسالة وسنقوم بالرد عليك فوراً."
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "admin_panel" and user_id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📊 إحصائيات", callback_data="adm_stats"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
        bot.edit_message_text("👑 **لوحة تحكم الأدمن**\n\nأهلاً بك يا زعيم، اختر ما تريد التحكم به:", chat_id, msg_id, reply_markup=markup, parse_mode="Markdown")

# --- معالجة الصور (الإيداع) ---

@bot.message_handler(content_types=['photo'])
def handle_deposit_photo(message):
    user_id = message.from_user.id
    username = message.from_user.username or "بدون يوزر"
    
    # تأكيد للمستخدم
    bot.reply_to(message, "✅ **تم استلام الصورة**\nجاري تدقيق العملية من قبل الإدارة وشحن رصيدك.")
    
    # إشعار فوري للأدمن (أنت)
    caption = f"🔔 **إشعار إيداع جديد!**\n\n👤 المستخدم: @{username}\n🆔 الآيدي: `{user_id}`"
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(ADMIN_ID, caption, parse_mode="Markdown")

bot.infinity_polling()
