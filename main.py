import discord
from discord.ui import Button, View, Modal, TextInput
import requests
import json
import os

TOKEN = 'MTE5MjA0MTI2MTA1NDU3MDUyNg.GmR8Zy.kE1mTrYzUk4Fddkj4R0dKHKfHS-Gf8aEDa0bw0'  # ใส่โทเค็นบอทของคุณที่นี่
channel_id = 1315866248227065957  # ใส่ ID ช่องที่ต้องการส่งข้อความไป

# กำหนดแอดมินที่สามารถเห็นปุ่ม "ดูประวัติการทำรายการ"
ADMIN_IDS = [486994554390577173, 987654321098765432]  # ใส่ ID ของแอดมินที่ต้องการ

intents = discord.Intents.default()
intents.message_content = True

# สร้าง client ของ Discord
client = discord.Client(intents=intents)

# ตัวแปรควบคุมการเชื่อมต่อห้องเสียง (True = เปิด, False = ปิด)
ENABLE_VOICE_CHANNEL = False  # เปลี่ยนเป็น False เพื่อปิดการเชื่อมต่อห้องเสียง

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    if ENABLE_VOICE_CHANNEL:
        # วนลูปผ่านทุก guild ที่บอทเป็นสมาชิก
        for guild in client.guilds:
            # ค้นหาห้องเสียงที่ต้องการในแต่ละ guild
            voice_channel = discord.utils.get(guild.voice_channels, name="botonline")  # แทนที่ชื่อห้องเสียงที่ต้องการ

            # ถ้าห้องเสียงมีอยู่ ให้บอทเข้าห้องเสียงนั้น
            if voice_channel:
                await voice_channel.connect()
                print(f"Connected to voice channel: {voice_channel.name} in guild: {guild.name}")
            else:
                print(f"ไม่พบห้องเสียงที่กำหนดใน guild: {guild.name}")
    else:
        print("Voice channel connection is disabled.")



# ฟังก์ชันเพื่ออ่านข้อมูลจากไฟล์ JSON
def load_data(group_id):
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

# ฟังก์ชันเพื่อบันทึกข้อมูลลงในไฟล์ JSON
def save_data(data, group_id):
    folder_path = "topup"
    # ตรวจสอบว่าโฟลเดอร์ topup มีอยู่หรือไม่ ถ้าไม่ให้สร้าง
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    data_file = os.path.join(folder_path, f"{group_id}.json")  # ตั้งชื่อไฟล์ตาม ID ของกลุ่ม
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



class GiftLinkModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="กรอกลิ้งซองของขวัญ")
        self.group_id = group_id
        self.gift_link = TextInput(label="Gift Link", placeholder="ใส่ลิ้งซองของขวัญที่นี่", required=True)
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

            # อ่านข้อมูลสมาชิกจากไฟล์
            user_data = load_data(self.group_id)
            user_id = str(interaction.user.id)  # ใช้ user id ของ Discord เป็น key

            # ถ้าผู้ใช้ไม่เคยมีข้อมูลในไฟล์ ให้สร้างข้อมูลใหม่
            if user_id not in user_data:
                user_data[user_id] = {"balance": 0.0, "history": []}

            # อัพเดตยอดเงินของผู้ใช้
            user_data[user_id]["balance"] += float(result['amount'])

            # บันทึกประวัติการทำรายการ
            transaction = {
                "amount": result['amount'],
                "gift_link": result['gift_link'],
                "time": result['time'],
                "status": result['status'],
                "phone": result['phone']
            }
            user_data[user_id]["history"].append(transaction)

            # บันทึกข้อมูลลงไฟล์
            save_data(user_data, self.group_id)

            # ส่งข้อความไปยังช่องที่ต้องการ
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(
                    f"เติมเงินสำเร็จจาก {interaction.user.name}!\n"
                    f"จำนวนเงิน: {result['amount']} บาท\n"
                    f"เบอร์รับเงิน: {result['phone']}\n"
                    f"ลิ้งซองของขวัญ: {result['gift_link']}\n"
                    f"เวลาทำรายการ: {result['time']}\n"
                    f"ยอดเงินรวมของ {interaction.user.name}: {user_data[user_id]['balance']} บาท"
                )
        else:
            message = f"ผิดพลาด: {result['message']}"

        # ส่งข้อความตอบกลับในช่องที่กดคำสั่ง
        await interaction.response.send_message(message, ephemeral=True)


