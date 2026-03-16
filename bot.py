import telebot
from telebot import types
from supabase import create_client, Client
import time

# --- الإعدادات الفنية ---
TOKEN = "8795395476:AAFVU9fXwQF8dwlh8kSnK1Z9GnOY4VEag8Q" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht"
ADMIN_ID = 6091303835 

bot = telebot.TeleBot(TOKEN)
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- كيبوردات الواجهة ---

def main_kb(uid):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📥 إيداع رصيد", callback_data="deposit"),
        types.InlineKeyboardButton("📤 سحب أرباح", callback_data="withdraw"),
        types.InlineKeyboardButton("👤 محفظتي", callback_data="wallet"),
        types.InlineKeyboardButton("👥 فريقي", callback_data="team"),
        types.InlineKeyboardButton("📈 تداول آلي (AI)", callback_data="trade_ai"),
        types.InlineKeyboardButton("📊 صفقات البوت", callback_data="bot_trades"),
        types.InlineKeyboardButton("💰 اربح معنا", callback_data="earn"),
        types.InlineKeyboardButton("🎁 جوائز الإحالات", callback_data="prizes"),
        types.InlineKeyboardButton("🏆 الوكيل الذهبي", callback_data="agents"),
        types.InlineKeyboardButton("🛠 الدعم الفني", url="https://t.me/tradinghubsy")
    )
    if uid == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👑 لوحة تحكم الأدمن", callback_data="admin_main"))
    return markup

def back_kb():
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة للقائمة", callback_data="home"))

# --- أوامر الأدمن ---

@bot.callback_query_handler(func=lambda call: call.data == "admin_main")
def admin_panel(call):
    if call.from_user.id != ADMIN_ID: return
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 تعميم صفقة جديدة", callback_data="adm_send_trade"),
        types.InlineKeyboardButton("✅ تعميم نتيجة صفقة", callback_data="adm_send_result"),
        types.InlineKeyboardButton("👥 إدارة الوكلاء الذهبيين", callback_data="adm_manage_agents"),
        types.InlineKeyboardButton("📊 إحصائيات البوت", callback_data="adm_stats"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="home")
    )
    bot.edit_message_text("👑 **لوحة التحكم العليا**\nأهلاً بك يا زعيم، اختر ما تريد التحكم به:", call.from_user.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "adm_stats")
def bot_stats(call):
    count = db.table("users").select("id", count='exact').execute().count
    bot.answer_callback_query(call.id, f"عدد المستخدمين الكلي: {count}")

