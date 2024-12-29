import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import json
import os
import random
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True  # เปิด intent สำหรับการเข้าถึงเนื้อหาของข้อความ
client = commands.Bot(command_prefix="!", intents=intents)

# กำหนด CONFIG
LOTTERY_PRICE = 50  # ราคา 1 ใบ (บาท)
NUM_DIGITS = 5  # จำนวนหลักของหมายเลขที่สุ่ม
TOPUP_FOLDER_PATH = "topup"  # โฟลเดอร์ที่ใช้จัดเก็บไฟล์ JSON สำหรับข้อมูลผู้ใช้
LOTTO_HISTORY_FOLDER_PATH = "data"  # โฟลเดอร์ที่ใช้จัดเก็บประวัติการซื้อ

# ฟังก์ชันเพื่ออ่านข้อมูลจากไฟล์ JSON
def load_data(group_id):
    folder_path = TOPUP_FOLDER_PATH
    data_file = os.path.join(folder_path, f"{group_id}.json")  # ตั้งชื่อไฟล์ตาม ID ของกลุ่ม

    if not os.path.exists(data_file):
        # สร้างโฟลเดอร์ "topup" ถ้ายังไม่มี
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # สร้างไฟล์ JSON ใหม่ด้วยข้อมูลเริ่มต้น
        default_data = {}
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

    # ถ้าไฟล์มีอยู่แล้วให้โหลดข้อมูลจากไฟล์
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# ฟังก์ชันเพื่อบันทึกข้อมูลลงในไฟล์ JSON
def save_data(data, group_id):
    folder_path = TOPUP_FOLDER_PATH
    data_file = os.path.join(folder_path, f"{group_id}.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ฟังก์ชันเพื่อบันทึกประวัติการซื้อล็อตเตอรี่
def save_lotto_history(group_id, user_id, lottery_numbers, total_price):
    folder_path = LOTTO_HISTORY_FOLDER_PATH
    history_file = os.path.join(folder_path, f"lotto{group_id}.json")

    # ถ้าไม่มีไฟล์ history ให้สร้างใหม่
    if not os.path.exists(history_file):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    # โหลดประวัติเดิม
    with open(history_file, 'r', encoding='utf-8') as f:
        history_data = json.load(f)

    # ถ้าไม่มีประวัติการซื้อของ user นี้ให้สร้างขึ้นใหม่
    if user_id not in history_data:
        history_data[user_id] = []

    # บันทึกข้อมูลประวัติการซื้อใหม่
    history_data[user_id].append({
        "lottery_numbers": lottery_numbers,
        "total_price": total_price,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # บันทึกข้อมูลประวัติลงในไฟล์
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)

# สร้างบอทและตั้งค่า prefix
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

class LotteryModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="ซื้อล็อตเตอรี่")
        self.group_id = group_id

        self.number_input = TextInput(
            label="จำนวนล็อตเตอรี่ที่ต้องการซื้อ",
            placeholder="กรอกจำนวนที่ต้องการซื้อ",
            required=True,
            min_length=1,
            max_length=3
        )
        self.add_item(self.number_input)

    async def on_submit(self, interaction: discord.Interaction):
        number_of_tickets = int(self.number_input.value)
        user_id = str(interaction.user.id)

        user_data = load_data(self.group_id)

        # ตรวจสอบว่า user มี balance เพียงพอหรือไม่
        user_balance = user_data.get(user_id, {}).get("balance", 0)
        total_price = number_of_tickets * LOTTERY_PRICE

        if user_balance < total_price:
            await interaction.response.send_message("คุณไม่มียอดเงินเพียงพอในการซื้อล็อตเตอรี่", ephemeral=True)
            return

        # สุ่มหมายเลขล็อตเตอรี่
        lottery_numbers = []
        for _ in range(number_of_tickets):
            lottery_numbers.append("".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)]))

        # หักยอด balance
        user_data[user_id]["balance"] -= total_price

        # บันทึกข้อมูลใหม่
        save_data(user_data, self.group_id)

        # บันทึกประวัติการซื้อ
        save_lotto_history(self.group_id, user_id, lottery_numbers, total_price)

        # แจ้งผลการสุ่มหมายเลขและหัก balance
        await interaction.response.send_message(f"คุณได้ซื้อล็อตเตอรี่ {number_of_tickets} ใบ\nหมายเลขที่สุ่มได้: {', '.join(lottery_numbers)}\nยอดเงินที่ถูกหัก: {total_price} บาท\nยอดเงินคงเหลือ: {user_data[user_id]['balance']} บาท", ephemeral=True)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content.lower() == "!lottery":
        group_id = message.guild.id  # ดึง ID ของกลุ่ม

        embed = discord.Embed(
            title="ล็อตเตอรี่",
            description=f"ราคาล็อตเตอรี่ 1 ใบ = {LOTTERY_PRICE} บาท\nเลือกจำนวนล็อตเตอรี่ที่ต้องการซื้อ",
            color=discord.Color.green()
        )

        # สร้างปุ่ม "ซื้อล็อตเตอรี่"
        lottery_button = Button(label="ซื้อล็อตเตอรี่", style=discord.ButtonStyle.green)

        async def lottery_button_callback(interaction: discord.Interaction):
            modal = LotteryModal(group_id)
            await interaction.response.send_modal(modal)

        lottery_button.callback = lottery_button_callback

        view = View()
        view.add_item(lottery_button)

        await message.channel.send(embed=embed, view=view)

# Run the bot
client.run("YOUR_DISCORD_BOT_TOKEN")