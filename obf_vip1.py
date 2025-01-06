# ระบบหักเงิน OK
# เพิ่มระบบเติมเงิน

import discord
from discord.ext import commands
import io
import random
import re
import ast
import string
import time
import os
from datetime import datetime
import json



USER_LIMIT_ENABLED = True  # เปิดใช้งานการจำกัดจำนวนครั้ง
USER_LIMIT_PER_DAY = 10  # จำนวนครั้งต่อวัน

# สร้างบอท
intents = discord.Intents.all()  # ใช้ all intents
bot = commands.Bot(command_prefix='!', intents=intents)




import discord
from discord.ui import Modal, TextInput
import requests

# ฟังก์ชันเพื่ออ่านข้อมูลจากไฟล์ JSON
def load_data(group_id):
    folder_path = "topup"
    data_file = os.path.join(folder_path, f"{group_id}.json")  # ตั้งชื่อไฟล์ตาม ID ของกลุ่ม

    # ถ้าไฟล์ไม่พบ ให้สร้างไฟล์ใหม่และคืนค่าข้อมูลเริ่มต้น
    if not os.path.exists(data_file):
        # สร้างโฟลเดอร์ "topup" ถ้ายังไม่มี
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # สร้างไฟล์ JSON ใหม่ด้วยข้อมูลเริ่มต้น
        default_data = {}
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

    # ถ้าไฟล์มีอยู่แล้วให้โหลดข้อมูลจากไฟล์
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# ฟังก์ชันเพื่อบันทึกข้อมูลลงในไฟล์ JSON
def save_data(data, group_id):
    folder_path = "topup"
    # ตรวจสอบว่าโฟลเดอร์ topup มีอยู่หรือไม่ ถ้าไม่ให้สร้าง
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    data_file = os.path.join(folder_path, f"{group_id}.json")  # ตั้งชื่อไฟล์ตาม ID ของกลุ่ม
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)




class GiftLinkModal(discord.ui.Modal):
    def __init__(self, group_id):
        super().__init__(title="กรอกลิ้งซองของขวัญ")
        self.group_id = group_id
        self.gift_link = TextInput(label="Gift Link", placeholder="ใส่ลิ้งซองของขวัญที่นี่", required=True)
        self.add_item(self.gift_link)

    async def on_submit(self, interaction: discord.Interaction):
        # รับค่าจาก Modal
        gift_link = self.gift_link.value
        phone = "0841304874"  # เบอร์รับเงินที่กำหนด

        # ส่งข้อมูลไปที่ API
        api_url = "https://byshop.me/api/truewallet"
        data = {
            "action": "truewallet", 
            "gift_link": gift_link,
            "phone": phone
        }

        response = requests.post(api_url, data=data)
        result = response.json()

        # ตรวจสอบผลลัพธ์จาก API
        if result["status"] == "success":
            message = f"สำเร็จ! จำนวนเงิน: {result['amount']} บาท\nเบอร์รับเงิน: {result['phone']}\nลิ้งซองของขวัญ: {result['gift_link']}\nเวลาทำรายการ: {result['time']}"

            # อ่านข้อมูลสมาชิกจากไฟล์
            user_data = load_data(self.group_id)
            user_id = str(interaction.user.id)  # ใช้ user id ของ Discord เป็น key

            # ถ้าผู้ใช้ไม่เคยมีข้อมูลในไฟล์ ให้สร้างข้อมูลใหม่
            if user_id not in user_data:
                user_data[user_id] = {"balance": 0.0, "history": []}

            # อัพเดตยอดเงินของผู้ใช้
            user_data[user_id]["balance"] += float(result['amount'])

            # บันทึกประวัติการทำรายการ
            transaction = {
                "amount": result['amount'],
                "gift_link": result['gift_link'],
                "time": result['time'],
                "status": result['status'],
                "phone": result['phone']
            }
            user_data[user_id]["history"].append(transaction)

            # บันทึกข้อมูลลงไฟล์
            save_data(user_data, self.group_id)

            # ส่งข้อความไปยังช่องที่ต้องการ
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(
                    f"เติมเงินสำเร็จจาก {interaction.user.name}!\n"
                    f"จำนวนเงิน: {result['amount']} บาท\n"
                    f"เบอร์รับเงิน: {result['phone']}\n"
                    f"ลิ้งซองของขวัญ: {result['gift_link']}\n"
                    f"เวลาทำรายการ: {result['time']}\n"
                    f"ยอดเงินรวมของ {interaction.user.name}: {user_data[user_id]['balance']} บาท"
                )
        else:
            message = f"ผิดพลาด: {result['message']}"

        # ส่งข้อความตอบกลับในช่องที่กดคำสั่ง
        await interaction.response.send_message(message, ephemeral=True)










