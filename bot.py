import os
import requests
import random
import string
import time
from threading import Thread
from flask import Flask
from tinydb import TinyDB, Query
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = "8563686414:AAHfcORCFzNYI8MGddJ8brFgHetbVJbv7HU"
ADMIN_ID = 8167337368
CHANNEL_ID = -1003838827644
CHANNEL_URL = "https://t.me/+5WJ-eDTIjgI0NmY1"

# Database & API
db = TinyDB('sepax_mail_v4.json')
User = Query()
API_URL = "https://www.1secmail.com/api/v1/action"

# --- WEB SERVER (For 24/7 Render) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "SepaxYt VIP Mail is Online!"
def run_web(): web_app.run(host="0.0.0.0", port=8080)

# --- UTILS ---
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_domains():
    return ["1secmail.com", "1secmail.org", "1secmail.net", "kzccv.com", "qiott.com", "wuuvo.com", "gafyut.com", "icznn.com"]

# --- KEYBOARDS ---
def main_menu_kb():
    keyboard = [
        [InlineKeyboardButton("📧 Generate Mail", callback_data="select_domain")],
        [InlineKeyboardButton("📥 Check Inbox", callback_data="check_inbox")],
        [InlineKeyboardButton("🛠 Other Tools", callback_data="other_bots")],
        [InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def domain_kb():
    domains = get_domains()
    keyboard = []
    # Making 2 buttons per row
    for i in range(0, len(domains), 2):
        row = [InlineKeyboardButton(f"@{domains[i]}", callback_data=f"set_{domains[i]}")]
        if i+1 < len(domains):
            row.append(InlineKeyboardButton(f"@{domains[i+1]}", callback_data=f"set_{domains[i+1]}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_home")])
    return InlineKeyboardMarkup(keyboard)

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not db.search(User.id == user.id):
        db.insert({'id': user.id, 'mail': None, 'joined': time.ctime()})

    if not await is_subscribed(user.id, context):
        keyboard = [[InlineKeyboardButton("📢 Join Official Channel", url=CHANNEL_URL)],
                    [InlineKeyboardButton("🔄 Verify & Start", callback_data="verify")]]
        return await update.message.reply_text(
            f"👋 **Hi {user.first_name}!**\n\n🔒 **ACCESS LOCKED**\n\nBhai, VIP Temp Mail use karne ke liye channel join karo!",
            reply_markup=InlineKeyboardMarkup(keyboard))

    await update.message.reply_text(
        "🔥 **SEPAXYT TEMP MAIL VIP** 🔥\n\n"
        "Bhai, ye bot 100% working OTP deta hai. Niche menu use karo:",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )

# --- CALLBACK HANDLER ---
async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "verify":
        if await is_subscribed(user_id, context):
            await query.edit_message_text("✅ Verified! Press /start", reply_markup=main_menu_kb())
        else: await query.answer("❌ Join nahi kiya!", show_alert=True)

    elif query.data == "select_domain":
        await query.edit_message_text("🌐 **Select Your Domain:**\n(Twitter/X ke liye `@qiott.com` ya `@kzccv.com` try karein)", reply_markup=domain_kb())

    elif query.data.startswith("set_"):
        domain = query.data.split("_")[1]
        user_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        full_mail = f"{user_name}@{domain}"
        db.update({'mail': full_mail}, User.id == user_id)
        
        await query.edit_message_text(
            f"📧 **YOUR VIP TEMP MAIL:**\n\n`{full_mail}`\n\n"
            "✨ *Copy karo aur OTP bhej kar Refresh dabao!*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh Inbox", callback_data="check_inbox")],
                [InlineKeyboardButton("🆕 Change Domain", callback_data="select_domain")],
                [InlineKeyboardButton("🏠 Home", callback_data="back_home")]
            ]))

    elif query.data == "check_inbox":
        user_data = db.search(User.id == user_id)
        if not user_data or not user_data[0]['mail']:
            return await query.answer("⚠️ Pehle email generate karo!", show_alert=True)

        mail = user_data[0]['mail']
        login, domain = mail.split('@')
        
        try:
            res = requests.get(f"{API_URL}=getMessages&login={login}&domain={domain}").json()
            if not res:
                await query.answer("📭 Inbox empty... 1 min wait karein.", show_alert=True)
            else:
                msg_text = f"📥 **INBOX FOR:** `{mail}`\n\n"
                for msg in res[:3]:
                    m_id = msg['id']
                    detail = requests.get(f"{API_URL}=readMessage&login={login}&domain={domain}&id={m_id}").json()
                    # Logic to get text or html body
                    body = detail.get('textBody') or detail.get('body') or detail.get('htmlBody') or "No content"
                    msg_text += f"👤 **From:** {msg['from']}\n💬 **Subject:** {msg['subject']}\n📄 **OTP/Code:**\n`{body[:500]}`\n\n---\n"
                
                await query.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=main_menu_kb())
        except: await query.answer("❌ API Error!", show_alert=True)

    elif query.data == "other_bots":
        keyboard = [[InlineKeyboardButton("⚡ Bypass Maker", url="https://t.me/bypassmakeribot")],
                    [InlineKeyboardButton("📥 Downloader", url="https://t.me/SocialmediaFuckbot")],
                    [InlineKeyboardButton("🔙 Back", callback_data="back_home")]]
        await query.edit_message_text("🛠 **OUR OTHER TOOLS:**", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "back_home":
        await query.edit_message_text("🏠 **MAIN MENU**", reply_markup=main_menu_kb())

    elif query.data == "admin_panel":
        if user_id != ADMIN_ID: return
        total = len(db.all())
        await query.edit_message_text(f"👑 **ADMIN PANEL**\n\nTotal Users: `{total}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_home")]]))

# --- MAIN ---
if __name__ == '__main__':
    Thread(target=run_web).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    print("SepaxYt Temp Mail Started!")
    app.run_polling()
