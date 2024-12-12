import discord
import json
import os
from discord.ui import Button, View, Select
from datetime import datetime

TOKEN = 'MTE5MjA0MTI2MTA1NDU3MDUyNg.GmR8Zy.kE1mTrYzUk4Fddkj4R0dKHKfHS-Gf8aEDa0bw0'  # ใส่โทเค็นบอทของคุณที่นี่
channel_id = 1315866248227065957  # ใส่ ID ช่องที่ต้องการส่งข้อความไป

intents = discord.Intents.default()
intents.message_content = True

# สร้าง client ของ Discord
client = discord.Client(intents=intents)

# ฟังก์ชันเพื่ออ่านข้อมูลจากไฟล์ JSON
def load_shop_data():
    folder_path = "topup"
    data_file = os.path.join(folder_path, "shop.json")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # ถ้าไฟล์ไม่มี ให้สร้างไฟล์ใหม่ด้วยข้อมูลสินค้าตัวอย่าง 2 รายการ
        shop_data = [
            {"id": 1, "name": "สินค้า 1", "price": 100, "detail": "รายละเอียดสินค้าของสินค้า 1", "secret_message": "นี่คือข้อความลับของสินค้า 1"},
            {"id": 2, "name": "สินค้า 2", "price": 200, "detail": "รายละเอียดสินค้าของสินค้า 2", "secret_message": "นี่คือข้อความลับของสินค้า 2"}
        ]
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(shop_data, f, ensure_ascii=False, indent=4)
        return shop_data

import json
import os
from datetime import datetime

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


class ShopSelect(Select):
    def __init__(self, shop_data):
        options = [discord.SelectOption(label=item["name"], value=str(item["id"])) for item in shop_data]
        super().__init__(placeholder="เลือกสินค้า", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_item_id = int(self.values[0])
        shop_data = load_shop_data()
        selected_item = next(item for item in shop_data if item["id"] == selected_item_id)
        
        # สร้าง Embed ที่มีข้อมูลสินค้า
        embed = discord.Embed(
            title=selected_item["name"],
            description=f"ราคา: {selected_item['price']} บาท\nรายละเอียด: {selected_item['detail']}",
            color=discord.Color.green()
        )
        
        # สร้างปุ่มยืนยันและยกเลิก
        confirm_button = Button(label="ยืนยัน", style=discord.ButtonStyle.green, custom_id=f"confirm_{selected_item['id']}")
        cancel_button = Button(label="ยกเลิก", style=discord.ButtonStyle.red, custom_id="cancel_button")
        
        # สร้าง View และเพิ่มปุ่ม
        view = View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        # Define button interaction handler here
        async def on_button_click(interaction: discord.Interaction):
            group_id = str(interaction.guild.id)
            if interaction.data["custom_id"].startswith("confirm_"):
                # ดึง ID สินค้าจาก custom_id
                selected_item_id = int(interaction.data["custom_id"].split("_")[1])
                selected_item = next(item for item in shop_data if item["id"] == selected_item_id)

                # เรียกใช้ฟังก์ชันอัปเดต balance โดยเพิ่ม redeem_key เป็นชื่อสินค้าหรือรหัสที่เกี่ยวข้อง
                redeem_key = selected_item["name"]  # หรือสามารถใช้ค่าอื่น ๆ ได้
                success, balance = update_balance(group_id, interaction.user.id, selected_item["price"], redeem_key)

                if success:
                    await interaction.response.send_message(
                        f"คุณซื้อสินค้า **{selected_item['name']}** ราคา {selected_item['price']} บาท สำเร็จ!\nยอดคงเหลือ: {balance} บาท",
                        ephemeral=True
                    )

                    # ส่งข้อความลับให้กับผู้ใช้ใน DM
                    user = interaction.user
                    secret_message = selected_item["secret_message"]
                    try:
                        # ส่ง DM ให้กับผู้ใช้
                        await user.send(f"ข้อความลับของสินค้า **{selected_item['name']}**: {secret_message}")
                    except discord.Forbidden:
                        await interaction.response.send_message("ไม่สามารถส่งข้อความลับให้คุณได้ เนื่องจากคุณปิดการรับ DM จากบอท", ephemeral=True)

                else:
                    await interaction.response.send_message(
                        f"ยอดเงินของคุณไม่เพียงพอในการซื้อสินค้า **{selected_item['name']}**\nยอดคงเหลือ: {balance} บาท",
                        ephemeral=True
                    )
            elif interaction.data["custom_id"] == "cancel_button":
                await interaction.response.send_message("คุณยกเลิกคำสั่งซื้อแล้ว!", ephemeral=True)
        
        # Add button interactions to view
        confirm_button.callback = on_button_click
        cancel_button.callback = on_button_click
        
        # ส่งข้อความพร้อม Embed และปุ่ม
        await interaction.response.send_message(embed=embed, view=view)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content.lower() == "!สินค้า":
        # อ่านข้อมูลสินค้าจาก shop.json
        shop_data = load_shop_data()
        
        embed = discord.Embed(
            title="รายการสินค้า",
            description="เลือกสินค้าใน Dropdown ด้านล่าง",
            color=discord.Color.blue()
        )
        
        # สร้าง Dropdown สำหรับเลือกสินค้า
        select = ShopSelect(shop_data)
        view = View()
        view.add_item(select)
        
        # ส่งข้อความพร้อม Embed และ Dropdown
        await message.channel.send(embed=embed, view=view)

client.run(TOKEN)
