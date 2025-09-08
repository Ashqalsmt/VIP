import os
import tempfile
from datetime import datetime
from pytz import timezone
import os
import shutil
from asyncio import sleep
from telethon import events

from yamenthon import zedub
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



# أمر الحفظ اليدوي (.ذاتيه)
@zedub.zed_cmd(pattern="ذاتيه$")
async def manual_save(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالـرد علـى صورة/فيديو ذاتيـة 𓆰...**")
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.edit("**✘ الرسالة لا تحتوي على ميديا**")

    tmp_path = None
    try:
        # ننشئ ملف مؤقت بدون حذف تلقائي (سنحذفه بأنفسنا لاحقاً)
        tf = tempfile.NamedTemporaryFile(delete=False)
        tmp_path = tf.name
        tf.close()

        file_path = await reply.download_media(file=tmp_path)
        if not file_path:
            return await event.edit("**✘ لم أستطع تنزيل الملف — قد يكون الوسيط منتهي الصلاحية أو محمي.**")

        caption = "**⎉╎تم حفـظ الصـورة/الفيديـو الذاتيـه .. بنجـاح ☑️𓆰**"
        await zedub.send_file("me", file_path, caption=caption)
        # حذف رسالة الأمر لتبقى المحادثة نظيفة
        await event.delete()
    except Exception as e:
        await event.edit(f"⚠️ خطأ أثناء حفظ الذاتية: {e}")
    finally:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


@zedub.on(events.NewMessage(func=lambda e: e.is_private and (e.photo or e.video or e.document) and e.media_unread))
async def sddm(event):
    global repself
    zelzal = event.sender_id
    malath = zedub.uid
    # تجاهل الرسائل اللي أنت أرسلتهـا بنفس الحساب
    if zelzal == malath:
        return
    # إذا الحفظ التلقائي معطل ما نكمل
    if not repself:
        return

    msg = event.message

    # نتأكد أنها وسائط ذاتية التدمير (TTL)
    if not (hasattr(msg.media, "ttl_seconds") and msg.media.ttl_seconds):
        return

    tmp_path = None
    try:
        # تنزيل الملف إلى مسار مؤقت
        tf = tempfile.NamedTemporaryFile(delete=False)
        tmp_path = tf.name
        tf.close()

        file_path = await event.download_media(file=tmp_path)
        if not file_path:
            LOGS.warning("download_media returned None for message %s", msg.id)
            return

        # بيانات المرسل/المحادثة
        sender = await event.get_sender()
        chat = await event.get_chat()
        chat_title = getattr(chat, "title", getattr(chat, "first_name", "Unknown"))
        username = getattr(chat, "username", None)

        # نعمل منشن آمن للمرسل باستخدام رابط tg://user?id=
        sender_name = sender.first_name or "المُرسل"
        sender_mention = f'<a href="tg://user?id={sender.id}">{sender_name}</a>'

        # تكست مشابه لكود Mr3rf1 (HTML)
        caption = (
            f"┏ᑕᕼᗩT Iᗪ ⤳ <a href=\"tg://user?id={event.chat_id}\">{event.chat_id}</a>\n"
            f"┣ᑌՏᗴᖇᑎᗩᗰᗴ ⤳ {'@' + username if username else '✗'}\n"
            f"┣ᑌՏՏᗴᘜᗴ Iᗪ ⤳ {msg.id}\n"
            f"┣ᗪᗩTᗴ TIᗰᗴ ⤳ {datetime.now(timezone('Asia/Riyadh')).strftime('%Y/%m/%d %H:%M:%S')}\n"
            f"┣ᗰᗴՏՏᗩᘜᗴ ⤳ {sender_mention}\n"
            f"┗ github.com/Mr3rf1\n\n"
            f"[ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 - حفـظ الذاتيـه 🧧](t.me/YamenThon)"
        )

        # إرسال الملف إلى Saved Messages
        await zedub.send_file("me", file_path, caption=caption, parse_mode="html")
        LOGS.info("Saved self-destructing media from %s (%s)", chat_title, zelzal)

    except Exception as e:
        LOGS.exception("فشل حفظ الذاتيه الآلي: %s", e)
        try:
            await zedub.send_message("me", f"⚠️ خطأ في حفظ الذاتيه: {e}")
        except Exception:
            pass
    finally:
        # حذف الملف المؤقت
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
