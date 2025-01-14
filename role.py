import discord
from discord.ext import commands
from discord.ui import Button, View

# กำหนด CONFIG สำหรับ ID ของยศ
CONFIG = {
    "role_id": 1322903274482962505  # แทนที่ด้วย ID ยศจริง
}

# ตั้งค่าบอท
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

# คำสั่ง !ยศ
@client.command()
async def ยศ(ctx):
    role_id = CONFIG.get("role_id")
    guild = ctx.guild
    role = guild.get_role(role_id)

    if not role:
        await ctx.send("❌ ไม่พบยศในเซิร์ฟเวอร์ กรุณาตรวจสอบการตั้งค่า")
        return

    # Embed
    embed = discord.Embed(
        title="รับยศ",
        description=f"กดปุ่มด้านล่างเพื่อรับยศ **{role.name}**",
        color=discord.Color.green()
    )

    # ปุ่มรับยศ
    button = Button(label="รับยศ", style=discord.ButtonStyle.primary)

    # ฟังก์ชันเมื่อกดปุ่ม
    async def button_callback(interaction):
        member = interaction.user
        if role in member.roles:
            await interaction.response.send_message(
                f"❌ คุณมียศ **{role.name}** อยู่แล้ว", ephemeral=True
            )
        else:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"✅ คุณได้รับยศ **{role.name}** เรียบร้อยแล้ว", ephemeral=True
            )

    button.callback = button_callback
    view = View()
    view.add_item(button)

    # ส่ง Embed พร้อมปุ่ม
    await ctx.send(embed=embed, view=view)

# รันบอท
client.run("YOUR_BOT_TOKEN")