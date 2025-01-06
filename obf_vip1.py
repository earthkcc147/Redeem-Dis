# รอแก้หักเงิน


import discord
from discord.ext import commands
import io
import random
import re
import ast
import os
from datetime import datetime
import json

USER_LIMIT_ENABLED = True  # เปิดใช้งานการจำกัดจำนวนครั้ง
USER_LIMIT_PER_DAY = 10  # จำนวนครั้งต่อวัน

# สร้างบอท
intents = discord.Intents.all()  # ใช้ all intents
bot = commands.Bot(command_prefix='!', intents=intents)

# ฟังก์ชันสำหรับเข้ารหัสโค้ด
def rename_code(code):
    pairs = {}
    used = set()
    code = remove_docs(code)  # ลบ comment และ docstring ด้วยฟังก์ชันใหม่
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
    """
    ลบ docstring และ comment ออกจากโค้ด Python
    """
    try:
        # ใช้ ast เพื่อจัดการ docstring
        parsed = ast.parse(source)
        for node in ast.walk(parsed):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                node.body = [stmt for stmt in node.body if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Str)]
        source = ast.unparse(parsed)  # แปลงกลับเป็น source code

        # ลบ comment ด้วย regex
        source = re.sub(r"#.*", "", source)  # ลบ comment ทั้งบรรทัดที่เริ่มต้นด้วย #
        return source
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการลบ docstring: {e}")
        return source


def check_user_limit(guild_id, user_id):
    if not USER_LIMIT_ENABLED:
        return True

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

@bot.event
async def on_ready():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    print("Bot พร้อมทำงานแล้ว")


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


async def save_log(filename, code):
    log_file = f"logs/{filename}.py"
    with open(log_file, "w") as file:
        file.write(code)
    return log_file

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
        # เรียกใช้งาน ObfuscationModal โดยส่ง interaction
        await interaction.response.send_modal(ObfuscationModal(interaction))

    @discord.ui.button(label="แปลง VIP (4000 ตัวอักษร)", style=discord.ButtonStyle.success)
    async def obfuscate_vip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # เมื่อกดปุ่ม "แปลง VIP"
        await interaction.response.send_modal(ObfuscationVIPModal(interaction=interaction))


class ObfuscationModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(title="กรุณากรอกโค้ด Python")
        self.group_id = str(interaction.guild.id)  # รับ group_id จาก interaction

    # ฟิลด์สำหรับกรอกโค้ดและชื่อไฟล์
    code_input = discord.ui.TextInput(
        label="โค้ด Python", style=discord.TextStyle.paragraph, placeholder="กรอกโค้ดที่ต้องการเข้ารหัส", required=True, max_length=2000)
    filename_input = discord.ui.TextInput(
        label="ชื่อไฟล์", placeholder="กรุณากรอกชื่อไฟล์ (ไม่ต้องใส่นามสกุล)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # ตรวจสอบจำนวนครั้งการใช้งาน
        if not check_user_limit(self.group_id, interaction.user.id):
            await interaction.response.send_message(
                "❌ คุณได้ใช้สิทธิ์การเข้ารหัสครบ 10 ครั้งในวันนี้แล้ว กรุณารอวันถัดไป",
                ephemeral=True
            )
            return

        code = self.code_input.value
        filename = self.filename_input.value

        # สร้างชื่อไฟล์ log
        log_filename = f"{filename}-obf"

        # เข้ารหัสโค้ด
        obfuscated_code = rename_code(code)

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


# Modal สำหรับการเข้ารหัสโค้ด Python (VIP)
class ObfuscationVIPModal(discord.ui.Modal):
    def __init__(self, interaction):
        super().__init__(title="กรุณากรอกโค้ด Python (VIP)")
        self.user_id = str(interaction.user.id)  # รับ user_id จาก interaction
        self.group_id = str(interaction.guild.id)  # รับ guild_id (ใช้เป็น group_id) จาก interaction
        self.interaction = interaction

    code_input = discord.ui.TextInput(label="โค้ด Python", style=discord.TextStyle.paragraph, placeholder="กรอกโค้ดที่ต้องการเข้ารหัส", required=True, max_length=4000)
    filename_input = discord.ui.TextInput(label="ชื่อไฟล์", placeholder="กรุณากรอกชื่อไฟล์ (ไม่ต้องใส่นามสกุล)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # หักเงิน 10 บาทจาก balance
        price = 10
        success, balance = update_balance(self.group_id, self.user_id, price, "obfuscate_vip")
        
        if not success:
            # หากยอดเงินไม่พอ
            await interaction.response.send_message(
                f"❌ คุณมีเงินไม่เพียงพอในการทำรายการ (ยอดเงินคงเหลือ: {balance} บาท)",
                ephemeral=True
            )
            return

        code = self.code_input.value
        filename = self.filename_input.value

        # สร้างชื่อไฟล์ใน logs
        log_filename = f"{filename}-obf-vip"

        # เข้ารหัสโค้ด
        obfuscated_code = rename_code(code)

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

# เริ่มบอท
bot.run('YOUR_DISCORD_BOT_TOKEN')

