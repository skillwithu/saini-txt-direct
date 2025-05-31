import os
import re
import sys
import m3u8
import json
import time
import pytz
import asyncio
import requests
import subprocess
import urllib
import urllib.parse
import yt_dlp
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from logs import logging
from bs4 import BeautifulSoup
import saini as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER, CREDIT, AUTH_USERS
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

cookies_file_path = os.getenv("cookies_file_path", "youtube_cookies.txt")
api_url = "http://master-api-v3.vercel.app/"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
token_cp ='eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9r'
adda_token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJkcGthNTQ3MEBnbWFpbC5jb20iLCJhdWQiOiIxNzg2OTYwNSIsImlhdCI6MTc0NDk0NDQ2NCwiaXNzIjoiYWRkYTI0Ny5jb20iLCJuYW1lIjoiZHBrYSIsImVtYWlsIjoiZHBrYTU0NzBAZ21haWwuY29tIiwicGhvbmUiOiI3MzUyNDA0MTc2IiwidXNlcklkIjoiYWRkYS52MS41NzMyNmRmODVkZDkxZDRiNDkxN2FiZDExN2IwN2ZjOCIsImxvZ2luQXBpVmVyc2lvbiI6MX0.0QOuYFMkCEdVmwMVIPeETa6Kxr70zEslWOIAfC_ylhbku76nDcaBoNVvqN4HivWNwlyT0jkUKjWxZ8AbdorMLg"
photologo = 'https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png' #https://envs.sh/GV0.jpg
photoyt = 'https://tinypic.host/images/2025/03/18/YouTube-Logo.wine.png' #https://envs.sh/GVi.jpg
photocp = 'https://tinypic.host/images/2025/03/28/IMG_20250328_133126.jpg'
photozip = 'https://envs.sh/cD_.jpg'


# Inline keyboard for start command
BUTTONSCONTACT = InlineKeyboardMarkup([[InlineKeyboardButton(text="📞 Contact", url="https://t.me/staystrongbros")]])
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="👨‍💻  Devloper", url="https://t.me/staystrongbros"),
            InlineKeyboardButton(text="👑  Owner", url="https://t.me/staystrongbros"),
        ],
    ]
)

# Image URLs for the random image feature
image_urls = [
    "https://i.postimg.cc/JtC1yjLj/IMG-20250529-123730-492.jpg",
    # Add more image URLs as needed
]

@bot.on_message(filters.command("addauth") & filters.private)
async def add_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    try:
        new_user_id = int(message.command[1])
        if new_user_id in AUTH_USERS:
            await message.reply_text("User ID is already authorized.")
        else:
            AUTH_USERS.append(new_user_id)
            await message.reply_text(f"User ID {new_user_id} added to authorized users.")
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid user ID.")

@bot.on_message(filters.command("users") & filters.private)
async def list_auth_users(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    user_list = '\n'.join(map(str, get_all_user_ids()))  # Get user IDs from MongoDB
    await message.reply_text(f"Authorized Users:\n{user_list}")

@bot.on_message(filters.command("rmauth") & filters.private)
async def remove_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    try:
        user_id_to_remove = int(message.command[1])
        if user_id_to_remove not in AUTH_USERS:
            await message.reply_text("User ID is not in the authorized users list.")
        else:
            AUTH_USERS.remove(user_id_to_remove)
            await message.reply_text(f"User ID {user_id_to_remove} removed from authorized users.")
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid user ID.")
    
        
@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    await m.reply_text(
        "Please upload the cookies file (.txt format).",
        quote=True
    )

    try:
        # Wait for the user to send the cookies file
        input_message: Message = await client.listen(m.chat.id)

        # Validate the uploaded file
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        # Download the cookies file
        downloaded_path = await input_message.download()

        # Read the content of the uploaded file
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        # Replace the content of the target cookies file
        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text(
            "✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`."
        )

    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["t2t"]))
async def text_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    # Inform the user to send the text data and its desired file name
    editable = await message.reply_text(f"<blockquote>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</blockquote>")
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("🚨 **error**: Send valid text data")
        return

    text_data = input_message.text.strip()
    await input_message.delete()  # Corrected here
    
    await editable.edit("**🔄 Send file name or send /d for filename**")
    inputn: Message = await bot.listen(message.chat.id)
    raw_textn = inputn.text
    await inputn.delete()  # Corrected here
    await editable.delete()

    if raw_textn == '/d':
        custom_file_name = 'txt_file'
    else:
        custom_file_name = raw_textn

    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await message.reply_document(document=txt_file, caption=f"`{custom_file_name}.txt`\n\nYou can now download your content! 📥")
    os.remove(txt_file)

# Define paths for uploaded file and processed file
UPLOAD_FOLDER = '/path/to/upload/folder'
EDITED_FILE_PATH = '/path/to/save/edited_output.txt'

@bot.on_message(filters.command(["y2t"]))
async def youtube_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    
    editable = await message.reply_text(
        f"Send YouTube Website/Playlist link for convert in .txt file"
    )

    input_message: Message = await bot.listen(message.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete(True)
    await editable.delete(True)

    # Fetch the YouTube information using yt-dlp with cookies
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'forcejson': True,
        'cookies': 'youtube_cookies.txt'  # Specify the cookies file
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=False)
            if 'entries' in result:
                title = result.get('title', 'youtube_playlist')
            else:
                title = result.get('title', 'youtube_video')
        except yt_dlp.utils.DownloadError as e:
            await message.reply_text(
                f"<pre><code>🚨 Error occurred {str(e)}</code></pre>"
            )
            return

    # Extract the YouTube links
    videos = []
    if 'entries' in result:
        for entry in result['entries']:
            video_title = entry.get('title', 'No title')
            url = entry['url']
            videos.append(f"{video_title}: {url}")
    else:
        video_title = result.get('title', 'No title')
        url = result['url']
        videos.append(f"{video_title}: {url}")

    # Create and save the .txt file with the custom name
    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    # Send the generated text file to the user with a pretty caption
    await message.reply_document(
        document=txt_file,
        caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<pre><code>{title}.txt</code></pre>\n'
    )

    # Remove the temporary text file after sending
    os.remove(txt_file)


