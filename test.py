#main
import sys, os
from openpyxl import load_workbook
import time
from copy import copy
import json
import asyncio
from datetime import datetime, timezone, date
# telegram
import python_socks
from telethon import TelegramClient, sync, utils, connection
import telethon
#crypto
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Pack:
    def __init__(self, name_dir=None, name_file=None, size_file=None, high=None):
        self.name = ""
        self.high = high
        for i in name_dir:
            if i == "-":
                break
            self.name += i 
        self.name_dir = name_dir
        self.name_file = name_file
        self.size_file = size_file

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
                proxy_secret = self.any_way_answer("Нужен прокси secret: ")
            else:
                proxy_host = None
                proxy_port = None
                proxy_secret = None
            name = None
            path = None
            target_date = None
            self.data = {
                "password": password,
                "api_id": api_id,
                "api_hash": api_hash,
                "is_proxy": is_proxy,
                "proxy_host": proxy_host,
                "proxy_port": proxy_port,
                "proxy_secret": proxy_secret,
                "name": name,
                "path": path,
                "date": target_date
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
                print(f"    Прокси HOST: {self.data['proxy_host']}\n    Прокси PORT: {self.data['proxy_port']}\n Проки SECRET: {self.data['proxy_secret']}")
            
    
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
                self.data['proxy_secret'] = self.not_any_way_answer("Новый прокси secret: ", self.data['proxy_secret'])
        self.data['name'] = self.not_any_way_answer(f"Имя файла xml({self.data['name']}): ", self.data['name'])
        self.data['path'] = self.not_any_way_answer(f"Путь до директории({self.data['path']}): ", self.data['path'])
        self.data['date'] = self.not_any_way_answer(f"Дата ({self.data['date']}): ", self.data['date'])
            
        
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
    def __init__(self, storage):
        self.storage = storage
        self.packed = []
        if self.storage.data["is_proxy"]:
            
            mtproto = (self.storage.data["proxy_host"], int(self.storage.data["proxy_port"]), self.storage.data["proxy_secret"])
            mtproto_connection = connection.tcpmtproxy.ConnectionTcpMTProxyAbridged
            self.client = telethon.TelegramClient('session',api_id=self.storage.data["api_id"],api_hash=self.storage.data["api_hash"],proxy=mtproto,connection=mtproto_connection)

        else:
            self.client = TelegramClient('autofillgeo', self.storage.data["api_id"], self.storage.data["api_hash"])

        with self.client:
            self.client.loop.run_until_complete(self.start_client())
            self.client.loop.run_until_complete(self.find_message())

    async def start_client(self):
        await self.client.start()
        me = await self.client.get_me()
        print(f'Привет, {me.first_name}! Соединение успешно установлено.')

        

    async def find_message(self):
        try:
            target_date = datetime.strptime(self.storage.data["date"], "%Y-%m-%d").date()
        except:
            raise ValueError("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
        
        start_of_day = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        end_of_day = datetime.combine(target_date, datetime.max.time(), tzinfo=timezone.utc)

        os.makedirs(self.storage.data["path"], exist_ok=True)
        async for message in self.client.iter_messages('me', offset_date=end_of_day):
            if message.date < start_of_day:
                break
            text = message.text.split(" ")
            if text[-1].isdigit() and text[0].split("-")[0] in ["ТСП-ОП", "ОП", "ГТСП"] and message.photo:
                name_point = " ".join(text[:-1])
                high_point = int(text[-1])
                print(f"Найдено имя: {name_point}, высота {high_point}")
                full_path =  f"{self.storage.data['path']}\\{name_point}"
                os.makedirs(full_path, exist_ok=True)
                self.packed.append(Pack(name_dir=name_point, high=high_point))
                idx = 1
                async for msg in self.client.iter_messages('me', limit=60, min_id=message.id - 30, max_id=message.id + 30):
                    full_path_img = os.path.join(full_path, f"{idx}.jpg")
                    if msg.grouped_id == message.grouped_id:
                        if not os.path.isfile(full_path_img):
                            await self.client.download_media(msg, file=full_path_img)
                        idx += 1
                        await asyncio.sleep(0.5)
        
        
            

class AutoXML:

    def __init__(self):
        self.storage = SafetyStorage()
        self.tg = TelegramConnect(self.storage)
        self.source_path = "\\".join(os.path.abspath(__file__).split("\\")[:-1])

    def search_into_directory(self, path):
        for dir_ in os.listdir(path):
            dir_path = f"{path}\\{dir_}"
            if os.path.isdir(dir_path):
                
                file_name = []
                for name in os.listdir(dir_path):
                    if name[-4:] == ".jps":
                        file_name.append(name[:-4])

                if len(file_name) != 1:
                    raise ValueError(f"Слишком много файлов .jps в одной папке {dir_}")
                for pck in self.tg.packed:
                    if pck.name_dir == dir_:
                        pck.size_file = str(round(os.path.getsize(f"{dir_path}\\{file_name[0]}.jps") / 1024 / 1024, 1)).replace(",", ".")
                        pck.name_file = file_name[0]



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
        ws[f'G{number_string}'] = string.high
        ws[f'I{number_string}'] = string.size_file
                
                
        
    def run(self):
        input("Можно создать XML файл? ")
        self.search_into_directory(self.storage.data["path"])
        self.create_XML(self.tg.packed)
        


            

if __name__ == "__main__":
    auto_xml = AutoXML()
    auto_xml.run()
    time.sleep(3)