class CheckBalanceButton(Button):
    def __init__(self, group_id):
        super().__init__(label="เช็คยอดเงิน", style=discord.ButtonStyle.blurple)
        self.group_id = group_id

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)  # ใช้ user id ของ Discord เป็น key
        user_data = load_data(self.group_id)

        if user_id in user_data:
            balance = user_data[user_id]["balance"]
            await interaction.response.send_message(f"ยอดเงินของคุณ: {balance} บาท", ephemeral=True)
        else:
            await interaction.response.send_message(
                "คุณยังไม่ได้เติมเงินหรือไม่มีข้อมูลในระบบ", 
                ephemeral=True
            )

class CheckHistoryButton(Button):
    def __init__(self, phone_number):
        super().__init__(label="ดูประวัติการทำรายการ", style=discord.ButtonStyle.green)
        self.phone_number = phone_number

    async def callback(self, interaction: discord.Interaction):
        # ตรวจสอบว่าเป็นแอดมินก่อน
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message("คุณไม่มีสิทธิ์ในการดูประวัติการทำรายการ", ephemeral=True)
            return

        api_url = f"https://byshop.me/api/history_truewallet?phone={self.phone_number}"
        response = requests.get(api_url)
        history = response.json()

        if isinstance(history, list) and history:
            history_message = "ประวัติการทำรายการ:\n"
            for item in history:
                history_message += f"ID: {item['id']}\n"
                history_message += f"เบอร์: {item['phone']}\n"
                history_message += f"ลิ้งซองของขวัญ: {item['gift_link']}\n"
                history_message += f"จำนวนเงิน: {item['amount']} บาท\n"
                history_message += f"สถานะ: {item['status']}\n"
                history_message += f"เวลาทำรายการ: {item['time']}\n\n"
            await interaction.response.send_message(history_message, ephemeral=True)
        else:
            await interaction.response.send_message("ไม่มีประวัติการทำรายการ", ephemeral=True)


class RedeemCodeModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="แลกโค้ดรับเงิน")
        self.group_id = group_id
        self.redeem_key = TextInput(label="Redeem Key", placeholder="ใส่โค้ดที่นี่", required=True)
        self.add_item(self.redeem_key)

    async def on_submit(self, interaction: discord.Interaction):
        redeem_key = self.redeem_key.value
        keys_file = "keys.json"  # ชื่อไฟล์ที่เก็บคีย์และยอดเงิน

        # ตรวจสอบว่าไฟล์ keys.json มีอยู่หรือไม่
        if not os.path.exists(keys_file):
            await interaction.response.send_message("ไม่มีข้อมูลโค้ดในระบบ", ephemeral=True)
            return

        # โหลดข้อมูลจาก keys.json
        with open(keys_file, 'r', encoding='utf-8') as f:
            keys_data = json.load(f)

        # ตรวจสอบว่าคีย์ที่ป้อนถูกต้องหรือไม่
        if redeem_key in keys_data:
            key_info = keys_data[redeem_key]

            # ตรวจสอบจำนวนคีย์ที่เหลือ
            if key_info["remaining"] <= 0:
                await interaction.response.send_message("คีย์นี้หมดอายุหรือไม่มีคีย์เหลือแล้ว", ephemeral=True)
                return

            amount = key_info["amount"]

            # อ่านข้อมูลสมาชิกจากไฟล์
            user_data = load_data(self.group_id)
            user_id = str(interaction.user.id)  # ใช้ user id ของ Discord เป็น key

            # ถ้าผู้ใช้ไม่เคยมีข้อมูลในไฟล์ ให้สร้างข้อมูลใหม่
            if user_id not in user_data:
                user_data[user_id] = {"balance": 0.0, "history": []}

            # อัปเดตยอดเงินของผู้ใช้
            user_data[user_id]["balance"] += float(amount)

            # บันทึกประวัติการทำรายการ
            transaction = {
                "amount": amount,
                "redeem_key": redeem_key,
                "time": interaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "success"
            }
            user_data[user_id]["history"].append(transaction)

            # ลดจำนวนคีย์ที่เหลือ
            keys_data[redeem_key]["remaining"] -= 1

            # บันทึกข้อมูลลงไฟล์
            save_data(user_data, self.group_id)

            # บันทึกการเปลี่ยนแปลงจำนวนคีย์ที่เหลือ
            with open(keys_file, 'w', encoding='utf-8') as f:
                json.dump(keys_data, f, ensure_ascii=False, indent=4)

            await interaction.response.send_message(
                f"แลกโค้ดสำเร็จ! คุณได้รับ {amount} บาท\nยอดเงินคงเหลือของคุณ: {user_data[user_id]['balance']} บาท",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("โค้ดที่คุณป้อนไม่ถูกต้องหรือหมดอายุแล้ว", ephemeral=True)

# ปุ่มแลกโค้ด
class RedeemCodeButton(Button):
    def __init__(self, group_id):
        super().__init__(label="กดแลกโค้ด", style=discord.ButtonStyle.primary)
        self.group_id = group_id

    async def callback(self, interaction: discord.Interaction):
        modal = RedeemCodeModal(self.group_id)
        await interaction.response.send_modal(modal)


class AddKeyModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="เพิ่มโค้ด")
        self.group_id = group_id
        self.redeem_key = TextInput(label="Redeem Key", placeholder="ใส่โค้ดที่นี่", required=True)
        self.amount = TextInput(label="จำนวนเงิน", placeholder="จำนวนเงินที่ต้องการเพิ่ม", required=True)
        self.remaining = TextInput(label="จำนวนคีย์ที่เหลือ", placeholder="จำนวนคีย์ที่เหลือ", required=True)
        self.add_item(self.redeem_key)
        self.add_item(self.amount)
        self.add_item(self.remaining)

    async def on_submit(self, interaction: discord.Interaction):
        redeem_key = self.redeem_key.value
        amount = self.amount.value
        remaining = self.remaining.value
        folder_path = "Topup"
        keys_file = os.path.join(folder_path, "keys.json")

        # ตรวจสอบว่าโฟลเดอร์ Topup มีอยู่หรือไม่
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)  # สร้างโฟลเดอร์หากยังไม่มี

        # ตรวจสอบว่าไฟล์ keys.json มีอยู่หรือไม่
        if not os.path.exists(keys_file):
            # ถ้าไฟล์ยังไม่มี ให้สร้างไฟล์ใหม่และเริ่มต้นข้อมูลเป็น dictionary ว่าง
            keys_data = {}
            with open(keys_file, 'w', encoding='utf-8') as f:
                json.dump(keys_data, f, ensure_ascii=False, indent=4)

        # โหลดข้อมูลจาก keys.json
        with open(keys_file, 'r', encoding='utf-8') as f:
            keys_data = json.load(f)

        # ตรวจสอบว่าโค้ดนี้มีอยู่แล้วหรือไม่
        if redeem_key in keys_data:
            await interaction.response.send_message("โค้ดนี้มีอยู่แล้วในระบบ", ephemeral=True)
            return

        # เพิ่มข้อมูลโค้ดใหม่
        keys_data[redeem_key] = {
            "amount": float(amount),
            "remaining": int(remaining)
        }

        # บันทึกข้อมูลลงไฟล์
        with open(keys_file, 'w', encoding='utf-8') as f:
            json.dump(keys_data, f, ensure_ascii=False, indent=4)

        await interaction.response.send_message(f"เพิ่มโค้ดสำเร็จ! โค้ด: {redeem_key}, จำนวนเงิน: {amount} บาท, จำนวนคีย์ที่เหลือ: {remaining}", ephemeral=True)


class AddKeyButton(Button):
    def __init__(self, group_id):
        super().__init__(label="เพิ่มคีย์", style=discord.ButtonStyle.primary)
        self.group_id = group_id

    async def callback(self, interaction: discord.Interaction):
        # ตรวจสอบว่า ID ของผู้ใช้ที่กดปุ่มมีอยู่ใน ADMIN_IDS หรือไม่
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message("คุณไม่มีสิทธิ์เข้าถึงฟังก์ชันนี้", ephemeral=True)
            return

        modal = AddKeyModal(self.group_id)
        await interaction.response.send_modal(modal)


