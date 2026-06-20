import telebot
from telebot import types
import re

# =================== TOKEN ===================
TOKEN = "8590013180:AAFYNYMabfKjzJHZUwC5cFMaw3tu820o-CQ"  # <- o'z tokeningiz
ADMIN_ID = 1386255005  # <- Admin ID

bot = telebot.TeleBot(TOKEN)

user_data = {}

# =================== KURSLAR ===================
COURSES = [
    "👨‍💻 Kompyuter savodxonligi",
    "👨‍💻 Grafik dizayn",
    "🧑‍💻 Excel Pro kursi",
    "👨‍💻 3D Modellashtirish",
    "👨‍💻 Sun'iy intellekt AI",
    "🧑‍💻 Video montaj",
    "🐍 Python dasturlash",
]

DAY_GROUPS = {
    "📅 Dushanba, Chorshanba, Juma": ["🕘 09:00 – 14:00", "🕑 14:00 – 16:00", "🕓 16:00 – 18:00"],
    "📅 Seshanba, Payshanba, Shanba": ["🕘 09:00 – 14:00", "🕑 14:00 – 16:00"],
}

# =================== START ===================
@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📋 Kurslarni ko'rish", "☎️ Biz bilan bog'lanish")
    markup.add("📍 Manzil")
    markup.add("🔴 Admin panel")
    bot.send_message(
        message.chat.id,
        "Assalomu alaykum! IT Park Buxoro botiga xush kelibsiz!\n"
        "Sizga qanaqa kompyuter kurslari kerak?",
        reply_markup=markup
    )

# =================== CONTACT ===================
@bot.message_handler(func=lambda m: m.text == "☎️ Biz bilan bog'lanish")
def contact_info(message):
    text = """☎️ Biz bilan bog'lanish:

📞 Telefon: 335951707
📱 Telegram: @Raxmonovv_Nodirbek
📸 Instagram: instagram.com/kompyuter_kurslari_buxoro"""
    bot.send_message(message.chat.id, text)

# =================== MANZIL ===================
@bot.message_handler(func=lambda m: m.text == "📍 Manzil")
def show_address(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        "🗺️ Google Xaritada ko'rish",
        url="https://www.google.com/maps/place/IT+Park+Buxoro/@39.7773595,64.424753,18z"
    ))
    bot.send_message(
        message.chat.id,
        "📍 Bizning manzilimiz:\n\n"
        "🏫 Buxoro shahar, 5-maktab ichida IT PARK\n"
        "⏰ Ish vaqti: Har kuni 09:00 – 18:00",
        reply_markup=markup
    )
    bot.send_location(message.chat.id, latitude=39.7773595, longitude=64.424753)

# =================== KURS MENU ===================
@bot.message_handler(func=lambda m: m.text == "📋 Kurslarni ko'rish")
def kurslar(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for course in COURSES:
        markup.add(course)
    markup.add("🔙 Orqaga")
    bot.send_message(
        message.chat.id,
        "📚 Quyidagi kurslardan birini tanlang:",
        reply_markup=markup
    )

# =================== KURS TANLASH ===================
@bot.message_handler(func=lambda m: m.text in COURSES)
def course_selected(message):
    user_data[message.chat.id] = {"course": message.text}
    bot.send_message(
        message.chat.id,
        f"✅ Kurs tanlandi: {message.text}\n\n"
        "✏️ Ism va familiyangizni kiriting:\n"
        "(Masalan: Azizov Farrux)"
    )
    bot.register_next_step_handler(message, get_full_name)

# =================== ISM FAMILIYA (BITTAGA) ===================
def get_full_name(message):
    full_name = message.text.strip()
    parts = full_name.split()
    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "⚠️ Iltimos, ism va familiyani birga yozing:\n"
            "(Masalan: Azizov Farrux)"
        )
        bot.register_next_step_handler(message, get_full_name)
        return
    user_data[message.chat.id]["full_name"] = full_name

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📱 Raqamni ulashish", request_contact=True))
    bot.send_message(
        message.chat.id,
        "📱 Telefon raqamingizni yuboring\n(tugmani bosing yoki +998XXXXXXXXX yozing):",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, get_phone)

