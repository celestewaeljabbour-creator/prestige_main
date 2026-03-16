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

# --- وظائف الأدمن ---

@bot.callback_query_handler(func=lambda call: call.data == "admin_main")
def admin_panel(call):
    time.sleep(0.5)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 تعميم صفقة جديدة", callback_data="adm_trade"),
        types.InlineKeyboardButton("✅ تعميم نتيجة صفقة", callback_data="adm_result"),
        types.InlineKeyboardButton("➕ إضافة وكيل ذهبي", callback_data="adm_add_agent"),
        types.InlineKeyboardButton("📊 إحصائيات المستخدمين", callback_data="adm_stats"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="home")
    )
    bot.edit_message_text("👑 **لوحة الإدارة العليا**\nتحكم بالبوت والوكلاء والرسائل الجماعية:", call.from_user.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "adm_stats")
def get_stats(call):
    count = db.table("users").select("id", count='exact').execute().count
    bot.answer_callback_query(call.id, f"إجمالي المستخدمين: {count}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "adm_add_agent")
def ask_agent_id(call):
    msg = bot.send_message(call.from_user.id, "أرسل ID المستخدم لترقيته لوكيل ذهبي:")
    bot.register_next_step_handler(msg, process_agent)

def process_agent(message):
    try:
        uid = int(message.text)
        db.table("users").update({"is_agent": True}).eq("id", uid).execute()
        bot.send_message(ADMIN_ID, f"✅ تم تعيين `{uid}` كوكيل ذهبي.")
        bot.send_message(uid, "🎊 مبروك! تم منحك رتبة **وكيل ذهبي**.")
    except: bot.send_message(ADMIN_ID, "❌ خطأ في الـ ID.")

# --- نظام التعميم ---

def broadcast(message, title):
    users = db.table("users").select("id").execute().data
    bot.send_message(ADMIN_ID, "⏳ بدأت عملية التعميم...")
    for u in users:
        try:
            time.sleep(0.1)
            bot.send_message(u['id'], f"{title}\n\n{message.text}", parse_mode="Markdown")
        except: continue
    bot.send_message(ADMIN_ID, "✅ تم الإرسال للجميع.")

@bot.callback_query_handler(func=lambda call: call.data == "adm_trade")
def trade_input(call):
    msg = bot.send_message(ADMIN_ID, "اكتب تفاصيل الصفقة الجديدة:")
    bot.register_next_step_handler(msg, broadcast, "🚨 **صفقة جديدة من الإدارة**")

@bot.callback_query_handler(func=lambda call: call.data == "adm_result")
def result_input(call):
    msg = bot.send_message(ADMIN_ID, "اكتب نتيجة الصفقة:")
    bot.register_next_step_handler(msg, broadcast, "✅ **تحديث نتيجة التداول**")

# --- معالجة الأزرار العامة ---

@bot.callback_query_handler(func=lambda call: True)
def handle_all_btns(call):
    uid = call.from_user.id
    mid = call.message.message_id
    
    # تأخير "الرزانة"
    time.sleep(0.5)
    bot.answer_callback_query(call.id)

    if call.data == "home":
        bot.edit_message_text("القائمة الرئيسية لمنصة Prestige:", uid, mid, reply_markup=main_kb(uid))

    elif call.data == "wallet":
        res = db.table("users").select("balance").eq("id", uid).execute()
        bal = res.data[0]['balance'] if res.data else 0.0
        bot.edit_message_text(f"👤 **محفظتي**\n\n💰 الرصيد المتاح: `{bal}$`", uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "team":
        link = f"https://t.me/Prestige_Trading_Bot?start={uid}"
        bot.edit_message_text(f"👥 **فريقك**\n\nرابط دعوتك:\n`{link}`\n\nعمولتك: 5% من إيداعات فريقك.", uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "earn":
        txt = ("💰 **اربح من الترويج**\n\n"
               "📹 تيك توك/يوتيوب: 10$ لكل 2000 مشاهدة.\n"
               "شرط وجود صورة البوت والهاشتاقات: #Prestige_Trading\n"
               "ارسل الرابط للدعم للمراجعة.")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb())

    elif call.data == "prizes":
        txt = ("🎁 **مسابقة الانطلاق (أول 10 أشخاص لكل فئة)**\n\n"
               "• 10 متداولين (إيداع 50$) ⬅️ **iPhone 15 Pro Max**\n"
               "• 10 متداولين (إيداع 25$) ⬅️ **iPhone 13 Pro**\n"
               "• 10 متداولين (إيداع 15$) ⬅️ **Xiaomi**\n"
               "• 10 متداولين (إيداع 10$) ⬅️ **Smart Watch**\n"
               "• 10 متداولين (إيداع 5$) ⬅️ **سماعات Bluetooth**\n\n"
               "اللعبة لعبة سرعة! خلص مطلوبك واستلم.")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb())

    elif call.data == "bot_trades":
        bot.edit_message_text("📊 **صفقات البوت**\n\nانتظر إشعارات الإدارة هنا لنسخ الصفقات فور صدورها.", uid, mid, reply_markup=back_kb())

    elif call.data == "withdraw":
        bot.edit_message_text("📤 **سحب الأرباح**\n\nأقل مبلغ للسحب هو 10$. رصيدك حالياً لا يسمح.", uid, mid, reply_markup=back_kb())

    elif call.data == "trade_ai":
        bot.edit_message_text("📈 **التداول الآلي**\n\nيتم حالياً تطوير ذكاء اصطناعي لفتح الصفقات تلقائياً. انتظرونا!", uid, mid, reply_markup=back_kb())

    elif call.data == "agents":
        bot.edit_message_text("🤵 **قسم الوكلاء**\n\nراتب شهري 100$ للوكلاء النشطين (فريق فوق 50 شخص). تواصل مع الدعم للتقديم.", uid, mid, reply_markup=back_kb())

    elif call.data == "deposit":
        bot.edit_message_text("📥 **إيداع**\n\nأرسل صورة الإيصال للدعم بعد التحويل لـ:\nUSDT: `0xbe3a3...`", uid, mid, reply_markup=back_kb())

# --- الأوامر ---

@bot.message_handler(commands=['start'])
def start_msg(message):
    time.sleep(0.5)
    bot.send_message(message.from_user.id, "💎 أهلاً بك في فخر التداول.. نظام Prestige جاهز.", reply_markup=main_kb(message.from_user.id))

bot.infinity_polling()
