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
            print(f"Lock acquired with key: {key}")
            return True
        return False

    def release(self, key, raise_error: bool = False) -> bool:
        if self._key == key:  # ตรวจสอบว่า key ตรงกับที่เก็บไว้หรือไม่
            self._lock.release()
            print(f"Lock released with key: {key}")
            return True
        if raise_error:
            raise RuntimeError('KeyLock.release called with a non-matching key!')
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
        print("Successfully acquired lock.")
        time.sleep(2)  # รอ 2 วินาทีเพื่อจำลองการทำงาน
        # ปลดล็อกด้วยคีย์ที่กำหนดใน config
        if key_lock.release(configured_key):
            print("Successfully released lock.")
    else:
        print("Failed to acquire lock.")

    # ทดสอบกรณีที่คีย์ไม่ตรงกันในการปลดล็อก
    if not key_lock.release('wrong_key', raise_error=True):
        print("Failed to release lock with wrong key.")

# เรียกใช้ฟังก์ชันทดสอบ
test_key_lock()