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

# --- প্রিমিয়াম ইমোজি ডিকশনারি ---
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
    "📣": "5352980533150259581", "📢": "5352980533150259581", "⌛": "5337172996211648018", 
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093", 
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385", 
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207", 
    "🔤": "5352727417842606016", "🔹": "5352638632278660622", "🎙": "5355102594886833928", 
    "💴": "5352985330628730418", "📅": "5352585194295564660", "🔐": "5353022963132174959", 
    "📴": "5352974971167611327", "✏️": "5395444784611480792", "🔗": "5420517437885943844", 
    "💬": "5337302974806922068", "⚙️": "5420155432272438703", "🫂": "5420145051336485498", 
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222", 
    "🖥": "5336879280578138635", "🌐": "5336972142066047577", "➤": "5420618897898381296", 
    "🏢": "5420156334215565595", "📍": "5352922460897452503", "💸": "5348469219761626211", 
    "🌟": "5348049249269487574", "🍏": "5337132498965010628", "🕓": "5336983442125001376", 
    "⚠️": "5336944168944047463", "🚫": "5336997731481193790"
}

def e(input_str):
    # পরিষ্কার করছি ভেরিয়েশন সিলেক্টর এবং স্পেস
    s = input_str.strip().replace('\ufe0f', '')
    
    # 🔗 এর জন্য সরাসরি হার্ডকোডেড চেক
    if s == "🔗":
        return '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>'
    if s == "📢" or s == "📣":
        return '<tg-emoji emoji-id="5352980533150259581">📢</tg-emoji>'
        
    if s in PREMIUM_EMOJIS:
        emoji_id = PREMIUM_EMOJIS[s]
        # নামের ক্ষেত্রে বেস 🖥 (মেইন অ্যাপের মতো)
        is_name = len(s) > 2 and all(c.isalnum() or c in " /" for c in s)
        base = "🖥" if is_name else s
        return f'<tg-emoji emoji-id="{emoji_id}">{base}</tg-emoji>'
    return input_str

# --- ডাটাবেস Helpers ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

def read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path): return []
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def write_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)

# --- গ্লোবাল স্টেট ---
USER_STATES = {}

def get_bot_config():
    config = read_json("config.json")
    if isinstance(config, list) or not config or not config.get("otpLink"): return {"otpLink": "https://t.me/dxaotpzone"}
    return config

def check_force_join(user_id):
    for ch in FORCE_JOIN_CHANNELS:
        try:
            member = bot.get_chat_member(ch["username"], user_id)
            if member.status in ["left", "kicked"]: return False
        except: return False
    return True

# --- মেনু ডিজাইনস (হুবহু মেইন অ্যাপের কপি) ---

def update_menu(chat_id, text, reply_markup):
    final_text = text + "\n‎" 
    state = USER_STATES.get(chat_id, {})
    last_id = state.get("last_menu_msg_id")
    if last_id:
        try:
            bot.edit_message_text(final_text, chat_id, last_id, reply_markup=reply_markup)
            return
        except Exception as err:
            if "message is not modified" in str(err): return
            try: bot.delete_message(chat_id, last_id)
            except: pass
    sent = bot.send_message(chat_id, final_text, reply_markup=reply_markup)
    if chat_id not in USER_STATES: USER_STATES[chat_id] = {}
    USER_STATES[chat_id]["last_menu_msg_id"] = sent.message_id

def show_start(chat_id, first_name, is_update=False):
    line1 = f"{e('🔥')} <b>DXA NUMBER BOT</b> {e('🔥')}\n"
    line2 = "━━━━━━━━━━━\n"
    line3 = f"{e('👋')} Hello, <b>{first_name}</b>! Welcome to DXA UNIVERSE.\n\n"
    line4 = f"{e('📌')} Tap Get Number to start!\n"
    line5 = "━━━━━━━━━━━\n"
    line6 = f"{e('😒')} POWERED BY DXA UNIVERSE"
    text = line1 + line2 + line3 + line4 + line5 + line6
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"Get Number", callback_data="back_to_services"))
    markup.add(types.InlineKeyboardButton(f"Stats", callback_data="stats"))
    
    if is_update:
        update_menu(chat_id, text, markup)
    else:
        state = USER_STATES.get(chat_id, {})
        if state.get("last_menu_msg_id"):
            try: bot.delete_message(chat_id, state["last_menu_msg_id"])
            except: pass
        sent = bot.send_message(chat_id, text, reply_markup=markup)
        USER_STATES[chat_id] = { **state, "last_menu_msg_id": sent.message_id }

