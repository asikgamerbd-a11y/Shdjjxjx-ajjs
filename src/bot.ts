import TelegramBot from 'node-telegram-bot-api';
import fs from 'fs';
import path from 'path';

// --- কনফিগারেশন ---
const BOT_TOKEN = "8716745260:AAGPEuKxQgK3Vv7kTQ5vmlup89acZ9trLNQ";
const ADMIN_ID = 8197284774;
const bot = new TelegramBot(BOT_TOKEN, { polling: true });

const FORCE_JOIN_CHANNELS = [
    { name: "DXA Universe", url: "https://t.me/dxa_universe", username: "@dxa_universe" },
    { name: "Developer X Asik", url: "https://t.me/developer_x_asik", username: "@developer_x_asik" }
];

// --- প্রিমিয়াম ইমোজি ডিকশনারি (সম্পূর্ণ লিস্ট) ---
const PREMIUM_EMOJIS: Record<string, string> = {
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
};

function escapeHtml(text: string) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function e(input: string) {
    const s = input.trim();
    if (PREMIUM_EMOJIS[s]) {
        const emojiId = PREMIUM_EMOJIS[s];
        const isName = s.length > 2 && /^[A-Za-z0-9 /]+$/.test(s);
        const base = isName ? "🖥" : s;
        return `<tg-emoji emoji-id="${emojiId}">${base}</tg-emoji>`;
    }
    return input;
}

// --- ডাটাবেস সেটআপ ---
const dataDir = path.join(process.cwd(), 'data');
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir);

function readJson(filename: string) {
    const filePath = path.join(dataDir, filename);
    if (!fs.existsSync(filePath)) return [];
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        return JSON.parse(content);
    } catch {
        return [];
    }
}

