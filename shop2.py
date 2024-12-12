import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
from datetime import datetime

TOKEN = 'MTE5MjA0MTI2MTA1NDU3MDUyNg.GmR8Zy.kE1mTrYzUk4Fddkj4R0dKHKfHS-Gf8aEDa0bw0'  # ใส่โทเค็นบอทของคุณที่นี่

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
        # ถ้าไฟล์ไม่มี ให้สร้างไฟล์ใหม่ด้วยข้อมูลสินค้าตัวอย่าง
        shop_data = [
            {"id": 1, "name": "สินค้า 1", "price": 100, "description": "รายละเอียดสินค้าของสินค้า 1", "secret_message": "นี่คือข้อความลับของสินค้า 1"},
            {"id": 2, "name": "สินค้า 2", "price": 200, "description": "รายละเอียดสินค้าของสินค้า 2", "secret_message": "นี่คือข้อความลับของสินค้า 2"}
        ]
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(shop_data, f, ensure_ascii=False, indent=4)
        return shop_data

# ฟังก์ชันโหลดข้อมูลจากไฟล์ JSON โดยใช้ guild.id เป็นชื่อไฟล์
def load_data(guild_id):
    file_path = f"topup/{guild_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# ฟังก์ชันบันทึกข้อมูลลงไฟล์ JSON โดยใช้ guild.id เป็นชื่อไฟล์
def save_data(guild_id, data):
    file_path = f"topup/{guild_id}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# ฟังก์ชันอัปเดตยอดเงิน
def update_balance(guild_id, user_id, price, item_id):
    data = load_data(guild_id)

    # ตรวจสอบว่า guild_id มีข้อมูลในไฟล์หรือไม่
    if str(user_id) not in data:
        return False, 0  # หากไม่มีข้อมูล user_id คืนค่า balance เป็น 0
    
    # ดึงยอดเงินปัจจุบันของ user_id
    balance = data[str(user_id)].get("balance", 0)

    if balance < price:
        return False, balance  # หากยอดเงินไม่เพียงพอ

    # หักเงินออกจาก balance
    balance -= price
    data[str(user_id)]["balance"] = balance

    # หาชื่อสินค้าจาก shop_data โดยใช้ item_id
    item = next((item for item in shop_data if item["id"] == item_id), None)
    if item:
        redeem_key = item["name"]  # ใช้ชื่อสินค้าจาก item

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
        save_data(guild_id, data)

        return True, balance
    else:
        return False, balance  # หากไม่พบสินค้าที่มี id ตรง

# โหลดข้อมูลสินค้า
shop_data = load_shop_data()

# สร้างบอท
bot = commands.Bot(command_prefix="!", intents=intents)

# ฟังก์ชันแสดงสินค้าและปุ่มซื้อ
async def send_shop_item(ctx, item_id):
    # ค้นหาข้อมูลสินค้าจาก shop.json
    item = next((item for item in shop_data if item["id"] == item_id), None)

    if item:
        # สร้าง embed
        embed = discord.Embed(
            title=item["name"],
            description=item["detail"],
            color=discord.Color.green()
        )
        embed.add_field(name="ราคา", value=f"{item['price']} บาท", inline=False)
        
        # สร้างปุ่ม
        button = Button(label="ซื้อสินค้า", style=discord.ButtonStyle.green, custom_id=f"buy_{item_id}")

        # สร้าง view สำหรับปุ่ม
        view = View()
        view.add_item(button)

        # ส่งข้อความพร้อม embed และปุ่ม
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send("ไม่พบสินค้านี้ในร้านค้า!")

# คำสั่ง !ร้านค้า1
@bot.command()
async def ร้านค้า1(ctx):
    await send_shop_item(ctx, 1)

# คำสั่ง !ร้านค้า2
@bot.command()
async def ร้านค้า2(ctx):
    await send_shop_item(ctx, 2)

# ฟังก์ชันจัดการปุ่มซื้อ
@bot.event
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
            # เรียกฟังก์ชันอัปเดตยอดเงินและประวัติการทำรายการ
            guild_id = str(interaction.guild.id)  # ใช้ guild_id จากการเชื่อมต่อกับเซิร์ฟเวอร์
            user_id = interaction.user.id  # ใช้ user_id จากผู้ใช้
            success, new_balance = update_balance(guild_id, user_id, item['price'], item['id'])

            if success:
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

                await interaction.followup.send(f"ยอดเงินของคุณได้รับการอัปเดตใหม่: {new_balance} บาท", ephemeral=True)
            else:
                # แจ้งเตือนว่าเงินไม่เพียงพอ
                await interaction.response.send_message("ยอดเงินไม่เพียงพอสำหรับการซื้อสินค้า", ephemeral=True)
        else:
            await interaction.response.send_message("ไม่พบสินค้านี้ในร้านค้า!", ephemeral=True)

    elif custom_id == "cancel_button":
        # ส่งข้อความแจ้งยกเลิก
        await interaction.response.edit_message(content="คุณได้ยกเลิกการซื้อสินค้าแล้ว!", view=None)

# เริ่มต้นบอท
bot.run(TOKEN)

