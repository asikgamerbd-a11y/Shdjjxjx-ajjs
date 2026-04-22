import telebot
import json
import os
import time
import random
import threading
import html
from telebot import types

# --- কনফিগারেশন ---
BOT_TOKEN = "8716745260:AAGPEuKxQgK3Vv7kTQ5vmlup89acZ9trLNQ"
ADMIN_ID = 8197284774
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

FORCE_JOIN_CHANNELS = [
    {"name": "DXA Universe", "url": "https://t.me/dxa_universe", "username": "@dxa_universe"},
    {"name": "Developer X Asik", "url": "https://t.me/developer_x_asik", "username": "@developer_x_asik"}
]

# --- প্রিমিয়াম ইমোজি ডিকশনারি (সম্পূর্ণ লিস্ট) ---
PREMIUM_EMOJIS = {
    "Facebook": "5334807341109908955", "WhatsApp": "5334759662677957452", "Telegram": "5337010556253543833",
    "WhatsApp Businesses": "5336814486701514414", "Imo": "5337155807752524558", "Instagram": "5334868205091459431",
    "Apple": "5334637951894722661", "Frozen/Ice": "5334530732331143967", "Nord Vpn": "5334944492300573096",
    "Snapchat": "5334584041465222978", "YouTube": "5334769042886533147", "Google": "5335010201005231986",
    "Microsoft": "5334880948259427772", "DXA UNIVERSE": "5334763399299506604", "Teams": "5334590977837403844",
    "Melbet": "5337102391244263212", "Tiktok": "5339213256001102461", "Bkash": "5348469219761626211",
    "Rocket": "5346042941196507141", "Bybit": "5348372939479751825", "Binance": "5348212415077064131",
    "Gmail": "5348494358205207761", "Messenger": "5348486915026884464", "Chrome": "5346311574221000149",
    "Google One": "5348075478634766440", "🔥": "5337267511261960341", "👋": "5353027129250453493",
    "📌": "5352922460897452503", "😒": "5334763399299506604", "📱": "5355208818017999139",
    "❌": "5420130255174145507", "👑": "5353032893096567467", "📊": "5352877703043258544",
    "👤": "5352861489541714456", "📁": "5352721946054268944", "🔢": "5352862640592949843",
    "✅": "5352694861990501856", "🚀": "5352597830089347330", "📤": "5353001161878182134",
    "📣": "5352980533150259581", "⌛": "5337172996211648018", "1️⃣": "5352651766288652742",
    "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093", "4️⃣": "5352566657216714037",
    "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385", "7️⃣": "5352859127309707652",
    "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207", "🔤": "5352727417842606016",
    "🔹": "5352638632278660622", "🎙": "5355102594886833928", "💴": "5352985330628730418",
    "📅": "5352585194295564660", "🔐": "5353022963132174959", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "🔗": "5420517437885943844", "💬": "5337302974806922068",
    "⚙️": "5420155432272438703", "🫂": "5420145051336485498", "➕": "5420323438508155202",
    "🗑": "5422557736330106570", "🎁": "5420396762189831222", "🖥": "5336879280578138635",
    "🌐": "5336972142066047577", "➤": "5420618897898381296", "🏢": "5420156334215565595",
    "📍": "5352922460897452503", "💸": "5348469219761626211", "🌟": "5348049249269487574",
    "🍏": "5337132498965010628", "🕓": "5336983442125001376", "⚠️": "5336944168944047463",
    "🚫": "5336997731481193790"
}

def e(input_str):
    s = input_str.strip()
    if s in PREMIUM_EMOJIS:
        emoji_id = PREMIUM_EMOJIS[s]
        is_name = s.replace(" ", "").isalnum() and len(s) > 2
        base = "🖥" if is_name else s
        return f'<tg-emoji emoji-id="{emoji_id}">{base}</tg-emoji>'
    return input_str

# --- ডাটাবেস সেটআপ ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def write_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- গ্লোবাল স্টেট ---
USER_STATES = {}

# --- এক্সপায়ারি চেক লজিক (২০ মিনিট) ---
def expiry_checker():
    while True:
        try:
            now = time.time()
            numbers = read_json("numbers.json")
            changed = False
            for n in numbers:
                if n.get("used") and n.get("allocatedAt") and (now - n.get("allocatedAt") / 1000 > 20 * 60):
                    n["used"] = False
                    n["allocatedAt"] = None
                    changed = True
            if changed:
                write_json("numbers.json", numbers)
        except:
            pass
        time.sleep(60)