m_file_path= "main.py"
@bot.on_message(filters.command("getcookies") & filters.private)
async def getcookies_handler(client: Client, m: Message):
    try:
        # Send the cookies file to the user
        await client.send_document(
            chat_id=m.chat.id,
            document=cookies_file_path,
            caption="Here is the `youtube_cookies.txt` file."
        )
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")     
@bot.on_message(filters.command("mfile") & filters.private)
async def getcookies_handler(client: Client, m: Message):
    try:
        await client.send_document(
            chat_id=m.chat.id,
            document=m_file_path,
            caption="Here is the `main.py` file."
        )
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["stop"]) )
async def restart_handler(_, m):
    if m.chat.id not in AUTH_USERS:
        print(f"User ID not in AUTH_USERS", m.chat.id)
        await bot.send_message(
            m.chat.id, 
            "<blockquote>__🚫<b>𝐎𝐨𝐩𝐬𝐬! 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐌𝐞𝐦𝐛𝐞𝐫 🌟</b>✨__\n"
            f"__**PLEASE /upgrade YOUR PLAN**__\n"
            f"__**Send me your user id for authorization**__\n"
            f"__**Your User id** __- `{m.chat.id}`</blockquote>\n\n"
        )
    else:
        await m.reply_text("🚦**STOPPED**🚦", True)
        os.execl(sys.executable, sys.executable, *sys.argv)
        

@bot.on_message(filters.command("start"))
async def start(bot, m: Message):
    user = await bot.get_me()
    mention = user.mention

    start_message = await bot.send_message(
        m.chat.id,
        f"🌟 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {m.from_user.first_name}! 🌟\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        f"🌟 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {m.from_user.first_name}! 🌟\n\n"
        f"╭──────────────╮\n"
        f"│ ⬡ ⬡ ⬡ ⬡ ⬡ ⬡ ⬡ ⬡ ⬡ ⬡ │\n"
        f"╰──────────────╯\n"
        f"🔧 𝐈𝐧𝐢𝐭𝐢𝐚𝐥𝐢𝐳𝐢𝐧𝐠 𝐦𝐞𝐜𝐡 𝐬𝐲𝐬𝐭𝐞𝐦...\n\n"
        f"𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬: 𝟎%"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        f"🌟 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {m.from_user.first_name}! 🌟\n\n"
        f"╭──────────────╮\n"
        f"│ ⬢ ⬢ ⬢ ⬡ ⬡ ⬡ ⬡ ⬡ ⬡ ⬡ │\n"
        f"╰──────────────╯\n"
        f"🔧 𝐋𝐨𝐚𝐝𝐢𝐧𝐠 𝐦𝐨𝐝𝐮𝐥𝐞𝐬...\n\n"
        f"𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬: 𝟐𝟓%"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        f"🌟 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {m.from_user.first_name}! 🌟\n\n"
        f"╭──────────────╮\n"
        f"│ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬡ ⬡ ⬡ ⬡ │\n"
        f"╰──────────────╯\n"
        f"🔧 𝐀𝐜𝐭𝐢𝐯𝐚𝐭𝐢𝐧𝐠 𝐞𝐧𝐠𝐢𝐧𝐞 𝐜𝐨𝐫𝐞...\n\n"
        f"𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬: 𝟓𝟎%"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        f"🌟 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {m.from_user.first_name}! 🌟\n\n"
        f"╭──────────────╮\n"
        f"│ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬡ ⬡ │\n"
        f"╰──────────────╯\n"
        f"🔧 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 𝐬𝐲𝐬𝐭𝐞𝐦 𝐬𝐭𝐚𝐛𝐢𝐥𝐢𝐭𝐲...\n\n"
        f"𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬: 𝟕𝟓%"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        f"🌟 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {m.from_user.first_name}! 🌟\n\n"
        f"╭──────────────╮\n"
        f"│ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ │\n"
        f"╰──────────────╯\n"
        f"✅ 𝐒𝐲𝐬𝐭𝐞𝐦 𝐨𝐧𝐥𝐢𝐧𝐞 𝐚𝐧𝐝 𝐫𝐞𝐚𝐝𝐲!\n\n"
        f"𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬: 𝟏𝟎𝟎%"
    )

    await asyncio.sleep(1)
    
    if m.chat.id in AUTH_USERS:
        await start_message.edit_text(
            f"🌟 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {m.from_user.first_name}! 🌟\n\n"
            f"𝐆𝐫𝐞𝐚𝐭! 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐚 𝐩𝐫𝐞𝐦𝐢𝐮𝐦 𝐦𝐞𝐦𝐛𝐞𝐫!\n"
            f"𝐔𝐬𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 : /help 𝐭𝐨 𝐠𝐞𝐭 𝐬𝐭𝐚𝐫𝐭𝐞𝐝 🌟\n\n"
            f"𝐈𝐟 𝐲𝐨𝐮 𝐟𝐚𝐜𝐞 𝐚𝐧𝐲 𝐩𝐫𝐨𝐛𝐥𝐞𝐦 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 - 𝐖𝐀𝐑𝐑𝐈𝐎𝐑 👨‍💻\n",
            disable_web_page_preview=True,
            reply_markup=BUTTONSCONTACT
        )

    else:
         await asyncio.sleep(2)
