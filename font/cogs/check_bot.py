import discord
from discord.ext import commands, tasks
import requests

# สร้างคลาสที่เป็น Cog
class BotStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_bot_status.start()  # เริ่มต้น task ที่จะเช็คสถานะบอท

    @tasks.loop(minutes=5)  # ตรวจสอบสถานะทุกๆ 5 นาที
    async def check_bot_status(self):
        bot_ids = ['BOT_ID_1', 'BOT_ID_2']  # แทนที่ด้วย ID ของบอทที่คุณต้องการตรวจสอบ
        for bot_id in bot_ids:
            bot = await self.bot.fetch_user(bot_id)  # ดึงข้อมูลของบอท
            status = 'online' if bot.status == discord.Status.online else 'offline'
            
            # ส่งข้อมูลไปยัง Webhook
            self.send_status_to_webhook(bot_id, status)

    def send_status_to_webhook(self, bot_id, status):
        # ส่งข้อมูลไปยัง Webhook
        webhook_url = "YOUR_WEBHOOK_URL"
        data = {
            "content": f"บอท ID {bot_id} สถานะ: {status}",
        }
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print(f"✅ ส่งข้อมูลสถานะไปยัง Webhook สำหรับบอท {bot_id} สถานะ {status}")
        else:
            print(f"❌ ไม่สามารถส่งข้อมูลไปยัง Webhook สำหรับบอท {bot_id}")

    @commands.command()
    async def check_status(self, ctx, bot_id: str):
        """เช็คสถานะของบอทที่กำหนด"""
        bot = await self.bot.fetch_user(bot_id)
        status = 'online' if bot.status == discord.Status.online else 'offline'
        await ctx.send(f"บอท ID {bot_id} สถานะ: {status}")

# เพิ่ม Cog เข้ากับบอท
def setup(bot):
    bot.add_cog(BotStatus(bot))