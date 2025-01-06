import random
import ast
import re

# ฟังก์ชันสำหรับเข้ารหัสโค้ด
def rename_code(code):
    pairs = {}
    used = set()
    code = remove_docs(code)  # ลบ comment และ docstring ด้วยฟังก์ชันใหม่
    parsed = ast.parse(code)

    # ค้นหาฟังก์ชัน, คลาส และอาร์กิวเมนต์ในโค้ด
    funcs = {node for node in ast.walk(parsed) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    classes = {node for node in ast.walk(parsed) if isinstance(node, ast.ClassDef)}
    args = {node.id for node in ast.walk(parsed) if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load)}

    # เปลี่ยนชื่อฟังก์ชัน
    for func in funcs:
        newname = generate_random_name()
        while newname in used:
            newname = generate_random_name()
        used.add(newname)
        pairs[func.name] = newname

    # เปลี่ยนชื่อคลาส
    for _class in classes:
        newname = generate_random_name()
        while newname in used:
            newname = generate_random_name()
        used.add(newname)
        pairs[_class.name] = newname

    # เปลี่ยนชื่ออาร์กิวเมนต์
    for arg in args:
        newname = generate_random_name()
        while newname in used:
            newname = generate_random_name()
        used.add(newname)
        pairs[arg] = newname

    # แทนที่ชื่อเดิมในโค้ด
    for key, value in pairs.items():
        code = re.sub(r"\b" + re.escape(key) + r"\b", value, code)

    return code

def generate_random_name():
    """
    ฟังก์ชันสำหรับสุ่มชื่อใหม่ที่ประกอบด้วยตัวอักษร 'I' และ 'l' ขนาดระหว่าง 8 ถึง 20 ตัว
    """
    return "".join(random.choice(["I", "l"]) for _ in range(random.randint(8, 20)))

def remove_docs(source):
    """
    ลบ docstring และ comment ออกจากโค้ด Python
    โดยจะจัดการกับภาษาไทยใน docstring และคอมเมนต์ด้วย
    """
    try:
        # ใช้ ast เพื่อจัดการ docstring
        parsed = ast.parse(source)
        for node in ast.walk(parsed):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                node.body = [stmt for stmt in node.body if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Str)]
        source = ast.unparse(parsed)  # แปลงกลับเป็น source code

        # ลบ comment ด้วย regex (คอมเมนต์ภาษาไทยก็จะถูกลบ)
        source = re.sub(r"#.*", "", source)  # ลบ comment ทั้งบรรทัดที่เริ่มต้นด้วย #
        
        # จัดการ docstring ภาษาไทย (หากมีการใช้ข้อความภาษาไทยใน docstring)
        source = re.sub(r'"""(.*?)"""', '', source, flags=re.DOTALL)
        source = re.sub(r"'''(.*?)'''", '', source, flags=re.DOTALL)
        
        return source
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการลบ docstring: {e}")
        return source

# ตัวอย่างการใช้ฟังก์ชัน
code = '''
def example_function(arg1, arg2):
    # นี่คือลายละเอียด
    return arg1 + arg2

class MyClass:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}")
'''

encoded_code = rename_code(code)
print(encoded_code)