@bot.callback_query_handler(func=lambda call: call.data == "adm_manage_agents")
def manage_agents_kb(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ إضافة وكيل", callback_data="add_agent_flow"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_main"))
    bot.edit_message_text("🛠 **إدارة الوكلاء**\nيمكنك منح صلاحيات الوكيل الذهبي للمستخدمين عبر الـ ID:", call.from_user.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add_agent_flow")
def ask_id(call):
    msg = bot.send_message(call.from_user.id, "ارسل ID المستخدم المراد ترقيته:")
    bot.register_next_step_handler(msg, process_agent_upgrade)

def process_agent_upgrade(message):
    try:
        uid = int(message.text)
        db.table("users").update({"is_agent": True}).eq("id", uid).execute()
        bot.send_message(ADMIN_ID, f"✅ تم تفعيل الوكيل الذهبي لـ `{uid}`")
        bot.send_message(uid, "🎊 تهانينا! تمت ترقيتك إلى **وكيل ذهبي**.")
    except: bot.send_message(ADMIN_ID, "❌ خطأ في الـ ID.")

# --- الأقسام العامة ---

@bot.callback_query_handler(func=lambda call: call.data == "earn")
def earn_section(call):
    time.sleep(0.6)
    txt = ("💰 **قسم اربح معنا (المروجين)**\n\n"
           "اربح دولارات مقابل الترويج للبوت:\n\n"
           "📹 **فيديو (تيك توك/يوتيوب):**\n"
           "• يجب أن يظهر البوت وصورته بشكل واضح.\n"
           "• استخدم هاشتاقات: #Prestige_Trading #تداول\n"
           "• المكافأة: 10$ لكل 2000 مشاهدة.\n\n"
           "📸 **منشورات اجتماعية:**\n"
           "• نشر الرابط في مجموعات تداول كبرى.\n\n"
           "ارسل رابط عملك للدعم الفني للتقييم.")
    bot.edit_message_text(txt, call.from_user.id, call.message.message_id, reply_markup=back_kb())

@bot.callback_query_handler(func=lambda call: call.data == "team")
def team_section(call):
    uid = call.from_user.id
    link = f"https://t.me/Prestige_Trading_Bot?start={uid}"
    txt = (f"👥 **نظام الشركاء**\n\n"
           f"رابط دعوتك الحصري:\n`{link}`\n\n"
           f"اربح عمولة 5% على كل إيداع يقوم به فريقك.")
    bot.edit_message_text(txt, uid, call.message.message_id, reply_markup=back_kb(), parse_mode="Markdown")

# --- نظام التعميم (Broadcast) ---

def broadcast_logic(message, title):
    bot.send_message(ADMIN_ID, "⏳ جاري الإرسال للجميع مع التأخير البرمجي...")
    users = db.table("users").select("id").execute().data
    for u in users:
        try:
            time.sleep(0.1) # التأخير المطلوب لمنع الحظر والتعليق
            bot.send_message(u['id'], f"{title}\n\n{message.text}", parse_mode="Markdown")
        except: continue
    bot.send_message(ADMIN_ID, "✅ تم اكتمال الإرسال.")

@bot.callback_query_handler(func=lambda call: call.data == "adm_send_trade")
def trade_msg(call):
    msg = bot.send_message(ADMIN_ID, "ارسل نص الصفقة الآن:")
    bot.register_next_step_handler(msg, broadcast_logic, "🚨 **صفقة جديدة من الإدارة**")

@bot.callback_query_handler(func=lambda call: call.data == "adm_send_result")
def result_msg(call):
    msg = bot.send_message(ADMIN_ID, "ارسل نص النتيجة الآن:")
    bot.register_next_step_handler(msg, broadcast_logic, "✅ **تحديث نتيجة التداول**")

# --- التشغيل الأساسي ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    time.sleep(0.5)
    bot.send_message(message.from_user.id, "💎 جاري تهيئة نظام Prestige...", reply_markup=main_kb(message.from_user.id))

@bot.callback_query_handler(func=lambda call: call.data == "home")
def home_btn(call):
    bot.edit_message_text("القائمة الرئيسية:", call.from_user.id, call.message.message_id, reply_markup=main_kb(call.from_user.id))

bot.infinity_polling()
    elif call.data == "wallet":
        res = db.table("users").select("balance").eq("id", uid).execute()
        bal = res.data[0]['balance'] if res.data else 0.0
        txt = (f"👤 **مركزك المالي**\n\n"
               f"💰 الرصيد المتاح: `{bal}$`\n"
               f"📉 أرباح التداول: `0.00$`\n"
               f"🎁 بونص الإحالات: `0.00$`")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "team":
        link = f"https://t.me/Prestige_Trading_Bot?start={uid}"
        txt = (f"👥 **نظام الشركاء**\n\n"
               f"شارك رابطك واربح 5% من إيداعات فريقك.\n\n"
               f"رابط دعوتك الحصري:\n`{link}`")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "bot_trades":
        txt = ("📊 **سجل التداول وصفقات البوت**\n\n"
               "في هذا القسم، تتلقى الإشعارات والتوصيات المباشرة من الإدارة لنسخ الصفقات.\n"
               "انتظر إشعارات البوت عند فتح أو إغلاق أي صفقة لتعرف نسبة الأرباح فوراً.")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "withdraw":
        txt = ("📤 **سحب الأرباح**\n\n"
               "عذراً، رصيدك الحالي غير كافٍ لإجراء عملية السحب. الحد الأدنى للسحب هو 10$.\n"
               "يتم السحب عبر شبكة USDT (BEP20) حصراً.")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "trade_ai":
        txt = ("📈 **التداول الآلي (AI)**\n\n"
               "قريباً سيتم تفعيل روبوت التداول الذكي الخاص بنا لنسخ الصفقات وإدارتها تلقائياً.")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "earn":
        txt = ("💰 **اربح معنا**\n\n"
               "سيتم إطلاق نظام المهام اليومية والمكافآت الإضافية في التحديث القادم. ابقَ على اطلاع!")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "prizes":
        txt = ("🎁 **مسابقة انطلاق البوت الكبرى**\n\n"
               "في مسابقة بالبوت أول ما يفتح فيها 5 أنواع جوائز وكل جائزة مسموحة بس **لأول 10 أشخاص** بيخلصوا المطلوب منهم يعني (50 رابح) وكل فترة تتجدد الجوائز:\n\n"
               "🍎 أول 10 بيجيبوا 10 متداولين يودعوا 50$ ⬅️ **iPhone 15 Pro Max**\n"
               "📱 أول 10 بيجيبوا 10 متداولين يودعوا 25$ ⬅️ **iPhone 13 Pro**\n"
               "📲 أول 10 بيجيبوا 10 متداولين يودعوا 15$ ⬅️ **موبايل Xiaomi**\n"
               "⌚️ أول 10 بيجيبوا 10 متداولين يودعوا 10$ ⬅️ **Smart Watch**\n"
               "🎧 أول 10 بيجيبوا 10 متداولين يودعوا 5$ ⬅️ **سماعات Bluetooth**\n\n"
               "اللعبة مو مين أكتر، اللعبة مين **أسرع** بيجيب الـ 10 متداولين ضمن فئته وبيخلص لياخد الجائزة فوراً قبل ما يخلصوا الكراسي الـ 10. السباق سيبدأ مع الانطلاق!")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "agents":
        txt = ("🤵 **برنامج الوكلاء (VIP)**\n\n"
               "الوكيل هو من يملك فريقاً نشطاً فوق الـ 50 شخص.\n\n"
               "💰 **المميزات:**\n"
               "• راتب شهري ثابت: **100$**.\n"
               "• نسبة عمولة ترتفع لـ **10%**.\n"
               "• دعم فني خاص متاح 24/7.\n\n"
               "تواصل مع الإدارة لطلب الترقية.")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "deposit":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("USDT (BEP20) ⚡️", callback_data="p_usdt"),
            types.InlineKeyboardButton("Syriatel Cash 🇸🇾", callback_data="p_cash"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="home")
        )
        bot.edit_message_text("📥 **شحن المحفظة**\nاختر وسيلة الدفع المناسبة:", uid, mid, reply_markup=markup)

    elif call.data.startswith("p_"):
        addr = USDT_ADDR if "usdt" in call.data else SYRIATEL_CASH
        msg = (f"⚠️ **تعليمات الشحن**\n\n"
               f"حول المبلغ المطلوب إلى:\n`{addr}`\n\n"
               f"📸 أرسل صورة الإيصال هنا فوراً ليتم تفعيل رصيدك.")
        bot.edit_message_text(msg, uid, mid, parse_mode="Markdown")

    # --- قسم الإدارة (تعميم الصفقات) ---
    elif call.data == "admin_main":
        if uid == ADMIN_ID:
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("📢 تعميم صفقة جديدة للكل", callback_data="admin_trade"),
                types.InlineKeyboardButton("✅ تعميم نتيجة صفقة (ربح/خسارة)", callback_data="admin_result"),
                types.InlineKeyboardButton("🔙 رجوع", callback_data="home")
            )
            bot.edit_message_text("👑 **لوحة تحكم الأدمن**\nاختر الإجراء المطلوب إرساله للمشتركين:", uid, mid, reply_markup=markup)

    elif call.data == "admin_trade":
        if uid == ADMIN_ID:
            msg = bot.edit_message_text("أرسل الآن تفاصيل الصفقة (العملة، السعر، الرافعة...) ليتم إرسالها لجميع المشتركين:", uid, mid)
            bot.register_next_step_handler(bot.send_message(uid, "اكتب الرسالة الآن:"), send_broadcast_trade)

    elif call.data == "admin_result":
        if uid == ADMIN_ID:
            msg = bot.edit_message_text("أرسل الآن تفاصيل النتيجة (مثال: تم إغلاق صفقة BTC بربح 20% ✅):", uid, mid)
            bot.register_next_step_handler(bot.send_message(uid, "اكتب الرسالة الآن:"), send_broadcast_result)

# --- استلام الصور (إشعارات الإيداع) ---

@bot.message_handler(content_types=['photo'])
def handle_docs(message):
    uid = message.from_user.id
    uname = message.from_user.username or "Unknown"
    
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    caption = (f"🔔 **إشعار إيداع جديد!**\n\n"
               f"👤 المستخدم: @{uname}\n"
               f"🆔 الآيدي: `{uid}`\n"
               f"تأكد من الوصول ثم اشحن الرصيد يدوياً.")
    bot.send_message(ADMIN_ID, caption, parse_mode="Markdown")
    
    bot.reply_to(message, "✅ **تم استلام الإيصال!**\nجاري تدقيق العملية من قبل الإدارة وسوف يتم إشعارك فور التفعيل.")

# --- تشغيل البوت ---
print("🚀 Prestige Bot is running...")
bot.infinity_polling()
