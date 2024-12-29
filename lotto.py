import discord
import random
import json
import os
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime

# CONFIG
LOTTERY_DIGITS = 5  # กำหนดจำนวนหลักของหมายเลขที่สุ่ม (5 หลัก)
LOTTERY_PRICE = 100  # ราคาของล็อตเตอรี่ 1 ใบ

TOKEN = 'YOUR_DISCORD_BOT_TOKEN'  # ใส่ Token ของบอทของคุณที่นี่

# สร้างบอท
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

# ฟังก์ชันสำหรับการโหลดข้อมูลจากไฟล์ JSON
def load_lotto_data(group_id):
    file_path = f"data/lotto{group_id}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# ฟังก์ชันสำหรับการบันทึกข้อมูลลงในไฟล์ JSON
def save_lotto_data(data, group_id):
    folder_path = "data"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    file_path = f"{folder_path}/lotto{group_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ฟังก์ชันสำหรับการโหลดข้อมูล Balance ของผู้ใช้
def load_balance_data(group_id):
    folder_path = "topup"
    data_file = os.path.join(folder_path, f"{group_id}.json")

    # หากไฟล์ไม่มีอยู่จะสร้างไฟล์ใหม่และใส่ข้อมูลเริ่มต้น
    if not os.path.exists(data_file):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        default_data = {}  # ข้อมูลเริ่มต้นเป็น dictionary ว่าง
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

    # โหลดข้อมูลจากไฟล์ JSON
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# ฟังก์ชันสำหรับการบันทึกข้อมูล Balance ของผู้ใช้
def save_balance_data(data, group_id):
    folder_path = "topup"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    data_file = os.path.join(folder_path, f"{group_id}.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ฟังก์ชันสำหรับการสุ่มเลขล็อตเตอรี่
def generate_lotto_number():
    min_value = 10**(LOTTERY_DIGITS - 1)
    max_value = (10**LOTTERY_DIGITS) - 1
    return random.randint(min_value, max_value)

# สร้าง Modal สำหรับกรอกจำนวนที่ต้องการซื้อ
class LottoModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="กรอกจำนวนที่ต้องการซื้อล็อตเตอรี่")
        self.group_id = group_id
        self.amount = TextInput(label="จำนวนที่ต้องการซื้อ", style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value)
            if amount < 1:
                await interaction.response.send_message("กรุณากรอกจำนวนที่มากกว่า 0", ephemeral=True)
                return

            # คำนวณราคาทั้งหมด
            total_price = amount * LOTTERY_PRICE

            # โหลดข้อมูล Balance ของผู้ใช้
            balance_data = load_balance_data(self.group_id)
            user_id = str(interaction.user.id)
            user_balance = balance_data.get(user_id, 0)

            # ตรวจสอบว่าเงินคงเหลือเพียงพอหรือไม่
            if user_balance < total_price:
                await interaction.response.send_message("ยอดเงินของคุณไม่เพียงพอในการซื้อล็อตเตอรี่", ephemeral=True)
                return

            # สร้างการยืนยันคำสั่งซื้อ
            confirm_button = Button(label="ยืนยันการซื้อ", style=discord.ButtonStyle.green)
            cancel_button = Button(label="ยกเลิกการซื้อ", style=discord.ButtonStyle.red)

            async def confirm_callback(interaction: discord.Interaction):
                # หักเงินจากยอด Balance
                balance_data[user_id] = user_balance - total_price
                save_balance_data(balance_data, self.group_id)

                # สุ่มหมายเลขล็อตเตอรี่
                lotto_numbers = [generate_lotto_number() for _ in range(amount)]

                # โหลดข้อมูลล็อตเตอรี่ของกลุ่ม
                lotto_data = load_lotto_data(self.group_id)
                if user_id not in lotto_data:
                    lotto_data[user_id] = []

                # บันทึกหมายเลขล็อตเตอรี่ของผู้ใช้พร้อมรายละเอียด
                purchase_details = {
                    "numbers": lotto_numbers,
                    "purchase_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "price": total_price
                }
                lotto_data[user_id].append(purchase_details)

                # บันทึกข้อมูลลงไฟล์
                save_lotto_data(lotto_data, self.group_id)

                # ส่งข้อความแสดงผล
                lotto_list = "\n".join(str(num) for num in lotto_numbers)
                await interaction.response.send_message(
                    f"คุณได้ซื้อล็อตเตอรี่ {amount} ใบ\nหมายเลขล็อตเตอรี่ของคุณ:\n{lotto_list}\n"
                    f"ราคาทั้งหมด: {total_price} บาท", ephemeral=True
                )

            async def cancel_callback(interaction: discord.Interaction):
                await interaction.response.send_message("การซื้อถูกยกเลิก", ephemeral=True)

            confirm_button.callback = confirm_callback
            cancel_button.callback = cancel_callback

            # สร้าง view ที่ใส่ปุ่ม
            view = View()
            view.add_item(confirm_button)
            view.add_item(cancel_button)

            # ส่งข้อความเพื่อยืนยันคำสั่งซื้อ
            await interaction.response.send_message(
                f"คุณต้องการซื้อล็อตเตอรี่ {amount} ใบ รวมทั้งหมด {total_price} บาท\n"
                f"กรุณายืนยันการซื้อหรือยกเลิก", ephemeral=True, view=view
            )

        except ValueError:
            await interaction.response.send_message("กรุณากรอกจำนวนที่เป็นตัวเลข", ephemeral=True)

# สร้างปุ่มซื้อล็อตเตอรี่
class LotteryButton(Button):
    def __init__(self):
        super().__init__(label="ซื้อล็อตเตอรี่", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        # เปิด Modal เมื่อกดปุ่ม
        modal = LottoModal(group_id=interaction.guild.id)

        # ส่ง Modal ผ่าน response
        await interaction.response.send_modal(modal)

# คำสั่ง !lottery ที่จะส่ง Embed พร้อมปุ่มซื้อล็อตเตอรี่
@client.event
async def on_message(message):
    if message.content.lower() == "!lottery":
        embed = discord.Embed(
            title="ล็อตเตอรี่",
            description="คุณสามารถซื้อล็อตเตอรี่ได้ที่นี่",
            color=discord.Color.blue()
        )
        embed.add_field(name="รางวัลใหญ่", value="1,000,000 บาท", inline=False)
        embed.add_field(name="ราคาล็อตเตอรี่", value="100 บาท", inline=False)

        # สร้างปุ่มซื้อล็อตเตอรี่
        lottery_button = LotteryButton()

        # สร้าง view ที่ใส่ปุ่ม
        view = View()
        view.add_item(lottery_button)

        # ส่ง Embed พร้อมปุ่ม
        await message.channel.send(embed=embed, view=view)

# เริ่มต้นบอท
client.run(TOKEN)