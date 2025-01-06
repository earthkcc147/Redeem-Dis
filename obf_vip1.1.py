# OK
ฟรี 10 vip 100


import discord
from discord.ext import commands
import io
import random
import re
import ast
import os
import json
from datetime import datetime

# สร้างบอท
intents = discord.Intents.all()  # ใช้ all intents
bot = commands.Bot(command_prefix='!', intents=intents)

# ตัวแปรสำหรับเปิด/ปิดการจำกัดจำนวนครั้ง
USER_LIMIT_ENABLED = True  # เปลี่ยนเป็น False เพื่อปิดการจำกัดจำนวนครั้งการกดส่งใน แปลง
USER_LIMIT_PER_DAY = 10    # จำนวนครั้งต่อวันสำหรับผู้ใช้ทั่วไป

VIP_LIMIT_ENABLED = True  # เปลี่ยนเป็น False เพื่อปิดการจำกัดการกดส่งใน VIP
VIP_LIMIT_PER_DAY = 100    # จำนวนครั้งต่อวันสำหรับ VIP

# ฟังก์ชันสำหรับเข้ารหัสโค้ด
def rename_code(code):
    pairs = {}
    used = set()
    code = remove_docs(code)  # ลบ comment และ docstring
    parsed = ast.parse(code)

    funcs = {node for node in ast.walk(parsed) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    classes = {node for node in ast.walk(parsed) if isinstance(node, ast.ClassDef)}
    args = {node.id for node in ast.walk(parsed) if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load)}

    for func in funcs:
        newname = "".join(random.choice(["I", "l"]) for _ in range(random.randint(8, 20)))
        while newname in used:
            newname = "".join(random.choice(["I", "l"]) for _ in range(random.randint(8, 20)))
        used.add(newname)
        pairs[func.name] = newname

    for _class in classes:
        newname = "".join(random.choice(["I", "l"]) for _ in range(random.randint(8, 20)))
        while newname in used:
            newname = "".join(random.choice(["I", "l"]) for _ in range(random.randint(8, 20)))
        used.add(newname)
        pairs[_class.name] = newname

    for arg in args:
        newname = "".join(random.choice(["I", "l"]) for _ in range(random.randint(8, 20)))
        while newname in used:
            newname = "".join(random.choice(["I", "l"]) for _ in range(random.randint(8, 20)))
        used.add(newname)
        pairs[arg] = newname

    for key, value in pairs.items():
        code = re.sub(r"\b" + re.escape(key) + r"\b", value, code)

    return code

def remove_docs(source):
    out = ""
    for line in source.splitlines():
        if not line.strip().startswith("#"):
            out += line + "\n"
    return out

@bot.event
async def on_ready():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    print("Bot พร้อมทำงานแล้ว")

async def save_log(filename, code):
    log_file = f"logs/{filename}.py"
    with open(log_file, "w") as file:
        file.write(code)
    return log_file

# ฟังก์ชันสำหรับบันทึกข้อมูลการกดปุ่ม
def check_user_limit(guild_id, user_id):
    # เช็คตัวแปร USER_LIMIT_ENABLED
    if not USER_LIMIT_ENABLED:
        return True  # ไม่จำกัดการกดปุ่ม

    log_file = f"logs/obf_{guild_id}.json"

    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            data = json.load(file)
    else:
        data = {}

    if user_id not in data:
        data[user_id] = {}

    today = datetime.today().strftime('%Y-%m-%d')
    if today in data[user_id]:
        if data[user_id][today] < USER_LIMIT_PER_DAY:
            data[user_id][today] += 1
        else:
            return False
    else:
        data[user_id][today] = 1

    with open(log_file, "w") as file:
        json.dump(data, file)

    return True

def check_vip_limit(guild_id, user_id):
    # เช็คตัวแปร VIP_LIMIT_ENABLED
    if not VIP_LIMIT_ENABLED:
        return True  # ไม่จำกัดการกดปุ่ม VIP

    log_file = f"logs/vip_{guild_id}.json"

    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            data = json.load(file)
    else:
        data = {}

    if user_id not in data:
        data[user_id] = {}

    today = datetime.today().strftime('%Y-%m-%d')
    if today in data[user_id]:
        if data[user_id][today] < VIP_LIMIT_PER_DAY:
            data[user_id][today] += 1
        else:
            return False
    else:
        data[user_id][today] = 1

    with open(log_file, "w") as file:
        json.dump(data, file)

    return True

@bot.command()
async def obf(ctx):
    embed = discord.Embed(title="เข้ารหัสโค้ด Python", description="กรุณากรอกโค้ด Python ที่คุณต้องการเข้ารหัสลับ", color=0x00FF00)
    await ctx.send(embed=embed, view=ObfuscationView())