threading.Thread(target=expiry_checker, daemon=True).start()

def get_bot_config():
    config = read_json("config.json")
    if isinstance(config, list) or not config.get("otpLink"):
        return {"otpLink": "https://t.me/dxaotpzone"}
    return config

# --- হেল্পার ফাংশন ---
def check_force_join(user_id):
    for channel in FORCE_JOIN_CHANNELS:
        try:
            member = bot.get_chat_member(channel["username"], user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

def get_main_menu_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📱 Get Number", "🛠 Support")
    if user_id == ADMIN_ID:
        markup.row("👑 Admin Panel")
    return markup

def update_menu(chat_id, text, reply_markup):
    final_text = text + "\n‎" 
    
    state = USER_STATES.get(chat_id, {})
    last_msg_id = state.get("last_menu_msg_id")
    
    if last_msg_id:
        try:
            bot.edit_message_text(final_text, chat_id, last_msg_id, reply_markup=reply_markup, parse_mode="HTML")
            return
        except Exception as e:
            if "message is not modified" in str(e): return
            try: bot.delete_message(chat_id, last_msg_id)
            except: pass
            
    sent = bot.send_message(chat_id, final_text, reply_markup=reply_markup, parse_mode="HTML")
    if chat_id not in USER_STATES: USER_STATES[chat_id] = {}
    USER_STATES[chat_id]["last_menu_msg_id"] = sent.message_id

# --- মেনু ফাংশনস ---
def show_start(chat_id, first_name, is_update=False):
    line1 = f"{e('🔥')} <b>DXA NUMBER BOT</b> {e('🔥')}\n"
    line2 = "━━━━━━━━━━━━━━\n"
    line3 = f"{e('👋')} <b>Welcome {first_name}!</b>\n"
    line4 = "━━━━━━━━━━━━━━\n"
    line5 = f"{e('👑')} <b>STATUS: PREMIUM USER</b>\n"
    line6 = "━━━━━━━━━━━━━━"
    text = line1 + line2 + line3 + line4 + line5 + line6
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{e('📱')} Get Number", callback_data="back_to_services"))
    markup.add(types.InlineKeyboardButton(f"{e('📊')} Stats", callback_data="stats"))
    
    update_menu(chat_id, text, markup)

def show_services(chat_id):
    numbers = read_json("numbers.json")
    services = sorted(list(set([n.get("service") for n in numbers if not n.get("used")])))
    
    markup = types.InlineKeyboardMarkup()
    for s in services:
        markup.add(types.InlineKeyboardButton(f"{e(s)} {s}", callback_data=f"sel_service:{s}"))
    markup.add(types.InlineKeyboardButton(f"{e('🔙')} Back", callback_data="go_home"))
    
    update_menu(chat_id, f"{e('📱')} <b>SELECT SERVICE</b>\n━━━━━━━━━━━━━━", markup)

def show_admin_panel(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{e('📤')} Upload Numbers", callback_data="admin_upload"))
    markup.add(types.InlineKeyboardButton(f"{e('📢')} Broadcast Message", callback_data="admin_broadcast"))
    markup.add(types.InlineKeyboardButton(f"{e('🔗')} Update OTP Link", callback_data="admin_otp_link"))
    markup.add(types.InlineKeyboardButton(f"{e('🗑')} Delete Files", callback_data="admin_delete_files"))
    markup.add(types.InlineKeyboardButton(f"{e('🔙')} Close", callback_data="go_home"))
    
    nums = read_json("numbers.json")
    stats = f"\n{e('📊')} Total Numbers: {len(nums)}\n{e('✅')} Available: {len([n for n in nums if not n.get('used')])}"
    update_menu(chat_id, f"{e('👑')} <b>ADMIN PANEL</b>\n━━━━━━━━━━━━━━" + stats, markup)

@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    if not check_force_join(user_id):
        markup = types.InlineKeyboardMarkup()
        for ch in FORCE_JOIN_CHANNELS:
            markup.add(types.InlineKeyboardButton(f"🔗 Join {ch['name']}", url=ch["url"]))
        markup.add(types.InlineKeyboardButton("✅ Checked", callback_data="check_join"))
        bot.send_message(msg.chat.id, f"{e('❌')} <b>Access Denied!</b>\nPlease join our channels first.", reply_markup=markup)
        return
    
    bot.send_message(msg.chat.id, f"{e('👋')} <b>Welcome!</b>", reply_markup=get_main_menu_keyboard(user_id))
    show_start(msg.chat.id, msg.from_user.first_name)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data
    
    if data == "check_join":
        if check_force_join(user_id):
            try: bot.delete_message(chat_id, call.message.message_id)
            except: pass
            show_start(chat_id, call.from_user.first_name)
        else:
            bot.answer_callback_query(call.id, "❌ Join all channels first!", show_alert=True)
    elif data == "go_home":
        show_start(chat_id, call.from_user.first_name)
    elif data == "back_to_services":
        show_services(chat_id)
    elif data == "stats":
        nums = read_json("numbers.json")
        text = f"{e('📊')} <b>TOTAL STATISTICS</b>\n━━━━━━━━━━━━━━\n"
        text += f"{e('📱')} Total Numbers: {len(nums)}\n"
        text += f"{e('✅')} Available: {len([n for n in nums if not n.get('used')])}\n"
        text += f"{e('👤')} Active Users: {len(USER_STATES)}"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(f"{e('🔙')} Back", callback_data="go_home"))
        update_menu(chat_id, text, markup)
    elif data.startswith("sel_service:"):
        service = data.split(":")[1]
        nums = read_json("numbers.json")
        countries = sorted(list(set([n.get("country") for n in nums if not n.get("used") and n.get("service") == service])))
        markup = types.InlineKeyboardMarkup()
        for c in countries:
            markup.add(types.InlineKeyboardButton(f"{e('📍')} {c}", callback_data=f"sel_country:{service}:{c}"))
        markup.add(types.InlineKeyboardButton(f"{e('🔙')} Back", callback_data="back_to_services"))
        update_menu(chat_id, f"{e('📍')} <b>Select Country for {service}:</b>", markup)
    elif data.startswith("sel_country:"):
        now = time.time()
        last_req = USER_STATES.get(user_id, {}).get("last_req_time", 0)
        if now - last_req < 10:
            bot.answer_callback_query(call.id, f"⌛ Wait {int(10 - (now-last_req))}s!", show_alert=True)
            return
        
        parts = data.split(":")
        service, country = parts[1], parts[2]
        all_nums = read_json("numbers.json")
        available = [n for n in all_nums if not n.get("used") and n.get("service") == service and n.get("country") == country]
        
        if len(available) < 3:
            bot.answer_callback_query(call.id, "❌ Not enough numbers!", show_alert=True)
            return
            
        USER_STATES[user_id]["last_req_time"] = now
        selected = random.sample(available, 3)
        selected_ids = [n.get("id") for n in selected]
        for n in all_nums:
            if n.get("id") in selected_ids:
                n["used"] = True
                n["allocatedAt"] = now * 1000
        write_json("numbers.json", all_nums)
        
        icons = [e("1️⃣"), e("2️⃣"), e("3️⃣")]
        formatted = []
        for i, n in enumerate(selected):
            num = n.get("number", "").strip()
            if not num.startswith("+"): num = "+" + num
            formatted.append(f"{icons[i]} <code>{num}</code>")
            
        text = "━━━━━━━━━━━\n" + \
               "《 " + e("✅") + " <b>NUMBERS ALLOCATED</b> 》\n" + \
               "━━━━━━━━━━━\n" + \
               f"<blockquote>{e('🔹')} Service {e(service)} {html.escape(service)}</blockquote>\n" + \
               f"<blockquote>{e('📍')} Country {e('🌐')} {html.escape(country)}</blockquote>\n" + \
               "━━━━━━━━━━━\n" + \
               "\n".join(formatted) + "\n" + \
               "━━━━━━━━━━━\n" + \
               f"{e('😒')} POWERED BY DXA UNIVERSE\n" + \
               "━━━━━━━━━━━"
               
        config = get_bot_config()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"{e('🔄')} Change Number", callback_data=f"sel_country:{service}:{country}"))
        markup.add(types.InlineKeyboardButton(f"{e('💬')} OTP Group", url=config["otpLink"]))
        markup.add(types.InlineKeyboardButton(f"{e('🔙')} Back", callback_data="back_to_services"))
        update_menu(chat_id, text, markup)
    elif data == "admin_upload":
        USER_STATES[user_id]["waiting_for"] = "upload_file"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(f"{e('🔙')} Cancel", callback_data="admin_panel_back"))
        update_menu(chat_id, f"{e('📤')} <b>UPLOAD NUMBERS</b>\n━━━━━━━━━━━━━\nPlease send the .txt file.", markup)
    elif data == "admin_broadcast":
        USER_STATES[user_id]["waiting_for"] = "broadcast_msg"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(f"{e('🔙')} Cancel", callback_data="admin_panel_back"))
        update_menu(chat_id, f"{e('📢')} <b>BROADCAST</b>\n━━━━━━━━━━━━━\nSend message to broadcast.", markup)
    elif data == "admin_otp_link":
        USER_STATES[user_id]["waiting_for"] = "update_otp_link"
        config = get_bot_config()
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(f"{e('🔙')} Cancel", callback_data="admin_panel_back"))
        update_menu(chat_id, f"{e('🔗')} <b>UPDATE OTP LINK</b>\n━━━━━━━━━━━━━\nCurrent: {config['otpLink']}\n\nPlease send the new link.", markup)
    elif data == "admin_delete_files":
        files = read_json("files.json")
        if not files:
            bot.answer_callback_query(call.id, "No files found!", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup()
        for f in files:
            markup.add(types.InlineKeyboardButton(f"❌ {f['fileName']}", callback_data=f"del_file:{f['id']}"))
        markup.add(types.InlineKeyboardButton(f"{e('🔙')} Back", callback_data="admin_panel_back"))
        update_menu(chat_id, f"{e('🗑')} <b>DELETE FILES</b>\n━━━━━━━━━━━━━", markup)
    elif data.startswith("del_file:"):
        fid = data.split(":")[1]
        files, nums = read_json("files.json"), read_json("numbers.json")
        write_json("files.json", [f for f in files if str(f['id']) != fid])
        write_json("numbers.json", [n for n in nums if str(n.get('fileId')) != fid])
        bot.answer_callback_query(call.id, "✅ Deleted!")
        show_admin_panel(chat_id)
    elif data == "admin_panel" or data == "admin_panel_back":
        show_admin_panel(chat_id)
        
    try: bot.answer_callback_query(call.id)
    except: pass

@bot.message_handler(func=lambda m: True, content_types=['text', 'document'])
def handle_msg(msg):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    if msg.text and msg.text.startswith('/'): return
    
    state = USER_STATES.get(user_id, {})
    if msg.text in ["📱 Get Number", "🛠 Support", "👑 Admin Panel"]:
        USER_STATES[user_id]["waiting_for"] = None
        
    if msg.text == "📱 Get Number":
        show_services(user_id)
    elif msg.text == "🛠 Support":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"{e('👤')} Admin", url="https://t.me/developer_x_asik"))
        bot.send_message(chat_id, f"{e('🛠')} <b>Support Team</b>\n━━━━━━━━━━━━━\nPlease contact the admin for any issues.", reply_markup=markup)
    elif msg.text == "👑 Admin Panel" and user_id == ADMIN_ID:
        show_admin_panel(chat_id)
    elif state.get("waiting_for") == "update_otp_link" and msg.text:
        write_json("config.json", {"otpLink": msg.text})
        USER_STATES[user_id]["waiting_for"] = None
        bot.send_message(chat_id, "✅ OTP Link updated!")
        show_admin_panel(chat_id)
    elif state.get("waiting_for") == "broadcast_msg" and msg.text:
        # Simple broadcast logic
        bot.send_message(chat_id, f"✅ Broadcasting to users...")
        USER_STATES[user_id]["waiting_for"] = None
    elif state.get("waiting_for") == "upload_file" and msg.document:
        # Simple upload logic
        file_info = bot.get_file(msg.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode('utf-8')
        lines = content.split('\n')
        
        nums = read_json("numbers.json")
        fid = int(time.time())
        new_count = 0
        for line in lines:
            if line.strip():
                nums.append({"id": int(time.time()*1000)+new_count, "number": line.strip(), "used": False, "fileId": fid, "service": "Imo", "country": "Venezuela"})
                new_count += 1
        write_json("numbers.json", nums)
        
        files = read_json("files.json")
        files.append({"id": fid, "fileName": msg.document.file_name, "service": "Imo"})
        write_json("files.json", files)
        
        USER_STATES[user_id]["waiting_for"] = None
        bot.send_message(chat_id, f"✅ Uploaded {new_count} numbers!")
        show_admin_panel(chat_id)

print("Bot is running...")
bot.infinity_polling()
