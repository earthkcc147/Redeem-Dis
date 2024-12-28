from threading import Lock
from typing import Optional
import time

# กำหนดคอนฟิกเพื่อให้สามารถกำหนดค่า key ได้
config = {
    'lock_key': 'gmr'  # คีย์ที่กำหนดใน config
}

class KeyLock:
    def __init__(self):
        self._lock = Lock()  # สร้างอ็อบเจกต์ Lock
        self._key: Optional[str] = None  # กำหนดตัวแปรสำหรับเก็บคีย์

    def acquire(self, key: 'str', blocking: bool = True, timeout: float = 10.0) -> bool:
        if self._lock.acquire(blocking=blocking, timeout=timeout):
            self._key = key  # เก็บคีย์เมื่อได้รับการล็อก
            print(f"ล็อกได้รับการยึดด้วยคีย์: {key}")
            return True
        return False

    def release(self, raise_error: bool = False) -> bool:
        # รับคีย์จากผู้ใช้ในฟังก์ชัน release
        key = input("กรุณากรอกคีย์เพื่อปลดล็อก: ")
        
        if self._key == key:  # ตรวจสอบว่า key ตรงกับที่เก็บไว้หรือไม่
            self._lock.release()
            print(f"ปลดล็อกด้วยคีย์: {key}")
            return True
        if raise_error:
            raise RuntimeError('KeyLock.release ถูกเรียกด้วยคีย์ที่ไม่ตรงกัน!')
        return False

    def locked(self):
        return self._lock.locked()  # ตรวจสอบสถานะการล็อก

# ทดสอบการใช้งาน KeyLock
def test_key_lock():
    key_lock = KeyLock()

    # ใช้คีย์จากคอนฟิกเพื่อทำการล็อก
    configured_key = config['lock_key']

    # ล็อกด้วยคีย์ที่กำหนดใน config
    if key_lock.acquire(configured_key):
        print("ล็อกได้รับการยึดสำเร็จ.")
        time.sleep(2)  # รอ 2 วินาทีเพื่อจำลองการทำงาน
        # ปลดล็อกโดยการรับคีย์จากผู้ใช้
        if key_lock.release(raise_error=True):
            print("ปลดล็อกสำเร็จ.")
    else:
        print("ไม่สามารถยึดล็อกได้.")

# เรียกใช้ฟังก์ชันทดสอบ
test_key_lock()