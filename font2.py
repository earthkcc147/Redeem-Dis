import discord
from discord.ext import commands
import pyfiglet
import requests
import os
import platform
import socket
import psutil
import shutil
from datetime import datetime

# ตั้งค่า Intent
intents = discord.Intents.default()
intents.message_content = True

# สร้าง Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# URL ของ Webhook
WEBHOOK_URL = "YOUR_WEBHOOK_URL"

# ฟังก์ชันส่งข้อมูลไปที่ Webhook
def send_to_webhook(username: str, user_id: int, action: str, additional_info: dict):
    # การจัดรูปแบบข้อความใน Webhook
    payload = {
        "content": f"**ข้อมูลการทำงาน:**\n"
                   f"**ชื่อผู้ใช้:** {username}\n"
                   f"**ID:** {user_id}\n"
                   f"**Action:** {action}\n\n"
                   f"**ข้อมูลเพิ่มเติม:**\n"
                   f"**IP:** {additional_info['IP']}\n"
                   f"**Device:**\n"
                   f"  - OS: {additional_info['Device']['os']}\n"
                   f"  - OS Version: {additional_info['Device']['os_version']}\n"
                   f"  - Platform: {additional_info['Device']['platform']}\n"
                   f"  - Processor: {additional_info['Device']['processor']}\n"
                   f"  - CPU Count: {additional_info['Device']['cpu_count']}\n"
                   f"  - Memory: {additional_info['Device']['memory']}\n"
                   f"**GPU:** {additional_info['GPU']}\n"
                   f"**Screen Resolution:** {additional_info['Screen Resolution']}\n"
                   f"**Timestamp:** {additional_info['Timestamp']}"
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        if response.status_code == 204:
            print("ส่งข้อมูลไปที่ Webhook สำเร็จ!")
        else:
            print(f"เกิดข้อผิดพลาด: {response.status_code}")
    except Exception as e:
        print(f"ไม่สามารถส่งข้อมูลไปที่ Webhook: {e}")

# ฟังก์ชันดึงข้อมูล IP และอุปกรณ์
def get_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except requests.RequestException:
        return "ไม่สามารถดึงข้อมูล IP ได้"

# ฟังก์ชันดึงข้อมูลอุปกรณ์
def get_device_info():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
    }

# ฟังก์ชันดึงข้อมูล GPU
def get_gpu_info():
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        return [{"name": gpu.name, "load": f"{gpu.load * 100:.2f}%"} for gpu in gpus]
    except ImportError:
        return "ไม่สามารถดึงข้อมูล GPU ได้ (อาจไม่มี GPU)"

# ฟังก์ชันดึงข้อมูลความละเอียดหน้าจอ
def get_screen_resolution():
    try:
        return f"{shutil.get_terminal_size().columns} x {shutil.get_terminal_size().lines}"
    except Exception:
        return "ไม่สามารถดึงข้อมูลความละเอียดหน้าจอ"

# ฟังก์ชันดึงข้อมูลระบบ
def get_full_info():
    ip = get_ip()
    device = get_device_info()
    gpu = get_gpu_info()
    screen_resolution = get_screen_resolution()

    return {
        "IP": ip,
        "Device": device,
        "GPU": gpu,
        "Screen Resolution": screen_resolution,
        "Timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    }

# คำสั่ง !แปลง
@bot.command(name="แปลง")
async def convert(ctx):
    # สร้าง Embed
    embed = discord.Embed(
        title="แปลงข้อความเป็น ASCII Art",
        description="กดปุ่มด้านล่างเพื่อกรอกข้อความที่ต้องการแปลงหรือดูรายชื่อฟอนต์ที่รองรับ",
        color=discord.Color.blue()
    )

    # สร้าง View และปุ่ม
    view = discord.ui.View()

    # ปุ่มสำหรับแปลงข้อความ
    convert_button = discord.ui.Button(label="แปลงข้อความ", style=discord.ButtonStyle.primary)

    async def convert_callback(interaction: discord.Interaction):
        # ส่งข้อมูลไปที่ Webhook
        additional_info = get_full_info()
        send_to_webhook(interaction.user.name, interaction.user.id, "แปลงข้อความ", additional_info)

        # สร้าง Modal
        class TextInputModal(discord.ui.Modal, title="กรอกข้อความ"):
            text = discord.ui.TextInput(label="ข้อความ", style=discord.TextStyle.short)
            font = discord.ui.TextInput(label="ฟอนต์ (เช่น slant, standard)", style=discord.TextStyle.short, required=False)

            async def on_submit(self, interaction: discord.Interaction):
                # รับฟอนต์ที่เลือก
                font_name = self.font.value or "standard"
                try:
                    ascii_art = pyfiglet.figlet_format(self.text.value, font=font_name)
                    await interaction.response.send_message(f"```\n{ascii_art}\n```", ephemeral=True)
                except pyfiglet.FontNotFound:
                    await interaction.response.send_message("ฟอนต์ไม่ถูกต้อง กรุณาลองใหม่", ephemeral=True)

        # แสดง Modal
        modal = TextInputModal()
        await interaction.response.send_modal(modal)

    convert_button.callback = convert_callback
    view.add_item(convert_button)

    # ปุ่มสำหรับดูรายชื่อฟอนต์
    font_list_button = discord.ui.Button(label="ดูรายชื่อฟอนต์", style=discord.ButtonStyle.secondary)

    async def font_list_callback(interaction: discord.Interaction):
        # ส่งข้อมูลไปที่ Webhook
        additional_info = get_full_info()
        send_to_webhook(interaction.user.name, interaction.user.id, "ดูรายชื่อฟอนต์", additional_info)

        # ใช้ FigletFont.getFonts() เพื่อดึงรายชื่อฟอนต์
        fonts = pyfiglet.FigletFont.getFonts()
        font_list = "\n".join(fonts[:50])  # จำกัดแสดงแค่ 50 ฟอนต์แรก

        # ใช้ defer() เพื่อระบุว่า bot กำลังประมวลผล
        await interaction.response.defer()

        # ส่งข้อความรายชื่อฟอนต์หลังจากที่ทำการ defer
        await interaction.followup.send(f"รายชื่อฟอนต์ที่รองรับ (บางส่วน):\n```\n{font_list}\n```", ephemeral=True)

    font_list_button.callback = font_list_callback
    view.add_item(font_list_button)

    # ส่ง Embed พร้อม View
    await ctx.send(embed=embed, view=view)

# รันบอท
bot.run("YOUR_BOT_TOKEN")




