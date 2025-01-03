import discord
from discord.ext import commands

# ตั้งค่า Intent
intents = discord.Intents.default()
intents.message_content = True

# สร้าง Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# โหลด Cog จากโฟลเดอร์ cogs
async def load_cogs():
    await bot.load_extension("cogs.convert_cog")

@bot.event
async def on_ready():
    print(f"Bot {bot.user} พร้อมใช้งานแล้ว!")

# รันบอท
if __name__ == "__main__":
    bot.loop.run_until_complete(load_cogs())
    bot.run("YOUR_BOT_TOKEN")