# ฟังก์ชันสำหรับเข้ารหัสโค้ด
def rename_code(code):
    pairs = {}
    used = set()
    code = remove_docs(code)  # ลบ comment และ docstring ด้วยฟังก์ชันใหม่
    parsed = ast.parse(code)

    # ค้นหาฟังก์ชัน, คลาส และอาร์กิวเมนต์ในโค้ด
    funcs = {node for node in ast.walk(parsed) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    classes = {node for node in ast.walk(parsed) if isinstance(node, ast.ClassDef)}
    args = {node.id for node in ast.walk(parsed) if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load)}

    # เปลี่ยนชื่อฟังก์ชัน
    for func in funcs:
        newname = generate_random_name()
        while newname in used:
            newname = generate_random_name()
        used.add(newname)
        pairs[func.name] = newname

    # เปลี่ยนชื่อคลาส
    for _class in classes:
        newname = generate_random_name()
        while newname in used:
            newname = generate_random_name()
        used.add(newname)
        pairs[_class.name] = newname

    # เปลี่ยนชื่ออาร์กิวเมนต์
    for arg in args:
        newname = generate_random_name()
        while newname in used:
            newname = generate_random_name()
        used.add(newname)
        pairs[arg] = newname

    # แทนที่ชื่อเดิมในโค้ด
    for key, value in pairs.items():
        code = re.sub(r"\b" + re.escape(key) + r"\b", value, code)

    # แทนที่ชื่อที่เป็นสตริงในข้อความต่างๆ (เช่น ใน print หรือ ในลิสต์)
    for key, value in pairs.items():
        code = re.sub(r"(\b" + re.escape(key) + r"\b)", value, code)

    return code

def generate_random_name():
    """
    ฟังก์ชันสำหรับสุ่มชื่อใหม่ที่ประกอบด้วยตัวอักษร 'I' และ 'l' ขนาดระหว่าง 8 ถึง 20 ตัว
    """
    return "".join(random.choice(["I", "l"]) for _ in range(random.randint(8, 20)))

def remove_docs(source):
    """
    ลบ docstring และ comment ออกจากโค้ด Python
    โดยจะจัดการกับภาษาไทยใน docstring และคอมเมนต์ด้วย
    """
    try:
        # ใช้ ast เพื่อจัดการ docstring
        parsed = ast.parse(source)
        for node in ast.walk(parsed):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                node.body = [stmt for stmt in node.body if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Str)]
        source = ast.unparse(parsed)  # แปลงกลับเป็น source code

        # ลบ comment ด้วย regex (คอมเมนต์ภาษาไทยก็จะถูกลบ)
        source = re.sub(r"#.*", "", source)  # ลบ comment ทั้งบรรทัดที่เริ่มต้นด้วย #
        
        # จัดการ docstring ภาษาไทย (หากมีการใช้ข้อความภาษาไทยใน docstring)
        source = re.sub(r'"""(.*?)"""', '', source, flags=re.DOTALL)
        source = re.sub(r"'''(.*?)'''", '', source, flags=re.DOTALL)
        
        return source
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการลบ docstring: {e}")
        return source


