import discord
from discord.ext import commands
import asyncio

# ตั้งค่า Intent
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # ให้บอทสามารถจัดการสถานะเสียงได้

# สร้าง Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# ตั้งค่าการเปิด/ปิดฟีเจอร์
enable_features = True  # กำหนดเป็น True เพื่อเปิดฟีเจอร์ หรือ False เพื่อปิดฟีเจอร์

# ฟังก์ชันสำหรับโหลด Cogs
async def load_cogs():
    try:
        await bot.load_extension("cogs")
        print("Cogs ถูกโหลดเรียบร้อยแล้ว!")
    except Exception as e:
        print(f"ไม่สามารถโหลด Cogs: {e}")

@bot.event
async def on_ready():
    print(f"Bot {bot.user} พร้อมใช้งานแล้ว!")
    print(f"ID ของบอท: {bot.user.id}")
    print(f"พร้อมให้บริการใน {len(bot.guilds)} เซิร์ฟเวอร์!")
    
    # แสดงชื่อของเซิร์ฟเวอร์ที่บอทเข้าร่วม
    for guild in bot.guilds:
        print(f"เซิร์ฟเวอร์ที่บอทเข้าร่วม: {guild.name} (ID: {guild.id})")
    
    print(f"การเชื่อมต่อกับ Discord API สำเร็จ")

    if enable_features:
        # สร้างหมวดหมู่ (category) ใหม่สำหรับ BOT หากยังไม่มี
        for guild in bot.guilds:
            category = discord.utils.get(guild.categories, name="BOT")
            if not category:
                # สร้างหมวดหมู่ใหม่หากไม่มี
                category = await guild.create_category("BOT")
                print(f"หมวดหมู่ 'BOT' ถูกสร้างในเซิร์ฟเวอร์ {guild.name}")
            
            # ตรวจสอบห้องเสียงว่า "bot online" มีอยู่หรือไม่
            voice_channel = discord.utils.get(guild.voice_channels, name="bot online")
            if not voice_channel:
                # สร้างห้องเสียง "bot online" ในหมวดหมู่ "BOT"
                voice_channel = await guild.create_voice_channel("bot online", category=category)
                print(f"ห้องเสียง 'bot online' ถูกสร้างในเซิร์ฟเวอร์ {guild.name}")
            else:
                print(f"ห้องเสียง 'bot online' มีอยู่แล้วในเซิร์ฟเวอร์ {guild.name}")

            # เข้าร่วมห้องเสียง "bot online" และปิดไมค์
            try:
                # เชื่อมต่อกับห้องเสียงและปิดไมค์
                await voice_channel.connect(self_mute=True)
                print(f"บอทเข้าร่วมห้องเสียง 'bot online' ในเซิร์ฟเวอร์ {guild.name} และปิดไมค์เรียบร้อยแล้ว")
            except Exception as e:
                print(f"ไม่สามารถเข้าร่วมห้องเสียง 'bot online' ในเซิร์ฟเวอร์ {guild.name}: {e}")
    else:
        print("การสร้างหมวดหมู่และห้องเสียงถูกปิดใช้งาน")

# ฟังก์ชันหลักสำหรับรันบอท
async def main():
    print("เริ่มต้นการเชื่อมต่อกับ Discord...")
    # โหลด Cogs
    await load_cogs()
    print("กำลังรันบอท...")
    # รันบอท
    await bot.start("YOUR_BOT_TOKEN")

# เริ่มต้นโปรแกรม
if __name__ == "__main__":
    asyncio.run(main())