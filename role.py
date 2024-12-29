import discord
from discord.ext import commands
from discord.ui import Button, View

# ตั้งค่าบอท
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

# คำสั่ง !รับยศ <role_id>
@client.command()
async def รับยศ(ctx, role_id: int):
    guild = ctx.guild
    role = guild.get_role(role_id)  # ค้นหายศจาก role_id ที่ผู้ใช้พิมพ์มา

    if not role:
        await ctx.send("❌ ไม่พบยศที่คุณต้องการ กรุณาตรวจสอบ ID ของยศ")
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

    # ส่ง Embed พร้อมปุ่มในห้องที่พิมพ์คำสั่ง
    await ctx.send(embed=embed, view=view)

# รันบอท
client.run("YOUR_BOT_TOKEN")