await start_message.edit_text(
    f"🎊 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {m.from_user.first_name} 𝐭𝐨 𝐃𝐑𝐌 𝐁𝐨𝐭! 🎊\n\n"
    f"🔓 𝐘𝐨𝐮 𝐜𝐚𝐧 𝐡𝐚𝐯𝐞 𝐚𝐜𝐜𝐞𝐬𝐬 𝐭𝐨 𝐝𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐚𝐥𝐥 𝐍𝐨𝐧-𝐃𝐑𝐌 + 𝐀𝐄𝐒 𝐄𝐧𝐜𝐫𝐲𝐩𝐭𝐞𝐝 𝐔𝐑𝐋𝐬 🔐 𝐢𝐧𝐜𝐥𝐮𝐝𝐢𝐧𝐠\n\n"
    f"✨ 𝐔𝐬𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 : /help 𝐭𝐨 𝐠𝐞𝐭 𝐬𝐭𝐚𝐫𝐭𝐞𝐝 ✨\n\n"
    f"<blockquote>"
    f"• 🗂️ 𝐀𝐩𝐩𝐱 𝐙𝐢𝐩 + 𝐄𝐧𝐜𝐫𝐲𝐩𝐭𝐞𝐝 𝐔𝐫𝐥\n"
    f"• 🎒 𝐂𝐥𝐚𝐬𝐬𝐩𝐥𝐮𝐬 𝐃𝐑𝐌 + 𝐍𝐃𝐑𝐌\n"
    f"• 👨‍🏫 𝐏𝐡𝐲𝐬𝐢𝐜𝐬𝐖𝐚𝐥𝐥𝐚𝐡 𝐃𝐑𝐌\n"
    f"• 📘 𝐂𝐚𝐫𝐞𝐞𝐫𝐖𝐢𝐥𝐥 + 𝐏𝐃𝐅\n"
    f"• 🧠 𝐊𝐡𝐚𝐧 𝐆𝐒\n"
    f"• 📝 𝐒𝐭𝐮𝐝𝐲 𝐈𝐐 𝐃𝐑𝐌\n"
    f"• ⚡ 𝐀𝐏𝐏𝐗 + 𝐀𝐏𝐏𝐗 𝐄𝐧𝐜 𝐏𝐃𝐅\n"
    f"• 📺 𝐕𝐢𝐦𝐞𝐨 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧\n"
    f"• 🎥 𝐁𝐫𝐢𝐠𝐡𝐭𝐜𝐨𝐯𝐞 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧\n"
    f"• 🎯 𝐕𝐢𝐬𝐢𝐨𝐧𝐢𝐚𝐬 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧\n"
    f"• 💻 𝐙𝐨𝐨𝐦 𝐕𝐢𝐝𝐞𝐨\n"
    f"• 📚 𝐔𝐭𝐤𝐚𝐫𝐬𝐡 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧 (𝐕𝐢𝐝𝐞𝐨 + 𝐏𝐃𝐅)\n"
    f"• 🔐 𝐀𝐥𝐥 𝐍𝐨𝐧 𝐃𝐑𝐌 + 𝐀𝐄𝐒 𝐄𝐧𝐜𝐫𝐲𝐩𝐭𝐞𝐝 𝐔𝐑𝐋𝐬\n"
    f"• 🧩 𝐌𝐏𝐃 𝐔𝐑𝐋𝐬 𝐢𝐟 𝐭𝐡𝐞 𝐤𝐞𝐲 𝐢𝐬 𝐤𝐧𝐨𝐰𝐧 (𝐞.𝐠., 𝐌𝐩𝐝_𝐮𝐫𝐥?𝐤𝐞𝐲=𝐤𝐞𝐲 𝐗𝐗:𝐗𝐗)\n"
    f"</blockquote>\n\n"
    f"🚫 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐛𝐞𝐝 𝐭𝐨 𝐚𝐧𝐲 𝐩𝐥𝐚𝐧 𝐲𝐞𝐭!\n\n"
    f"<blockquote>💸 𝐃𝐚𝐢𝐥𝐲 𝐏𝐥𝐚𝐧: 100</blockquote>\n\n"
    f"📩 𝐈𝐟 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭 𝐭𝐨 𝐛𝐮𝐲 𝐦𝐞𝐦𝐛𝐞𝐫𝐬𝐡𝐢𝐩 𝐨𝐟 𝐭𝐡𝐞 𝐛𝐨𝐭, 𝐟𝐞𝐞𝐥 𝐟𝐫𝐞𝐞 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐭𝐡𝐞 𝐁𝐨𝐭 𝐀𝐝𝐦𝐢𝐧.\n",
    disable_web_page_preview=True,
    reply_markup=keyboard
)

