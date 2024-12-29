import datetime

# ฟังก์ชันสุ่มรางวัลที่ปรับปรุงแล้ว
@tasks.loop(minutes=RAFFLE_INTERVAL)
async def raffle():
    today_month = datetime.datetime.today().month  # เดือนปัจจุบัน
    today_year = datetime.datetime.today().year    # ปีปัจจุบัน

    for guild in client.guilds:
        group_id = guild.id

        user_data = load_data(group_id)
        winners = {}  # คำสั่งเก็บผู้ถูกรางวัลสำหรับแต่ละหมายเลข
        all_numbers = []  # รายการเก็บหมายเลขทั้งหมดที่จะใช้ในการสุ่ม
        raffle_results = []  # รายการเก็บผลรางวัลทั้งหมด

        # กำหนดจำนวนรางวัลที่แต่ละหมายเลขจะได้รับ
        prize_amounts = [prize_1, prize_1, prize_3, prize_4, prize_5]  

        # สร้างหมายเลขรางวัลที่ 1
        prize_1_number = "".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)])
        all_numbers.append(prize_1_number)

        # สร้างหมายเลขรางวัลใกล้เคียงรางวัลที่ 1
        near_prize_1_numbers = [
            str(int(prize_1_number) - 1).zfill(NUM_DIGITS),
            str(int(prize_1_number) + 1).zfill(NUM_DIGITS)
        ]
        all_numbers.extend(near_prize_1_numbers)

        # สร้างหมายเลขรางวัลอื่นๆ
        for i in range(1, 6):  # กำหนดจำนวนรางวัลที่ต้องการ (เช่น 5 รางวัล)
            all_numbers.append("".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)]))

        # เพิ่มหมายเลขสำหรับรางวัลเลขท้าย 3 ตัว (2 รางวัล)
        for _ in range(2):
            last_three_digits = "".join([str(random.randint(0, 9)) for _ in range(3)])
            all_numbers.append(last_three_digits)

        # เพิ่มหมายเลขสำหรับรางวัลเลขท้าย 2 ตัว (1 รางวัล)
        last_two_digits = "".join([str(random.randint(0, 9)) for _ in range(2)])
        all_numbers.append(last_two_digits)

        # เลือกผู้ถูกรางวัลโดยมีโอกาส 10% สำหรับแต่ละผู้ใช้
        for user_id, data in user_data.items():
            # ตรวจสอบว่าเดือนและปีของการซื้อเป็นเดือนและปีปัจจุบันหรือไม่
            purchase_month = datetime.datetime.fromtimestamp(data.get('created_at')).month
            purchase_year = datetime.datetime.fromtimestamp(data.get('created_at')).year

            if purchase_month == today_month and purchase_year == today_year and random.random() < (RAFFLE_CHANCE / 100):
                winner_number = "".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)])
                if winner_number not in winners:
                    winners[winner_number] = [user_id]
                else:
                    winners[winner_number].append(user_id)

        # ตรวจสอบว่าใครถูกรางวัลบ้าง
        for i, number in enumerate(all_numbers):
            # กำหนดประเภทของรางวัลที่จะแสดง
            if i == 0:
                prize_type = "รางวัลที่ 1: "
                prize_amount = prize_1
            elif i == 1 or i == 2:
                prize_type = "รางวัลใกล้เคียงรางวัลที่ 1: "
                prize_amount = near_prize_1
            elif i < 7:
                prize_type = f"รางวัลที่ {i + 1}: "
                prize_amount = prize_amounts[i]
            elif i < 9:
                prize_type = f"รางวัลเลขท้าย 3 ตัว {i - 6}: "
                prize_amount = RAFFLE_3DIGIT_PRIZE
            else:
                prize_type = "รางวัลเลขท้าย 2 ตัว: "
                prize_amount = RAFFLE_2DIGIT_PRIZE

            # หากมีผู้ถูกรางวัลให้แสดงข้อมูลผู้ถูกรางวัล
            if number in winners:
                winner_mentions = " ".join([f"<@{user_id}>" for user_id in winners[number]])
                raffle_results.append(f"{prize_type}{winner_mentions} - หมายเลข: {number} - รับเงิน {prize_amount} บาท")

                # เพิ่มยอดเงินให้กับผู้ถูกรางวัล
                for user_id in winners[number]:
                    if user_id in user_data:
                        user_data[user_id]["balance"] += prize_amount
                        save_data(user_data, group_id)

            else:
                # หากไม่มีผู้ถูกรางวัล
                raffle_results.append(f"{prize_type}ไม่มีผู้ที่ถูกรางวัล - หมายเลข: {number}")

        # สร้าง Embed เพื่อประกาศผลรางวัล
        embed = discord.Embed(
            title="ประกาศผลรางวัลล็อตเตอรี่",
            description="ผลรางวัลทั้งหมด:\n" + "\n".join(raffle_results),
            color=discord.Color.gold()
        )

        # ส่งผลรางวัลในช่อง 'lottery'
        channel = discord.utils.get(guild.text_channels, name="lottery")
        if channel:
            await channel.send(embed=embed)