def show_services(chat_id):
    nums = read_json("numbers.json")
    services = sorted(list(set([n.get("service") for n in nums if not n.get("used")])))
    markup = types.InlineKeyboardMarkup()
    if not services:
        text = f"{e('❌')} No numbers available at the moment."
    else:
        text = f"{e('📱')} <b>Select a Service:</b>"
        for s in services:
            markup.add(types.InlineKeyboardButton(f"🔹 {s}", callback_data=f"sel_service:{s}"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="go_home"))
    update_menu(chat_id, text, markup)

def show_admin_panel(chat_id):
    users, nums, files = read_json("users.json"), read_json("numbers.json"), read_json("files.json")
    assigned = len([n for n in nums if n.get("used")])
    available = len([n for n in nums if not n.get("used")])
    total = len(nums)
    percent = int((available/total)*10) if total > 0 else 0
    bar = "█"*percent + "░"*(10-percent)
    
    txt = f"{e('👑')} <b>ADMIN PANEL</b> {e('👑')}\n"
    txt += "━━━━━━━━━━━━━\n\n"
    txt += f"{e('📊')} <b>DATABASE OVERVIEW</b>\n"
    txt += "─ ─ ─ ─ ─ ─ ─\n"
    txt += f"  {e('👤')}  Users       »  {len(users)}\n"
    txt += f"  {e('📁')}  Files       »  {len(files)}\n"
    txt += f"  {e('🔢')}  Numbers     »  {total}\n"
    txt += f"  {e('✅')}  Assigned    »  {assigned}\n"
    txt += f"  {e('🚀')}  Available   »  {available}\n\n"
    txt += f"{e('📊')} <b>STOCK LEVEL</b>\n"
    txt += "─ ─ ─ ─ ─ ─ ─\n"
    txt += f"  [{bar}]  {available} free\n\n"
    txt += "━━━━━━━━━━━━━"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📤 Upload Numbers", callback_data="admin_upload"))
    markup.add(types.InlineKeyboardButton("🗑 Delete Files", callback_data="admin_delete_files"))
    markup.add(types.InlineKeyboardButton("🔗 Update OTP Link", callback_data="admin_otp_link"))
    markup.add(types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="go_home"))
    update_menu(chat_id, txt, markup)

# ---Handlers ---

@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    # জয়েন চেক
    if not check_force_join(uid):
        markup = types.InlineKeyboardMarkup()
        for ch in FORCE_JOIN_CHANNELS: markup.add(types.InlineKeyboardButton(f"Join {ch['name']} 🔗", url=ch["url"]))
        markup.add(types.InlineKeyboardButton("Joined ✅", callback_data="check_join"))
        bot.send_message(msg.chat.id, "You must join our channels to use this bot:", reply_markup=markup)
        return
    
    users = read_json("users.json")
    if not any(u.get("uid") == str(uid) for u in users):
        users.append({"uid": str(uid), "username": msg.from_user.username, "joinedAt": time.ctime()})
        write_json("users.json", users)
    
    show_start(msg.chat.id, msg.from_user.first_name)

