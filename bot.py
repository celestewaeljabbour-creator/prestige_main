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
        types.InlineKeyboardButton("🎯 صفقة اليوم", callback_data="signal"),
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
    
    # تنظيف الكيبورد القديم
    bot.send_message(uid, "💎 جاري تهيئة نظام Prestige...", reply_markup=types.ReplyKeyboardRemove())
    
    # معالجة الإحالة
    ref_by = None
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_by = int(args[1]) if int(args[1]) != uid else None

    # التسجيل في القاعدة
    try:
        db.table("users").upsert({"id": uid, "username": uname, "referred_by": ref_by}).execute()
        if ref_by:
            # تحديث عدد إحالات الداعي
            db.rpc('increment_refs', {'user_id': ref_by}).execute()
    except: pass

    welcome = (f"🏆 **منصة Prestige Trading**\n\n"
               f"أهلاً بك {uname} في أقوى سيستم تداول.\n"
               f"حسابك جاهز الآن لتحقيق الأرباح.\n\n"
               f"💰 رصيدك الحالي: **0.00$**")
    bot.send_message(uid, welcome, reply_markup=main_kb(uid), parse_mode="Markdown")

# --- معالجة الضغطات ---

@bot.callback_query_handler(func=lambda call: True)
def handle_btns(call):
    uid = call.from_user.id
    mid = call.message.message_id

    # إعطاء استجابة تحميل لتجنب التنقل اللحظي السريع
    bot.answer_callback_query(call.id, "جاري المعالجة...")
    time.sleep(0.4) 

    if call.data == "home":
        bot.edit_message_text("القائمة الرئيسية للمنصة:", uid, mid, reply_markup=main_kb(uid))

    elif call.data == "wallet":
        # جلب البيانات الحقيقية
        res = db.table("users").select("balance").eq("id", uid).execute()
        bal = res.data[0]['balance'] if res.data else 0.0
        txt = (f"👤 **مركزك المالي**\n\n"
               f"💰 الرصيد المتاح: `{bal}$`\n"
               f"📉 أرباح التداول: `0.00$`\n"
               f"🎁 بونص الإحالات: `0.00$`")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    elif call.data == "team":
        # رابط الدعوة الحقيقي
        link = f"https://t.me/Prestige_Trading_Bot?start={uid}"
        txt = (f"👥 **نظام الشركاء**\n\n"
               f"شارك رابطك واربح 5% من إيداعات فريقك.\n\n"
               f"رابط دعوتك الحصري:\n`{link}`")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    # --- قسم صفقة اليوم ---
    elif call.data == "signal":
        txt = ("📊 **توصية التداول الحالية (VIP)**\n\n"
               "🔹 **العملة:** `BTC/USDT`\n"
               "📈 **الرافعة المالية:** `20x`\n"
               "📥 **سعر الدخول:** `65,200$`\n"
               "🎯 **جني الأرباح:** `66,500$`\n\n"
               "⚠️ يرجى التداول بحذر والالتزام بإدارة رأس المال.")
        bot.edit_message_text(txt, uid, mid, reply_markup=back_kb(), parse_mode="Markdown")

    # --- قسم الجوائز ---
    elif call.data == "prizes":
        txt = ("🎁 **جوائز الإحالات الكبرى**\n\n"
               "حقق الأهداف التالية واستلم جائزتك فوراً:\n\n"
               "• 50 إحالة نشطة ⬅️ **سماعة AirPods Pro** 🎧\n"
               "• 150 إحالة نشطة ⬅️ **Xiaomi Redmi Note 13** 📱\n"
               "• 500 إحالة نشطة ⬅️ **iPhone 15 Pro Max** 🍎\n\n"
               "سيتم مراجعة الإحالات يدوياً لضمان عدم وجود حسابات وهمية.")
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

# --- استلام الصور (إشعارات الإيداع) ---

@bot.message_handler(content_types=['photo'])
def handle_docs(message):
    uid = message.from_user.id
    uname = message.from_user.username or "Unknown"
    
    # توجيه للأدمن
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    caption = (f"🔔 **إشعار إيداع جديد!**\n\n"
               f"👤 المستخدم: @{uname}\n"
               f"🆔 الآيدي: `{uid}`\n"
               f"تأكد من الوصول ثم اشحن الرصيد.")
    bot.send_message(ADMIN_ID, caption, parse_mode="Markdown")
    
    bot.reply_to(message, "✅ **تم استلام الإيصال!**\nجاري تدقيق العملية من قبل الإدارة وسوف يتم إشعارك فور التفعيل.")

# --- تشغيل البوت ---
print("🚀 Prestige Bot is running with Prizes System...")
bot.infinity_polling()
