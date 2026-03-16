import telebot
from telebot import types
from supabase import create_client, Client
import time

# --- الإعدادات الفنية ---
TOKEN = "8795395476:AAFVU9fXwQF8dwlh8kSnK1Z9GnOY4VEag8Q" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht"
ADMIN_ID = 6091303835 
SUPPORT_USER = "@tradinghubsy"

# عناوين الإيداع
USDT_ADDR = "0xbe3a3F17f1574EE9483eab41B9EE2022Ec316149"
SYRIATEL_CASH = "92274277 - 26092765"

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
        types.InlineKeyboardButton("🤵 جوائز الوكلاء", callback_data="agents"),
        types.InlineKeyboardButton("🛠 الدعم الفني", url=f"https://t.me/{SUPPORT_USER[1:]}")
    )
    if uid == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👑 لوحة تحكم الأدمن", callback_data="admin_main"))
    return markup

def back_kb():
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة للقائمة", callback_data="home"))

# --- الأوامر الأساسية ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    uname = message.from_user.username or "Prestige_User"
    
    bot.send_message(uid, "💎 جاري تهيئة نظام Prestige...", reply_markup=types.ReplyKeyboardRemove())
    
    ref_by = None
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_by = int(args[1]) if int(args[1]) != uid else None

    try:
        db.table("users").upsert({"id": uid, "username": uname, "referred_by": ref_by}).execute()
        if ref_by:
            db.rpc('increment_refs', {'user_id': ref_by}).execute()
    except: pass

    welcome = (f"🏆 **منصة Prestige Trading**\n\n"
               f"أهلاً بك {uname} في أقوى سيستم تداول.\n"
               f"حسابك جاهز الآن لتحقيق الأرباح.\n\n"
               f"💰 رصيدك الحالي: **0.00$**")
    bot.send_message(uid, welcome, reply_markup=main_kb(uid), parse_mode="Markdown")

# --- دوال الإرسال الجماعي (للأدمن) ---
def send_broadcast_trade(message):
    bot.send_message(ADMIN_ID, "⏳ جاري إرسال الصفقة للجميع...")
    try:
        users = db.table("users").select("id").execute().data
        count = 0
        for u in users:
            try:
                bot.send_message(u['id'], f"🚨 **صفقة جديدة من الإدارة** 🚨\n\n{message.text}")
                count += 1
            except: pass
        bot.send_message(ADMIN_ID, f"✅ تم إرسال الصفقة بنجاح إلى {count} متداول.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ خطأ: {e}")

def send_broadcast_result(message):
    bot.send_message(ADMIN_ID, "⏳ جاري إرسال النتيجة للجميع...")
    try:
        users = db.table("users").select("id").execute().data
        count = 0
        for u in users:
            try:
                bot.send_message(u['id'], f"💰 **تحديث نتيجة الصفقة** 💰\n\n{message.text}")
                count += 1
            except: pass
        bot.send_message(ADMIN_ID, f"✅ تم إرسال النتيجة بنجاح إلى {count} متداول.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ خطأ: {e}")

# --- معالجة الضغطات ---

@bot.callback_query_handler(func=lambda call: True)
def handle_btns(call):
    uid = call.from_user.id
    mid = call.message.message_id

    # تأخير خفيف جداً يمنع التعليق ويوحي بالانتقال الطبيعي
    bot.answer_callback_query(call.id, "جاري المعالجة...")
    time.sleep(0.3) 

    if call.data == "home":
        bot.edit_message_text("القائمة الرئيسية للمنصة:", uid, mid, reply_markup=main_kb(uid))

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
