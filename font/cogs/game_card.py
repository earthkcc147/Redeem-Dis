import discord
from discord.ext import commands
import random
import os
import json
from datetime import datetime

# เปิดใช้งาน Intents ทั้งหมด
intents = discord.Intents.all()

# สร้างบอทพร้อม Intents
bot = commands.Bot(command_prefix="!", intents=intents)

# รางวัลและเปอร์เซ็นต์ (กำหนดในรูปแบบ Dictionary)
PRIZES = {
    "รางวัลที่ 1: 1000 Coins": 10,   # 10%
    "รางวัลที่ 2: 500 Coins": 15,    # 15%
    "รางวัลที่ 3: 100 Coins": 20,    # 20%
    "รางวัลพิเศษ: 1 Spin เพิ่ม": 70, # 70%
    "ไม่มีรางวัล": 80,               # 80%
    "รางวัลที่ 4: 50 Coins": 30,     # 30%
    "รางวัลที่ 5: 20 Coins": 40,     # 40%
    "รางวัลใหญ่: 5000 Coins": 2,    # 2%
    "รางวัลเล็ก: 10 Coins": 50,     # 50%
    "รางวัลพิเศษสุด: 10000 Coins": 1 # 1%
}

# จำนวนเงินที่เพิ่มเมื่อได้รับรางวัล
PRIZE_VALUES = {
    "รางวัลที่ 1: 1000 Coins": 1000,
    "รางวัลที่ 2: 500 Coins": 500,
    "รางวัลที่ 3: 100 Coins": 100,
    "รางวัลพิเศษ: 1 Spin เพิ่ม": 0,  # No money, but grants 1 more spin
    "ไม่มีรางวัล": 0,                # No reward
    "รางวัลที่ 4: 50 Coins": 50,
    "รางวัลที่ 5: 20 Coins": 20,
    "รางวัลใหญ่: 5000 Coins": 5000,
    "รางวัลเล็ก: 10 Coins": 10,
    "รางวัลพิเศษสุด: 10000 Coins": 10000
}

# ฟังก์ชันสำหรับสุ่มรางวัล
def get_random_prize():
    return random.choices(list(PRIZES.keys()), weights=list(PRIZES.values()), k=1)[0]

# ฟังก์ชันโหลดข้อมูลจากไฟล์ JSON โดยใช้ group_id เป็นชื่อไฟล์
def load_data(group_id):
    file_path = f"topup/{group_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# ฟังก์ชันบันทึกข้อมูลลงไฟล์ JSON โดยใช้ group_id เป็นชื่อไฟล์
def save_data(group_id, data):
    file_path = f"topup/{group_id}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# ฟังก์ชันอัปเดตยอดเงิน
def update_balance(group_id, user_id, price, redeem_key):
    data = load_data(group_id)

    # ตรวจสอบว่า group_id มีข้อมูลในไฟล์หรือไม่
    if str(user_id) not in data:
        return False, 0  # หากไม่มีข้อมูล user_id คืนค่า balance เป็น 0

    # ดึงยอดเงินปัจจุบันของ user_id
    balance = data[str(user_id)].get("balance", 0)

    if balance < price:
        return False, balance  # หากยอดเงินไม่เพียงพอ

    # หักเงินออกจาก balance
    balance -= price
    data[str(user_id)]["balance"] = balance

    # เพิ่มประวัติการทำรายการ
    if "history" not in data[str(user_id)]:
        data[str(user_id)]["history"] = []
    data[str(user_id)]["history"].append({
        "amount": price,
        "redeem_key": redeem_key,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success"
    })

    # บันทึกข้อมูลกลับลงไฟล์
    save_data(group_id, data)

    return True, balance

# สร้าง View สำหรับปุ่ม
class CardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # ไม่มีการหมดอายุ

        # เพิ่มปุ่ม 10 ปุ่ม
        for i in range(1, 11):
            self.add_item(CardButton(label=str(i), custom_id=f"button_{i}"))

class CardButton(discord.ui.Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        try:
            # คำนวณราคา (5 บาท)
            price = 5

            # ตรวจสอบยอดเงินของผู้ใช้
            success, balance = update_balance("group_id_example", interaction.user.id, price, interaction.custom_id)
            
            if not success:
                await interaction.response.send_message(f"คุณมีเงินไม่เพียงพอ! ยอดเงินของคุณ: {balance} บาท", ephemeral=True)
                return

            # สุ่มรางวัล
            prize = get_random_prize()

            # เพิ่มเงินตามรางวัล
            prize_value = PRIZE_VALUES[prize]
            if prize_value > 0:
                # เพิ่มยอดเงินตามรางวัล
                data = load_data("group_id_example")
                if str(interaction.user.id) in data:
                    data[str(interaction.user.id)]["balance"] += prize_value
                    save_data("group_id_example", data)

            # ตอบกลับเมื่อกดปุ่ม
            await interaction.response.send_message(f"คุณได้รับ: **{prize}**", ephemeral=True)

        except discord.errors.NotFound:
            # ถ้าเกิดข้อผิดพลาดที่เกี่ยวข้องกับ Interaction ที่ไม่พบ
            await interaction.followup.send("เกิดข้อผิดพลาดในการตอบกลับ! กรุณาลองใหม่.", ephemeral=True)

# สร้างคำสั่ง !card ใน Cog
class CardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="card")
    async def card(self, ctx):
        # แสดงรายการรางวัลใน Embed โดยไม่แสดงเปอร์เซ็นต์
        prize_list = "\n".join(PRIZES.keys())

        embed = discord.Embed(
            title="สุ่มรางวัล!",
            description=f"กดปุ่มด้านล่างเพื่อสุ่มรางวัลของคุณ!\n\nรายการรางวัล:\n{prize_list}",
            color=discord.Color.gold()
        )
        embed.set_footer(text="คุณสามารถกดปุ่มได้ตลอดเวลา!")
        
        view = CardView()
        await ctx.send(embed=embed, view=view)

# เพิ่ม Cog เข้า Bot
async def setup(bot):
    await bot.add_cog(CardCog(bot))