@Client.on_message(filters.command(["upgrade"]))
async def id_command(client, message: Message):
    await message.reply_text(
        f"🎉 Welcome {message.from_user.first_name} to DRM Bot! 🎉\n\n"
        f"You can have access to download all Non-DRM+AES Encrypted URLs 🔐 including\n\n"
        f"Use Command : /help to get started 🌟\n\n"
        f"• 📚 Appx Zip+Encrypted Url\n"
        f"• 🎓 Classplus DRM+ NDRM\n"
        f"• 🧑‍🏫 PhysicsWallah DRM\n"
        f"• 📚 CareerWill + PDF\n"
        f"• 🎓 Khan GS\n"
        f"• 🎓 Study Iq DRM\n"
        f"• 🚀 APPX + APPX Enc PDF\n"
        f"• 🎓 Vimeo Protection\n"
        f"• 🎓 Brightcove Protection\n"
        f"• 🎓 Visionias Protection\n"
        f"• 🎓 Zoom Video\n"
        f"• 🎓 Utkarsh Protection(Video + PDF)\n"
        f"• 🎓 All Non DRM+AES Encrypted URLs\n"
        f"• 🎓 MPD URLs if the key is known (e.g., Mpd_url?key=key XX:XX)\n\n"
        f"<blockquote>💵 Daily Plan: 100</blockquote>\n\n"
        f"If you want to buy membership of the bot, feel free to contact the Bot Admin.\n",
        disable_web_page_preview=True,
        reply_markup=BUTTONSCONTACT
    )
@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    await message.reply_text(f"<blockquote>The ID of this chat id is:</blockquote>\n`{chat_id}`")

@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    
    text = (
        f"╭────────────────╮\n"
        f"│✨ **Your Telegram Info**✨ \n"
        f"├────────────────\n"
        f"├🔹**Name :** `{update.from_user.first_name} {update.from_user.last_name if update.from_user.last_name else 'None'}`\n"
        f"├🔹**User ID :** @{update.from_user.username}\n"
        f"├🔹**TG ID :** `{update.from_user.id}`\n"
        f"├🔹**Profile :** {update.from_user.mention}\n"
        f"╰────────────────╯"
    )
    
    await update.reply_text(        
        text=text,
        disable_web_page_preview=True,
        reply_markup=BUTTONSCONTACT
    )

@bot.on_message(filters.command(["help"]))
async def txt_handler(client: Client, m: Message):
    await bot.send_photo(
        chat_id=m.chat.id,
        photo="https://i.postimg.cc/DfPjCqYf/c78f47eb1be7788ebe3f60079d6cbe40.jpg",
        caption=(
            """
 ═════𓆩🍧𓆪═════╗  
🦚  𝐇𝐄𝐋𝐏 𝐌𝐄𝐍𝐔  🦚  
╚═════𓆩🍧𓆪═════╝

🧩 𝐁𝐚𝐬𝐢𝐜:

• /start — 𝐒𝐭𝐚𝐫𝐭 𝐭𝐡𝐞 𝐁𝐨𝐭  
• /drm — 𝐃𝐫𝐚𝐰 𝐟𝐫𝐨𝐦 .𝐭𝐱𝐭  
• /stop — 𝐒𝐭𝐨𝐩 𝐚𝐧𝐲 𝐭𝐚𝐬𝐤

💻 𝐕𝐢𝐝𝐞𝐨 𝐓𝐨𝐨𝐥𝐬:

• /y2t — 𝐘𝐓 𝐭𝐨 𝐓𝐞𝐱𝐭  
• /cookies — 𝐔𝐩𝐝𝐚𝐭𝐞 𝐂𝐨𝐨𝐤𝐢𝐞𝐬

👤 𝐔𝐬𝐞𝐫:

• /id — 𝐘𝐨𝐮𝐫 𝐈𝐃  
• /info — 𝐘𝐨𝐮𝐫 𝐃𝐞𝐭𝐚𝐢𝐥𝐬  
• /logs — 𝐕𝐢𝐞𝐰 𝐀𝐜𝐭𝐢𝐯𝐢𝐭𝐲

🔐 𝐀𝐝𝐦𝐢𝐧 𝐌𝐨𝐝𝐞:

• /addauth /rmauth /users

💎 𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲: @staystrongbros
╰━━━━━━━━━━━━━━━━━━━━━━━╯
"""
        )
    ) 
          
@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):  # Correct parameter name
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("**📤 Sending you ....**")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(f"Error sending logs: {e}")

