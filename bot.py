import os
import requests
import random
import string
import time
from threading import Thread
from flask import Flask
from tinydb import TinyDB, Query
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = "8563686414:AAHfcORCFzNYI8MGddJ8brFgHetbVJbv7HU"
ADMIN_ID = 8167337368
CHANNEL_ID = -1003838827644
CHANNEL_URL = "https://t.me/+5WJ-eDTIjgI0NmY1"

# Database & API
db = TinyDB('tempmail_v3_db.json')
User = Query()
API_URL = "https://www.1secmail.com/api/v1/action"

# --- WEB SERVER (For 24/7) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "SepaxYt Temp Mail is Online!"
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
        [InlineKeyboardButton("📧 Generate VIP Mail", callback_data="gen_mail")],
        [InlineKeyboardButton("📥 Check Inbox", callback_data="check_inbox")],
        [InlineKeyboardButton("🛠 Other Free Tools", callback_data="other_bots")],
        [InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def other_bots_kb():
    keyboard = [
        [InlineKeyboardButton("⚡ Bypass Maker Bot", url="https://t.me/bypassmakeribot")],
        [InlineKeyboardButton("📥 Video Downloader", url="https://t.me/SocialmediaFuckbot")],
        [InlineKeyboardButton("🔙 Back to Home", callback_data="back_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not db.search(User.id == user.id):
        db.insert({'id': user.id, 'username': user.username, 'mail': None, 'joined': time.ctime()})

    if not await is_subscribed(user.id, context):
        keyboard = [[InlineKeyboardButton("📢 Join Official Channel", url=CHANNEL_URL)],
                    [InlineKeyboardButton("🔄 Verify & Start", callback_data="verify")]]
        return await update.message.reply_text(
            f"👋 **Namaste {user.first_name}!**\n\n🔒 **ACCESS LOCKED**\n\nBhai, ye VIP Temp Mail bot sirf **SepaxYt Family** ke liye hai. Pehle join karein fir use karein!",
            reply_markup=InlineKeyboardMarkup(keyboard))

    await update.message.reply_text(
        "🔥 **WELCOME TO SEPAXYT TEMP MAIL VIP** 🔥\n\n"
        "Bhai, yahan se aap **Unlimited Fake Emails** le sakte ho OTP aur Verification ke liye.\n\n"
        "✅ Real-looking Domains\n"
        "✅ Instant Inbox Refresh\n"
        "✅ 100% Safe & Private",
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
            await query.edit_message_text("✅ **Verified!** Ab aap bot use kar sakte hain.", reply_markup=main_menu_kb())
        else:
            await query.answer("❌ Abhi tak join nahi kiya, bhai!", show_alert=True)

    elif query.data == "gen_mail":
        user_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        domain = random.choice(get_domains())
        full_mail = f"{user_name}@{domain}"
        db.update({'mail': full_mail}, User.id == user_id)
        
        await query.edit_message_text(
            f"📧 **YOUR VIP TEMP MAIL:**\n\n`{full_mail}`\n\n"
            "✨ *Is mail ko copy karke kahin bhi use karein. Jab OTP bhej dein, toh 'Check Inbox' par click karein.*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh Inbox", callback_data="check_inbox")],
                [InlineKeyboardButton("🆕 Change Mail", callback_data="gen_mail")],
                [InlineKeyboardButton("🔙 Home", callback_data="back_home")]
            ]))

    elif query.data == "check_inbox":
        user_data = db.search(User.id == user_id)
        if not user_data or not user_data[0]['mail']:
            return await query.answer("⚠️ Pehle email toh banao!", show_alert=True)

        mail = user_data[0]['mail']
        login, domain = mail.split('@')
        
        try:
            res = requests.get(f"{API_URL}=getMessages&login={login}&domain={domain}").json()
            if not res:
                await query.answer("📭 Inbox is empty. Thoda wait karein...", show_alert=True)
            else:
                msg_text = f"📥 **INBOX FOR:** `{mail}`\n\n"
                for msg in res[:3]:
                    m_id = msg['id']
                    detail = requests.get(f"{API_URL}=readMessage&login={login}&domain={domain}&id={m_id}").json()
                    msg_text += f"👤 **From:** {msg['from']}\n💬 **Subject:** {msg['subject']}\n📄 **Message:** `{detail['textBody'][:300]}`\n\n---\n"
                
                await query.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=main_menu_kb())
        except:
            await query.answer("❌ Error fetching inbox!", show_alert=True)

    elif query.data == "other_bots":
        await query.edit_message_text("🛠 **OUR OTHER USEFUL BOTS**\n\nInhe bhi try karein aur dosto ko share karein:", reply_markup=other_bots_kb())

    elif query.data == "back_home":
        await query.edit_message_text("🏠 **MAIN MENU**\nBhai, kya karna chahte ho?", reply_markup=main_menu_kb())

    elif query.data == "admin_panel":
        if user_id != ADMIN_ID: return await query.answer("❌ Only for Aman Patel!", show_alert=True)
        total = len(db.all())
        await query.edit_message_text(f"👑 **ADMIN PANEL**\n\n👥 Total Users: `{total}`\n\nUse `/broadcast [msg]` to send alert.", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_home")]]))

# --- ADMIN BROADCAST ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return await update.message.reply_text("Syntax: `/broadcast Hello Users`")
    
    msg = " ".join(context.args)
    users = db.all()
    count = 0
    for u in users:
        try:
            await context.bot.send_message(u['id'], f"📢 **OFFICIAL UPDATE**\n\n{msg}")
            count += 1
        except: pass
    await update.message.reply_text(f"✅ Sent to {count} users.")

# --- MAIN ---
if __name__ == '__main__':
    Thread(target=run_web).start()
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    
    print("SepaxYt Temp Mail Started!")
    app.run_polling()
