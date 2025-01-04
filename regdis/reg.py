import nextcord
from nextcord.ext import commands
import requests
import json
from capmonster_python import HCaptchaTask

config = json.load(open('config.json'))

def hcaptchabypassing(sitekey):
    capmonster = HCaptchaTask(config['capmonster_key'])
    task_id = capmonster.create_task('https://discord.com/', sitekey)
    result = capmonster.join_task_result(task_id)
    return result.get('gRecaptchaResponse')

bot = commands.Bot(
    command_prefix='!',
    intents=nextcord.Intents.all(),
    help_command=None
)

class Generator(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title='GZ SHOP | Generator Token')
        self.input1 = nextcord.ui.TextInput(label='ชื่อที่จะใช้แสดง',placeholder='xxxxxxxxxxxxxxxxxxxxx', max_length=10, required=True)
        self.input2 = nextcord.ui.TextInput(label='อีเมลหรือเบอร์โทรศัพท์มือถือ',placeholder='xxxxxxxxxxxxxxxxxxxxx', max_length=10, required=True)
        self.input3 = nextcord.ui.TextInput(label='ตั้งรหัสผ่าน',placeholder='xxxxxxxxxxxxxxxxxxxxx', max_length=20, required=True)
        # self.input2 = nextcord.ui.TextInput(label='โค้ดลิงก์เชิญ (ตัวอย่าง xrTcs02)',placeholder='xxxxxxxxxxxxxxxxxxxxx', max_length=10, required=True)
        self.add_item(self.input1)
        self.add_item(self.input2)
        self.add_item(self.input3)
    
    async def callback(self, interaction: nextcord.Interaction):
        msg = await interaction.response.send_message('## > [+] กำลังตรวจสอบชื่อผู้ใช้...', ephemeral=True)
        response1 = requests.get("https://discord.com/")
        cookie = response1.cookies.get_dict()
        cookie['locale'] = "us"
        __dcfduid = cookie['__dcfduid']
        __sdcfduid = cookie['__sdcfduid']
        __cfruid = cookie['__cfruid']
        headers_reg = {
            "accept": "/",
            "authority": "discord.com",
            "method": "POST",
            "path": "/api/v9/auth/register",
            "scheme": "https",
            "origin": "discord.com",
            "referer": "discord.com/register",
            "x-debug-options": "bugReporterEnabled",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-Type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9003 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36",
            "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDAzIiwib3NfdmVyc2lvbiI6IjEwLjAuMjIwMDAiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTA0OTY3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "cookie": f"__dcfduid={__dcfduid};__sdcfduid={__sdcfduid};_gcl_au=1.1.112584149.1686070530;OptanonConsent=isIABGlobal=false&datestamp=Tue+Jun+06+2023+23%3A55%3A30+GMT%2B0700+(%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%B2%E0%B8%AD%E0%B8%B4%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%88%E0%B8%B5%E0%B8%99)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2FADJqYCUD&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1;_ga=GA1.1.1610756780.1686070537;_ga_Q149DFWHT7=GS1.1.1686070536.1.0.1686070539.0.0.0;__cf_bm=btpRH4vTOEcwikDHB0QBu404QuPhOivnK86ngimpulA-1686711134-0-ATfCY3ZxHGCsLUjU9HVNEX3RRk45FFeLwMkv5r21pc1VyYri80f0okPZqwv5f9aPDA==;__cfruid={__cfruid}"
        }
        response = requests.get(f'https://discord.com/api/v9/unique-username/username-suggestions-unauthed?global_name={self.input1.value}',headers=headers_reg)
        if response.status_code == 200:
            if response.json()['username'] == None:
                return await msg.edit(content='## > ชื่อผู้ใช้นี้ไม่สามารถใช้งานได้')
            else:
                await msg.edit(content='## > [+] กำลังสร้างบัญชี...')
                responsee = requests.get("https://discordapp.com/api/v9/experiments", headers=headers_reg, allow_redirects=True).json()
                fingerprint = responsee["fingerprint"]
                username = response.json()['username']
                response2 = requests.post('https://discord.com/api/v9/auth/register',json={"fingerprint":fingerprint,"email":self.input2.value,"username":username,"global_name":username,"password":self.input3.value,"invite":None,"consent":True,"date_of_birth":"1998-05-05","gift_code_sku_id":None,"promotional_email_opt_in":True},headers=headers_reg)
                if response.status_code == 400:
                    site = response2.json()['captcha_sitekey']
                    await msg.edit(content='## > กำลังบายพาสแคปช่าโปรดรอ...')
                    headers_reg2 = {
                        "accept": "/",
                        "authority": "discord.com",
                        "method": "POST",
                        "path": "/api/v9/auth/register",
                        "scheme": "https",
                        "origin": "discord.com",
                        "x-fingerprint": fingerprint,
                        "referer": "discord.com/register",
                        "x-debug-options": "bugReporterEnabled",
                        "accept-language": "en-US,en;q=0.9",
                        "connection": "keep-alive",
                        "content-Type": "application/json",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9003 Chrome/91.0.4472.164 Electron/13.4.0 Safari/537.36",
                        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDAzIiwib3NfdmVyc2lvbiI6IjEwLjAuMjIwMDAiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTA0OTY3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-origin",
                        "cookie": f"__dcfduid={__dcfduid};__sdcfduid={__sdcfduid};_gcl_au=1.1.112584149.1686070530;OptanonConsent=isIABGlobal=false&datestamp=Tue+Jun+06+2023+23%3A55%3A30+GMT%2B0700+(%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%B2%E0%B8%AD%E0%B8%B4%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%88%E0%B8%B5%E0%B8%99)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2FADJqYCUD&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1;_ga=GA1.1.1610756780.1686070537;_ga_Q149DFWHT7=GS1.1.1686070536.1.0.1686070539.0.0.0;__cf_bm=btpRH4vTOEcwikDHB0QBu404QuPhOivnK86ngimpulA-1686711134-0-ATfCY3ZxHGCsLUjU9HVNEX3RRk45FFeLwMkv5r21pc1VyYri80f0okPZqwv5f9aPDA==;__cfruid={__cfruid}"
                    }
                    

                    response3 = requests.post('https://discord.com/api/v9/auth/register',json={"fingerprint":fingerprint,"email":self.input2.value,"username":username,"global_name":username,"password":self.input3.value,"invite":None,"consent":True,"date_of_birth":"1998-05-05","gift_code_sku_id":None,"promotional_email_opt_in":True,'captcha_key': hcaptchabypassing(site)},headers=headers_reg2)
                    if response3.status_code == 400:
                        return await msg.edit(content='## > ไม่สามารถสร้างบัญชีให้คุณได้!')
                    elif response3.status_code == 429:
                        return await msg,edit(content='## > ขณะนี้ติดดีเลย์กรุณารอ!')
                    else:
                        token = response3.json()['token']
                        embed = nextcord.Embed(
                            title='สร้างบัญชีให้คุณเรียบร้อยแล้ว (ไม่ได้ยืนยันเมล-เบอร์)',
                            description=f'> EMAIL: {self.input2.value}\n> Password: {self.input3.value}\n> Tokens: {token}',
                            color=0x3aeb34
                        )
                        return await msg.edit(content=None, embed=embed)
                elif response2.status_code == 200 or response2.status_code == 201 or response2.status_code == 204:
                    token = response2.json()['token']
                    embed = nextcord.Embed(
                        title='สร้างบัญชีให้คุณเรียบร้อยแล้ว',
                        description=f'Email: {self.input2.value}\nPassword: {self.input3.value}\nTokens: {token}',
                        color=0x3aeb34
                    )
                    return await msg.edit(content=None, embed=embed)
                else:
                    embed = nextcord.Embed(
                        title='เกิดข้อผิดพลาด',
                        description=f'เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุหรืออาจจะเป็นเพราะติดดีเลย์และอีเมลไม่พร้อมใช้งาน กรุณารอและลองใหม่อีกครั้ง',
                        color=0xff0000
                    )
                    return await msg.edit(content=None, embed=embed)
    