@bot.on_message(filters.command(["drm"]) )
async def txt_handler(bot: Client, m: Message):  
    editable = await m.reply_text(f"🌟 𝐇𝐢𝐢, 𝐈 𝐚𝐦 𝐃𝐑𝐌 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐫 𝐁𝐨𝐭\n\n"
f"📥 𝐒𝐞𝐧𝐝 𝐌𝐞 𝐘𝐨𝐮𝐫 .𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐰𝐡𝐢𝐜𝐡 𝐢𝐧𝐜𝐥𝐮𝐝𝐞𝐬 𝐍𝐚𝐦𝐞 𝐰𝐢𝐭𝐡 𝐮𝐫𝐥...\n"
f"💫 𝐄.𝐠: 𝐍𝐚𝐦𝐞: 𝐋𝐢𝐧𝐤")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))  # Extract filename & extension
    path = f"./downloads/{m.chat.id}"
    pdf_count = 0
    img_count = 0
    other_count = 0
    
    try:    
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        
        links = []
        for i in content:
            if "://" in i:
                url = i.split("://", 1)[1]
                links.append(i.split("://", 1))
                if ".pdf" in url:
                    pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")):
                    img_count += 1
                else:
                    other_count += 1
        os.remove(x)
    except:
        await m.reply_text("<pre><code>🔹Invalid file input.</code></pre>")
        os.remove(x)
        return
    
    await editable.edit(f"🧾 𝐖𝐨𝐰! {len(links)} 🔗 𝐋𝐢𝐧𝐤𝐬 𝐃𝐞𝐭𝐞𝐜𝐭𝐞𝐝!\n⚡ 𝐑𝐞𝐩𝐥𝐲 𝐰𝐢𝐭𝐡 𝐭𝐡𝐞 𝐒𝐭𝐚𝐫𝐭 𝐏𝐨𝐢𝐧𝐭 — 𝐁𝐲 𝐃𝐞𝐟𝐚𝐮𝐥𝐭: 𝟏")
    if m.chat.id not in AUTH_USERS:
        print(f"User ID not in AUTH_USERS", m.chat.id)
        await bot.send_message(m.chat.id, f"🚫 𝐎𝐨𝐩𝐬𝐬! 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 😚 𝐦𝐞𝐦𝐛𝐞𝐫. 𝐏𝐋𝐄𝐀𝐒𝐄 /upgrade 𝐲𝐨𝐮𝐫 𝐩𝐥𝐚𝐧. 𝐒𝐞𝐧𝐝 𝐦𝐞 𝐲𝐨𝐮𝐫 𝐮𝐬𝐞𝐫 𝐢𝐝 𝐟𝐨𝐫 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐳𝐚𝐭𝐢𝐨𝐧. 🆔 𝐘𝐨𝐮𝐫 𝐔𝐬𝐞𝐫 𝐈𝐃 - `{m.chat.id}`")
        return
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
           
    await editable.edit(f"📝 𝐄𝐧𝐭𝐞𝐫 𝐁𝐚𝐭𝐜𝐡 𝐍𝐚𝐦𝐞 𝐨𝐫 𝐬𝐞𝐧𝐝 /d 𝐟𝐨𝐫 𝐠𝐫𝐚𝐛𝐛𝐢𝐧𝐠 𝐟𝐫𝐨𝐦 𝐭𝐞𝐱𝐭 𝐟𝐢𝐥𝐞𝐧𝐚𝐦𝐞. 📂")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == '/d':
        b_name = file_name.replace('_', ' ')
    else:
        b_name = raw_text0

    await editable.edit("𝐄𝐧𝐭𝐞𝐫 𝐫𝐞𝐬𝐨𝐥𝐮𝐭𝐢𝐨𝐧 𝐨𝐫 𝐕𝐢𝐝𝐞𝐨 𝐐𝐮𝐚𝐥𝐢𝐭𝐲 💻 (`144`, `240`, `360`, `480`, `720`, `1080`)__") 
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    quality = f"{raw_text2}p"
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"

    await editable.edit("__Enter the credit name for the caption. If you want both a permanent credit in the caption and the file name, separate them with a comma (,). or you want default then send /d__\n\n<blockquote><i>Example for caption only: Admin\nExample for both caption and file name: Admin,Prename</i></blockquote>")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    if raw_text3 == '/d':
        CR = f"{CREDIT}"
    elif "," in raw_text3:
        CR, PRENAME = raw_text3.split(",")
    else:
        CR = raw_text3

    await editable.edit("🔸𝐄𝐧𝐭𝐞𝐫 𝐘𝐨𝐮𝐫 𝐏𝐖 𝐓𝐨𝐤𝐞𝐧 𝐅𝐨𝐫 𝐌𝐏𝐃 𝐔𝐑𝐋\n🔸𝐒𝐞𝐧𝐝 /anything 𝐟𝐨𝐫 𝐮𝐬𝐞 𝐝𝐞𝐟𝐚𝐮𝐥𝐭")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)

    await editable.edit(f"𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐕𝐢𝐝𝐞𝐨 𝐓𝐡𝐮𝐦𝐛 𝐔𝐑𝐋\n𝐒𝐞𝐧𝐝 /d 𝐟𝐨𝐫 𝐮𝐬𝐞 𝐝𝐞𝐟𝐚𝐮𝐥𝐭\n\n𝐘𝐨𝐮 𝐜𝐚𝐧 𝐝𝐢𝐫𝐞𝐜𝐭 𝐮𝐩𝐥𝐨𝐚𝐝 𝐭𝐡𝐮𝐦𝐛\n𝐒𝐞𝐧𝐝 No 𝐟𝐨𝐫 𝐮𝐬𝐞 𝐝𝐞𝐟𝐚𝐮𝐥𝐭")
    input6 = message = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)

    if input6.photo:
        thumb = await input6.download()  # Use the photo sent by the user
    elif raw_text6.startswith("http://") or raw_text6.startswith("https://"):
        # If a URL is provided, download thumbnail from the URL
        getstatusoutput(f"wget '{raw_text6}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = raw_text6

    await editable.edit("📺 𝐏𝐥𝐞𝐚𝐬𝐞 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐢𝐝 𝐨𝐫 𝐰𝐡𝐞𝐫𝐞 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭 𝐭𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 𝐯𝐢𝐝𝐞𝐨 𝐨𝐫 𝐒𝐞𝐧𝐭 𝐕𝐢𝐝𝐞𝐨 𝐨𝐭𝐡𝐞𝐫𝐰𝐢𝐬𝐞 /d\n\n__⚠️ 𝐀𝐧𝐝 𝐦𝐚𝐤𝐞 𝐦𝐞 𝐚𝐝𝐦𝐢𝐧 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐭𝐡𝐞𝐧 𝐢 𝐜𝐚𝐧 𝐚𝐛𝐥𝐞 𝐭𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 𝐨𝐭𝐡𝐞𝐫𝐰𝐢𝐬𝐞 𝐢 𝐜𝐚𝐧'𝐭")
    input7: Message = await bot.listen(editable.chat.id)
    raw_text7 = input7.text
    if "/d" in input7.text:
        channel_id = m.chat.id
    else:
        channel_id = input7.text
    await input7.delete()     
    await editable.delete()

    if "/d" in raw_text7:
        batch_message = await m.reply_text(f"<b>⚡Target Batch : {b_name}</b>")
    else:
        try:
            batch_message = await bot.send_message(chat_id=channel_id, text=f"<b> Target Batch : {b_name}</b>")
            await bot.send_message(chat_id=m.chat.id, text=f"<b><i>⚡Target Batch : {b_name}</i></b>\n\n🔄 Your Task is under processing, please check your Set Channel📱. Once your task is complete, I will inform you 📩")
        except Exception as e:
            await m.reply_text(f"**Fail Reason »** {e}\n")
            return
        
    failed_count = 0
    count =int(raw_text)    
    arg = int(raw_text)
    try:
        for i in range(arg-1, len(links)):
            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            link0 = "https://" + Vxy

            name1 = links[i][0].replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            if "," in raw_text3:
                 name = f'{PRENAME} {name1[:60]}'
            else:
                 name = f'{name1[:60]}'
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'

            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "classplusapp.com/drm/" in url:
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "tencdn.classplusapp" in url:
                headers = {'Host': 'api.classplusapp.com', 'x-access-token': f'{token_cp}', 'user-agent': 'Mobile-Android', 'app-version': '1.4.37.1', 'api-version': '18', 'device-id': '5d0d17ac8b3c9f51', 'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30', 'accept-encoding': 'gzip'}
                params = (('url', f'{url}'))
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']  

            elif 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{token_cp}'}).json()['url']
            
            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                headers = { 'x-access-token': f'{token_cp}',"X-CDN-Tag": "empty"}
                response = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers)
                url   = response.json()['url']

            elif "childId" in url and "parentId" in url:
                url = f"https://anonymousrajputplayer-9ab2f2730a02.herokuapp.com/pw?url={url}&token={raw_text4}"
                           
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={raw_text4}"

            if ".pdf*" in url:
                url = f"https://dragoapi.vercel.app/pdf/{url}"
            
            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

            if "youtu" in url:
                ytf = f"bv*[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[height<=?{raw_text2}]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                cc = f'[💻]Video : {str(count).zfill(3)}\n**Video Title :** `{name1} [{res}p] .mkv`\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by➤**`{CR}`\n'
                cc1 = f'[📕]Pdf Id : {str(count).zfill(3)}\n**File Title :** `{name1} .pdf`\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by➤**`{CR}`\n'
                cczip = f'[📁]Zip Id : {str(count).zfill(3)}\n**Zip Title :** `{name1} .zip`\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by➤**`{CR}`\n' 
                ccimg = f'[🖼️]Img Id : {str(count).zfill(3)}\n**Img Title :** `{name1} .jpg`\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by➤**`{CR}`\n'
                ccm = f'[🎵]Audio Id : {str(count).zfill(3)}\n**Audio Title :** `{name1} .mp3`\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by➤**`{CR}`\n'
                cchtml = f'[🌐]Html Id : {str(count).zfill(3)}\n**Html Title :** `{name1} .html`\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by➤**`{CR}`\n'
                  
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=channel_id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
  
                elif ".pdf" in url:
                    if "cwmediabkt99" in url:
                        max_retries = 15  # Define the maximum number of retries
                        retry_delay = 4  # Delay between retries in seconds
                        success = False  # To track whether the download was successful
                        failure_msgs = []  # To keep track of failure messages
                        
                        for attempt in range(max_retries):
                            try:
                                await asyncio.sleep(retry_delay)
                                url = url.replace(" ", "%20")
                                scraper = cloudscraper.create_scraper()
                                response = scraper.get(url)

                                if response.status_code == 200:
                                    with open(f'{name}.pdf', 'wb') as file:
                                        file.write(response.content)
                                    await asyncio.sleep(retry_delay)  # Optional, to prevent spamming
                                    copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                                    count += 1
                                    os.remove(f'{name}.pdf')
                                    success = True
                                    break  # Exit the retry loop if successful
                                else:
                                    failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {response.status_code} {response.reason}")
                                    failure_msgs.append(failure_msg)
                                    
                            except Exception as e:
                                failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                                failure_msgs.append(failure_msg)
                                await asyncio.sleep(retry_delay)
                                continue 
                        for msg in failure_msgs:
                            await msg.delete()
                            
                    else:
                        try:
                            cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                            download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                            os.system(download_cmd)
                            copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                            count += 1
                            os.remove(f'{name}.pdf')
                        except FloodWait as e:
                            await m.reply_text(str(e))
                            time.sleep(e.x)
                            continue    

                elif ".ws" in url and  url.endswith(".ws"):
                    try:
                        await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}",f"{name}.html")
                        time.sleep(1)
                        await bot.send_document(chat_id=channel_id, document=f"{name}.html", caption=cchtml)
                        os.remove(f'{name}.html')
                        count += 1
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
                            
                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_photo(chat_id=channel_id, photo=f'{name}.{ext}', caption=ccimg)
                        count += 1
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=channel_id, document=f'{name}.{ext}', caption=ccm)
                        count += 1
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
                    
                elif 'encrypted.m' in url:    
                    Show = f"__**Video Downloading__**\n<pre><code>{str(count).zfill(3)}) {name1}</code></pre>"
                    prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                    filename = res_file  
                    await prog.delete(True)  
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    count += 1  
                    await asyncio.sleep(1)  
                    continue  

                elif 'drmcdni' in url or 'drm/wv' in url:
                    Show = f"__**Video Downloading__**\n<pre><code>{str(count).zfill(3)}) {name1}</code></pre>"
                    prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    count += 1
                    await asyncio.sleep(1)
                    continue
     
                else:
                    Show = f"__**Video Downloading__**\n<pre><code>{str(count).zfill(3)}) {name1}</code></pre>"
                    prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    count += 1
                    time.sleep(1)
                
            except Exception as e:
                await bot.send_message(channel_id, f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}\n\n<pre><i><b>Failed Reason: {str(e)}</b></i></pre>', disable_web_page_preview=True)
                count += 1
                failed_count += 1
                continue

    except Exception as e:
        await m.reply_text(e)
        time.sleep(2)

    success_count = len(links) - failed_count
    if raw_text7 == "/d":
        await bot.send_message(channel_id, f"""
<b>╭─❍ 𓆩🪐𓆪 ❍─╮</b>  
<b>✅ 𝐔𝐩𝐥𝐨𝐚𝐝 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞</b>  
<b>╰─❍ 𓆩🪐𓆪 ❍─╯</b>

🔮 <b>𝐁𝐚𝐭𝐜𝐡 𝐍𝐚𝐦𝐞:</b> <code>{b_name}</code>  
🔗 <b>𝐓𝐨𝐭𝐚𝐥 𝐔𝐑𝐋𝐬:</b> <code>{len(links)}</code>  
🗑 <b>𝐅𝐚𝐢𝐥𝐞𝐝:</b> <code>{failed_count}</code>  
✅ <b>𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥:</b> <code>{success_count}</code>  

<b>🗂 𝐅𝐢𝐥𝐞 𝐁𝐫𝐞𝐚𝐤𝐝𝐨𝐰𝐧:</b>  
💻 𝐕𝐢𝐝𝐞𝐨𝐬: <code>{other_count}</code>  
📄 𝐏𝐃𝐅𝐬: <code>{pdf_count}</code>  
🎄 𝐈𝐦𝐚𝐠𝐞𝐬: <code>{img_count}</code>
""")
        await bot.send_message(m.chat.id, f"<blockquote><b>✅ 𝐘𝐨𝐮𝐫 𝐓𝐚𝐬𝐤 𝐢𝐬 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝, 𝐩𝐥𝐞𝐚𝐬𝐞 𝐜𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐒𝐞𝐭 𝐂𝐡𝐚𝐧𝐧𝐞𝐥📱</b></blockquote>")


