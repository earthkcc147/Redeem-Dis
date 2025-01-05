import discord
from discord.ext import commands
import random
import re
import ast
import os

# ฟังก์ชันสำหรับเข้ารหัสโค้ด
def rename_code(code):
    # ฟังก์ชันเข้ารหัสโค้ด
    pairs = {}
    used = set()
    code = remove_docs(code)  # ลบ comment และ docstring
    parsed = ast.parse(code)

    funcs = {node for node in ast.walk(parsed) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    classes = {node for node in ast.walk(parsed) if isinstance(node, ast.ClassDef)}
    args = {node.id for node in ast.walk(parsed) if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load)}

    # สร้างชื่อใหม่แบบสุ่มสำหรับฟังก์ชัน, คลาส และตัวแปร
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

    # ทำการแปลงโค้ด
    for key, value in pairs.items():
        code = re.sub(r"\b" + re.escape(key) + r"\b", value, code)

    return code

def remove_docs(source):
    # ฟังก์ชันลบ comment และ docstring
    out = ""
    for line in source.splitlines():
        if not line.strip().startswith("#"):
            out += line + "\n"
    return out

class Obfuscation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def obf(self, ctx):
        embed = discord.Embed(title="เข้ารหัสโค้ด Python", description="กรุณากรอกโค้ด Python ที่คุณต้องการเข้ารหัสลับ", color=0x00FF00)
        await ctx.send(embed=embed, view=ObfuscationView())

class ObfuscationView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="แปลง", style=discord.ButtonStyle.primary)
    async def obfuscate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ObfuscationModal())

class ObfuscationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="กรุณากรอกโค้ด Python")

    code_input = discord.ui.TextInput(label="โค้ด Python", style=discord.TextStyle.paragraph, placeholder="กรอกโค้ดที่ต้องการเข้ารหัส", required=True, max_length=4000)
    filename_input = discord.ui.TextInput(label="ชื่อไฟล์", placeholder="กรุณากรอกชื่อไฟล์ (ไม่ต้องใส่นามสกุล)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        code = self.code_input.value
        filename = self.filename_input.value

        # ปรับชื่อไฟล์
        filename = f"{filename}-obf.py"

        # เข้ารหัสโค้ด
        obfuscated_code = rename_code(code)

        # สร้างไฟล์ที่เข้ารหัสแล้ว
        with open(filename, "w") as file:
            file.write(obfuscated_code)

        # ส่งไฟล์ให้ผู้ใช้
        await interaction.response.send_message(file=discord.File(filename), content="ไฟล์โค้ดที่เข้ารหัสลับแล้ว:", ephemeral=True)

        # ลบไฟล์หลังส่ง
        os.remove(filename)

# เพิ่ม Cog นี้ไปยังบอท
async def setup(bot):
    await bot.add_cog(Obfuscation(bot))