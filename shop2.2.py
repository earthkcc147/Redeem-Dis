import discord
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
    data_file = os.path.join(folder_path, "shop2.json")  # ถ้าไม่ได้ใช้ shop.json
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # ถ้าไฟล์ไม่มี ให้สร้างไฟล์ใหม่ด้วยข้อมูลสินค้าตัวอย่าง
        shop_data = [
            {"id": 1, "name": "สินค้า 1", "price": 100, "description": "รายละเอียดสินค้าของสินค้า 1", "secret_message": "นี่คือข้อความลับของสินค้า 1"},
            {"id": 2, "name": "สินค้า 2", "price": 200, "description": "รายละเอียดสินค้าของสินค้า 2", "secret_message": "นี่คือข้อความลับของสินค้า 2"}
        ]
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(shop_data, f, ensure_ascii=False, indent=4)
        return shop_data


# ฟังก์ชันแสดงสินค้าและปุ่มซื้อ
async def send_shop_item(channel, item_id):
    
    # โหลดข้อมูลสินค้า
    shop_data = load_shop_data()

    # ค้นหาข้อมูลสินค้าจาก shop.json
    item = next((item for item in shop_data if item["id"] == item_id), None)

    if item:
        # สร้าง embed
        embed = discord.Embed(
            title=item["name"],
            description=item["description"],
            color=discord.Color.green()
        )
        embed.add_field(name="ราคา", value=f"{item['price']} บาท", inline=False)

        # สร้างปุ่ม
        button = Button(label="ซื้อสินค้า", style=discord.ButtonStyle.green, custom_id=f"buy_{item_id}")

        # สร้าง view สำหรับปุ่ม
        view = View()
        view.add_item(button)

        # ส่งข้อความพร้อม embed และปุ่ม
        await channel.send(embed=embed, view=view)
    else:
        await channel.send("ไม่พบสินค้านี้ในร้านค้า!")

# ฟังก์ชันสำหรับจัดการข้อความ
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!ร้านค้า1"):
        await send_shop_item(message.channel, 1)
    elif message.content.startswith("!ร้านค้า2"):
        await send_shop_item(message.channel, 2)

# ฟังก์ชันจัดการปุ่มซื้อ
@client.event
async def on_interaction(interaction: discord.Interaction):
    custom_id = interaction.data["custom_id"]

    if custom_id.startswith("buy_"):
        # ดึง id สินค้า
        item_id = int(custom_id.split("_")[1])
        item = next((item for item in shop_data if item["id"] == item_id), None)

        if item:
            # สร้างปุ่มยืนยันและยกเลิก
            confirm_button = Button(label="ยืนยัน", style=discord.ButtonStyle.success, custom_id=f"confirm_{item_id}")
            cancel_button = Button(label="ยกเลิก", style=discord.ButtonStyle.danger, custom_id="cancel_button")

            # สร้าง view สำหรับปุ่มยืนยันและยกเลิก
            view = View()
            view.add_item(confirm_button)
            view.add_item(cancel_button)

            # ตอบกลับพร้อมปุ่ม
            await interaction.response.send_message(
                f"คุณกำลังจะซื้อสินค้า **{item['name']}** ราคา {item['price']} บาท\nกรุณายืนยันหรือยกเลิก",
                view=view,
                ephemeral=True
            )
        else:
            await interaction.response.send_message("ไม่พบสินค้านี้ในร้านค้า!", ephemeral=True)

    elif custom_id.startswith("confirm_"):
        # ดึง id สินค้า
        item_id = int(custom_id.split("_")[1])
        item = next((item for item in shop_data if item["id"] == item_id), None)

        if item:
            # ส่งข้อความยืนยันการซื้อ
            await interaction.response.edit_message(
                content=f"คุณได้ซื้อสินค้า **{item['name']}** ราคา {item['price']} บาท สำเร็จ!",
                view=None
            )

            # ส่งข้อความลับให้ผู้ใช้
            secret_message = item["secret_message"]
            try:
                await interaction.user.send(f"ข้อความลับสำหรับสินค้า **{item['name']}**: {secret_message}")
            except discord.Forbidden:
                await interaction.followup.send("ไม่สามารถส่งข้อความลับให้คุณได้ เนื่องจากคุณปิดการรับ DM จากบอท", ephemeral=True)

        else:
            await interaction.response.send_message("ไม่พบสินค้านี้ในร้านค้า!", ephemeral=True)

    elif custom_id == "cancel_button":
        # ส่งข้อความแจ้งยกเลิก
        await interaction.response.edit_message(content="คุณได้ยกเลิกการซื้อสินค้าแล้ว!", view=None)

# เริ่มต้นบอท
client.run(TOKEN)
