import subprocess
import os
from colorama import Fore, Style
from tqdm import tqdm

def autoupdate_repository():
    repo_dir = '.'  # ระบุให้ใช้ . (โฟลเดอร์ปัจจุบัน)
    repo_url = 'https://github.com/earthkcc147/Redeem-Dis.git'

    # ฟังก์ชันที่ช่วยแสดง progress bar สำหรับคำสั่ง git clone
    def clone_with_progress(repo_url, repo_dir):
        # ใช้ subprocess กับ tqdm เพื่อแสดง progress bar
        process = subprocess.Popen(['git', 'clone', repo_url, repo_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # อ่านข้อมูลจาก stdout และอัปเดต progress bar
        for line in process.stdout:
            line = line.decode('utf-8')
            if 'Receiving objects' in line:
                # ค้นหาข้อความที่บอกสถานะการรับข้อมูล (เพื่อให้ใช้กับ progress bar)
                # กำหนดให้รับข้อมูลขนาดไฟล์ที่ดึงมา
                if 'Receiving objects' in line:
                    start_index = line.find('[') + 1
                    end_index = line.find(']')
                    progress_str = line[start_index:end_index]
                    progress_percentage = int(progress_str.replace('%', '').strip())
                    tqdm.write(f"กำลังดาวน์โหลด: {progress_percentage}%")
                    tqdm.update(progress_percentage)
        process.wait()

    # เช็คว่าโฟลเดอร์ repository มีอยู่แล้วหรือไม่
    if os.path.exists(repo_dir):
        print(Fore.YELLOW + "🎉 พบ repository ที่มีอยู่แล้ว กำลังดึงข้อมูลล่าสุด...")
        # ใช้คำสั่ง git fetch เพื่อดึงการเปลี่ยนแปลงทั้งหมด
        subprocess.run(['git', '-C', repo_dir, 'fetch'], check=True)  
        # รีเซ็ตไฟล์ทั้งหมดให้ตรงกับ branch main
        subprocess.run(['git', '-C', repo_dir, 'reset', '--hard', 'origin/main'], check=True)
        print(Fore.GREEN + "✔️ การอัปเดตสำเร็จ!")
    else:
        print(Fore.RED + "❌ ไม่พบ repository กำลังทำการ clone...")
        # ใช้ฟังก์ชัน clone_with_progress เพื่อแสดง progress bar
        with tqdm(total=100, desc="ดาวน์โหลด repository", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            clone_with_progress(repo_url, repo_dir)
        print(Fore.GREEN + "✔️ การ clone สำเร็จ!")

# if __name__ == '__main__':
    # autoupdate_repository()