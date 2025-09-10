import os
import tempfile
from asyncio import sleep
from telethon import events, types
from datetime import datetime
from pytz import timezone
import logging

from yamenthon import zedub
from ..core.managers import edit_delete, edit_or_reply
from . import BOTLOG, BOTLOG_CHATID

LOGS = logging.getLogger(__name__)
repself = True

# ---- رسالة المساعدة والأوامر تبقى كما هي ----
# (حافظت على أوامرك كما في كودك الأصلي)

# أمر الحفظ بالرد (كما عندك)
@zedub.zed_cmd(pattern=f"{POSC}(?: |$)(.*)")
async def oho(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالـرد علـى صورة ذاتيـة التدميـر 𓆰...**")
    e_7_v = await event.get_reply_message()
    if not e_7_v.media:
        return await event.edit("**- ❝ ⌊الرد يجب أن يكون على صورة أو فيديو 𓆰...**")
    pic = None
    try:
        pic = await e_7_v.download_media()
        await zedub.send_file("me", pic, caption=f"**⎉╎تم حفـظ الصـورة الذاتيـه .. بنجـاح ☑️𓆰**")
        await event.delete()
    except Exception as e:
        await event.edit(f"**- ❝ ⌊خطأ في حفظ الذاتية: {e} 𓆰...**")
    finally:
        try:
            if pic and os.path.exists(pic):
                os.remove(pic)
        except:
            pass

# تفعيل/تعطيل كما في كودك
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

# ---- الهااندلر التلقائي المُحدّث: يكتشف أي وسائط في الخاص بما فيها ذاتية الحذف ----
@zedub.on(events.NewMessage(func=lambda e: e.is_private and e.media is not None))
async def sddm(event):
    """
    هذا handler يلتقط أي رسالة خاصة تحمل media (صور/فيديو/مستندات)
    ويجرب تنزيلها وحفظها في Saved Messages بغض النظر إن كانت view-once أو لا.
    """
    global repself
    try:
        if not repself:
            return

        # تجاهل رسائلك أنت
        me = await zedub.get_me()
        if event.sender_id == me.id:
            return

        msg = event.message

        # تحقق إن الميديا من نوع صورة/فيديو/مستند يحتوي على image/video mime
        is_media = False
        if getattr(msg, "photo", None) or getattr(msg, "video", None):
            is_media = True
        elif getattr(msg, "document", None):
            mt = getattr(msg.document, "mime_type", "") or ""
            if mt.startswith("image") or mt.startswith("video"):
                is_media = True

        if not is_media:
            return  # ليس صورة/فيديو — نتجاهل

        tmp_path = None
        file_path = None

        # تنزيل فوري إلى ملف مؤقت (نستخدم طرق متنوعة كاحتياط)
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_path = tmp_file.name
            # 1) حاول تنزيل من الرسالة نفسها
            try:
                file_path = await msg.download_media(file=tmp_path)
            except Exception:
                # 2) محاولة بديلة عن طريق client.download_media
                try:
                    file_path = await zedub.download_media(msg, file=tmp_path)
                except Exception:
                    # 3) محاولة client API صريحة
                    file_path = await event.client.download_media(msg, file=tmp_path)

            if not file_path or not os.path.exists(file_path):
                LOGS.warning("فشل في تنزيل الميديا للرسالة %s", msg.id)
                return

            # تجهيز الكابشن مع معلومات المرسل
            sender = await event.get_sender()
            chat = await event.get_chat()
            chat_title = getattr(chat, "title", getattr(chat, "first_name", "Unknown"))
            username = getattr(chat, "username", None)
            sender_name = getattr(sender, "first_name", "المُرسل")
            sender_mention = f'<a href="tg://user?id={sender.id}">{sender_name}</a>'

            caption = (
                f"┏ᑕᕼᗩT Iᗪ ⤳ <a href=\"tg://user?id={event.chat_id}\">{event.chat_id}</a>\n"
                f"┣ᑌՏᗴᖇᑎᗩᗰᗴ ⤳ {'@' + username if username else '✗'}\n"
                f"┣ᑌՏՏᗴᘜᗴ Iᗪ ⤳ {msg.id}\n"
                f"┣ᗪᗩTᗴ TIᗰᗴ ⤳ {datetime.now(timezone('Asia/Riyadh')).strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"┣ᗰᗴՏՏᗩᘜᗴ ⤳ {sender_mention}\n"
                f"┗ @T_A_Tl \n"
                f"عـزيـزي المـالك 🫂\n⌔╎ تـم حفـظ الذاتيـة تلقائيـاً .. بنجـاح ☑️\n\n"
                f"[ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 - حفـظ الذاتيـه 🧧](t.me/YamenThon)"
            )

            # إرسال الملف إلى Saved Messages
            await zedub.send_file("me", file_path, caption=caption, parse_mode="html")
            LOGS.info("تم حفظ ذاتية من %s (%s)", chat_title, event.sender_id)

        except Exception as e:
            LOGS.exception("فشل حفظ الذاتيه الآلي: %s", e)
            try:
                await zedub.send_message("me", f"⚠️ خطأ في حفظ الذاتيه: {e}")
            except Exception:
                pass
        finally:
            # حذف الملف المؤقت إن وجد
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    except Exception as outer_e:
        LOGS.exception("حصل خطأ غير متوقع في handler: %s", outer_e)
