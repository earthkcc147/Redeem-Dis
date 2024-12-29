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
LOTTERY_CUSTOM_PRICE = 100  # ราคา 1 ใบ (บาท)
LOTTERY_PRICE = 50  # ราคา 1 ใบ (บาท)
NUM_DIGITS = 5  # จำนวนหลักของหมายเลขที่สุ่ม
TOPUP_FOLDER_PATH = "topup"  # โฟลเดอร์ที่ใช้จัดเก็บไฟล์ JSON สำหรับข้อมูลผู้ใช้
LOTTO_HISTORY_FOLDER_PATH = "data"  # โฟลเดอร์ที่ใช้จัดเก็บประวัติการซื้อ
RAFFLE_INTERVAL = 1  # เวลาระยะห่างในการสุ่มรางวัล (นาที)
RAFFLE_CHANCE = 10.0  # โอกาสในการมีผู้ถูกรางวัล (เปอร์เซ็นต์)
# กำหนดจำนวนรางวัลที่แต่ละหมายเลขจะได้รับ
prize_1 = 1000  # รางวัล 1000 บาท
near_prize_1 = 800 # รางวัล 800 บาท
prize_2 = 500    # รางวัล 500 บาท
prize_3 = 300    # รางวัล 300 บาท
prize_4 = 100    # รางวัล 100 บาท
prize_5 = 50      # รางวัล 50 บาท
RAFFLE_3DIGIT_PRIZE = 2000  # รางวัลเลขท้าย 3 ตัว
RAFFLE_2DIGIT_PRIZE = 3000  # รางวัลเลขท้าย 2 ตัว

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


