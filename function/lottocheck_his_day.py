import datetime

# ฟังก์ชันสุ่มรางวัลที่ปรับปรุงแล้ว
@tasks.loop(minutes=RAFFLE_INTERVAL)
async def raffle():
    today_date = datetime.datetime.today().date()  # วันที่ปัจจุบัน

    for guild in client.guilds:
        group_id = guild.id

        user_data = load_data(group_id)
        winners = {}  # คำสั่งเก็บผู้ถูกรางวัลสำหรับแต่ละหมายเลข
        all_numbers = []  # รายการเก็บหมายเลขทั้งหมดที่จะใช้ในการสุ่ม
        raffle_results = []  # รายการเก็บผลรางวัลทั้งหมด

        # กำหนดจำนวนรางวัลที่แต่ละหมายเลขจะได้รับ
        prize_amounts = [prize_1, prize_1, prize_3, prize_4, prize_5]  

        # สร้างหมายเลขทั้งหมดที่เป็นไปได้สำหรับการสุ่ม
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
            # ตรวจสอบว่าการซื้อเป็นวันนี้หรือไม่
            purchase_date = datetime.datetime.fromtimestamp(data.get('created_at')).date()
            if purchase_date == today_date and random.random() < (RAFFLE_CHANCE / 100):
                winner_number = "".join([str(random.randint(0, 9)) for _ in range(NUM_DIGITS)])
                if winner_number not in winners:
                    winners[winner_number] = [user_id]
                else:
                    winners[winner_number].append(user_id)

        # ตรวจสอบว่าใครถูกรางวัลบ้าง
        for i, number in enumerate(all_numbers):
            # กำหนดประเภทของรางวัลที่จะแสดง
            if i < 5:
                prize_type = f"รางวัลที่ {i + 1}: "
            elif i < 7:
                prize_type = f"รางวัลเลขท้าย 3 ตัว {i - 4}: "
            else:
                prize_type = f"รางวัลเลขท้าย 2 ตัว: "

            # หากมีผู้ถูกรางวัลให้แสดงข้อมูลผู้ถูกรางวัล
            if number in winners:
                winner_mentions = " ".join([f"<@{user_id}>" for user_id in winners[number]])
                prize_amount = prize_amounts[i] if i < len(prize_amounts) else RAFFLE_3DIGIT_PRIZE if len(all_numbers) - i <= 3 else RAFFLE_2DIGIT_PRIZE
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