import discord
from discord.ext import commands
import pyfiglet

# สร้าง Bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# สร้าง FontMenuView สำหรับ Pagination
class FontMenuView(discord.ui.View):
    def __init__(self, fonts, ctx):
        super().__init__(timeout=60)
        self.fonts = fonts
        self.ctx = ctx
        self.current_page = 0
        self.per_page = 10
        self.total_pages = (len(self.fonts) - 1) // self.per_page + 1

        # เพิ่มปุ่มสำหรับเลื่อนหน้า
        self.prev_button = discord.ui.Button(label="ก่อนหน้า", style=discord.ButtonStyle.secondary, disabled=True)
        self.next_button = discord.ui.Button(label="ถัดไป", style=discord.ButtonStyle.secondary, disabled=self.total_pages <= 1)

        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    async def update_buttons(self):
        self.prev_button.disabled = self.current_page <= 0
        self.next_button.disabled = self.current_page >= self.total_pages - 1

    async def send_current_page(self):
        start_idx = self.current_page * self.per_page
        end_idx = start_idx + self.per_page
        fonts_on_page = self.fonts[start_idx:end_idx]
        embed = discord.Embed(
            title="รายชื่อฟอนต์ที่รองรับ",
            description="\n".join(f"`{font}`" for font in fonts_on_page),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"หน้า {self.current_page + 1}/{self.total_pages}")
        if hasattr(self, "message"):
            await self.message.edit(embed=embed, view=self)
        else:
            self.message = await self.ctx.send(embed=embed, view=self)

    async def prev_page(self, interaction: discord.Interaction):
        self.current_page -= 1
        await self.update_buttons()
        await self.send_current_page()

    async def next_page(self, interaction: discord.Interaction):
        self.current_page += 1
        await self.update_buttons()
        await self.send_current_page()

# Cog สำหรับการแปลงข้อความ
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
                font = discord.ui.TextInput(
                    label="ฟอนต์ (เช่น slant, standard)",
                    style=discord.TextStyle.short,
                    required=False,
                    placeholder="ค่าเริ่มต้นคือ standard"
                )

                async def on_submit(self, interaction: discord.Interaction):
                    font_name = self.font.value or "standard"
                    try:
                        ascii_art = pyfiglet.figlet_format(self.text.value, font=font_name)
                        await interaction.response.send_message(f"```\n{ascii_art}\n```", ephemeral=True)
                    except pyfiglet.FontNotFound:
                        await interaction.response.send_message("ฟอนต์ไม่ถูกต้อง กรุณาลองใหม่", ephemeral=True)

            modal = TextInputModal()
            await interaction.response.send_modal(modal)

        convert_button.callback = convert_callback
        view.add_item(convert_button)

        # ปุ่มสำหรับดูรายชื่อฟอนต์
        font_list_button = discord.ui.Button(label="ดูรายชื่อฟอนต์", style=discord.ButtonStyle.secondary)

        async def font_list_callback(interaction: discord.Interaction):
            fonts = pyfiglet.FigletFont.getFonts()
            view = FontMenuView(fonts, ctx)
            await view.send_current_page()

        font_list_button.callback = font_list_callback
        view.add_item(font_list_button)

        # ส่ง Embed พร้อม View
        await ctx.send(embed=embed, view=view)

# เพิ่ม Cog เข้า Bot
async def setup(bot):
    await bot.add_cog(ConvertCog(bot))