def check_user_limit(guild_id, user_id):
    if not USER_LIMIT_ENABLED:
        return True

    log_file = f"logs/obf_{guild_id}.json"

    # อ่านข้อมูลจากไฟล์ JSON ถ้ามี
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            data = json.load(file)
    else:
        data = {}

    # หาก user_id ยังไม่มีในข้อมูลของ guild
    if str(user_id) not in data:
        data[str(user_id)] = {}

    # หาวันที่ปัจจุบัน
    today = datetime.today().strftime('%Y-%m-%d')

    # ตรวจสอบจำนวนครั้งในวันที่ปัจจุบัน
    if today in data[str(user_id)]:
        if data[str(user_id)][today] < USER_LIMIT_PER_DAY:
            data[str(user_id)][today] += 1  # เพิ่มจำนวนครั้งที่ใช้
        else:
            return False  # หากเกินจำนวนที่ตั้งไว้
    else:
        # หากไม่เคยใช้งานในวันนี้ให้เริ่มนับใหม่
        data[str(user_id)][today] = 0

    # บันทึกข้อมูลใหม่กลับลงไฟล์
    with open(log_file, "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return True


def get_user_usage_count(guild_id, user_id):
    log_file = f"logs/obf_{guild_id}.json"

    # อ่านข้อมูลจากไฟล์ JSON ถ้ามี
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            data = json.load(file)
    else:
        data = {}

    # หาก user_id ยังไม่มีในข้อมูลของ guild
    if str(user_id) not in data:
        return 0  # หากไม่มีข้อมูลการใช้งานของ user นี้

    # หาวันที่ปัจจุบัน
    today = datetime.today().strftime('%Y-%m-%d')

    # หากวันนี้มีการใช้งานของ user นี้
    if today in data[str(user_id)]:
        return data[str(user_id)][today]
    else:
        return 0  # หากยังไม่ได้ใช้บริการในวันนี้

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

    @discord.ui.button(label="เติมเงิน", style=discord.ButtonStyle.primary)
    async def gift_link_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # เปิด Modal สำหรับกรอก Gift Link
        await interaction.response.send_modal(GiftLinkModal(group_id=str(interaction.guild.id)))
    
    @discord.ui.button(label="แปลง", style=discord.ButtonStyle.primary)
    async def obfuscate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # เรียกใช้งาน ObfuscationModal โดยส่ง interaction
        await interaction.response.send_modal(ObfuscationModal(interaction))

    @discord.ui.button(label="แปลง VIP (4000 ตัวอักษร)", style=discord.ButtonStyle.success)
    async def obfuscate_vip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # เมื่อกดปุ่ม "แปลง VIP"
        await interaction.response.send_modal(ObfuscationVIPModal(interaction=interaction))

    @discord.ui.button(label="ตรวจสอบจำนวนครั้ง", style=discord.ButtonStyle.secondary)
    async def check_limit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ตรวจสอบจำนวนครั้งที่ใช้ไปแล้วในวันนี้
        user_id = interaction.user.id
        group_id = str(interaction.guild.id)

        # ใช้ฟังก์ชัน get_user_usage_count เพื่อดึงข้อมูลจำนวนครั้งที่ใช้ไปแล้วในวันนี้
        used_count = get_user_usage_count(group_id, user_id)

        if used_count >= 10:
            embed = discord.Embed(
                title="ข้อผิดพลาด",
                description="❌ คุณได้ใช้สิทธิ์การเข้ารหัสครบ 10 ครั้งในวันนี้แล้ว กรุณารอวันถัดไป",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="จำนวนครั้งที่ใช้",
                description=f"✅ คุณได้ใช้สิทธิ์การเข้ารหัสไปแล้ว {used_count} ครั้งในวันนี้.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

# Modal สำหรับการเข้ารหัสโค้ด Python
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
            embed = discord.Embed(
                title="ข้อผิดพลาด",
                description="❌ คุณได้ใช้สิทธิ์การเข้ารหัสครบ 10 ครั้งในวันนี้แล้ว กรุณารอวันถัดไป",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        code = self.code_input.value
        filename = self.filename_input.value

        # สร้างชื่อไฟล์ log
        log_filename = f"{filename}-obf"

        # เข้ารหัสโค้ด
        obfuscated_code = rename_code(code)

        # บันทึกโค้ดในโฟลเดอร์ logs
        log_file = await save_log(log_filename, obfuscated_code)

        # สร้าง embed สำหรับส่งข้อมูล
        embed = discord.Embed(
            title="โค้ดที่เข้ารหัสลับแล้ว",
            description=f"📂 ไฟล์โค้ดที่เข้ารหัสลับแล้วถูกบันทึกใน `{log_file}`",
            color=discord.Color.green()
        )
        embed.add_field(name="ชื่อไฟล์", value=f"`{log_filename}`", inline=False)
        embed.add_field(name="การเข้ารหัส", value="โค้ดได้ถูกเข้ารหัสลับเรียบร้อยแล้ว", inline=False)

        # ส่งไฟล์พร้อม embed
        await interaction.response.send_message(
            file=discord.File(log_file),
            embed=embed,
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
            embed = discord.Embed(
                title="ข้อผิดพลาด",
                description=f"❌ คุณมีเงินไม่เพียงพอในการทำรายการ (ยอดเงินคงเหลือ: {balance} บาท)",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        code = self.code_input.value
        filename = self.filename_input.value

        # สร้างชื่อไฟล์ใน logs
        log_filename = f"{filename}-obf-vip"

        # เข้ารหัสโค้ด
        obfuscated_code = rename_code(code)

        # บันทึกโค้ดในโฟลเดอร์ logs
        log_file = await save_log(log_filename, obfuscated_code)

        # สร้าง embed สำหรับส่งข้อมูล
        embed = discord.Embed(
            title="โค้ดที่เข้ารหัสลับแล้ว",
            description=f"📂 ไฟล์โค้ดที่เข้ารหัสลับแล้วถูกบันทึกใน `{log_file}`",
            color=discord.Color.green()
        )
        embed.add_field(name="ชื่อไฟล์", value=f"`{log_filename}`", inline=False)
        embed.add_field(name="การเข้ารหัส", value="โค้ดได้ถูกเข้ารหัสลับเรียบร้อยแล้ว", inline=False)

        # ส่งไฟล์พร้อม embed
        await interaction.response.send_message(
            file=discord.File(log_file),
            embed=embed,
            ephemeral=True
        )

        # ลบไฟล์หลังส่ง
        if os.path.exists(log_file):
            os.remove(log_file)

        # แจ้งยอดเงินคงเหลือ
        balance_embed = discord.Embed(
            title="ยอดเงินคงเหลือ",
            description=f"✅ ทำรายการสำเร็จ! ยอดเงินคงเหลือของคุณคือ {balance} บาท",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=balance_embed, ephemeral=True)

# เริ่มบอท
bot.run('YOUR_DISCORD_BOT_TOKEN')