function writeJson(filename: string, data: any) {
    const filePath = path.join(dataDir, filename);
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

// --- গ্লোবাল স্টেট ট্র্যাকিং ---
interface UserState {
    lastMenuMsgId?: number;
    lastReqTime?: number;
    waitingFor?: 'upload_file' | 'broadcast_msg' | 'service_name' | 'country_name' | 'update_otp_link';
    tempData?: any;
    isBusy?: boolean;
}
const USER_STATES: Record<number, UserState> = {};

// --- এক্সপায়ারি চেক লজিক (২০ মিনিট) ---
setInterval(() => {
    const now = Date.now();
    const numbers = readJson("numbers.json");
    let changed = false;
    const updated = numbers.map((n: any) => {
        if (n.used && n.allocatedAt && (now - n.allocatedAt > 20 * 60 * 1000)) {
            changed = true;
            return { ...n, used: false, allocatedAt: undefined };
        }
        return n;
    });
    if (changed) writeJson("numbers.json", updated);
}, 60 * 1000);

function getBotConfig() {
    const config = readJson("config.json");
    if (Array.isArray(config) || !config.otpLink) return { otpLink: "https://t.me/dxaotpzone" };
    return config;
}

// --- হেল্পার ফাংশন ---
async function checkForceJoin(userId: number): Promise<boolean> {
    for (const channel of FORCE_JOIN_CHANNELS) {
        try {
            const member = await bot.getChatMember(channel.username, userId);
            if (['left', 'kicked'].includes(member.status)) return false;
        } catch {
            return false;
        }
    }
    return true;
}

function getMainMenuKeyboard(userId: number) {
    const buttons = [
        [{ text: "📱 Get Number" }, { text: "🛠 Support" }]
    ];
    if (userId === ADMIN_ID) buttons.push([{ text: "👑 Admin Panel" }]);
    return {
        keyboard: buttons,
        resize_keyboard: true
    };
}

async function deleteUserMsg(chatId: number, msgId: number) {
    try { await bot.deleteMessage(chatId, msgId); } catch {}
}

async function updateMenu(chatId: number, text: string, replyMarkup: TelegramBot.InlineKeyboardMarkup) {
    const state = USER_STATES[chatId] || {};
    // Add a tiny invisible change to force edit even if text is same
    const finalText = text + "\n‎"; 

    if (state.lastMenuMsgId) {
        try {
            await bot.editMessageText(finalText, {
                chat_id: chatId,
                message_id: state.lastMenuMsgId,
                parse_mode: 'HTML',
                reply_markup: replyMarkup
            });
            return;
        } catch (err: any) {
            if (err.message && err.message.includes("message is not modified")) return;
            try { await bot.deleteMessage(chatId, state.lastMenuMsgId); } catch {}
        }
    }
    const sent = await bot.sendMessage(chatId, finalText, {
        parse_mode: 'HTML',
        reply_markup: replyMarkup
    });
    if (!USER_STATES[chatId]) USER_STATES[chatId] = {};
    USER_STATES[chatId].lastMenuMsgId = sent.message_id;
}

// --- মেনুFunction ---

async function showStart(chatId: number, firstName: string, isUpdate = false) {
    const line1 = e("🔥") + " <b>DXA NUMBER BOT</b> " + e("🔥") + "\n";
    const line2 = "━━━━━━━━━━━\n";
    const line3 = e("👋") + ` Hello, <b>${firstName}</b>! Welcome to DXA UNIVERSE.\n\n`;
    const line4 = e("📌") + " Tap Get Number to start!\n";
    const line5 = "━━━━━━━━━━━\n";
    const line6 = e("😒") + " POWERED BY DXA UNIVERSE";
    const text = line1 + line2 + line3 + line4 + line5 + line6;

    const markup: TelegramBot.InlineKeyboardMarkup = { inline_keyboard: [] };

    if (isUpdate) {
        await updateMenu(chatId, text, markup);
    } else {
        const state = USER_STATES[chatId] || {};
        if (state.lastMenuMsgId) {
            try { await bot.deleteMessage(chatId, state.lastMenuMsgId); } catch {}
        }
        const sent = await bot.sendMessage(chatId, text, {
            parse_mode: 'HTML',
            reply_markup: getMainMenuKeyboard(chatId)
        });
        USER_STATES[chatId] = { ...state, lastMenuMsgId: sent.message_id };
    }
}

async function showServices(chatId: number) {
    const numbers = readJson("numbers.json");
    const available = numbers.filter((n: any) => !n.used);
    const services = Array.from(new Set(available.map((n: any) => n.service))).sort();

    const markup: TelegramBot.InlineKeyboardMarkup = { inline_keyboard: [] };
    let text = "";

    if (services.length === 0) {
        text = e("❌") + " No numbers available at the moment.";
    } else {
        text = e("📱") + " <b>Select a Service:</b>";
        for (const s of services) {
            markup.inline_keyboard.push([{ text: `🔹 ${s}`, callback_data: `sel_service:${s}` }]);
        }
    }
    markup.inline_keyboard.push([{ text: "🔙 Back", callback_data: "go_home" }]);
    await updateMenu(chatId, text, markup);
}

async function showAdminPanel(chatId: number) {
    const users = readJson("users.json");
    const numbers = readJson("numbers.json");
    const files = readJson("files.json");
    const assigned = numbers.filter((n: any) => n.used).length;
    const available = numbers.filter((n: any) => !n.used).length;
    const total = numbers.length;
    const percent = total > 0 ? Math.floor((available / total) * 10) : 0;
    const bar = "█".repeat(percent) + "░".repeat(10 - percent);

    const line1 = e("👑") + " <b>ADMIN PANEL</b> " + e("👑") + "\n";
    const line2 = "━━━━━━━━━━━━━\n\n";
    const line3 = e("📊") + " <b>DATABASE OVERVIEW</b>\n";
    const line4 = "─ ─ ─ ─ ─ ─ ─\n";
    const line5 = "  " + e("👤") + `  Users       »  ${users.length}\n`;
    const line6 = "  " + e("📁") + `  Files       »  ${files.length}\n`;
    const line7 = "  " + e("🔢") + `  Numbers     »  ${total}\n`;
    const line8 = "  " + e("✅") + `  Assigned    »  ${assigned}\n`;
    const line9 = "  " + e("🚀") + `  Available   »  ${available}\n\n`;
    const line10 = e("📊") + " <b>STOCK LEVEL</b>\n";
    const line11 = "─ ─ ─ ─ ─ ─ ─\n";
    const line12 = `  [${bar}]  ${available} free\n\n`;
    const line13 = "━━━━━━━━━━━━━";

    const text = line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10 + line11 + line12 + line13;
    const markup: TelegramBot.InlineKeyboardMarkup = {
        inline_keyboard: [
            [{ text: "📤 Upload Numbers", callback_data: "admin_upload" }],
            [{ text: "🗑 Delete Files", callback_data: "admin_delete_files" }],
            [{ text: "🔗 Update OTP Link", callback_data: "admin_otp_link" }],
            [{ text: "📢 Broadcast", callback_data: "admin_broadcast" }],
            [{ text: "🔙 Back", callback_data: "go_home" }]
        ]
    };
    await updateMenu(chatId, text, markup);
}

async function showSupport(chatId: number, firstName: string) {
    const text = e("🔥") + " <b>DXA SUPPORT CENTER</b> " + e("🔥") + "\n" +
        "━━━━━━━━━━━\n" +
        e("👋") + ` Hello, <b>${firstName}</b>! Tell me how I can help.\n\n` +
        e("📌") + " Contact our admin for assistance.\n" +
        "━━━━━━━━━━━\n" +
        e("😒") + " POWERED BY DXA UNIVERSE";
    const markup = {
        inline_keyboard: [
            [{ text: "💬 Support Center", url: "https://t.me/asik_x_bd_bot" }],
            [{ text: "🔙 Back", callback_data: "go_home" }]
        ]
    };
    await updateMenu(chatId, text, markup);
}

// --- টেলিগ্রাম ইভেন্টস ---

bot.onText(/\/start/, async (msg) => {
    const userId = msg.from?.id;
    if (!userId) return;
    await deleteUserMsg(userId, msg.message_id);
    const state = USER_STATES[userId] || {};
    if (state.lastMenuMsgId) {
        try { await bot.deleteMessage(userId, state.lastMenuMsgId); } catch {}
    }
    const users = readJson("users.json");
    if (!users.some((u: any) => u.uid === userId.toString())) {
        users.push({ uid: userId.toString(), username: msg.from?.username, joinedAt: new Date().toISOString() });
        writeJson("users.json", users);
    }
    if (!(await checkForceJoin(userId))) {
        const state = USER_STATES[userId] || {};
        const markup: TelegramBot.InlineKeyboardMarkup = {
            inline_keyboard: FORCE_JOIN_CHANNELS.map(c => [{ text: `Join ${c.name} 🔗`, url: c.url }])
        };
        markup.inline_keyboard.push([{ text: "Joined ✅", callback_data: "check_join" }]);
        const sent = await bot.sendMessage(userId, "You must join our channels to use this bot:", { reply_markup: markup });
        USER_STATES[userId] = { ...state, lastMenuMsgId: sent.message_id };
        return;
    }
    await showStart(userId, msg.from?.first_name || "User");
});

bot.on('callback_query', async (call) => {
    const chatId = call.message?.chat.id;
    const userId = call.from.id;
    if (!chatId) return;

    if (USER_STATES[userId]?.isBusy) return bot.answerCallbackQuery(call.id, { text: "⌛ Please wait...", show_alert: false });

    async function safeAnswer(text?: string, showAlert = false) {
        try { await bot.answerCallbackQuery(call.id, { text, show_alert: showAlert }); } catch {}
    }

    if (call.data !== "check_join" && !(await checkForceJoin(userId))) return safeAnswer("❌ Join all channels first!", true);

    const data = call.data || "";

    if (data === "admin_panel" || data === "admin_panel_back" || data === "go_home") {
        if (USER_STATES[userId]) {
            USER_STATES[userId].waitingFor = undefined;
            USER_STATES[userId].tempData = undefined;
        }
    }

    if (data === "check_join") {
        if (await checkForceJoin(userId)) {
            try { await bot.deleteMessage(chatId, call.message!.message_id); } catch {}
            await showStart(userId, call.from.first_name);
        } else safeAnswer("❌ Join all channels first!", true);
    } else if (data === "go_home") {
        await showStart(chatId, call.from.first_name, true);
    } else if (data === "back_to_services") {
        await showServices(chatId);
    } else if (data.startsWith("sel_service:")) {
        const service = data.split(":")[1];
        const numbers = readJson("numbers.json").filter((n: any) => !n.used && n.service === service);
        const countries = Array.from(new Set(numbers.map((n: any) => n.country))).sort();
        const markup = { inline_keyboard: countries.map(c => [{ text: `📍 ${c}`, callback_data: `sel_country:${service}:${c}` }]) };
        markup.inline_keyboard.push([{ text: "🔙 Back", callback_data: "back_to_services" }]);
        await updateMenu(chatId, e("📍", PREMIUM_EMOJIS.PIN) + ` <b>Select Country for ${service}:</b>`, markup);
    } else if (data.startsWith("sel_country:")) {
        const now = Date.now();
        const lastReq = USER_STATES[userId]?.lastReqTime || 0;
        if ((now - lastReq) / 1000 < 10) return safeAnswer(`⌛ Wait ${Math.ceil(10 - (now - lastReq) / 1000)}s!`, true);

        const parts = data.split(":");
        const service = parts[1], country = parts[2];
        const allNums = readJson("numbers.json");
        const available = allNums.filter((n: any) => !n.used && n.service === service && n.country === country);

        if (available.length < 3) return safeAnswer("❌ Not enough numbers!", true);

        if (!USER_STATES[userId]) USER_STATES[userId] = {};
        USER_STATES[userId].lastReqTime = now;

        const selected = available.sort(() => 0.5 - Math.random()).slice(0, 3);
        const selectedIds = selected.map((s: any) => s.id);
        allNums.forEach((n: any) => { if (selectedIds.includes(n.id)) { n.used = true; n.allocatedAt = Date.now(); } });
        writeJson("numbers.json", allNums);

        const icons = [e("1️⃣"), e("2️⃣"), e("3️⃣")];
        const formatted = selected.map((n: any, i: number) => {
            let num = n.number.trim();
            if (!num.startsWith("+")) num = "+" + num;
            return `${icons[i]} <code>${num}</code>`;
        }).join("\n");

        const text = "━━━━━━━━━━━\n" +
            "《 " + e("✅") + " <b>NUMBERS ALLOCATED</b> 》\n" +
            "━━━━━━━━━━━\n" +
            `<blockquote>${e("🔹")} Service ${e(service)} ${escapeHtml(service)}</blockquote>\n` +
            `<blockquote>${e("📍")} Country ${e("🌐")} ${escapeHtml(country)}</blockquote>\n` +
            "━━━━━━━━━━━\n" +
            formatted + "\n" +
            "━━━━━━━━━━━\n" +
            e("😒") + " POWERED BY DXA UNIVERSE\n" +
            "━━━━━━━━━━━";

        const config = getBotConfig();
        const markup = {
            inline_keyboard: [
                [{ text: "🔄 Change Number", callback_data: `sel_country:${service}:${country}` }],
                [{ text: "💬 OTP Group", url: config.otpLink }],
                [{ text: "🔙 Back", callback_data: "back_to_services" }]
            ]
        };
        await updateMenu(chatId, text, markup);
    } else if (data === "admin_upload") {
        USER_STATES[userId] = { ...USER_STATES[userId] || {}, waitingFor: 'upload_file' };
        await updateMenu(chatId, e("📤", PREMIUM_EMOJIS.UPLOAD) + " <b>UPLOAD NUMBERS</b>\n━━━━━━━━━━━━━\nPlease send the .txt file.", { inline_keyboard: [[{ text: "🔙 Cancel", callback_data: "admin_panel" }]] });
    } else if (data === "admin_broadcast") {
        USER_STATES[userId] = { ...USER_STATES[userId] || {}, waitingFor: 'broadcast_msg' };
        await updateMenu(chatId, e("📢", PREMIUM_EMOJIS.BROADCAST) + " <b>BROADCAST</b>\n━━━━━━━━━━━━━\nSend message to broadcast.", { inline_keyboard: [[{ text: "🔙 Cancel", callback_data: "admin_panel" }]] });
    } else if (data === "admin_otp_link") {
        USER_STATES[userId] = { ...USER_STATES[userId] || {}, waitingFor: 'update_otp_link' };
        const config = getBotConfig();
        await updateMenu(chatId, "🔗 <b>UPDATE OTP LINK</b>\n━━━━━━━━━━━━━\nCurrent: " + config.otpLink + "\n\nPlease send the new link (start with https://t.me/).", { inline_keyboard: [[{ text: "🔙 Cancel", callback_data: "admin_panel" }]] });
    } else if (data === "admin_delete_files") {
        const files = readJson("files.json");
        if (files.length === 0) return safeAnswer("No files found!", true);
        const markup = { inline_keyboard: files.map((f: any) => [{ text: `❌ ${f.fileName} (${f.service})`, callback_data: `del_file:${f.id}` }]) };
        markup.inline_keyboard.push([{ text: "🔙 Back", callback_data: "admin_panel" }]);
        await updateMenu(chatId, e("🗑", PREMIUM_EMOJIS.FILE) + " <b>DELETE FILES</b>\n━━━━━━━━━━━━━", markup);
    } else if (data.startsWith("del_file:")) {
        const fileId = data.split(":")[1];
        let files = readJson("files.json"), numbers = readJson("numbers.json");
        files = files.filter((f: any) => f.id !== fileId);
        numbers = numbers.filter((n: any) => n.fileId !== fileId);
        writeJson("files.json", files); writeJson("numbers.json", numbers);
        safeAnswer("✅ Deleted!"); await showAdminPanel(chatId);
    } else if (data === "admin_panel" || data === "admin_panel_back") {
        await showAdminPanel(chatId);
    }
    safeAnswer();
});

bot.on('message', async (msg) => {
    const userId = msg.from?.id;
    if (!userId || msg.text?.startsWith('/')) return;
    const state = USER_STATES[userId] || {};
    if (msg.text === "📱 Get Number" || msg.text === "🛠 Support" || (msg.text === "👑 Admin Panel" && userId === ADMIN_ID)) {
        USER_STATES[userId] = { ...state, waitingFor: undefined, tempData: undefined };
    }
    if (msg.text === "📱 Get Number") { await deleteUserMsg(userId, msg.message_id); await showServices(userId); return; }
    else if (msg.text === "🛠 Support") { await deleteUserMsg(userId, msg.message_id); await showSupport(userId, msg.from?.first_name || "User"); return; }
    else if (msg.text === "👑 Admin Panel" && userId === ADMIN_ID) { await deleteUserMsg(userId, msg.message_id); await showAdminPanel(userId); return; }

    if (!state.waitingFor) return;
    await deleteUserMsg(userId, msg.message_id);

    if (state.waitingFor === 'broadcast_msg') {
        const users = readJson("users.json");
        USER_STATES[userId] = { ...state, isBusy: true };
        await updateMenu(userId, e("⌛", PREMIUM_EMOJIS.WAIT) + " Broadcasting...", { inline_keyboard: [] });
        for (const u of users) { try { await bot.copyMessage(u.uid, msg.chat.id, msg.message_id); } catch {} }
        USER_STATES[userId] = { ...USER_STATES[userId], waitingFor: undefined, isBusy: false };
        await showAdminPanel(userId);
    } else if (state.waitingFor === 'update_otp_link') {
        if (!msg.text?.startsWith('https://t.me/')) return bot.sendMessage(userId, "❌ Invalid link! Must start with https://t.me/");
        writeJson("config.json", { otpLink: msg.text });
        USER_STATES[userId].waitingFor = undefined;
        await bot.sendMessage(userId, "✅ OTP Link updated successfully!");
        await showAdminPanel(userId);
    } else if (state.waitingFor === 'upload_file') {
        if (!msg.document || !msg.document.file_name?.endsWith('.txt')) return bot.sendMessage(userId, "❌ Please send a .txt file.");
        USER_STATES[userId].tempData = { docId: msg.document.file_id, fileName: msg.document.file_name };
        USER_STATES[userId].waitingFor = 'service_name';
        await updateMenu(userId, "🔹 Enter Service Name:", { inline_keyboard: [[{ text: "🔙 Cancel", callback_data: "admin_panel" }]] });
    } else if (state.waitingFor === 'service_name') {
        USER_STATES[userId].tempData.service = msg.text;
        USER_STATES[userId].waitingFor = 'country_name';
        await updateMenu(userId, "📍 Enter Country Name:", { inline_keyboard: [[{ text: "🔙 Cancel", callback_data: "admin_panel" }]] });
    } else if (state.waitingFor === 'country_name') {
        const country = msg.text, tempData = state.tempData;
        USER_STATES[userId] = { ...state, isBusy: true };
        await updateMenu(userId, e("⌛", PREMIUM_EMOJIS.WAIT) + " Processing...", { inline_keyboard: [] });
        try {
            const fileLink = await bot.getFileLink(tempData.docId);
            const response = await fetch(fileLink);
            const content = await response.text();
            const lines = content.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            const numbers = readJson("numbers.json"), files = readJson("files.json");
            const fileId = Date.now().toString();
            files.push({ id: fileId, fileName: tempData.fileName, service: tempData.service, country, count: lines.length });
            lines.forEach(n => numbers.push({ id: Math.random().toString(36).substring(2, 11), number: n, service: tempData.service, country, used: false, fileId }));
            writeJson("numbers.json", numbers); writeJson("files.json", files);
            USER_STATES[userId] = { ...USER_STATES[userId], waitingFor: undefined, tempData: undefined, isBusy: false };
            await showAdminPanel(userId);
        } catch (err) { USER_STATES[userId].isBusy = false; await bot.sendMessage(userId, "❌ Error processing file."); await showAdminPanel(userId); }
    }
});

bot.on('polling_error', console.error);
bot.on('error', console.error);
export default bot;
