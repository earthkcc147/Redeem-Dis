import discord
import random
import os
import json
from discord.ui import Button, View, Modal, TextInput
import discord
from discord.ext import commands

# สร้าง intents
intents = discord.Intents.default()
intents.messages = True  # เปิดใช้งาน intents สำหรับรับข้อความ

# สร้างบอทด้วย intents
client = commands.Bot(command_prefix="!", intents=intents)


# CONFIG: กำหนดจำนวนหลักที่สุ่ม
LOTTERY_DIGITS = 5
LOTTERY_PRICE = 10  # ราคาของแต่ละล็อตเตอรี่ (สามารถปรับตามต้องการ)

# ฟังก์ชันเพื่ออ่านข้อมูลจากไฟล์ JSON
def load_data(group_id):
    folder_path = "data"
    data_file = os.path.join(folder_path, f"lotto{group_id}.json")  # ตั้งชื่อไฟล์ตาม ID ของกลุ่ม

    # ถ้าไฟล์ไม่พบ ให้สร้างไฟล์ใหม่และคืนค่าข้อมูลเริ่มต้น
    if not os.path.exists(data_file):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        default_data = {}
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# ฟังก์ชันเพื่อบันทึกข้อมูลลงในไฟล์ JSON
def save_data(data, group_id):
    folder_path = "data"
    data_file = os.path.join(folder_path, f"lotto{group_id}.json")

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ฟังก์ชันเพื่อสุ่มเลขล็อตเตอรี่
def generate_lottery_number():
    return str(random.randint(10**(LOTTERY_DIGITS-1), 10**LOTTERY_DIGITS - 1))

# สร้าง Modal สำหรับกรอกจำนวนล็อตเตอรี่
class LotteryModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="กรอกจำนวนล็อตเตอรี่ที่ต้องการ")
        self.group_id = group_id

        self.number_input = TextInput(
            label="จำนวนล็อตเตอรี่ที่ต้องการซื้อ",
            placeholder="กรอกจำนวน",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.number_input)

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_data = load_data(self.group_id)

        try:
            quantity = int(self.number_input.value)
            total_cost = quantity * LOTTERY_PRICE

            # ตรวจสอบว่า user มี balance พอหรือไม่
            if user_id not in user_data:
                await interaction.response.send_message("คุณยังไม่ได้ลงทะเบียน กรุณาลงทะเบียนก่อน", ephemeral=True)
                return

            balance = user_data[user_id].get("balance", 0)
            if balance < total_cost:
                await interaction.response.send_message("ยอดเงินของคุณไม่เพียงพอสำหรับการซื้อล็อตเตอรี่", ephemeral=True)
                return

            # สุ่มเลขล็อตเตอรี่
            lottery_numbers = [generate_lottery_number() for _ in range(quantity)]

            # หักยอด balance
            user_data[user_id]["balance"] -= total_cost

            # บันทึกข้อมูลลงในไฟล์
            save_data(user_data, self.group_id)

            # แจ้งผล
            await interaction.response.send_message(
                f"คุณได้ซื้อล็อตเตอรี่จำนวน {quantity} ใบ\nเลขที่สุ่มได้คือ: {', '.join(lottery_numbers)}\nหักยอด {total_cost} บาทจากบัญชีของคุณ"
            )
        except ValueError:
            await interaction.response.send_message("กรุณากรอกจำนวนเป็นตัวเลข", ephemeral=True)

@client.event
async def on_message(message):
    if message.content.lower() == "!lottery":
        group_id = message.guild.id

        embed = discord.Embed(
            title="ซื้อล็อตเตอรี่",
            description="กดปุ่มด้านล่างเพื่อซื้อล็อตเตอรี่",
            color=discord.Color.blue()
        )

        # สร้างปุ่มซื้อ
        buy_button = Button(label="ซื้อล็อตเตอรี่", style=discord.ButtonStyle.green)

        async def buy_button_callback(interaction: discord.Interaction):
            modal = LotteryModal(group_id)
            await interaction.response.send_modal(modal)

        buy_button.callback = buy_button_callback

        # สร้าง View และเพิ่มปุ่ม
        view = View()
        view.add_item(buy_button)

        # ส่ง Embed พร้อมปุ่ม
        await message.channel.send(embed=embed, view=view)

client.run(TOKEN)