import discord
from discord.ext import commands
import random
import json
import os
from datetime import datetime

# เปิดใช้งาน Intents ทั้งหมด
intents = discord.Intents.all()

# สร้างบอทพร้อม Intents
bot = commands.Bot(command_prefix="!", intents=intents)

# ฟังก์ชันโหลดข้อมูลรางวัลจากไฟล์ JSON
def load_prizes(group_id):
    folder_path = "card"
    file_path = os.path.join(folder_path, f"card_{group_id}.json")
    
    # ตรวจสอบว่าโฟลเดอร์ "card" มีอยู่หรือไม่ หากไม่มีให้สร้าง
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # หากไฟล์ไม่อยู่จะกำหนดค่าเริ่มต้น
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return {
            "รางวัลที่ 1: 1000 Coins": {"percent": 10, "amount": 1000},
            "รางวัลที่ 2: 500 Coins": {"percent": 15, "amount": 500},
            "รางวัลที่ 3: 100 Coins": {"percent": 20, "amount": 100},
            "รางวัลพิเศษ: 1 Spin เพิ่ม": {"percent": 70, "amount": 0},
            "ไม่มีรางวัล": {"percent": 80, "amount": 0},
            "รางวัลที่ 4: 50 Coins": {"percent": 30, "amount": 50},
            "รางวัลที่ 5: 20 Coins": {"percent": 40, "amount": 20},
            "รางวัลใหญ่: 5000 Coins": {"percent": 2, "amount": 5000},
            "รางวัลเล็ก: 10 Coins": {"percent": 50, "amount": 10},
            "รางวัลพิเศษสุด: 10000 Coins": {"percent": 1, "amount": 10000}
        }

# ฟังก์ชันบันทึกข้อมูลรางวัลลงในไฟล์ JSON
def save_prizes(group_id, prizes):
    folder_path = "card"
    file_path = os.path.join(folder_path, f"card_{group_id}.json")
    
    # สร้างโฟลเดอร์หากไม่พบ
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # บันทึกข้อมูลลงไฟล์
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(prizes, file, ensure_ascii=False, indent=4)

# ฟังก์ชันสำหรับสุ่มรางวัล
def get_random_prize(group_id):
    prizes = load_prizes(group_id)
    prize_list = list(prizes.keys())
    weights = [prizes[prize]["percent"] for prize in prize_list]
    return random.choices(prize_list, weights=weights, k=1)[0]

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
def update_balance(group_id, user_id, price):
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
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success"
    })

    # บันทึกข้อมูลกลับลงไฟล์
    save_data(group_id, data)

    return True, balance

# ฟังก์ชันเพิ่มรางวัลในยอดเงิน
def add_prize_balance(group_id, user_id, prize_key):
    data = load_data(group_id)
    if str(user_id) not in data:
        data[str(user_id)] = {"balance": 0, "history": []}

    # เพิ่มเงินจากรางวัล
    prize_amount = load_prizes(group_id)[prize_key]["amount"]
    data[str(user_id)]["balance"] += prize_amount

    # บันทึกประวัติ
    data[str(user_id)]["history"].append({
        "amount": prize_amount,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "prize",
        "prize": prize_key
    })

    save_data(group_id, data)
    return data[str(user_id)]["balance"]

# ฟังก์ชันบันทึกประวัติการหมุนลงในไฟล์ spin_(group_id).json
def log_spin_history(group_id, user_id, prize_key):
    folder_path = "card"
    file_path = os.path.join(folder_path, f"spin_{group_id}.json")
    
    # ตรวจสอบว่าไฟล์ spin_(group_id).json มีอยู่หรือไม่
    if not os.path.exists(file_path):
        # ถ้าไม่มีให้สร้างไฟล์และโครงสร้างข้อมูลเริ่มต้น
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
    
    # โหลดข้อมูลเก่าจากไฟล์
    with open(file_path, "r", encoding="utf-8") as file:
        spin_data = json.load(file)

    # เพิ่มประวัติการหมุน
    if str(user_id) not in spin_data:
        spin_data[str(user_id)] = {"spins": 0, "history": []}

    # เพิ่มจำนวนรอบการหมุน
    spin_data[str(user_id)]["spins"] += 1

    # เพิ่มประวัติการหมุน
    spin_data[str(user_id)]["history"].append({
        "prize": prize_key,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # บันทึกข้อมูลกลับไปยังไฟล์
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(spin_data, file, ensure_ascii=False, indent=4)

# สร้าง View สำหรับปุ่ม
class CardView(discord.ui.View):
    def __init__(self, group_id, user_id):
        super().__init__(timeout=None)  # ไม่มีการหมดอายุ
        self.group_id = group_id
        self.user_id = user_id

        # เพิ่มปุ่ม 10 ปุ่ม
        for i in range(1, 11):
            self.add_item(CardButton(label=str(i), custom_id=f"button_{i}", group_id=self.group_id, user_id=self.user_id))

class CardButton(discord.ui.Button):
    def __init__(self, label, custom_id, group_id, user_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=custom_id)
        self.group_id = group_id
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        try:
            # รอ 1 วินาที
            await asyncio.sleep(1)

            # ตรวจสอบยอดเงิน
            price = 5  # ราคา 5 บาทต่อการสุ่ม
            success, balance = update_balance(self.group_id, self.user_id, price)

            if not success:
                await interaction.response.send_message(f"ยอดเงินของคุณไม่เพียงพอ! ยอดคงเหลือ: {balance} บาท", ephemeral=True)
                return

            # ส่งข้อความ "กำลังสุ่ม..." และรอเวลา
            msg = await interaction.response.send_message("กำลังสุ่ม...", ephemeral=True)

            # รอ 2 วินาที
            await asyncio.sleep(2)
            # ลบข้อความ "กำลังสุ่ม..."
            await msg.delete()

            # สุ่มรางวัล
            prize = get_random_prize(self.group_id)

            # เพิ่มเงินจากรางวัล (ถ้ามี)
            new_balance = add_prize_balance(self.group_id, self.user_id, prize)

            # บันทึกประวัติการหมุน
            log_spin_history(self.group_id, self.user_id, prize)

            # ตอบกลับเมื่อกดปุ่ม
            await interaction.response.send_message(
                f"คุณได้รับ: **{prize}**\nยอดคงเหลือปัจจุบัน: {new_balance} บาท",
                ephemeral=True
            )

        except discord.errors.NotFound:
            await interaction.followup.send("เกิดข้อผิดพลาดในการตอบกลับ! กรุณาลองใหม่.", ephemeral=True)

# สร้างคำสั่ง !card ใน Cog
class CardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="card")
    async def card(self, ctx):
        group_id = str(ctx.guild.id)  # ใช้ ID ของกลุ่มที่ผู้ใช้เข้าร่วม
        user_id = ctx.author.id     # ใช้ ID ของผู้ใช้งานใน Discord

        # แสดงรายการรางวัลใน Embed โดยไม่แสดงเปอร์เซ็นต์
        prize_list = "\n".join(load_prizes(group_id).keys())

        embed = discord.Embed(
            title="สุ่มรางวัล!",
            description=f"กดปุ่มด้านล่างเพื่อสุ่มรางวัลของคุณในราคา 5 บาท!\n\nรายการรางวัล:\n{prize_list}",
            color=discord.Color.gold()
        )
        embed.set_footer(text="คุณสามารถกดปุ่มได้ตลอดเวลา!")
        
        view = CardView(group_id, user_id)
        await ctx.send(embed=embed, view=view)

# เพิ่ม Cog เข้า Bot
async def setup(bot):
    await bot.add_cog(CardCog(bot))