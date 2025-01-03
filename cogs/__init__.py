import os
from discord.ext import commands

async def setup(bot: commands.Bot):
    # วนลูปโหลดไฟล์ .py ทั้งหมดในโฟลเดอร์ cogs
    for filename in os.listdir(os.path.dirname(__file__)):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")