#main
import sys, os
from openpyxl import load_workbook
import time
from copy import copy
import json
# telegram
import python_socks
from telethon import TelegramClient
#crypto
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Pack:
    def __init__(self, name_dir, name_file, size_file):
        self.name = ""
        for i in name_dir:
            if i == "-":
                break
            
            self.name += i 
        self.name_dir = name_dir
        self.name_file = name_file
        self.size_file = str(round(size_file / 1024 / 1024, 1)).replace(",", ".")
        print(self.name, name_dir, name_file, self.size_file)

class SafetyStorage:
    def __init__(self):
        if not os.path.exists('log.enc'):
            print("Файла log.bin нет, создаем...")
            password = self.any_way_answer("Новый пароль: ")
            api_id = self.any_way_answer("Новый API ID: ")
            api_hash = self.any_way_answer("Новый API HASH: ")
            is_proxy = bool(self.any_way_answer("Нужен прокси: "))
            if is_proxy:
                proxy_host = self.any_way_answer("Нужен прокси host: ")
                proxy_port = self.any_way_answer("Нужен прокси port: ")
            else:
                proxy_host = None
                proxy_port = None
            name = None
            path = None
            self.data = {
                "password": password,
                "api_id": api_id,
                "api_hash": api_hash,
                "is_proxy": is_proxy,
                "proxy_host": proxy_host,
                "proxy_port": proxy_port,
                "name": name,
                "path": path
            }
            self.save_data()
            return
            
        with open('log.enc', 'rb') as file:
            self.data_crypted = file.read()
        
        password = input("Пароль: ")
        used_salt = self.data_crypted[:16]
        data_crypted = self.data_crypted[16:]
        
        try:
            data = self.decrypt_data(data_crypted, password, used_salt)
            self.data = json.loads(data)
            print(f"Успешно расшифровано")
            
        except Exception as e:
            raise ValueError(f"\nОшибка расшифровки! Неверный пароль или данные повреждены. {e}")

        self.question_print_data()
        self.question_change_data()
        self.save_data()

    def save_data(self):
        data = json.dumps(self.data, ensure_ascii=False, indent=4)
        with open('log.enc', 'wb') as f:
            encrypted_data, salt = self.encrypt_data(data, self.data['password'])
            f.write(salt+encrypted_data)
            
    def any_way_answer(self, text):
        a = None
        while not a:
            a = input(text)
        return a

    def not_any_way_answer(self, text, a_):
        a = input(text)
        if a:
            return a
        return a_

    def question_print_data(self):
        if input("Вывести данные: "):
            print(f"    Пароль: {self.data['password']}\n    API ID: {self.data['api_id']}\n    API HASH: {self.data['api_hash']}")
            print(f"    Нужен ли прокси: {self.data['is_proxy']}")
            if self.data['is_proxy']:
                print(f"    Прокси HOST: {self.data['proxy_host']}\n    Прокси PORT: {self.data['proxy_port']}")
            
    
    def question_change_data(self):
        if input("Изменить что-то: "):
            self.data['password'] = self.not_any_way_answer("Новый пароль: ", self.data['password'])
            self.data['api_id'] = self.not_any_way_answer("Новый API ID: ", self.data['api_id'])
            self.data['api_hash'] = self.not_any_way_answer("Новый API HASH: ", self.data['api_hash'])
            is_proxy = input("Нужен прокси: ")
            if is_proxy == "no":
                self.data['is_proxy'] = False
            elif is_proxy == "yes" or self.data["is_proxy"]:
                self.data['is_proxy'] = True
                self.data['proxy_host'] = self.not_any_way_answer("Новый прокси host: ", self.data['proxy_host'])
                self.data['proxy_port'] = self.not_any_way_answer("Новый прокси port: ", self.data['proxy_port'])
        self.data['name'] = self.not_any_way_answer(f"Имя файла xml({self.data['name']}): ", self.data['name'])
        self.data['path'] = self.not_any_way_answer(f"Путь до директории({self.data['path']}): ", self.data['path'])
            
        
    def generate_key(self, password: str, salt: bytes) -> bytes:
        """Генерирует криптографический ключ на основе пароля и соли."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1_000_000, 
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_data(self, data: str, password: str) -> tuple[bytes, bytes]:
        """Шифрует данные по паролю. Возвращает (зашифрованные_данные, соль)."""
        salt = os.urandom(16) 
        key = self.generate_key(password, salt)
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data, salt

    def decrypt_data(self, encrypted_data: bytes, password: str, salt: bytes) -> str:
        """Расшифровывает данные, используя исходный пароль и соль."""
        key = self.generate_key(password, salt)
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode()
    
        
class TelegramConnect:
    def __init__(self):
        self.api_id = None
        self.api_hash = None
        self.proxy_type = python_socks.ProsyType.SOCK5
        self.proxy_host = "127.0.0.1"
        self.proxy_port = 1443
        self.proxy_user = None
        self.proxy_password = None

class AutoXML:

    def __init__(self):
        self.storage = SafetyStorage()
        self.source_path = "\\".join(os.path.abspath(__file__).split("\\")[:-1])

    def search_into_directory(self, path):
        list_= []
        for dir_ in os.listdir(path):
            dir_path = f"{path}\\{dir_}"
            if os.path.isdir(dir_path):
                
                file_name = []
                for name in os.listdir(dir_path):
                    if name[-4:] == ".jps":
                        file_name.append(name[:-4])

                if len(file_name) != 1:
                    raise ValueError(f"Слишком много файлов .jps в одной папке {dir_}")
                list_.append(Pack(dir_, file_name[0], os.path.getsize(f"{dir_path}\\{file_name[0]}.jps")))
        return list_


    def full_copy_paste(self, copy_target, paste_target):
        paste_target.value = copy_target.value
        paste_target.font = copy(copy_target.font)
        paste_target.fill = copy(copy_target.fill)
        paste_target.border = copy(copy_target.border)
        paste_target.alignment = copy(copy_target.alignment)
        paste_target.number_format = copy(copy_target.number_format)
        paste_target.protection = copy(copy_target.protection)

    def full_copy_paste_string(self, ws, copy_target_number, paste_target_number, length):
        for i in range(length):
            copy_ = ws.cell(row=copy_target_number, column=i+1)
            paste_ = ws.cell(row=paste_target_number, column=i+1)
            self.full_copy_paste(copy_, paste_)
        

    def create_XML(self, list_info):
        wb = load_workbook(f"{self.source_path}\\pattern.xlsx")
        ws = wb.active  
        ws.title = "Данные координирования"

        number_of_end_string = 5+len(list_info)
        
        self.full_copy_paste(ws["A5"], ws[f"A{number_of_end_string}"])
        self.full_copy_paste(ws["B5"], ws[f"B{number_of_end_string}"])
        ws.unmerge_cells("B5:I5") 
        ws.delete_rows(idx=5)
        ws.merge_cells(f"B{number_of_end_string-1}:I{number_of_end_string-1}")
        ws.row_dimensions[5].height = 15
        for i, info in enumerate(list_info):
            self.full_copy_paste_string(ws, 4, 4+i, 10)
            self.fill_string(ws, 4+i, info)
            

        wb.save(f"{self.storage.data['path']}\\{self.storage.data['name']}.xlsx")

    def fill_string(self, ws, number_string, string):
        ws[f'A{number_string}'] = string.name
        ws[f'B{number_string}'] = string.name_dir
        ws[f'H{number_string}'] = string.name_file
        ws[f'I{number_string}'] = string.size_file
                
                
        
    def run(self):
        list_information = self.search_into_directory(self.storage.data["path"])
        self.create_XML(list_information)
        


            

if __name__ == "__main__":
    auto_xml = AutoXML()
    auto_xml.run()
    time.sleep(3)
