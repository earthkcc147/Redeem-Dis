import discord
from discord.ext import commands
import pyfiglet

class ConvertCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="แปลง")
    async def convert(self, ctx):
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

# ฟังก์ชันสำหรับเพิ่ม Cog
async def setup(bot):
    await bot.add_cog(ConvertCog(bot))