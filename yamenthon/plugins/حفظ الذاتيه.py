import os
import tempfile
import shutil
from asyncio import sleep
from telethon import events, types
from jdatetime import datetime
from pytz import timezone
from argparse import ArgumentParser
from socks import SOCKS5
from colorama import Fore
import sqlite3
import getpass
import re


from yamenthon import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..core.logger import logging
from ..helpers.utils import _format
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..sql_helper.echo_sql import addecho, get_all_echos, get_echos, is_echo, remove_all_echos, remove_echo, remove_echos

from ..sql_helper.autopost_sql import get_all_post
from ..core.logger import logging
from . import BOTLOG, BOTLOG_CHATID
plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)
repself = True

POSC = gvarstatus("R_POSC") or "(مم|ذاتية|ذاتيه|جلب الوقتيه)"

BaqirSelf_cmd = (
    "𓆩 [ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 - حفـظ الذاتيـه 🧧](t.me/YamenThon) 𓆪\n\n"
    "**⪼** `.تفعيل الذاتيه`\n"
    "**لـ تفعيـل الحفظ التلقائي للذاتيـه**\n"
    "**سوف يقوم حسابك بحفظ الذاتيه تلقائياً في حافظة حسابك عندما يرسل لك اي شخص ميديـا ذاتيـه**\n\n"
    "**⪼** `.تعطيل الذاتيه`\n"
    "**لـ تعطيـل الحفظ التلقائي للذاتيـه**\n\n"
    "**⪼** `.ذاتيه`\n"
    "**بالـرد ؏ــلى صـوره ذاتيـه لحفظهـا في حال كان امر الحفظ التلقائي معطـل**\n\n\n"
    "**⪼** `.اعلان`\n"
    "**الامـر + الوقت بالدقائق + الرسـاله**\n"
    "**امـر مفيـد لجماعـة التمويـل لـ عمـل إعـلان مـؤقت بالقنـوات**\n\n"
    "\n 𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉](t.me/YamenThon) 𓆪"
)

@zedub.zed_cmd(pattern="الذاتيه")
async def cmd(baqir):
    await edit_or_reply(baqir, BaqirSelf_cmd)

@zedub.zed_cmd(pattern=f"{POSC}(?: |$)(.*)")
async def oho(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالـرد علـى صورة ذاتيـة التدميـر 𓆰...**")
    
    e_7_v = await event.get_reply_message()
    if not (e_7_v.photo or e_7_v.video or (e_7_v.document and e_7_v.document.mime_type.startswith(('image', 'video')))):
        return await event.edit("**- ❝ ⌊الرد يجب أن يكون على صورة أو فيديو 𓆰...**")
    
    try:
        pic = await e_7_v.download_media()
        await zedub.send_file("me", pic, caption=f"**⎉╎تم حفـظ الصـورة الذاتيـه .. بنجـاح ☑️𓆰**")
        await event.delete()
    except Exception as e:
        await event.edit(f"**- ❝ ⌊خطأ في حفظ الذاتية: {e} 𓆰...**")
    finally:
        # تنظيف الملف المؤقت
        try:
            if pic and os.path.exists(pic):
                os.remove(pic)
        except:
            pass

@zedub.zed_cmd(pattern="(تفعيل الذاتيه|تفعيل الذاتية)")
async def start_datea(event):
    global repself
    if repself:
        return await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. مفعـله مسبقـاً ☑️**")
    repself = True
    await edit_or_reply(event, "**⎉╎تم تفعيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")

@zedub.zed_cmd(pattern="(تعطيل الذاتيه|تعطيل الذاتية)")
async def stop_datea(event):
    global repself
    if repself:
        repself = False
        return await edit_or_reply(event, "**⎉╎تم تعطيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")
    await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. معطلـه مسبقـاً ☑️**")
    
# التلقائي - الطريقة الصحيحة لاكتشاف الذاتية
@zedub.on(events.NewMessage(func=lambda e: e.is_private and e.media))
async def sddm(event):
    global repself

    if event.sender_id == zedub.uid:
        return

    if not repself:
        return

    msg = event.message

    is_ttl = hasattr(msg.media, "ttl_seconds") and msg.media.ttl_seconds
    is_view_once = getattr(msg.media, "spoiler", False) or (
        isinstance(msg.media, types.MessageMediaPhoto) and msg.media.photo and msg.media.photo.has_view_once
    ) or (
        isinstance(msg.media, types.MessageMediaDocument) and msg.media.document and any(
            getattr(attr, "view_once", False) for attr in msg.media.document.attributes
        )
    )

    if not (is_ttl or is_view_once):
        return

    tmp_path = None
    try:
        sender = await event.get_sender()
        username = getattr(sender, 'username', None)
        sender_mention = f"<a href='tg://user?id={sender.id}'>{sender.first_name}</a>"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_path = tmp_file.name

        file_path = await msg.download_media(file=tmp_path)
        if not file_path or not os.path.exists(file_path):
            return

        await zedub.send_file(
            "me",
            file_path,
            caption=(
                f"┏ᑕᕼᗩT Iᗪ ⤳ <a href=\"tg://user?id={event.chat_id}\">{event.chat_id}</a>\n"
                f"┣ᑌՏᗴᖇᑎᗩᗰᗴ ⤳ {'@' + username if username else '✗'}\n"
                f"┣ᑌՏՏᗴᘜᗴ Iᗪ ⤳ {msg.id}\n"
                f"┣ᗪᗩTᗴ TIᗰᗴ ⤳ {datetime.now(timezone('Asia/Riyadh')).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"┣ᗰᗴՏՏᗩᘜᗴ ⤳ {sender_mention}\n"
                f"┗ @T_A_Tl \n"
                f"عـزيـزي المـالك 🫂\n⌔╎ تـم حفـظ الذاتيـة تلقائيـاً .. بنجـاح ☑️** ❝\n\n"
                f"[ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 - حفـظ الذاتيـه🧧](t.me/YamenThon)"
            )
        )

    except Exception as e:
        await zedub.send_message("me", f"⚠️ خطأ: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
