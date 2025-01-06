#. OK จำนวน -1 ต่อครัง ฟรี10/วัน
# รอเพอ่มปถ่มกดเติมเงิน

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








# ฟังก์ชันเพื่ออ่านข้อมูลจากไฟล์ JSON สำหรับยอดเงิน
def load_data_balance(group_id):
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

# ฟังก์ชันเพื่อบันทึกข้อมูลลงในไฟล์ JSON สำหรับยอดเงิน
def save_data_balance(data, group_id):
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
        self.gift_link = discord.ui.TextInput(label="Gift Link", placeholder="ใส่ลิ้งซองของขวัญที่นี่", required=True)
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

            # อัพเดตจำนวน normal_count ของผู้ใช้
            user_id = str(interaction.user.id)  # ใช้ user id ของ Discord เป็น key
            amount = float(result['amount'])
            normal_count_increment = int(amount // 10)  # เพิ่ม 1 normal_count ต่อการเติมเงิน 10 บาท

            usage_data = load_usage_data(self.group_id)

            if user_id not in usage_data:
                usage_data[user_id] = {"free_count": 3, "normal_count": 0, "last_used": ""}

            usage_data[user_id]["normal_count"] += normal_count_increment  # เพิ่มจำนวน normal_count
            save_usage_data(self.group_id, usage_data)  # บันทึกข้อมูลจำนวนครั้งที่สามารถกดได้

            # ส่งข้อความไปยังช่องที่ต้องการ
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(
                    f"เติมเงินสำเร็จจาก {interaction.user.name}!\n"
                    f"จำนวนเงิน: {result['amount']} บาท\n"
                    f"เบอร์รับเงิน: {result['phone']}\n"
                    f"ลิ้งซองของขวัญ: {result['gift_link']}\n"
                    f"เวลาทำรายการ: {result['time']}\n"
                    f"จำนวน normal_count ที่ได้รับ: {normal_count_increment} ครั้ง"
                )
        else:
            message = f"ผิดพลาด: {result['message']}"

        # ส่งข้อความตอบกลับในช่องที่กดคำสั่ง
        await interaction.response.send_message(message, ephemeral=True)










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
    else:
        # ถ้าไม่พบไฟล์ ให้สร้างไฟล์ใหม่พร้อมข้อมูลเริ่มต้น
        usage_data = {}
        save_usage_data(group_id, usage_data)
        return usage_data

# ฟังก์ชันสำหรับบันทึกข้อมูลจำนวนครั้งที่สามารถกดได้
def save_usage_data(group_id, data):
    file_path = f"logs/obf_{group_id}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


# ฟังก์ชันสำหรับตรวจสอบการใช้งานในวันนี้และจำนวนครั้งที่เหลือ
def can_use_today(usage_data, user_id, group_id, is_free=False):
    today = datetime.today().strftime('%Y-%m-%d')
    if user_id not in usage_data:
        # ถ้าผู้ใช้ไม่เคยใช้งาน ให้ตั้งค่าเริ่มต้น
        usage_data[user_id] = {"free_count": free_obfuscate_limit, "normal_count": 0, "last_used": ""}
    
    # หากต้องการรีเซ็ตการใช้งานแปลงฟรี
    if is_free and usage_data[user_id]['last_used'] != today:
        usage_data[user_id]['free_count'] = free_obfuscate_limit  # รีเซ็ตจำนวนแปลงฟรี
        usage_data[user_id]['last_used'] = today
        save_usage_data(group_id, usage_data)

    if is_free:
        if usage_data[user_id]['free_count'] > 0:
            return True  # สามารถใช้งานแปลงฟรีได้
    else:
        if usage_data[user_id]['normal_count'] > 0:  # แปลงปกติไม่จำกัด
            return True

    return False


@bot.command()
async def obf(ctx):
    embed = discord.Embed(title="เข้ารหัสโค้ด Python", description="กรุณากรอกโค้ด Python ที่คุณต้องการเข้ารหัสลับ", color=0x00FF00)
    await ctx.send(embed=embed, view=ObfuscationView(ctx))

class ObfuscationView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="เติมเงิน", style=discord.ButtonStyle.primary)
    async def gift_link_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        load_usage_data(str(interaction.guild.id))  # จะทำให้โฟลเดอร์และไฟล์ถูกสร้างขึ้นถ้ายังไม่มี
        
        # เปิด Modal สำหรับกรอก Gift Link
        await interaction.response.send_modal(GiftLinkModal(group_id=str(interaction.guild.id)))

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

        if can_use_today(usage_data, user_id, group_id, is_free=True):  # ส่ง is_free=True สำหรับแปลงฟรี
            usage_data[user_id]['free_count'] -= 1  # ลดจำนวนการใช้งานแปลงฟรี
            save_usage_data(group_id, usage_data)

            code = self.code_input.value
            filename = self.filename_input.value

            # เข้ารหัสโค้ด
            obfuscated_code = rename_code(code)

            log_filename = f"{filename}-obf"
            log_file = await save_log(log_filename, obfuscated_code)

            await interaction.response.send_message(
                file=discord.File(log_file),
                content=f"📂 ไฟล์โค้ดที่เข้ารหัสลับแล้วถูกบันทึกใน `{log_file}`",
                ephemeral=True
            )

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
        usage_data = load_usage_data(self.group_id)

        # ตรวจสอบการใช้งานแปลงปกติ
        if usage_data.get(self.user_id, {}).get('normal_count', 0) > 0:  # ตรวจสอบว่า normal_count มากกว่า 0
            if can_use_today(usage_data, self.user_id, self.group_id, is_free=False):
                usage_data[self.user_id]['normal_count'] -= 1  # ลดจำนวนการใช้งานแปลงปกติ
                save_usage_data(self.group_id, usage_data)

                code = self.code_input.value
                filename = self.filename_input.value
                obfuscated_code = rename_code(code)

                log_filename = f"{filename}-obf"
                log_file = await save_log(log_filename, obfuscated_code)

                await interaction.response.send_message(
                    file=discord.File(log_file),
                    content=f"📂 ไฟล์โค้ดที่เข้ารหัสลับแล้วถูกบันทึกใน `{log_file}`",
                    ephemeral=True
                )

                if os.path.exists(log_file):
                    os.remove(log_file)
            else:
                await interaction.response.send_message(
                    "คุณไม่สามารถแปลงโค้ดได้แล้ว เนื่องจากคุณหมดจำนวนครั้งที่สามารถใช้งานได้",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "คุณไม่สามารถแปลงโค้ดได้ เนื่องจากจำนวนการใช้งานแปลงปกติของคุณหมดแล้ว",
                ephemeral=True
            )


# เริ่มบอท
bot.run('YOUR_DISCORD_BOT_TOKEN')