class ShowKeysButton(Button):
    def __init__(self, group_id):
        super().__init__(label="แสดงคีย์ทั้งหมด", style=discord.ButtonStyle.primary)
        self.group_id = group_id

    async def callback(self, interaction: discord.Interaction):
        # ตรวจสอบว่า ID ของผู้ใช้เป็นแอดมินหรือไม่
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message("คุณไม่มีสิทธิ์ใช้งานปุ่มนี้", ephemeral=True)
            return

        folder_path = "Topup"
        keys_file = os.path.join(folder_path, "keys.json")

        # ตรวจสอบว่าไฟล์ keys.json มีอยู่หรือไม่
        if not os.path.exists(keys_file):
            await interaction.response.send_message("ไม่มีข้อมูลคีย์ในระบบ", ephemeral=True)
            return

        # โหลดข้อมูลจาก keys.json
        with open(keys_file, 'r', encoding='utf-8') as f:
            keys_data = json.load(f)

        # ตรวจสอบว่าไฟล์มีข้อมูลหรือไม่
        if not keys_data:
            await interaction.response.send_message("ไม่มีคีย์ในระบบ", ephemeral=True)
            return

        # สร้างข้อความเพื่อแสดงคีย์ทั้งหมด
        keys_list = "\n".join([
            f"โค้ด: {key}, จำนวนเงิน: {data['amount']} บาท, คีย์ที่เหลือ: {data['remaining']}" 
            for key, data in keys_data.items()
        ])

        # ส่งข้อความแสดงคีย์ทั้งหมด
        await interaction.response.send_message(f"คีย์ทั้งหมดในระบบ:\n{keys_list}", ephemeral=True)


class DeleteKeyModal(Modal):
    def __init__(self, group_id):
        super().__init__(title="ลบโค้ด")
        self.group_id = group_id
        self.redeem_key = TextInput(label="Redeem Key", placeholder="ใส่โค้ดที่ต้องการลบ", required=True)
        self.add_item(self.redeem_key)

    async def on_submit(self, interaction: discord.Interaction):
        redeem_key = self.redeem_key.value
        folder_path = "Topup"
        keys_file = os.path.join(folder_path, "keys.json")

        # ตรวจสอบว่าโฟลเดอร์ Topup มีอยู่หรือไม่ ถ้าไม่มีให้สร้าง
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # ตรวจสอบว่าไฟล์ keys.json มีอยู่หรือไม่
        if not os.path.exists(keys_file):
            await interaction.response.send_message("ไม่มีข้อมูลคีย์ในระบบ", ephemeral=True)
            return

        # โหลดข้อมูลจาก keys.json
        with open(keys_file, 'r', encoding='utf-8') as f:
            keys_data = json.load(f)

        # ตรวจสอบว่าโค้ดนี้มีอยู่หรือไม่
        if redeem_key not in keys_data:
            await interaction.response.send_message("ไม่พบโค้ดนี้ในระบบ", ephemeral=True)
            return

        # ลบคีย์ออกจากระบบ
        del keys_data[redeem_key]

        # บันทึกข้อมูลลงไฟล์
        with open(keys_file, 'w', encoding='utf-8') as f:
            json.dump(keys_data, f, ensure_ascii=False, indent=4)

        await interaction.response.send_message(f"ลบโค้ดสำเร็จ! โค้ด: {redeem_key}", ephemeral=True)


class DeleteKeyButton(Button):
    def __init__(self, group_id):
        super().__init__(label="ลบคีย์", style=discord.ButtonStyle.danger)
        self.group_id = group_id

    async def callback(self, interaction: discord.Interaction):
        # ตรวจสอบว่า ID ของผู้ใช้ที่กดปุ่มมีอยู่ใน ADMIN_IDS หรือไม่
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message("คุณไม่มีสิทธิ์เข้าถึงฟังก์ชันนี้", ephemeral=True)
            return

        modal = DeleteKeyModal(self.group_id)
        await interaction.response.send_modal(modal)