@bot.callback_query_handler(func=lambda call: True)
def cb_handler(call):
    chat_id, uid, data = call.message.chat.id, call.from_user.id, call.data
    
    if data != "check_join" and not check_force_join(uid):
        bot.answer_callback_query(call.id, "❌ Join all channels first!", show_alert=True)
        return

    if data == "check_join":
        if check_force_join(uid):
            try: bot.delete_message(chat_id, call.message.message_id)
            except: pass
            show_start(chat_id, call.from_user.first_name)
    elif data == "go_home":
        show_start(chat_id, call.from_user.first_name, True)
    elif data == "back_to_services":
        show_services(chat_id)
    elif data.startswith("sel_service:"):
        svc = data.split(":")[1]
        nums = read_json("numbers.json")
        avail_countries = sorted(list(set([n.get("country") for n in nums if not n.get("used") and n.get("service") == svc])))
        markup = types.InlineKeyboardMarkup()
        for c in avail_countries: markup.add(types.InlineKeyboardButton(f"📍 {c}", callback_data=f"sel_country:{svc}:{c}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_services"))
        update_menu(chat_id, f"{e('📍')} <b>Select Country for {svc}:</b>", markup)
    elif data.startswith("sel_country:"):
        # নাম্বার অ্যালোকেশন লজিক
        svc, country = data.split(":")[1], data.split(":")[2]
        nums = read_json("numbers.json")
        avail = [n for n in nums if not n.get("used") and n.get("service") == svc and n.get("country") == country]
        if len(avail) < 3:
            bot.answer_callback_query(call.id, "❌ Not enough numbers!", show_alert=True)
            return

        sel = random.sample(avail, 3)
        sel_ids = [s.get("id") for s in sel]
        for n in nums:
            if n.get("id") in sel_ids: n["used"] = True; n["allocatedAt"] = time.time()*1000
        write_json("numbers.json", nums)
        
        icons = [e("1️⃣"), e("2️⃣"), e("3️⃣")]
        fmt = "\n".join([f"{icons[i]} <code>{n.get('number')}</code>" for i, n in enumerate(sel)])
        
        txt = "━━━━━━━━━━━\n" + \
              "《 " + e("✅") + " <b>NUMBERS ALLOCATED</b> 》\n" + \
              "━━━━━━━━━━━\n" + \
              f"<blockquote>{e('🔹')} Service {e(svc)} {html.escape(svc)}</blockquote>\n" + \
              f"<blockquote>{e('📍')} Country {e('🌐')} {html.escape(country)}</blockquote>\n" + \
              "━━━━━━━━━━━\n" + fmt + "\n" + \
              "━━━━━━━━━━━\n" + \
              f"{e('😒')} POWERED BY DXA UNIVERSE\n" + \
              "━━━━━━━━━━━"
        
        cfg = get_bot_config()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Change Number", callback_data=f"sel_country:{svc}:{country}"))
        markup.add(types.InlineKeyboardButton("💬 OTP Group", url=cfg["otpLink"]))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_services"))
        update_menu(chat_id, txt, markup)
    # এডমিন ফাংশনগুলো
    elif data == "admin_upload":
        USER_STATES[uid] = { "waiting_for": "up" }
        update_menu(chat_id, f"{e('📤')} <b>UPLOAD NUMBERS</b>\nPlease send the .txt file.", types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_panel")))
    elif data == "admin_otp_link":
        USER_STATES[uid] = { "waiting_for": "otp" }
        update_menu(chat_id, f"{e('🔗')} <b>UPDATE OTP LINK</b>\nPlease send the link.", types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_panel")))
    elif data == "admin_broadcast":
        USER_STATES[uid] = { "waiting_for": "bc" }
        update_menu(chat_id, f"{e('📢')} <b>BROADCAST</b>\nSend the message.", types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_panel")))
    elif data == "admin_delete_files":
        files = read_json("files.json")
        markup = types.InlineKeyboardMarkup()
        for f in files: markup.add(types.InlineKeyboardButton(f"❌ {f['fileName']}", callback_data=f"del_file:{f['id']}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel"))
        update_menu(chat_id, "🗑 <b>DELETE FILES</b>", markup)
    elif data == "admin_panel":
        show_admin_panel(chat_id)

    try: bot.answer_callback_query(call.id)
    except: pass

print("Bot is running...")
bot.infinity_polling()