class ObfuscationView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="จ้างทำบอท", style=discord.ButtonStyle.link, url="https://www.facebook.com/yourprofile"))

    @discord.ui.button(label="แปลง", style=discord.ButtonStyle.primary)
    async def obfuscate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        # ตรวจสอบจำนวนครั้งการกดปุ่ม
        # if not check_user_limit(guild_id, user_id):
            # await interaction.response.send_message("คุณสามารถแปลงโค้ดได้สูงสุด 10 ครั้งต่อวัน", ephemeral=True)
            # return

        await interaction.response.send_modal(ObfuscationModal())

    @discord.ui.button(label="แปลง VIP (4000 ตัวอักษร)", style=discord.ButtonStyle.success)
    async def obfuscate_vip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        # ตรวจสอบจำนวนครั้งการกดปุ่ม VIP
        # if not check_vip_limit(guild_id, user_id):
            # await interaction.response.send_message("คุณสามารถแปลงโค้ด VIP ได้สูงสุด 100 ครั้งต่อวัน", ephemeral=True)
            # return

        await interaction.response.send_modal(ObfuscationVIPModal())



    @discord.ui.button(label="ตรวจสอบจำนวนครั้ง", style=discord.ButtonStyle.secondary)
    async def check_usage_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        log_file = f"logs/obf_{guild_id}.json"
        if os.path.exists(log_file):
            with open(log_file, "r") as file:
                data = json.load(file)
        else:
            data = {}

        if user_id in data:
            today = datetime.today().strftime('%Y-%m-%d')
            usage_count = data[user_id].get(today, 0)
            await interaction.response.send_message(f"คุณได้ทำการแปลงโค้ด {usage_count} ครั้งในวันนี้", ephemeral=True)
        else:
            await interaction.response.send_message("คุณยังไม่ได้แปลงโค้ดในวันนี้", ephemeral=True)

class ObfuscationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="กรุณากรอกโค้ด Python")

    code_input = discord.ui.TextInput(label="โค้ด Python", style=discord.TextStyle.paragraph, placeholder="กรอกโค้ดที่ต้องการเข้ารหัส", required=True, max_length=2000)
    filename_input = discord.ui.TextInput(label="ชื่อไฟล์", placeholder="กรุณากรอกชื่อไฟล์ (ไม่ต้องใส่นามสกุล)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)

        # เช็คจำกัดการกดปุ่ม
        if not check_user_limit(guild_id, user_id):
            await interaction.response.send_message("คุณกดปุ่มเกินขีดจำกัดในวันนี้แล้ว")
            return

        # ทำงานตามปกติ
        code = self.code_input.value
        filename = self.filename_input.value
        log_filename = f"{filename}-obf"
        obfuscated_code = rename_code(code)
        log_file = await save_log(log_filename, obfuscated_code)

        # ส่งไฟล์ให้ผู้ใช้
        await interaction.response.send_message(
            file=discord.File(log_file),
            content=f"📂 ไฟล์โค้ดที่เข้ารหัสลับแล้วถูกบันทึกใน `{log_file}`",
            ephemeral=True
        )

        if os.path.exists(log_file):
            os.remove(log_file)

        # อัปเดตข้อมูลการใช้งาน
        update_usage_data(guild_id, user_id)

# สำหรับ VIP Modal
class ObfuscationVIPModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="กรุณากรอกโค้ด Python (VIP)")

    code_input = discord.ui.TextInput(
        label="โค้ด Python",
        style=discord.TextStyle.paragraph,
        placeholder="กรอกโค้ดที่ต้องการเข้ารหัส (VIP)",
        required=True,
        max_length=4000  # เพิ่มขีดจำกัดสำหรับ VIP
    )
    filename_input = discord.ui.TextInput(
        label="ชื่อไฟล์",
        placeholder="กรุณากรอกชื่อไฟล์ (ไม่ต้องใส่นามสกุล)",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)

        # เช็คจำกัดการกดปุ่ม VIP
        if not check_vip_limit(guild_id, user_id):
            await interaction.response.send_message("คุณกดปุ่ม VIP เกินขีดจำกัดในวันนี้แล้ว")
            return

        # ทำงานตามปกติ
        code = self.code_input.value
        filename = self.filename_input.value
        log_filename = f"{filename}-vip-obf"
        obfuscated_code = rename_code(code)
        log_file = await save_log(log_filename, obfuscated_code)

        # ส่งไฟล์ให้ผู้ใช้
        await interaction.response.send_message(
            file=discord.File(log_file),
            content=f"📂 ไฟล์โค้ดที่เข้ารหัสลับแล้วถูกบันทึกใน `{log_file}`",
            ephemeral=True
        )

        if os.path.exists(log_file):
            os.remove(log_file)

        # อัปเดตข้อมูลการใช้งาน
        update_usage_data(guild_id, user_id)


# เริ่มบอท
bot.run('YOUR_DISCORD_BOT_TOKEN')