# ฟังก์ชันในการดึงข้อมูลล็อตเตอรี่ที่ผู้ใช้ได้ซื้อมาจากไฟล์ JSON
async def check_lotto_history(interaction: discord.Interaction, group_id, user_id):
    history_file = os.path.join(LOTTO_HISTORY_FOLDER_PATH, f"lotto{group_id}.json")

    if not os.path.exists(history_file):
        await interaction.response.send_message("ไม่มีประวัติการซื้อล็อตเตอรี่", ephemeral=True)
        return

    with open(history_file, 'r', encoding='utf-8') as f:
        history_data = json.load(f)

    if user_id not in history_data or not history_data[user_id]:
        await interaction.response.send_message("คุณยังไม่มีประวัติการซื้อล็อตเตอรี่", ephemeral=True)
        return

    history_entries = history_data[user_id]
    history_text = "\n".join([
        f"หมายเลขล็อตเตอรี่: {entry['lottery_numbers']} | ยอดเงินที่ใช้: {entry['total_price']} บาท | วันที่: {entry['date']}"
        for entry in history_entries
    ])

    embed = discord.Embed(
        title="ประวัติการซื้อล็อตเตอรี่",
        description=history_text,
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

# เพิ่มปุ่มตรวจสอบล็อตเตอรี่
@client.event
async def on_message(message):
    if message.content.lower() == "!lottery":
        group_id = message.guild.id  # ดึง ID ของกลุ่ม
        user_id = str(message.author.id)  # ดึง ID ของผู้ใช้

        embed = discord.Embed(
            title="ล็อตเตอรี่",
            description=f"ราคาล็อตเตอรี่ 1 ใบ = {LOTTERY_PRICE} บาท\nเลือกจำนวนล็อตเตอรี่ที่ต้องการซื้อ",
            color=discord.Color.green()
        )

        lottery_button = Button(label="ซื้อล็อตเตอรี่", style=discord.ButtonStyle.green)
        check_lotto_button = Button(label="ตรวจสอบล็อตเตอรี่ที่มี", style=discord.ButtonStyle.blurple)

        async def lottery_button_callback(interaction: discord.Interaction):
            modal = LotteryModal(group_id)
            await interaction.response.send_modal(modal)

        async def check_lotto_button_callback(interaction: discord.Interaction):
            # เปลี่ยนการใช้ user_id เป็น interaction.user.id
            await check_lotto_history(interaction, group_id, str(interaction.user.id))

        lottery_button.callback = lottery_button_callback
        check_lotto_button.callback = check_lotto_button_callback

        view = View()
        view.add_item(lottery_button)
        view.add_item(check_lotto_button)

        await message.channel.send(embed=embed, view=view)


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


class CustomLotteryModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="ซื้อเลขล็อตเตอรี่เอง")
        self.group_id = group_id

        self.number_input = TextInput(
            label="กรอกหมายเลขล็อตเตอรี่ที่ต้องการซื้อ",
            placeholder="กรอกหมายเลขที่ต้องการ (เช่น 12345)",
            required=True,
            min_length=NUM_DIGITS,
            max_length=NUM_DIGITS
        )
        self.add_item(self.number_input)

    async def on_submit(self, interaction: discord.Interaction):
        lottery_number = self.number_input.value
        user_id = str(interaction.user.id)

        user_data = load_data(self.group_id)

        user_balance = user_data.get(user_id, {}).get("balance", 0)
        total_price = LOTTERY_CUSTOM_PRICE

        if user_balance < total_price:
            await interaction.response.send_message("คุณไม่มียอดเงินเพียงพอในการซื้อล็อตเตอรี่", ephemeral=True)
            return

        # บันทึกหมายเลขที่ผู้ใช้เลือก
        embed = discord.Embed(
            title="ยืนยันคำสั่งซื้อ",
            description=f"คุณต้องการซื้อหมายเลข: {lottery_number}\nยอดเงินที่ถูกหัก: {total_price} บาท\nยอดเงินคงเหลือ: {user_data[user_id]['balance'] - total_price} บาท",
            color=discord.Color.green()
        )

        confirm_button = Button(label="ตกลง", style=discord.ButtonStyle.green)
        cancel_button = Button(label="ยกเลิก", style=discord.ButtonStyle.red)

        async def confirm_button_callback(interaction: discord.Interaction):
            user_data[user_id]["balance"] -= total_price
            save_data(user_data, self.group_id)
            save_lotto_history(self.group_id, user_id, [lottery_number], total_price)

            await interaction.response.send_message(f"คุณได้ซื้อล็อตเตอรี่หมายเลข {lottery_number}\nยอดเงินที่ถูกหัก: {total_price} บาท\nยอดเงินคงเหลือ: {user_data[user_id]['balance']} บาท", ephemeral=True)

        async def cancel_button_callback(interaction: discord.Interaction):
            await interaction.response.send_message("ยกเลิกการซื้อล็อตเตอรี่", ephemeral=True)

        confirm_button.callback = confirm_button_callback
        cancel_button.callback = cancel_button_callback

        view = View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class Lottery3DigitsModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="ซื้อล็อตเตอรี่ (เลขท้าย 3 ตัว)")
        self.group_id = group_id

        self.number_input = TextInput(
            label="กรุณากรอกเลขท้าย 3 ตัว",
            placeholder="กรอกเลขที่ต้องการซื้อ",
            required=True,
            min_length=3,
            max_length=3
        )
        self.add_item(self.number_input)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        number = self.number_input.value  # เลขที่ผู้ใช้กรอก

        if not number.isdigit() or len(number) != 3:
            await interaction.response.send_message("กรุณากรอกเลขที่มี 3 หลักเท่านั้น", ephemeral=True)
            return

        user_data = load_data(self.group_id)
        user_balance = user_data.get(user_id, {}).get("balance", 0)

        # ใช้ LOTTERY_CUSTOM_PRICE แทน LOTTERY_PRICE
        if user_balance < LOTTERY_CUSTOM_PRICE:
            await interaction.response.send_message("คุณไม่มียอดเงินเพียงพอในการซื้อล็อตเตอรี่", ephemeral=True)
            return

        # หักยอดเงินและบันทึกข้อมูล
        user_data[user_id]["balance"] -= LOTTERY_CUSTOM_PRICE
        save_data(user_data, self.group_id)

        # บันทึกประวัติการซื้อล็อตเตอรี่
        save_lotto_history(self.group_id, user_id, [number], LOTTERY_CUSTOM_PRICE)

        # ส่งข้อความยืนยัน
        await interaction.response.send_message(f"คุณได้ซื้อล็อตเตอรี่หมายเลข {number} เลขท้าย 3 ตัว\nยอดเงินที่ถูกหัก: {LOTTERY_CUSTOM_PRICE} บาท\nยอดเงินคงเหลือ: {user_data[user_id]['balance']} บาท", ephemeral=True)


class LottoLastTwoModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="ซื้อเลขท้าย 2 ตัว")
        self.group_id = group_id

        self.number_input = TextInput(
            label="กรอกเลขท้าย 2 ตัวที่ต้องการซื้อ (0-99)",
            placeholder="กรอกเลขท้าย 2 ตัว",
            required=True,
            min_length=2,
            max_length=2
        )
        self.add_item(self.number_input)

    async def on_submit(self, interaction: discord.Interaction):
        last_two_number = self.number_input.value.strip()
        user_id = str(interaction.user.id)

        if not last_two_number.isdigit() or len(last_two_number) != 2:
            await interaction.response.send_message("กรุณากรอกเลขท้าย 2 ตัวที่ถูกต้อง (0-99)", ephemeral=True)
            return

        user_data = load_data(self.group_id)
        user_balance = user_data.get(user_id, {}).get("balance", 0)
        total_price = LOTTERY_CUSTOM_PRICE  # เปลี่ยนมาใช้ LOTTERY_CUSTOM_PRICE

        if user_balance < total_price:
            await interaction.response.send_message("คุณไม่มียอดเงินเพียงพอในการซื้อเลขท้าย 2 ตัว", ephemeral=True)
            return

        embed = discord.Embed(
            title="ยืนยันการซื้อเลขท้าย 2 ตัว",
            description=f"คุณต้องการซื้อเลขท้าย 2 ตัว: {last_two_number} ด้วยราคา {total_price} บาท\nยอดเงินคงเหลือ: {user_balance - total_price} บาท",
            color=discord.Color.green()
        )

        confirm_button = Button(label="ตกลง", style=discord.ButtonStyle.green)
        cancel_button = Button(label="ยกเลิก", style=discord.ButtonStyle.red)

        async def confirm_button_callback(interaction: discord.Interaction):
            user_data[user_id]["balance"] -= total_price
            save_data(user_data, self.group_id)
            save_lotto_history(self.group_id, user_id, [last_two_number], total_price)

            await interaction.response.send_message(f"คุณได้ซื้อเลขท้าย 2 ตัว: {last_two_number} ด้วยราคา {total_price} บาท\nยอดเงินคงเหลือ: {user_data[user_id]['balance']} บาท", ephemeral=True)

        async def cancel_button_callback(interaction: discord.Interaction):
            await interaction.response.send_message("ยกเลิกการซื้อเลขท้าย 2 ตัว", ephemeral=True)

        confirm_button.callback = confirm_button_callback
        cancel_button.callback = cancel_button_callback

        view = View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ฟังก์ชันอ่านข้อมูลการซื้อของผู้ใช้จากไฟล์ (เฉพาะคำสั่งซื้อในวันนี้)
def load_lotto_history(group_id):
    folder_path = LOTTO_HISTORY_FOLDER_PATH
    history_file = os.path.join(folder_path, f"lotto{group_id}.json")

    if not os.path.exists(history_file):
        return {}

    with open(history_file, 'r', encoding='utf-8') as f:
        history_data = json.load(f)

    # ฟังก์ชันกรองคำสั่งซื้อที่เกิดขึ้นในวันนี้
    today = datetime.now().strftime('%Y-%m-%d')
    filtered_history = {}

    for user_id, purchases in history_data.items():
        filtered_history[user_id] = [purchase for purchase in purchases if purchase['date'].startswith(today)]

    return filtered_history

