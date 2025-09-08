import os
import tempfile
from datetime import datetime
from pytz import timezone

# تأكد أن المتغير الافتراضي موجود
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


# الحدث الآلي: حفظ الوسائط ذاتية التدمير عند الوصول في الخاص
@zedub.on(events.NewMessage(func=lambda e: e.is_private and e.media))
async def sddm(event):
    global repself
    if not repself:
        return

    # نتأكد أنها ميديا ذاتية التدمير (ttl)
    if not (hasattr(event.message.media, "ttl_seconds") and event.message.media.ttl_seconds):
        return

    tmp_path = None
    try:
        tf = tempfile.NamedTemporaryFile(delete=False)
        tmp_path = tf.name
        tf.close()

        file_path = await event.download_media(file=tmp_path)
        if not file_path:
            LOGS.warning("download_media returned None for message %s", event.message.id)
            return

        sender = await event.get_sender()
        caption = (
            f"[ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 - حفـظ الذاتيـه 🧧](t.me/YamenThon)\n\n"
            f"**⌔╎تم حفـظ الوسائـط الذاتيـة تلقائيـاً ☑️**\n"
            f"**⌔╎المـرسـل** {_format.mentionuser(sender.first_name, sender.id)}\n"
            f"**⌔╎التاريـخ** {datetime.now(timezone('Asia/Riyadh')).strftime('%Y/%m/%d %H:%M:%S')}"
        )
        await zedub.send_file("me", file_path, caption=caption, parse_mode="md")
    except Exception as e:
        LOGS.exception("فشل حفظ الذاتيه الآلي: %s", e)
        try:
            await zedub.send_message("me", f"⚠️ خطأ في حفظ الذاتيه: {e}")
        except Exception:
            pass
    finally:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