class Button(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @nextcord.ui.button(
        label='สร้างบัญชี',
        style=nextcord.ButtonStyle.primary,
        row=1
    )
    async def callback(self, button, interaction: nextcord.Interaction):
        return await interaction.response.send_modal(Generator())
        
    
    
@bot.event
async def on_ready():
    bot.add_view(Button())
    print('Connected!')


@bot.command(pass_context=True)
async def gen(interaction: nextcord.Interaction):
    await interaction.message.delete()
    if interaction.author.name == config['admin_name']:
        embed = nextcord.Embed(
            title='Discord Token Generator',
            description='ระบบนี้เป็นระบบออโต้สร้างบัญชี Discord\n## คุณสมบัติ\n > ยืนยันเมลอัตโนมัติ\n> ต้องเตรียมเบอร์ไว้สำหรับยืนยัน\n> ใช้เวลาการสร้างในแต่ละรอบ 2-3 นาที\n> ได้รับ Email Password Token\n\n**ยศสมาชิกธรรมดาสามารถใช้งานได้เพียง 1 ครั้ง หากต้องการใช้งานได้มากกว่า 1 ครั้งให้ดูเรทราคาการเติมเงินเพื่อซื้อเครดิตเข้าใช้งาน**',
            color=0x3700ff
        )
        embed.set_image(url='https://cdn.discordapp.com/attachments/1182606424963022859/1183812498709807134/discord.gif?ex=6589b24d&is=65773d4d&hm=e2e1da04b80ddeb1faed6efc9ed419749165ff3df2564d5346c77f792c7c749d&')
        await interaction.send(embed=embed, view=Button())

bot.run(config['token'])







