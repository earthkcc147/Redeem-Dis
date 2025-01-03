import discord
from discord.ext import commands
from discord.ext.menus import ListPageSource, MenuPages
import pyfiglet

# สร้าง Bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# สร้าง FontMenu
class FontMenu(ListPageSource):
    def __init__(self, fonts):
        super().__init__(fonts, per_page=10)

    async def format_page(self, menu, fonts):
        embed = discord.Embed(
            title="รายชื่อฟอนต์ที่รองรับ",
            description="\n".join(f"`{font}`" for font in fonts),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"หน้า {menu.current_page + 1}/{self.get_max_pages()}")
        return embed

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
            menu = MenuPages(source=FontMenu(fonts), clear_reactions_after=True)
            await menu.start(ctx)

        font_list_button.callback = font_list_callback
        view.add_item(font_list_button)

        # ส่ง Embed พร้อม View
        await ctx.send(embed=embed, view=view)

# เพิ่ม Cog เข้า Bot
async def setup(bot):
    await bot.add_cog(ConvertCog(bot))

# รันบอท
bot.run("YOUR_BOT_TOKEN")