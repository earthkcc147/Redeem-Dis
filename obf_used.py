#. OK จำนวน -1 ต่อครัง ฟรี1/วัน

import discord
from discord.ext import commands
import io
import random
import re
import ast
import os
import json
from datetime import datetime

# กำหนดจำนวนครั้งที่สามารถแปลงฟรีได้ต่อวัน
free_obfuscate_limit = 10

# สร้างบอท
intents = discord.Intents.all()  # ใช้ all intents
bot = commands.Bot(command_prefix='!', intents=intents)

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

# ฟังก์ชันสำหรับโหลดข้อมูลจำนวนครั้งที่สามารถกดได้จากไฟล์ JSON
def load_usage_data(group_id):
    file_path = f"logs/obf_{group_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

# ฟังก์ชันสำหรับบันทึกข้อมูลจำนวนครั้งที่สามารถกดได้
def save_usage_data(group_id, data):
    file_path = f"logs/obf_{group_id}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


# ฟังก์ชันสำหรับตรวจสอบการใช้งานในวันนี้และจำนวนครั้งที่เหลือ
def can_use_today(usage_data, user_id):
    today = datetime.today().strftime('%Y-%m-%d')
    if user_id not in usage_data:
        usage_data[user_id] = {"count": free_obfuscate_limit, "last_used": ""}
    
    if usage_data[user_id]['last_used'] != today:
        # ถ้ายังไม่เคยใช้ในวันนี้ ให้รีเซ็ตจำนวนครั้ง
        usage_data[user_id]['count'] = free_obfuscate_limit
        usage_data[user_id]['last_used'] = today
        save_usage_data(group_id, usage_data)

    if usage_data[user_id]['count'] > 0:
        return True  # สามารถใช้งานได้
    return False


@bot.command()
async def obf(ctx):
    embed = discord.Embed(title="เข้ารหัสโค้ด Python", description="กรุณากรอกโค้ด Python ที่คุณต้องการเข้ารหัสลับ", color=0x00FF00)
    await ctx.send(embed=embed, view=ObfuscationView(ctx))

class ObfuscationView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="แปลงฟรี", style=discord.ButtonStyle.green)
    async def free_obfuscate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ObfuscationFreeModal(self.ctx))

    @discord.ui.button(label="แปลง", style=discord.ButtonStyle.primary)
    async def obfuscate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        group_id = str(self.ctx.guild.id)
        user_id = str(interaction.user.id)
        usage_data = load_usage_data(group_id)

        if user_id not in usage_data:
            usage_data[user_id] = {"count": 0, "last_used": ""}
          
            await interaction.response.send_modal(ObfuscationModal(self.ctx, group_id, user_id))
        

# ฟังก์ชันที่เรียกใช้เมื่อมีการกดปุ่มแปลงฟรี
class ObfuscationFreeModal(discord.ui.Modal):
    def __init__(self, ctx):
        super().__init__(title="กรุณากรอกโค้ด Python")
        self.ctx = ctx

    code_input = discord.ui.TextInput(label="โค้ด Python", style=discord.TextStyle.paragraph, placeholder="กรอกโค้ดที่ต้องการเข้ารหัส", required=True, max_length=2000)
    filename_input = discord.ui.TextInput(label="ชื่อไฟล์", placeholder="กรุณากรอกชื่อไฟล์ (ไม่ต้องใส่นามสกุล)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        group_id = str(self.ctx.guild.id)
        user_id = str(interaction.user.id)
        usage_data = load_usage_data(group_id)

        # ตรวจสอบการใช้งานในวันนี้
        if can_use_today(usage_data, user_id):
            # บันทึกวันที่ที่ใช้แปลงและลดจำนวนการใช้งาน
            usage_data[user_id]['count'] -= 1  # ลดจำนวนการใช้งาน
            save_usage_data(group_id, usage_data)

            # ดำเนินการแปลงโค้ด
            code = self.code_input.value
            filename = self.filename_input.value

            # เข้ารหัสโค้ด
            obfuscated_code = rename_code(code)

            # สร้างชื่อไฟล์ใน logs
            log_filename = f"{filename}-obf"

            # บันทึกโค้ดในโฟลเดอร์ logs
            log_file = await save_log(log_filename, obfuscated_code)

            # ส่งไฟล์ให้ผู้ใช้
            await interaction.response.send_message(
                file=discord.File(log_file),
                content=f"📂 ไฟล์โค้ดที่เข้ารหัสลับแล้วถูกบันทึกใน `{log_file}`",
                ephemeral=True
            )

            # ลบไฟล์หลังส่ง
            if os.path.exists(log_file):
                os.remove(log_file)
        else:
            await interaction.response.send_message(
                f"คุณสามารถแปลงโค้ดได้เพียง {free_obfuscate_limit} ครั้งต่อวันเท่านั้น กรุณาลองใหม่ในวันพรุ่งนี้",
                ephemeral=True
            )



class ObfuscationModal(discord.ui.Modal):
    def __init__(self, ctx, group_id, user_id):
        super().__init__(title="กรุณากรอกโค้ด Python")
        self.ctx = ctx
        self.group_id = group_id
        self.user_id = user_id

    code_input = discord.ui.TextInput(label="โค้ด Python", style=discord.TextStyle.paragraph, placeholder="กรอกโค้ดที่ต้องการเข้ารหัส", required=True, max_length=2000)
    filename_input = discord.ui.TextInput(label="ชื่อไฟล์", placeholder="กรุณากรอกชื่อไฟล์ (ไม่ต้องใส่นามสกุล)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # โหลดข้อมูลการใช้งานจากไฟล์
        usage_data = load_usage_data(self.group_id)

        # ตรวจสอบจำนวนครั้งที่เหลือ
        if usage_data[self.user_id]['count'] > 0:
            # ลดจำนวนครั้งการใช้งาน
            usage_data[self.user_id]['count'] -= 1
            save_usage_data(self.group_id, usage_data)

            # เข้ารหัสโค้ด
            code = self.code_input.value
            filename = self.filename_input.value
            obfuscated_code = rename_code(code)

            # สร้างชื่อไฟล์ใน logs
            log_filename = f"{filename}-obf"
            log_file = await save_log(log_filename, obfuscated_code)

            # ส่งไฟล์ให้ผู้ใช้
            await interaction.response.send_message(
                file=discord.File(log_file),
                content=f"📂 ไฟล์โค้ดที่เข้ารหัสลับแล้วถูกบันทึกใน `{log_file}`",
                ephemeral=True
            )

            # ลบไฟล์หลังส่ง
            if os.path.exists(log_file):
                os.remove(log_file)

        else:
            # ถ้าหมดจำนวนครั้งการใช้งาน
            await interaction.response.send_message(
                "คุณไม่สามารถแปลงโค้ดได้แล้ว เนื่องจากคุณหมดจำนวนครั้งที่สามารถใช้งานได้",
                ephemeral=True
            )


# เริ่มบอท
bot.run('YOUR_DISCORD_BOT_TOKEN')