import telebot
from telebot import types
from supabase import create_client, Client
import time

# ==========================================
# 1. الإعدادات الأساسية (بياناتك الرسمية)
# ==========================================
TOKEN = "8795395476:AAFVU9fXwQF8dwlh8kSnK1Z9GnOY4VEag8Q" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht"
ADMIN_ID = 6091303835 
SUPPORT_LINK = "https://t.me/tradinghubsy"

# ربط مباشر (على Render ما بتحتاج بروكسي)
bot = telebot.TeleBot(TOKEN, threaded=True)
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. وظائف النظام (الدماغ)
# ==========================================
def get_user(uid):
    try:
        res = db.table("users").select("*").eq("id", uid).execute()
        return res.data[0] if res.data else None
    except: return None

def register_user(user, ref_id=None):
    if not get_user(user.id):
        db.table("users").insert({
            "id": user.id, 
            "username": user.username or "Prestige_User", 
            "balance": 0.0, 
            "referred_by": ref_id,
            "role": "user"
        }).execute()

# ==========================================
# 3. لوحات المفاتيح (القوائم الكاملة)
# ==========================================
def main_menu(uid):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📥 إيداع رصيد", callback_data="m_dep"),
        types.InlineKeyboardButton("📤 سحب أرباح", callback_data="m_wit"),
        types.InlineKeyboardButton("👤 محفظتي", callback_data="m_wal"),
        types.InlineKeyboardButton("👥 فريقي", callback_data="m_team"),
        types.InlineKeyboardButton("📈 تداول AI", callback_data="m_ai"),
        types.InlineKeyboardButton("📊 صفقات حية", callback_data="m_live"),
        types.InlineKeyboardButton("🎁 مسابقات", callback_data="m_prizes"),
        types.InlineKeyboardButton("🤵 الوكلاء", callback_data="m_agent"),
        types.InlineKeyboardButton("🛠 الدعم الفني", url=SUPPORT_LINK)
    )
    if uid == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👑 لوحة التحكم (أدمن)", callback_data="admin_panel"))
    return markup

def back_home():
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة للقائمة", callback_data="go_home"))

# ==========================================
# 4. معالجة البداية (Start)
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    uid = message.from_user.id
    args = message.text.split()
    ref_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
    register_user(message.from_user, ref_id)
    
    welcome_text = (f"💎 **أهلاً بك في Prestige Trading**\n\n"
                    f"المنصة رقم #1 للتداول الآلي والصفقات الحية.\n"
                    f"استخدم القائمة أدناه لإدارة استثماراتك.")
    bot.send_message(uid, welcome_text, reply_markup=main_menu(uid), parse_mode="Markdown")

# ==========================================
# 5. منطق الأزرار (المضمون الكامل)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    u_data = get_user(uid)
    if not u_data: return

    if call.data == "go_home":
        bot.edit_message_text("💎 القائمة الرئيسية للمنصة:", uid, call.message.message_id, reply_markup=main_menu(uid))

    elif call.data == "m_wal":
        txt = (f"👤 **معلومات الحساب**\n\n"
               f"💰 الرصيد الحالي: `{u_data['balance']}$`\n"
               f"🎟 الرتبة: `{u_data['role']}`\n"
               f"🆔 المعرف: `{uid}`")
        bot.edit_message_text(txt, uid, call.message.message_id, reply_markup=back_home(), parse_mode="Markdown")

    elif call.data == "m_team":
        ref_link = f"https://t.me/Prestige_Trading_Bot?start={uid}"
        txt = (f"👥 **نظام المكافآت والفريق**\n\n"
               f"• اربح **5%** عمولة فورية عن كل إيداع لفريقك.\n"
               f"• نظام مكافآت أسبوعي لأكثر فريق نشط.\n\n"
               f"🔗 رابط الإحالة الخاص بك:\n`{ref_link}`")
        bot.edit_message_text(txt, uid, call.message.message_id, reply_markup=back_home(), parse_mode="Markdown")

    elif call.data == "m_ai":
        txt = "📈 **التداول عبر الذكاء الاصطناعي**\n\nالبوت يقوم الآن بتحليل السوق (BTC/USDT). سيتم تنفيذ الصفقات تلقائياً وتوزيع الأرباح كل 24 ساعة."
        bot.edit_message_text(txt, uid, call.message.message_id, reply_markup=back_home())

    elif call.data == "m_prizes":
        txt = "🎁 **المسابقات الحالية**\n\n1. مسابقة أعلى إيداع: الجائزة **100$**\n2. مسابقة 20 إحالة: الجائزة **رصيد تداول 50$**"
        bot.edit_message_text(txt, uid, call.message.message_id, reply_markup=back_home())

    elif call.data == "m_dep":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("سيرياتيل كاش 🇸🇾", callback_data="pay_sy"),
                   types.InlineKeyboardButton("USDT (BEP20) ⚡️", callback_data="pay_usdt"))
        bot.edit_message_text("📥 اختر وسيلة الإيداع المفضلة:", uid, call.message.message_id, reply_markup=markup)

    elif call.data == "pay_sy":
        bot.edit_message_text("🚀 حول لـ `092274277`\n\nثم أرسل **صورة الإيصال** هنا 👇", uid, call.message.message_id, parse_mode="Markdown")

    elif call.data == "admin_panel" and uid == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 تعميم (برودكاست)", callback_data="adm_bc"),
                   types.InlineKeyboardButton("🔙 رجوع", callback_data="go_home"))
        bot.edit_message_text("👑 **تحكم الأدمن الصارم**", uid, call.message.message_id, reply_markup=markup)

# ==========================================
# 6. معالجة الإيصالات (الصور) والتحكم
# ==========================================
@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    uid = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_app_{uid}"),
               types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_rej_{uid}"))
    
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(ADMIN_ID, f"🔔 **طلب إيداع جديد**\nمن: `{uid}`", reply_markup=markup, parse_mode="Markdown")
    bot.reply_to(message, "⏳ تم إرسال طلبك للإدارة. سيتم تفعيل الرصيد بعد المراجعة.")

# ==========================================
# 7. أوامر سريعة للأدمن (آيدي مبلغ)
# ==========================================
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and len(m.text.split()) == 2)
def admin_quick_add(message):
    try:
        tid, amt = int(message.text.split()[0]), float(message.text.split()[1])
        u = get_user(tid)
        if not u: return bot.reply_to(message, "❌ المستخدم غير مسجل.")
        
        new_bal = u['balance'] + amt
        db.table("users").update({"balance": new_bal}).eq("id", tid).execute()
        bot.reply_to(message, f"✅ تم! الرصيد الجديد لـ `{tid}`: `{new_bal}$`")
        bot.send_message(tid, f"🔔 تم إضافة `{amt}$` لحسابك بنجاح!")
    except: pass

# ==========================================
# 8. التشغيل (Infinity)
# ==========================================
if __name__ == "__main__":
    print("🚀 Prestige Ultimate is Live on Render!")
    bot.infinity_polling()