class RegisterButton(Button):
    def __init__(self, group_id):
        super().__init__(label="ลงทะเบียน", style=discord.ButtonStyle.green)
        self.group_id = group_id

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)  # ใช้ user id ของ Discord เป็น key
        user_data = load_data(self.group_id)

        # ตรวจสอบว่าผู้ใช้มีข้อมูลในไฟล์หรือไม่
        if user_id in user_data:
            await interaction.response.send_message("คุณได้ลงทะเบียนแล้ว!", ephemeral=True)
        else:
            # ถ้ายังไม่มีข้อมูล ให้ลงทะเบียนผู้ใช้ใหม่
            user_data[user_id] = {"balance": 0.0, "history": []}  # เพิ่มข้อมูลผู้ใช้ใหม่
            save_data(user_data, self.group_id)  # บันทึกข้อมูลลงในไฟล์
            await interaction.response.send_message("ลงทะเบียนสำเร็จ! คุณสามารถเริ่มใช้งานได้แล้ว.", ephemeral=True)


class AdminPanelButton(Button):
    def __init__(self):
        super().__init__(label="Admin Panel", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        # ตรวจสอบว่าเป็นแอดมินหรือไม่
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message("คุณไม่มีสิทธิ์เข้าถึง Admin Panel นี้", ephemeral=True)
            return

        # สร้างปุ่มที่ใช้ใน Admin Panel
        admin_view = View()

        # เพิ่มปุ่มเฉพาะของแอดมิน เช่น ปุ่มแสดงคีย์ทั้งหมด

        check_history_button = CheckHistoryButton(phone_number="0841304874")  # เปลี่ยนเบอร์ตามต้องการ
        show_keys_button = ShowKeysButton(group_id=None)  # ปุ่มใหม่เพื่อแสดงคีย์ทั้งหมด
        add_key_button = AddKeyButton(group_id=None)  # เพิ่มปุ่มเพิ่มคีย์
        delete_key_button = DeleteKeyButton(group_id=None)  # ปุ่มใหม่เพื่อให้แอดมินลบคีย์

        admin_view.add_item(check_history_button) # เพิ่มปุ่มตรวจสอบประวัติ
        admin_view.add_item(show_keys_button) # เพิ่มปุ่มเช็คคีย์ทั้งหมด
        admin_view.add_item(add_key_button)  # เพิ่มปุ่มเพิ่มคีย์
        admin_view.add_item(delete_key_button)  # เพิ่มปุ่มลบคีย์

        # ส่งข้อความพร้อมกับปุ่มใน admin view
        await interaction.response.send_message("นี่คือ Admin Panel:", view=admin_view, ephemeral=True)


@client.event
async def on_message(message):
    if message.content.lower() == "!เติมเงิน":
        group_id = message.guild.id  # ดึง ID ของกลุ่ม

        embed = discord.Embed(
            title="เติมเงิน TrueMoney",
            description="เลือกการดำเนินการที่ต้องการ",
            color=discord.Color.blue()
        )

        # สร้างปุ่มต่างๆ
        button_recharge = Button(label="เติมเงิน", style=discord.ButtonStyle.green)
        check_balance_button = CheckBalanceButton(group_id)
        redeem_code_button = RedeemCodeButton(group_id)
        register_button = RegisterButton(group_id)  # ปุ่มลงทะเบียน

        # check_history_button = CheckHistoryButton(phone_number="0841304874")  # เปลี่ยนเบอร์ตามต้องการ
        # add_key_button = AddKeyButton(group_id)  # เพิ่มปุ่มเพิ่มคีย์
        # show_keys_button = ShowKeysButton(group_id)  # ปุ่มใหม่เพื่อแสดงคีย์ทั้งหมด

        async def button_callback(interaction: discord.Interaction):
            modal = GiftLinkModal(group_id)
            await interaction.response.send_modal(modal)

        button_recharge.callback = button_callback

        view = View()
        view.add_item(button_recharge)
        view.add_item(check_balance_button)
        view.add_item(redeem_code_button)
        view.add_item(register_button)  # เพิ่มปุ่มลงทะเบียนใน view

        if message.author.id in ADMIN_IDS:
            # เพิ่มปุ่ม "Admin Panel" สำหรับแอดมิน
            admin_panel_button = AdminPanelButton()
            view.add_item(admin_panel_button)

        await message.channel.send(embed=embed, view=view)


client.run(TOKEN)
