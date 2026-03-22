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
db = TinyDB('mail_tm_v2.json')
User = Query()
BASE_URL = "https://api.mail.tm"

# --- WEB SERVER (For 24/7) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "SepaxYt Mail.tm is Live!"
def run_web(): web_app.run(host="0.0.0.0", port=8080)

# --- MAIL.TM CORE LOGIC ---
def get_domain():
    try:
        res = requests.get(f"{BASE_URL}/domains").json()
        return res['hydra:member'][0]['domain']
    except: return "mail.tm"

def create_premium_acc():
    domain = get_domain()
    user_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{user_part}@{domain}"
    password = "SepaxVIPUser123" # Standard pass for API
    
    # Step 2: Create Account
    res = requests.post(f"{BASE_URL}/accounts", json={"address": email, "password": password})
    if res.status_code == 201:
        # Step 3: Get Token
        token_res = requests.post(f"{BASE_URL}/token", json={"address": email, "password": password}).json()
        return email, token_res['token']
    return None, None

# --- KEYBOARDS ---
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Generate Premium Mail", callback_data="gen_mail")],
        [InlineKeyboardButton("📥 Check Inbox", callback_data="check_inbox")],
        [InlineKeyboardButton("🛠 Other Tools", callback_data="other_tools")]
    ])

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db.search(User.id == user_id):
        db.insert({'id': user_id, 'email': None, 'token': None})

    await update.message.reply_text(
        "🔥 **WELCOME TO SEPAXYT PREMIUM MAIL** 🔥\n\n"
        "Bhai, ye bot Mail.tm API use karta hai jo X/Twitter aur Insta ke liye best hai.\n\n"
        "👉 Niche button dabao email lene ke liye.",
        reply_markup=main_menu())

# --- CALLBACKS ---
async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "gen_mail":
        await query.edit_message_text("⏳ **Generating VIP Account...**")
        email, token = create_premium_acc()
        
        if email:
            db.update({'email': email, 'token': token}, User.id == user_id)
            await query.edit_message_text(
                f"✅ **YOUR NEW PREMIUM MAIL:**\n\n`{email}`\n\n"
                "✨ **Steps:**\n1. Copy this mail.\n2. Use it on X/Twitter.\n3. Wait 30 seconds.\n4. Click 'Check Inbox' below.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Check Inbox (Refresh)", callback_data="check_inbox")],
                    [InlineKeyboardButton("🆕 New Email", callback_data="gen_mail")]
                ]))
        else:
            await query.edit_message_text("❌ API Limit reached or Error. Try again in 1 minute.", reply_markup=main_menu())

    elif query.data == "check_inbox":
        user_data = db.get(User.id == user_id)
        if not user_data or not user_data['token']:
            return await query.answer("⚠️ Pehle email toh generate karo!", show_alert=True)

        token = user_data['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Step 4: Fetch Messages
            res = requests.get(f"{BASE_URL}/messages", headers=headers).json()
            messages = res.get('hydra:member')

            if not messages:
                await query.answer("📭 Inbox khali hai. OTP aane mein 1 minute lag sakta hai.", show_alert=True)
            else:
                msg_id = messages[0]['id']
                # Get Full Message Content
                detail = requests.get(f"{BASE_URL}/messages/{msg_id}", headers=headers).json()
                from_adr = messages[0]['from']['address']
                subject = messages[0]['subject']
                body = detail.get('text') or detail.get('html')[0] if detail.get('html') else "No Content"

                await query.message.reply_text(
                    f"📥 **NEW MESSAGE RECEIVED!**\n\n"
                    f"👤 **From:** `{from_adr}`\n"
                    f"💬 **Subject:** `{subject}`\n\n"
                    f"📄 **Body/OTP:**\n`{body[:600]}`",
                    parse_mode="Markdown",
                    reply_markup=main_menu())
        except:
            await query.answer("❌ Error fetching inbox!")

    elif query.data == "other_tools":
        kb = [[InlineKeyboardButton("⚡ Bypass Maker", url="https://t.me/bypassmakeribot")],
              [InlineKeyboardButton("📥 Downloader", url="https://t.me/SocialmediaFuckbot")],
              [InlineKeyboardButton("🔙 Back", callback_data="back_home")]]
        await query.edit_message_text("🛠 **Aman Patel's Other Tools:**", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "back_home":
        await query.edit_message_text("🏠 **MAIN MENU**", reply_markup=main_menu())

# --- MAIN ---
if __name__ == '__main__':
    Thread(target=run_web).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    print("SepaxYt Mail.tm Bot Started!")
    app.run_polling()