# =================== TELEFON ===================
def get_phone(message):
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = message.text.strip()
        clean = phone.replace(" ", "").replace("-", "")
        if not re.match(r"^\+?998\d{9}$", clean):
            bot.send_message(message.chat.id, "⚠️ Raqam noto'g'ri. +998XXXXXXXXX formatida kiriting:")
            bot.register_next_step_handler(message, get_phone)
            return
    user_data[message.chat.id]["phone"] = phone

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for day in DAY_GROUPS.keys():
        markup.add(day)
    bot.send_message(message.chat.id, "📅 Dars kunlarini tanlang:", reply_markup=markup)
    bot.register_next_step_handler(message, get_day_group)

# =================== KUN GURUHI ===================
def get_day_group(message):
    if message.text not in DAY_GROUPS:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for day in DAY_GROUPS.keys():
            markup.add(day)
        bot.send_message(message.chat.id, "⚠️ Ro'yxatdan kun tanlang:", reply_markup=markup)
        bot.register_next_step_handler(message, get_day_group)
        return
    user_data[message.chat.id]["day_group"] = message.text

    slots = DAY_GROUPS[message.text]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for s in slots:
        markup.add(s)
    bot.send_message(message.chat.id, "🕐 Dars vaqtini tanlang:", reply_markup=markup)
    bot.register_next_step_handler(message, get_time_slot)

# =================== VAQT ===================
def get_time_slot(message):
    day = user_data[message.chat.id].get("day_group", "")
    valid = DAY_GROUPS.get(day, [])
    if message.text not in valid:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for s in valid:
            markup.add(s)
        bot.send_message(message.chat.id, "⚠️ Ro'yxatdan vaqt tanlang:", reply_markup=markup)
        bot.register_next_step_handler(message, get_time_slot)
        return
    user_data[message.chat.id]["time_slot"] = message.text

    d = user_data[message.chat.id]

    summary = (
        "🎉 Ro'yxatdan o'tdingiz!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism Familiya: {d['full_name']}\n"
        f"📱 Telefon: {d['phone']}\n"
        f"📚 Kurs: {d['course']}\n"
        f"📅 Dars kunlari: {d['day_group']}\n"
        f"🕐 Dars vaqti: {d['time_slot']}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ Ma'lumotlaringiz qabul qilindi!\n"
        "📞 Tez orada siz bilan bog'lanamiz."
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📋 Kurslarni ko'rish", "☎️ Biz bilan bog'lanish")
    markup.add("📍 Manzil")
    markup.add("🔴 Admin panel")

    bot.send_message(message.chat.id, summary, reply_markup=markup)

    admin_msg = (
        "🔔 YANGI RO'YXAT!\n\n"
        f"👤 Ism Familiya: {d['full_name']}\n"
        f"📱 Tel: {d['phone']}\n"
        f"📚 Kurs: {d['course']}\n"
        f"📅 Kunlar: {d['day_group']}\n"
        f"🕐 Vaqt: {d['time_slot']}\n"
        f"🆔 Telegram ID: {message.chat.id}"
    )
    try:
        bot.send_message(ADMIN_ID, admin_msg)
    except Exception as e:
        print(f"Admin xabar yuborishda xato: {e}")

# =================== ADMIN PANEL ===================
@bot.message_handler(func=lambda m: m.text == "🔴 Admin panel")
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Sizda ruxsat yo'q.")
        return
    count = len(user_data)
    bot.send_message(
        message.chat.id,
        f"🔴 Admin Panel\n\n"
        f"👥 Jami foydalanuvchilar: {count}\n"
        f"✅ Bot ishlayapti"
    )

# =================== ORQAGA ===================
@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def go_back(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📋 Kurslarni ko'rish", "☎️ Biz bilan bog'lanish")
    markup.add("📍 Manzil")
    markup.add("🔴 Admin panel")
    bot.send_message(message.chat.id, "🏠 Bosh menyu:", reply_markup=markup)

# =================== POLLING ===================
print("Bot ishga tushdi ✅")
bot.polling(none_stop=True)