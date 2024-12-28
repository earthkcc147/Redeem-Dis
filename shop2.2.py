import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
from datetime import datetime

TOKEN = 'MTE5MjA0MTI2MTA1NDU3MDUyNg.GAjtli.9Lcf8EW1K6PIWQTe6JfiatQD4d31MANVuGh7rc'  # ใส่โทเค็นบอทของคุณที่นี่

# ตั้งค่า intents
intents = discord.Intents.default()
intents.message_content = True

# สร้าง client ของ Discord
client = discord.Client(intents=intents)

# ฟังก์ชันเพื่ออ่านข้อมูลจากไฟล์ JSON
def load_shop_data():
    folder_path = "topup"
    data_file = os.path.join(folder_path, "shop2.json")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        shop_data = [
            {"id": 1, "name": "สินค้า 1", "price": 100, "description": "รายละเอียดสินค้าของสินค้า 1", "secret_message": "นี่คือข้อความลับของสินค้า 1"},
            {"id": 2, "name": "สินค้า 2", "price": 200, "description": "รายละเอียดสินค้าของสินค้า 2", "secret_message": "นี่คือข้อความลับของสินค้า 2"}
        ]
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(shop_data, f, ensure_ascii=False, indent=4)
        return shop_data

# ฟังก์ชันโหลดและบันทึกข้อมูล JSON
def load_data(guild_id):
    file_path = f"topup/{guild_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_data(guild_id, data):
    file_path = f"topup/{guild_id}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# ฟังก์ชันอัปเดตยอดเงิน
def update_balance(guild_id, user_id, price, item_id):
    data = load_data(guild_id)

    if str(user_id) not in data:
        return False, 0

    balance = data[str(user_id)].get("balance", 0)
    if balance < price:
        return False, balance

    balance -= price
    data[str(user_id)]["balance"] = balance

    item = next((item for item in shop_data if item["id"] == item_id), None)
    if item:
        redeem_key = item["name"]
        if "history" not in data[str(user_id)]:
            data[str(user_id)]["history"] = []
        data[str(user_id)]["history"].append({
            "amount": price,
            "redeem_key": redeem_key,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success"
        })
        save_data(guild_id, data)
        return True, balance
    return False, balance

# โหลดข้อมูลสินค้า
shop_data = load_shop_data()

# ฟังก์ชันแสดงสินค้าและปุ่มซื้อ
async def send_shop_item(interaction, item_id):
    item = next((item for item in shop_data if item["id"] == item_id), None)
    if item:
        embed = discord.Embed(
            title=item["name"],
            description=item["description"],
            color=discord.Color.green()
        )
        embed.add_field(name="ราคา", value=f"{item['price']} บาท", inline=False)

        button = Button(label="ซื้อสินค้า", style=discord.ButtonStyle.green, custom_id=f"buy_{item_id}")
        view = View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    else:
        await interaction.response.send_message("ไม่พบสินค้านี้ในร้านค้า!", ephemeral=True)

# อีเวนต์สำหรับปุ่ม
@client.event
async def on_interaction(interaction: discord.Interaction):
    custom_id = interaction.data.get("custom_id", "")

    if custom_id.startswith("buy_"):
        item_id = int(custom_id.split("_")[1])
        await send_shop_item(interaction, item_id)

    elif custom_id.startswith("confirm_"):
        item_id = int(custom_id.split("_")[1])
        item = next((item for item in shop_data if item["id"] == item_id), None)

        if item:
            guild_id = str(interaction.guild.id)
            user_id = interaction.user.id
            success, new_balance = update_balance(guild_id, user_id, item['price'], item['id'])

            if success:
                await interaction.response.edit_message(
                    content=f"คุณได้ซื้อสินค้า **{item['name']}** ราคา {item['price']} บาท สำเร็จ!",
                    view=None
                )
                secret_message = item["secret_message"]
                try:
                    await interaction.user.send(f"ข้อความลับสำหรับสินค้า **{item['name']}**: {secret_message}")
                except discord.Forbidden:
                    await interaction.followup.send("ไม่สามารถส่งข้อความลับได้ (DM ปิดอยู่)", ephemeral=True)
                await interaction.followup.send(f"ยอดเงินใหม่ของคุณ: {new_balance} บาท", ephemeral=True)
            else:
                await interaction.response.send_message("ยอดเงินไม่เพียงพอ!", ephemeral=True)

    elif custom_id == "cancel_button":
        await interaction.response.edit_message(content="คุณได้ยกเลิกการซื้อสินค้าแล้ว!", view=None)

# เริ่มต้นบอท
client.run(TOKEN)