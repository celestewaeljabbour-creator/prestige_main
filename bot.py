import telebot
from telebot import types
from supabase import create_client, Client
import time

# --- الإعدادات الأساسية (تأكد من صحتها) ---
TOKEN = "8795395476:AAFVU9fXwQF8dwlh8kSnK1Z9GnOY4VEag8Q" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht"
ADMIN_ID = 6091303835  # الآيدي الخاص بك

# بيانات المحافظ (للعرض فقط)
USDT_ADDR = "0xbe3a3F17f1574EE9483eab41B9EE2022Ec316149"
SYRIATEL_CASH = "92274277 - 26092765"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 1. دوال القوائم الذكية (المنيو) ---

def get_main_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📥 إيداع", callback_data="deposit"),
        types.InlineKeyboardButton("📤 سحب", callback_data="withdraw"),
        types.InlineKeyboardButton("👤 محفظتي", callback_data="wallet"),
        types.InlineKeyboardButton("👥 فريقي", callback_data="team"),
        types.InlineKeyboardButton("📈 تداول الآن", callback_data="trade_now"),
        types.InlineKeyboardButton("🛠 الدعم الفني", callback_data="support")
    )
    # تظهر فقط للأدمن
    if user_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👑 لوحة تحكم الأدمن (VIP)", callback_data="admin_panel"))
    return markup

def admin_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊 إحصائيات النظام الشاملة", callback_data="adm_stats"),
        types.InlineKeyboardButton("📣 إذاعة (رسالة لكل المستخدمين)", callback_data="adm_broadcast"),
        types.InlineKeyboardButton("💰 تعديل رصيد مستخدم", callback_data="adm_edit_bal"),
        types.InlineKeyboardButton("❌ إغلاق المنصة مؤقتاً", callback_data="adm_lock"),
        types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_main")
    )
    return markup

# --- 2. معالجة الأوامر ---

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.from_user.id
    uname = message.from_user.username or "Prestige_User"
    
    # محاولة تسجيل المستخدم في قاعدة البيانات
    try:
        supabase.table("users").upsert({"id": uid, "username": uname}).execute()
    except: pass

    # تنظيف أي كيبورد قديم (ReplyKeyboard) لضمان نظافة الواجهة
    bot.send_message(uid, "💎 **مرحباً بك في منصة Prestige للتداول**", 
                     reply_markup=types.ReplyKeyboardRemove())
    
    msg = (f"مرحباً {uname}!\n\n"
           f"أنت الآن متصل بالخادم الرئيسي.\n"
           f"الحالة: **متصل (Online)** ✅\n\n"
           f"استخدم القائمة أدناه لإدارة استثماراتك.")
    bot.send_message(uid, msg, reply_markup=get_main_keyboard(uid), parse_mode="Markdown")

# --- 3. معالجة التفاعلات (Callback) ---

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    mid = call.message.message_id

    # -- القائمة الرئيسية --
    if call.data == "back_main":
        bot.edit_message_text("القائمة الرئيسية للمنصة:", uid, mid, reply_markup=get_main_keyboard(uid))

    # -- نظام الإحالة (رابط الدعوة) --
    elif call.data == "team":
        # تصحيح الرابط ليظهر آيدي المستخدم تلقائياً
        invite_link = f"https://t.me/Prestige_Trading_Bot?start={uid}"
        text = (f"👥 **نظام الفريق والإحالات**\n\n"
                f"شارك رابطك واربح 5% من كل إيداع يقوم به فريقك.\n\n"
                f"رابطك الخاص:\n`{invite_link}`")
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        bot.edit_message_text(text, uid, mid, reply_markup=markup, parse_mode="Markdown")

    # -- المحفظة --
    elif call.data == "wallet":
        # هنا يتم جلب البيانات من سوبا بايس فعلياً
        user_data = supabase.table("users").select("balance").eq("id", uid).execute()
        balance = user_data.data[0]['balance'] if user_data.data else 0.0
        text = (f"👤 **مركز البيانات المالية**\n\n"
                f"💰 الرصيد المتاح: `{balance}$`\n"
                f"🚀 أرباح التداول اليومية: `0.00$`\n"
                f"📥 إجمالي الإيداعات: `0.00$`")
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        bot.edit_message_text(text, uid, mid, reply_markup=markup, parse_mode="Markdown")

    # -- لوحة تحكم الأدمن --
    elif call.data == "admin_panel":
        if uid == ADMIN_ID:
            bot.edit_message_text("👑 **لوحة التحكم العليا للأدمن**\nلديك كامل الصلاحيات لإدارة المنصة:", 
                                 uid, mid, reply_markup=admin_keyboard(), parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ خطأ: ليس لديك صلاحيات أدمن!")

    elif call.data == "adm_stats" and uid == ADMIN_ID:
        res = supabase.table("users").select("id", count="exact").execute()
        count = res.count
        bot.answer_callback_query(call.id, f"📊 إحصائيات حية:\nعدد المستخدمين: {count}", show_alert=True)

    # -- نظام الإيداع --
    elif call.data == "deposit":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("USDT (BEP20)", callback_data="pay_usdt"),
            types.InlineKeyboardButton("سيريتل كاش", callback_data="pay_cash"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
        )
        bot.edit_message_text("📥 **اختر طريقة الإيداع المناسبة:**", uid, mid, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("pay_"):
        method = "USDT" if "usdt" in call.data else "سيريتل كاش"
        addr = USDT_ADDR if "usdt" in call.data else SYRIATEL_CASH
        msg = (f"⚠️ **إيداع عبر {method}**\n\n"
               f"حول المبلغ المطلوب إلى العنوان التالي:\n`{addr}`\n\n"
               f"📸 بعد التحويل، **أرسل صورة الإيصال** هنا مباشرة.")
        bot.edit_message_text(msg, uid, mid, parse_mode="Markdown")

# --- 4. معالجة الإيداع (استلام الصور) ---

@bot.message_handler(content_types=['photo'])
def handle_deposit_receipt(message):
    uid = message.from_user.id
    uname = message.from_user.username or "بدون يوزر"
    
    # تحويل الإيصال للأدمن فوراً مع أزرار قبول/رفض
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    
    # إرسال بيانات المستخدم للأدمن للتواصل معه
    admin_msg = (f"🔔 **وصل إيداع جديد!**\n\n"
                 f"👤 المستخدم: @{uname}\n"
                 f"🆔 الآيدي: `{uid}`\n"
                 f"تأكد من الحساب ثم اشحن رصيده.")
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    
    # تأكيد للمستخدم
    bot.reply_to(message, "✅ **تم استلام الإيصال بنجاح!**\nجاري تدقيق العملية من قبل الإدارة وسوف يتم شحن رصيدك فوراً.")

# --- 5. تشغيل البوت ---
print("✅ Prestige Trading Bot is now Online...")
bot.infinity_polling()
