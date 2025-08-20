# سورس يمنثون - تحديث السورس
from .. import zedub
from ..core.managers import edit_or_reply
import asyncio
import os
import sys
import subprocess
import git  # تحتاج تثبيت مكتبة GitPython: pip install GitPython

# ----------------------------------------
# دوال مساعدة لتعويض الدوال المفقودة
# ----------------------------------------

# دالة تنفيذ أوامر الباش
async def bash(cmd: str):
    """تشغيل أمر باش بشكل غير متزامن"""
    process = await asyncio.create_subprocess_shell(cmd)
    await process.communicate()


# دالة التحقق من التحديثات
def check_update():
    """ترجع True إذا هناك تحديثات متاحة"""
    try:
        repo = git.Repo(os.getcwd())
        origin = repo.remotes.origin
        origin.fetch()
        local = repo.head.commit
        remote = repo.remotes.origin.refs[repo.active_branch.name].commit
        return local.hexsha != remote.hexsha
    except Exception:
        return False


# دالة الحصول على الريموت URL
def get_remote_url():
    """ترجع رابط الريبو الحالي"""
    try:
        repo = git.Repo(os.getcwd())
        return next(repo.remote().urls)
    except Exception:
        return ""


# ----------------------------------------
# كود التحديث نفسه
# ----------------------------------------

@zedub.zed_cmd(pattern=r"تحديث(?:\s+(.*)|$)")
async def update_yamenthon(event):
    xx = await edit_or_reply(event, "**⌔∮ جار البحث عن تحديثات لسورس يـــمنثون**")
    cmd = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""

    # التحديث السريع أو الخفيف
    if cmd and ("سريع" in cmd or "خفيف" in cmd):
        await bash("git pull -f")
        await xx.edit("**⌔∮ جار التحديث الخفيف يرجى الأنتظار**")
        os.execl(sys.executable, sys.executable, "-m", "yamenthon")
        return

    # التحقق من التحديثات
    await xx.edit("**⌔∮ جاري التحقق من التحديثات...**")
    await asyncio.sleep(1)

    remote_url = get_remote_url()
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]

    has_update = check_update()
    if not has_update:
        return await xx.edit(
            f'<strong>سورس يـــمنثون مُحدث بأخر أصدار</strong>',
            parse_mode="html",
            link_preview=False,
        )

    # رسائل التقدم أثناء التحديث
    steps = [
        (10, "**⌔∮ جاري تحميل التحديثات...🌐**\n\n%𝟷𝟶 ▬▭▭▭▭▭▭▭▭▭"),
        (20, "**⌔∮ جاري تحميل التحديثات...🌐**\n\n%𝟸𝟶 ▬▬▭▭▭▭▭▭▭▭"),
        (30, "**⌔∮ جاري تحميل التحديثات...🌐**\n\n%𝟹𝟶 ▬▬▬▭▭▭▭▭▭▭"),
        (40, "**⌔∮ جاري تحميل التحديثات...🌐**\n\n%𝟺𝟶 ▬▬▬▬▭▭▭▭▭▭"),
        (50, "**⌔∮ جاري تطبيق التحديثات...🌐**\n\n%𝟻𝟶 ▬▬▬▬▬▭▭▭▭▭"),
        (60, "**⌔∮ جاري تطبيق التحديثات...🌐**\n\n%𝟼𝟶 ▬▬▬▬▬▬▭▭▭▭"),
        (70, "**⌔∮ جاري تثبيت المتطلبات...🌐**\n\n%𝟽𝟶 ▬▬▬▬▬▬▬▭▭▭"),
        (80, "**⌔∮ جاري تثبيت المتطلبات...🌐**\n\n%𝟾𝟶 ▬▬▬▬▬▬▬▬▭▭"),
        (90, "**⌔∮ جاري الانتهاء من التحديث...🌐**\n\n%𝟿𝟶 ▬▬▬▬▬▬▬▬▬▭"),
        (100, "**⌔∮ تم التحديث بنجاح! جاري إعادة التشغيل...🔄**\n\n%𝟷𝟶𝟶 ▬▬▬▬▬▬▬▬▬▬💯")
    ]

    for percent, message in steps:
        await xx.edit(message)
        await asyncio.sleep(1)

    await perform_update(xx)


async def perform_update(xx):
    await bash(f"git pull && {sys.executable} -m pip install -r requirements.txt")
    await xx.edit("✅ <strong>تم تجهيز السورس للعمل انتظر قليلا حتى يصلك اشعار في مجموعة السجل تفيد بأن السورس بدا في العمل.</strong>", parse_mode="html")
    os.execl(sys.executable, sys.executable, "-m", "yamenthon")
