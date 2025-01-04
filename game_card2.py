@bot.command(name="card")
async def card(ctx):
    group_id = str(ctx.guild.id)  # ใช้ ID ของกลุ่มที่
    user_id = str(ctx.author.id)  # ใช้ ID ของผู้ใช้

    # สร้างมุมมองของบัตร
    view = CardView(group_id, user_id)

    # ส่งข้อความและแสดงปุ่ม
    await ctx.send(
        "เลือกหมายเลขที่คุณต้องการสุ่มรางวัล!",
        view=view
    )

# เริ่มต้นบอท
@bot.event
async def on_ready():
    print(f"Bot is logged in as {bot.user}")

# เริ่มต้นการใช้งานบอท
bot.run("YOUR_BOT_TOKEN")