@bot.on_message(filters.text & filters.private)
async def text_handler(bot: Client, m: Message):
    if m.from_user.is_bot:
        return
    links = m.text
    path = None
    match = re.search(r'https?://\S+', links)
    if match:
        link = match.group(0)
    else:
        await m.reply_text("<pre><code>Invalid link format.</code></pre>")
        return
        
    editable = await m.reply_text(f"<pre><code>**🔹Processing your link...\n🔁Please wait...⏳**</code></pre>")
    await m.delete()

    await editable.edit(f"╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`{CREDIT}`]⚡⌋━━➣ ")
    input2: Message = await bot.listen(editable.chat.id, filters=filters.text & filters.user(m.from_user.id))
    raw_text2 = input2.text
    quality = f"{raw_text2}p"
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
          
    await editable.edit("<pre><code>Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋\nOtherwise send anything</code></pre>")
    input4: Message = await bot.listen(editable.chat.id, filters=filters.text & filters.user(m.from_user.id))
    raw_text4 = input4.text
    await input4.delete(True)
    await editable.delete(True)
     
    thumb = "/d"
    count =0
    arg =1
    channel_id = m.chat.id
    try:
            Vxy = link.replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = Vxy

            name1 = links.replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{name1[:60]}'
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'

            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "classplusapp.com/drm/" in url:
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "tencdn.classplusapp" in url:
                headers = {'Host': 'api.classplusapp.com', 'x-access-token': f'{token_cp}', 'user-agent': 'Mobile-Android', 'app-version': '1.4.37.1', 'api-version': '18', 'device-id': '5d0d17ac8b3c9f51', 'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30', 'accept-encoding': 'gzip'}
                params = (('url', f'{url}'))
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']  

            elif 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{token_cp}'}).json()['url']
            
            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                headers = { 'x-access-token': f'{token_cp}',"X-CDN-Tag": "empty"}
                response = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers)
                url   = response.json()['url']

            elif "childId" in url and "parentId" in url:
                url = f"https://pwplayer-38c1ae95b681.herokuapp.com/pw?url={url}&token={raw_text4}"
                           
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                vid_id =  url.split('/')[-2]
                #url = f"https://pwplayer-38c1ae95b681.herokuapp.com/pw?url={url}&token={raw_text4}"
                url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={raw_text4}"
                #url =  f"{api_url}pw-dl?url={url}&token={raw_text4}&authorization={api_token}&q={raw_text2}"
                #url = f"https://dl.alphacbse.site/download/{vid_id}/master.m3u8"
            
            #elif '/master.mpd' in url:    
                #headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NDYyODQwNTYuOTIsImRhdGEiOnsiX2lkIjoiNjdlYTcyYjZmODdlNTNjMWZlNzI5MTRlIiwidXNlcm5hbWUiOiI4MzQ5MjUwMTg1IiwiZmlyc3ROYW1lIjoiSGFycnkiLCJvcmdhbml6YXRpb24iOnsiX2lkIjoiNWViMzkzZWU5NWZhYjc0NjhhNzlkMTg5Iiwid2Vic2l0ZSI6InBoeXNpY3N3YWxsYWguY29tIiwibmFtZSI6IlBoeXNpY3N3YWxsYWgifSwicm9sZXMiOlsiNWIyN2JkOTY1ODQyZjk1MGE3NzhjNmVmIl0sImNvdW50cnlHcm91cCI6IklOIiwidHlwZSI6IlVTRVIifSwiaWF0IjoxNzQ1Njc5MjU2fQ.6WMjQPLUPW-fMCViXERGSqhpFZ-FyX-Vjig7L531Q6U", "client-type": "WEB", "randomId": "142d9660-50df-41c0-8fcb-060609777b03"}
                #id =  url.split("/")[-2] 
                #policy = requests.post('https://api.penpencil.xyz/v1/files/get-signed-cookie', headers=headers, json={'url': f"https://d1d34p8vz63oiq.cloudfront.net/" + id + "/master.mpd"}).json()['data']
                #url = "https://sr-get-video-quality.selav29696.workers.dev/?Vurl=" + "https://d1d34p8vz63oiq.cloudfront.net/" + id + f"/hls/{raw_text2}/main.m3u8" + policy
                #print(url)

            if ".pdf*" in url:
                url = f"https://dragoapi.vercel.app/pdf/{url}"
            if ".zip" in url:
                url = f"https://video.pablocoder.eu.org/appx-zip?url={url}"
                
            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

            if "youtu" in url:
                ytf = f"bv*[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[height<=?{raw_text2}]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                cc = f'🎞️𝐓𝐢𝐭𝐥𝐞 » `{name} [{res}].mp4`\n🔗𝐋𝐢𝐧𝐤 » <a href="{link}">__**CLICK HERE**__</a>\n\n🌟𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 » `{CREDIT}`'
                cc1 = f'📕𝐓𝐢𝐭𝐥𝐞 » `{name}`\n🔗𝐋𝐢𝐧𝐤 » <a href="{link}">__**CLICK HERE**__</a>\n\n🌟𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 » `{CREDIT}`'
                  
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass

                elif ".pdf" in url:
                    if "cwmediabkt99" in url:
                        max_retries = 15  # Define the maximum number of retries
                        retry_delay = 4  # Delay between retries in seconds
                        success = False  # To track whether the download was successful
                        failure_msgs = []  # To keep track of failure messages
                        
                        for attempt in range(max_retries):
                            try:
                                await asyncio.sleep(retry_delay)
                                url = url.replace(" ", "%20")
                                scraper = cloudscraper.create_scraper()
                                response = scraper.get(url)

                                if response.status_code == 200:
                                    with open(f'{name}.pdf', 'wb') as file:
                                        file.write(response.content)
                                    await asyncio.sleep(retry_delay)  # Optional, to prevent spamming
                                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                                    os.remove(f'{name}.pdf')
                                    success = True
                                    break  # Exit the retry loop if successful
                                else:
                                    failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {response.status_code} {response.reason}")
                                    failure_msgs.append(failure_msg)
                                    
                            except Exception as e:
                                failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                                failure_msgs.append(failure_msg)
                                await asyncio.sleep(retry_delay)
                                continue  # Retry the next attempt if an exception occurs

                        # Delete all failure messages if the PDF is successfully downloaded
                        for msg in failure_msgs:
                            await msg.delete()
                            
                        if not success:
                            # Send the final failure message if all retries fail
                            await m.reply_text(f"Failed to download PDF after {max_retries} attempts.\n⚠️**Downloading Failed**⚠️\n**Name** =>> {str(count).zfill(3)} {name1}\n**Url** =>> {link0}", disable_web_page_preview)
                            
                    else:
                        try:
                            cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                            download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                            os.system(download_cmd)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            os.remove(f'{name}.pdf')
                        except FloodWait as e:
                            await m.reply_text(str(e))
                            time.sleep(e.x)
                            pass   

                elif ".ws" in url and  url.endswith(".ws"):
                    try:
                        await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}",f"{name}.html")
                        time.sleep(1)
                        await bot.send_document(chat_id=m.chat.id, document=f"{name}.html", caption=cc1)
                        os.remove(f'{name}.html')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass
                        
                elif ".zip" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.zip" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.zip', caption=cc1)
                        os.remove(f'{name}.zip')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass    

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -x --audio-format {ext} -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        await bot.send_document(chat_id=m.chat.id, document=f'{name}.{ext}', caption=cc1)
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass

                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_photo(chat_id=m.chat.id, photo=f'{name}.{ext}', caption=cc1)
                        count += 1
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass
                                
                elif 'encrypted.m' in url:    
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                    filename = res_file  
                    await prog.delete(True)  
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    await asyncio.sleep(1)  
                    pass

                elif 'drmcdni' in url or 'drm/wv' in url:
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    await asyncio.sleep(1)
                    pass
     
                else:
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    time.sleep(1)

            except Exception as e:
                    await m.reply_text(f"⚠️𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐈𝐧𝐭𝐞𝐫𝐮𝐩𝐭𝐞𝐝\n\n🔗𝐋𝐢𝐧𝐤 » `{link}`\n\n__**⚠️Failed Reason »**__\n{str(e)}")
                    pass

    except Exception as e:
        await m.reply_text(str(e))




bot.run()