# ฟังก์ชันสุ่มรางวัล
@tasks.loop(minutes=RAFFLE_INTERVAL)
async def raffle():
    for guild in client.guilds:
        group_id = guild.id

        # โหลดข้อมูลคำสั่งซื้อจากไฟล์ประวัติของวันนี้
        history_data = load_lotto_history(group_id)
        winners = {}  # คำสั่งเก็บผู้ถูกรางวัลสำหรับแต่ละหมายเลข
        all_numbers = []  # รายการเก็บหมายเลขทั้งหมดที่จะใช้ในการสุ่ม
        raffle_results = []  # รายการเก็บผลรางวัลทั้งหมด

        # กำหนดจำนวนรางวัลที่แต่ละหมายเลขจะได้รับ
        prize_amounts = [prize_1, prize_1, prize_3, prize_4, prize_5]  

        # สร้างหมายเลขรางวัลที่ 1
        prize_1_number = "".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)])
        all_numbers.append(prize_1_number)

        # สร้างหมายเลขรางวัลใกล้เคียงรางวัลที่ 1
        near_prize_1_numbers = [
            str(int(prize_1_number) - 1).zfill(NUM_DIGITS),
            str(int(prize_1_number) + 1).zfill(NUM_DIGITS)
        ]
        all_numbers.extend(near_prize_1_numbers)

        # สร้างหมายเลขทั้งหมดที่เป็นไปได้สำหรับการสุ่ม (รางวัลที่ 2-5)
        for i in range(1, 6):  # กำหนดจำนวนรางวัลที่ต้องการ (เช่น 5 รางวัล)
            all_numbers.append("".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)]))

        # เพิ่มหมายเลขสำหรับรางวัลเลขท้าย 3 ตัว (2 รางวัล)
        for _ in range(2):
            last_three_digits = "".join([str(random.randint(0, 9)) for _ in range(3)])
            all_numbers.append(last_three_digits)

        # เพิ่มหมายเลขสำหรับรางวัลเลขท้าย 2 ตัว (1 รางวัล)
        last_two_digits = "".join([str(random.randint(0, 9)) for _ in range(2)])
        all_numbers.append(last_two_digits)

        # ค้นหาผู้ถูกรางวัลจากข้อมูลคำสั่งซื้อ
        for user_id, purchases in history_data.items():
            for purchase in purchases:
                lottery_numbers = purchase["lottery_numbers"]
                total_price = purchase["total_price"]

                if random.random() < (RAFFLE_CHANCE / 100):
                    # ตรวจสอบว่าหมายเลขนี้ถูกรางวัลหรือไม่
                    if lottery_numbers in all_numbers:
                        if lottery_numbers not in winners:
                            winners[lottery_numbers] = [user_id]
                        else:
                            winners[lottery_numbers].append(user_id)

        # ตรวจสอบว่าใครถูกรางวัลบ้าง
        for i, number in enumerate(all_numbers):
            # กำหนดประเภทของรางวัลที่จะแสดง
            if i == 0:
                prize_type = "รางวัลที่ 1: "
                prize_amount = prize_1
            elif i == 1 or i == 2:  # รางวัลใกล้เคียงรางวัลที่ 1
                prize_type = f"รางวัลใกล้เคียงรางวัลที่ 1 {i}: "
                prize_amount = near_prize_1
            elif i < len(prize_amounts):  # ตรวจสอบให้แน่ใจว่า i อยู่ในขอบเขตของ prize_amounts
                prize_type = f"รางวัลที่ {i}: "
                prize_amount = prize_amounts[i]
            elif i < 8:
                prize_type = f"รางวัลเลขท้าย 3 ตัว {i - 5}: "
                prize_amount = RAFFLE_3DIGIT_PRIZE
            else:
                prize_type = "รางวัลเลขท้าย 2 ตัว: "
                prize_amount = RAFFLE_2DIGIT_PRIZE

            # หากมีผู้ถูกรางวัลให้แสดงข้อมูลผู้ถูกรางวัล
            if number in winners:
                winner_mentions = " ".join([f"<@{user_id}>" for user_id in winners[number]])
                raffle_results.append(f"{prize_type}{winner_mentions} - หมายเลข: {number} - รับเงิน {prize_amount} บาท")

                # เพิ่มยอดเงินให้กับผู้ถูกรางวัล
                for user_id in winners[number]:
                    # เพิ่มยอดเงินในบัญชีผู้ชนะ
                    user_data = load_data(group_id)
                    if user_id in user_data:
                        user_data[user_id]["balance"] += prize_amount
                        save_data(user_data, group_id)

            else:
                # หากไม่มีผู้ถูกรางวัล
                raffle_results.append(f"{prize_type}ไม่มีผู้ที่ถูกรางวัล - หมายเลข: {number}")

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
           