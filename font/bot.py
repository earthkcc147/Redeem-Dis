import discord
from discord.ext import commands
import asyncio

# ตั้งค่า Intent
intents = discord.Intents.default()
intents.message_content = True

# สร้าง Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# ฟังก์ชันสำหรับโหลด Cogs
async def load_cogs():
    await bot.load_extension("cogs")

@bot.event
async def on_ready():
    print(f"Bot {bot.user} พร้อมใช้งานแล้ว!")

# ฟังก์ชันหลักสำหรับรันบอท
async def main():
    # โหลด Cogs
    await load_cogs()
    # รันบอท
    await bot.start("YOUR_BOT_TOKEN")

# เริ่มต้นโปรแกรม
if __name__ == "__main__":
    asyncio.run(main())