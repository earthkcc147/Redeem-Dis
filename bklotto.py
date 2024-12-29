import discord
from discord.ext import commands, tasks
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
RAFFLE_INTERVAL = 1  # เวลาระยะห่างในการสุ่มรางวัล (นาที)
RAFFLE_CHANCE = 10.0  # โอกาสในการมีผู้ถูกรางวัล (เปอร์เซ็นต์)

# ฟังก์ชันเพื่ออ่านข้อมูลจากไฟล์ JSON
def load_data(group_id):
    folder_path = TOPUP_FOLDER_PATH
    data_file = os.path.join(folder_path, f"{group_id}.json")  # ตั้งชื่อไฟล์ตาม ID ของกลุ่ม

    if not os.path.exists(data_file):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        default_data = {}
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, group_id):
    folder_path = TOPUP_FOLDER_PATH
    data_file = os.path.join(folder_path, f"{group_id}.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_lotto_history(group_id, user_id, lottery_numbers, total_price):
    folder_path = LOTTO_HISTORY_FOLDER_PATH
    history_file = os.path.join(folder_path, f"lotto{group_id}.json")

    if not os.path.exists(history_file):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    with open(history_file, 'r', encoding='utf-8') as f:
        history_data = json.load(f)

    if user_id not in history_data:
        history_data[user_id] = []

    history_data[user_id].append({
        "lottery_numbers": lottery_numbers,
        "total_price": total_price,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)

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

        user_balance = user_data.get(user_id, {}).get("balance", 0)
        total_price = number_of_tickets * LOTTERY_PRICE

        if user_balance < total_price:
            await interaction.response.send_message("คุณไม่มียอดเงินเพียงพอในการซื้อล็อตเตอรี่", ephemeral=True)
            return

        lottery_numbers = []
        for _ in range(number_of_tickets):
            lottery_numbers.append("".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)]))

        embed = discord.Embed(
            title="ยืนยันคำสั่งซื้อ",
            description=f"คุณต้องการซื้อ {number_of_tickets} ใบ\nหมายเลขที่สุ่มได้: {', '.join(lottery_numbers)}\nยอดเงินที่ถูกหัก: {total_price} บาท\nยอดเงินคงเหลือ: {user_data[user_id]['balance'] - total_price} บาท",
            color=discord.Color.green()
        )

        confirm_button = Button(label="ตกลง", style=discord.ButtonStyle.green)
        cancel_button = Button(label="ยกเลิก", style=discord.ButtonStyle.red)

        async def confirm_button_callback(interaction: discord.Interaction):
            user_data[user_id]["balance"] -= total_price
            save_data(user_data, self.group_id)
            save_lotto_history(self.group_id, user_id, lottery_numbers, total_price)

            await interaction.response.send_message(f"คุณได้ซื้อล็อตเตอรี่ {number_of_tickets} ใบ\nหมายเลขที่สุ่มได้: {', '.join(lottery_numbers)}\nยอดเงินที่ถูกหัก: {total_price} บาท\nยอดเงินคงเหลือ: {user_data[user_id]['balance']} บาท", ephemeral=True)

        async def cancel_button_callback(interaction: discord.Interaction):
            await interaction.response.send_message("ยกเลิกการซื้อล็อตเตอรี่", ephemeral=True)

        confirm_button.callback = confirm_button_callback
        cancel_button.callback = cancel_button_callback

        view = View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# สร้างฟังก์ชันสุ่มรางวัล
@tasks.loop(minutes=RAFFLE_INTERVAL)
async def raffle():
    for guild in client.guilds:
        group_id = guild.id

        user_data = load_data(group_id)
        winners = {}  # คำสั่งเก็บผู้ถูกรางวัลสำหรับแต่ละหมายเลข
        all_numbers = []  # รายการเก็บหมายเลขทั้งหมดที่จะใช้ในการสุ่ม
        raffle_results = []  # รายการเก็บผลรางวัลทั้งหมด

        # สร้างหมายเลขทั้งหมดที่เป็นไปได้สำหรับการสุ่ม
        for i in range(1, 6):  # กำหนดจำนวนรางวัลที่ต้องการ (เช่น 5 รางวัล)
            all_numbers.append("".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)]))

        # เลือกผู้ถูกรางวัลโดยมีโอกาส 10% สำหรับแต่ละผู้ใช้
        for user_id, data in user_data.items():
            if random.random() < (RAFFLE_CHANCE / 100):
                winner_number = "".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)])
                if winner_number not in winners:
                    winners[winner_number] = [user_id]
                else:
                    winners[winner_number].append(user_id)

        # ตรวจสอบว่าใครถูกรางวัลบ้าง
        for i, number in enumerate(all_numbers):
            # หากมีผู้ถูกรางวัลให้แสดงข้อมูลผู้ถูกรางวัล
            if number in winners:
                winner_mentions = " ".join([f"<@{user_id}>" for user_id in winners[number]])
                raffle_results.append(f"รางวัล {i + 1}: {winner_mentions} - หมายเลข: {number}")
            else:
                # หากไม่มีผู้ถูกรางวัล
                raffle_results.append(f"รางวัล {i + 1}: ไม่มีผู้ที่ถูกรางวัล - หมายเลข: {number}")

        # สร้าง Embed เพื่อประกาศผลรางวัล
        embed = discord.Embed(
            title="ประกาศผลรางวัลล็อตเตอรี่",
            description="ผลรางวัลทั้งหมด:\n" + "\n".join(raffle_results),
            color=discord.Color.gold()
        )

        # ส่งผลรางวัลในช่อง 'lottery'
        channel = discord.utils.get(guild.text_channels, name="lottery")
        if channel:
            await channel.send(embed=embed)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # ตรวจสอบว่า raffle task กำลังทำงานหรือยัง
    if not raffle.is_running():
        raffle.start()  # เริ่ม task raffle ถ้ายังไม่ได้เริ่ม

@client.event
async def on_message(message):
    if message.content.lower() == "!lottery":
        group_id = message.guild.id  # ดึง ID ของกลุ่ม

        embed = discord.Embed(
            title="ล็อตเตอรี่",
            description=f"ราคาล็อตเตอรี่ 1 ใบ = {LOTTERY_PRICE} บาท\nเลือกจำนวนล็อตเตอรี่ที่ต้องการซื้อ",
            color=discord.Color.green()
        )

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