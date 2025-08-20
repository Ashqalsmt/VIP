# الملف: restart_plugin.py
# حقوق: الأسطورة عاشق الصمت
# سورس يمنثون - إعادة تشغيل السورس

import os
import sys
import asyncio
import time
from .. import zedub 
from ..core.managers import edit_or_reply

@zedub.zed_cmd(pattern=r"(اعاده تشغيل|اعادة تشغيل|اعاده التشغيل|اعادة التشغيل)$")
async def restart_ymthon(event):
    restart_steps = [
        {"percent": 10, "message": "جـاري إعـادة تشغيـل السـورس.. 🌐", "bar": "▰▱▱▱▱▱▱▱▱"},
        {"percent": 20, "message": "جـاري إغلـاق الاتصـالات.. 📡", "bar": "▰▰▱▱▱▱▱▱▱"},
        {"percent": 30, "message": "جـاري حفظ الإعدادات.. 💾", "bar": "▰▰▰▱▱▱▱▱▱"},
        {"percent": 40, "message": "جـاري إيقـاف الوحـدات.. ⚙️", "bar": "▰▰▰▰▱▱▱▱▱"},
        {"percent": 50, "message": "جـاري تحميـل الملفـات.. 📂", "bar": "▰▰▰▰▰▱▱▱▱"},
        {"percent": 60, "message": "جـاري تهيئـة النظـام.. 🔧", "bar": "▰▰▰▰▰▰▱▱▱"},
        {"percent": 70, "message": "جـاري تشغيـل الخدمـات.. 🛠️", "bar": "▰▰▰▰▰▰▰▱▱"},
        {"percent": 80, "message": "جـاري التحقـق من القـواعد.. 📊", "bar": "▰▰▰▰▰▰▰▰▱"},
        {"percent": 90, "message": "جـاري تنشـيط النظـام.. ⚡", "bar": "▰▰▰▰▰▰▰▰▰"},
        {"percent": 100, "message": "تمـت العمليـة بنجـاح! ✅", "bar": "▰▰▰▰▰▰▰▰▰▰"}
    ]

    msg = await edit_or_reply(event, "**⎈ بدء إجراءات إعادة التشغيل.. 🌀**")
    
    for step in restart_steps:
        progress_text = (
            f"𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉](t.me/YamenThon) 𓆪\n"
            f"**{step['message']}**\n\n"
            f"⎔ **التقدم:** {step['percent']}%\n"
            f"⎔ **الحالة:** `{step['bar']}`\n\n"
            f"**⎈ الرجـاء الانتظـار..** ⎝⏳⎠"
        )
        await msg.edit(progress_text)
        await asyncio.sleep(0.8)

    success_msg = (
        f"𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉](t.me/YamenThon) 𓆪\n\n"
        f"**⎈ تم إعـادة تشغيـل السـورس بنجـاح! 🎉**\n\n"
        f"⎔ **الحالة:** `✅ تم التنفيذ بنجاح`\n"
        f"⎔ **الوقت:** `{time.strftime('%H:%M:%S')}`\n\n"
        f"**⎈ تتم الان عمليه تجهيز البيانات انتظر 5 دقائق** ✨"
    )
    
    await msg.edit(success_msg)
    await asyncio.sleep(2)

    # إعادة تشغيل السورس فعليًا
    os.execl(sys.executable, sys.executable, "-m", "yamenthon")
