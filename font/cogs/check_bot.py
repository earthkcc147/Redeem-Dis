import discord
from discord.ext import commands, tasks
import requests
import json

class BotStatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.WEBHOOK_URL = "YOUR_WEBHOOK_URL"
        self.bots_to_check = [
            {"name": "Bot1", "id": 123456789012345678},  # เปลี่ยนเป็น ID ของบอทที่ต้องการตรวจสอบ
            {"name": "Bot2", "id": 987654321098765432},
            # เพิ่มบอทที่ต้องการตรวจสอบในลิสต์นี้
        ]
        self.check_bots.start()

    # ฟังก์ชันตรวจสอบสถานะของบอท
    async def check_bot_status(self, bot_id: int):
        try:
            # เช็คสถานะออนไลน์ของบอท
            bot_user = await self.bot.fetch_user(bot_id)  # ดึงข้อมูลของบอท
            if bot_user.status != discord.Status.offline:
                status = "ออนไลน์"
            else:
                status = "ออฟไลน์"
            return status
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return "ไม่สามารถตรวจสอบสถานะได้"

    # ฟังก์ชันส่งข้อมูลไปที่ Webhook
    def send_to_webhook(self, bot_name: str, status: str):
        payload = {
            "content": f"บอท {bot_name} สถานะ: {status}"
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(self.WEBHOOK_URL, data=json.dumps(payload), headers=headers)
            if response.status_code == 204:
                print(f"ส่งข้อมูลสถานะของ {bot_name} ไปที่ Webhook สำเร็จ!")
            else:
                print(f"เกิดข้อผิดพลาดในการส่งข้อมูล: {response.status_code}")
        except Exception as e:
            print(f"ไม่สามารถส่งข้อมูลไปที่ Webhook: {e}")

    # ตั้งเวลาตรวจสอบทุกๆ 60 วินาที
    @tasks.loop(seconds=60)
    async def check_bots(self):
        for bot_info in self.bots_to_check:
            bot_id = bot_info["id"]
            bot_name = bot_info["name"]
            status = await self.check_bot_status(bot_id)
            self.send_to_webhook(bot_name, status)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} เข้าสู่ระบบสำเร็จ!")

def setup(bot):
    bot.add_cog(BotStatusCog(bot))