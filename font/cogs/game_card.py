import discord
from discord.ext import commands
import random

# รางวัลและเปอร์เซ็นต์ (กำหนดในรูปแบบ Dictionary)
PRIZES = {
    "รางวัลที่ 1: 1000 Coins": 10,   # 10%
    "รางวัลที่ 2: 500 Coins": 15,    # 15%
    "รางวัลที่ 3: 100 Coins": 20,    # 20%
    "รางวัลพิเศษ: 1 Spin เพิ่ม": 70, # 70%
    "ไม่มีรางวัล": 80,               # 80%
    "รางวัลที่ 4: 50 Coins": 30,     # 30%
    "รางวัลที่ 5: 20 Coins": 40,     # 40%
    "รางวัลใหญ่: 5000 Coins": 2,    # 2%
    "รางวัลเล็ก: 10 Coins": 50,     # 50%
    "รางวัลพิเศษสุด: 10000 Coins": 1 # 1%
}

# ฟังก์ชันสำหรับสุ่มรางวัล
def get_random_prize():
    return random.choices(list(PRIZES.keys()), weights=list(PRIZES.values()), k=1)[0]

# สร้าง View สำหรับปุ่ม
class CardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # ไม่มีการหมดอายุ

        # เพิ่มปุ่ม 10 ปุ่ม
        for i in range(1, 11):
            self.add_item(CardButton(label=str(i), custom_id=f"button_{i}"))

class CardButton(discord.ui.Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        try:
            # สุ่มรางวัล
            prize = get_random_prize()

            # ตอบกลับเมื่อกดปุ่ม
            await interaction.response.send_message(f"คุณได้รับ: **{prize}**", ephemeral=True)

        except discord.errors.NotFound:
            # ถ้าเกิดข้อผิดพลาดที่เกี่ยวข้องกับ Interaction ที่ไม่พบ
            await interaction.followup.send("เกิดข้อผิดพลาดในการตอบกลับ! กรุณาลองใหม่.", ephemeral=True)

class CardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="card")
    async def card(self, ctx):
        embed = discord.Embed(
            title="สุ่มรางวัล!",
            description="กดปุ่มด้านล่างเพื่อสุ่มรางวัลของคุณ!",
            color=discord.Color.gold()
        )
        embed.set_footer(text="คุณสามารถกดปุ่มได้ตลอดเวลา!")
        
        view = CardView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(CardCog(bot))