import discord
from discord.ext import commands
import asyncio
import os

# เปิดใช้งาน Intents ทั้งหมด
intents = discord.Intents.all()

# สร้างบอทพร้อม Intents
bot = commands.Bot(command_prefix="!", intents=intents)

# ตั้งค่าการเปิด/ปิดฟีเจอร์
enable_features = True  # กำหนดเป็น True เพื่อเปิดฟีเจอร์ หรือ False เพื่อปิดฟีเจอร์

# ฟังก์ชันสำหรับโหลด Cogs
async def load_cogs():
    try:
        # โฟลเดอร์ cogs มีไฟล์ .py ที่บอทจะโหลด
        cog_folder = "cogs"
        if os.path.exists(cog_folder):
            for filename in os.listdir(cog_folder):
                if filename.endswith(".py"):
                    cog_name = f"cogs.{filename[:-3]}"  # เอาชื่อไฟล์มาสร้างเป็นชื่อ Cog
                    try:
                        if cog_name in bot.extensions:
                            await bot.unload_extension(cog_name)  # หาก Cog ถูกโหลดแล้วจะทำการปลดโหลด
                            print(f"🔴 Cog '{cog_name}' ถูกปลดโหลดก่อนที่จะทำการโหลดใหม่จากไฟล์ {filename}")
                        await bot.load_extension(cog_name)
                        print(f"✅ Cog '{cog_name}' ถูกโหลดเรียบร้อยจากไฟล์ {filename}")
                    except Exception as e:
                        print(f"❌ ไม่สามารถโหลด/ปลดโหลด Cog '{cog_name}' จากไฟล์ {filename}: {e}")
        else:
            print("❌ ไม่พบโฟลเดอร์ 'cogs'")
    except Exception as e:
        print(f"❌ ไม่สามารถโหลด Cogs: {e}")

@bot.event
async def on_ready():
    try:
        print(f"\n🚀 บอท {bot.user} พร้อมใช้งานแล้ว!\n")
        print(f"🆔 ID ของบอท: {bot.user.id}")
        print(f"🌍 พร้อมให้บริการใน {len(bot.guilds)} เซิร์ฟเวอร์!\n")

        # แสดงชื่อของเซิร์ฟเวอร์ที่บอทเข้าร่วม
        for guild in bot.guilds:
            print(f"📡 เซิร์ฟเวอร์ที่บอทเข้าร่วม: {guild.name} (ID: {guild.id})")

        print(f"\n✅ การเชื่อมต่อกับ Discord API สำเร็จ\n")

        # เส้นคั่น
        print("-" * 50)

        if enable_features:
            # สร้างหมวดหมู่ (category) ใหม่สำหรับ BOT หากยังไม่มี
            for guild in bot.guilds:
                category = discord.utils.get(guild.categories, name="BOT")
                if not category:
                    try:
                        # สร้างหมวดหมู่ใหม่หากไม่มี
                        category = await guild.create_category("BOT")
                        print(f"✨ หมวดหมู่ 'BOT' ถูกสร้างในเซิร์ฟเวอร์ {guild.name}")
                    except Exception as e:
                        print(f"❌ ไม่สามารถสร้างหมวดหมู่ 'BOT' ในเซิร์ฟเวอร์ {guild.name}: {e}")

                # ตรวจสอบห้องเสียงว่า "bot online" มีอยู่หรือไม่
                voice_channel = discord.utils.get(guild.voice_channels, name="bot online")
                if not voice_channel:
                    try:
                        # สร้างห้องเสียง "bot online" ในหมวดหมู่ "BOT"
                        voice_channel = await guild.create_voice_channel("bot online", category=category)
                        print(f"🎤 ห้องเสียง 'bot online' ถูกสร้างในเซิร์ฟเวอร์ {guild.name}")
                    except Exception as e:
                        print(f"❌ ไม่สามารถสร้างห้องเสียง 'bot online' ในเซิร์ฟเวอร์ {guild.name}: {e}")
                else:
                    print(f"✅ ห้องเสียง 'bot online' มีอยู่แล้วในเซิร์ฟเวอร์ {guild.name}")

                # เข้าร่วมห้องเสียง "bot online" และปิดไมค์
                try:
                    # เชื่อมต่อกับห้องเสียงและปิดไมค์
                    await voice_channel.connect(self_mute=True)
                    print(f"🔊 บอทเข้าร่วมห้องเสียง 'bot online' ในเซิร์ฟเวอร์ {guild.name} และปิดไมค์เรียบร้อยแล้ว")
                except Exception as e:
                    print(f"❌ ไม่สามารถเข้าร่วมห้องเสียง 'bot online' ในเซิร์ฟเวอร์ {guild.name}: {e}")
        else:
            print("❌ การสร้างหมวดหมู่และห้องเสียงถูกปิดใช้งาน")

        # เส้นคั่น
        print("-" * 50)

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดใน on_ready: {e}")

# ฟังก์ชันหลักสำหรับรันบอท
async def main():
    try:
        print("🔗 เริ่มต้นการเชื่อมต่อกับ Discord...\n")
        # โหลด Cogs
        await load_cogs()
        print("🎮 กำลังรันบอท...\n")
        # รันบอท
        await bot.start("YOUR_BOT_TOKEN")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อกับ Discord หรือรันบอท: {e}")

# เริ่มต้นโปรแกรม
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเริ่มต้นโปรแกรม: {e}")