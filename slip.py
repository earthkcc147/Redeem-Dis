import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, InputText
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# สร้างคำสั่ง !slip
@bot.command()
async def slip(ctx):
    # สร้าง Embed ที่จะส่ง
    embed = discord.Embed(title="สร้างสลีป", description="กรอกข้อมูลเพื่อสร้างสลีป", color=discord.Color.blue())
    embed.add_field(name="ข้อมูลการโอน", value="กรุณากดปุ่มเพื่อกรอกข้อมูล", inline=False)

    # สร้างปุ่มสำหรับเปิด modal
    button = Button(label="สร้างสลีป", style=discord.ButtonStyle.green)

    # สร้าง View และเพิ่มปุ่มเข้าไป
    view = View()
    view.add_item(button)

    # เมื่อปุ่มถูกกด, ให้แสดง modal
    async def button_callback(interaction):
        modal = Modal(title="กรอกข้อมูลสำหรับสร้างสลีป")
        modal.add_item(InputText(label="ชื่อผู้โอนจ่าย"))
        modal.add_item(InputText(label="ชื่อผู้รับเงิน"))
        modal.add_item(InputText(label="เบอร์โทรศัพท์ผู้รับ"))
        modal.add_item(InputText(label="จำนวนเงิน"))

        await interaction.response.send_modal(modal)

    button.callback = button_callback

    # ส่ง Embed พร้อมปุ่มไปที่ Discord
    await ctx.send(embed=embed, view=view)

# สร้างฟังก์ชันสำหรับสร้างสลีปเมื่อได้รับข้อมูลจาก modal
@bot.event
async def on_modal_submit(modal, interaction):
    name_user_id = modal.children[0].value
    name_me_id = modal.children[1].value
    phone_me_id = modal.children[2].value
    money_id = modal.children[3].value

    # เวลาในประเทศไทย
    thailand_timezone = pytz.timezone('Asia/Bangkok')
    current_time_thailand = datetime.now(thailand_timezone)
    time = current_time_thailand.strftime("%H:%M:%S")
    day = current_time_thailand.strftime("%d")
    month = current_time_thailand.strftime("%m")
    year = current_time_thailand.strftime("%Y")

    # โหลดภาพพื้นหลัง
    image = Image.open("Bank/K-bank 4.png")
    draw = ImageDraw.Draw(image)

    # กำหนดฟอนต์
    font_size_money = 87
    font_size_user = 48
    font_size_me = 48
    font_size_phone = 40
    font_size_time = 37
    font_size_order = 37
    font_path_money = "Font/PSL158.ttf"
    font_path_user = "Font/PSL159.ttf"
    font_path_phone = "Font/PSL160.ttf"

    font_money = ImageFont.truetype(font_path_money, font_size_money)
    font_user = ImageFont.truetype(font_path_user, font_size_user)
    font_me = ImageFont.truetype(font_path_user, font_size_me)
    font_phone = ImageFont.truetype(font_path_phone, font_size_phone)
    font_time = ImageFont.truetype(font_path_user, font_size_time)
    font_order = ImageFont.truetype(font_path_user, font_size_order)

    # เตรียมข้อความที่จะใส่ลงไปในภาพ
    phone = phone_me_id
    text_money = money_id + ".00"
    text_name_user = name_user_id
    text_name_me = name_me_id
    text_name_phone = f"{phone[:3]}-xxx-{phone[6:]}"
    text_name_time = f"  {day}/{month}/{year} {time}"
    text_name_order = "50018935012188"

    # กำหนดตำแหน่งของข้อความในภาพ
    text_position_money = (560, 270)
    text_position_user = (302, 485)
    text_position_me = (302, 648)
    text_position_phone = (302, 720)
    text_position_time = (781, 885)
    text_position_order = (827, 953)

    # กำหนดสีของข้อความ
    text_color_money = (44, 44, 44)
    text_color_user = (-20, -20, -20)
    text_color_me = (-20, -20, -20)
    text_color_phone = (80, 80, 80)
    text_color_time = (60, 60, 60)
    text_color_order = (60, 60, 60)

    # ใส่ข้อความลงในภาพ
    draw.text(text_position_money, text_money, font=font_money, fill=text_color_money)
    draw.text(text_position_user, text_name_user, font=font_user, fill=text_color_user)
    draw.text(text_position_me, text_name_me, font=font_me, fill=text_color_me)
    draw.text(text_position_phone, text_name_phone, font=font_phone, fill=text_color_phone)
    draw.text(text_position_time, text_name_time, font=font_time, fill=text_color_time)
    draw.text(text_position_order, text_name_order, font=font_order, fill=text_color_order)

    # เพิ่มโลโก้ลงในภาพ
    logo_image = "Bank/K-bank.png"
    logo_size = (130, 130)
    logo_position = (45, 540)

    # โหลดโลโก้ที่มีพื้นหลังโปร่งใส
    logo = Image.open(logo_image)
    logo = logo.resize(logo_size)

    # วางโลโก้บนภาพ
    image.paste(logo, logo_position, logo)  # ใช้โลโก้เป็น Mask เพื่อให้พื้นหลังโปร่งใส

    # บันทึกภาพที่มีข้อความและโลโก้
    image.save("truemoney_with_text_and_logo.png")

    # ส่งภาพกลับไปยัง Discord
    await interaction.response.send_message("สลีปปลอมสำเร็จ!", file=discord.File("truemoney_with_text_and_logo.png"))

# เริ่มบอท
bot.run('YOUR_BOT_TOKEN')